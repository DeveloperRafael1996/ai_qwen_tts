"""Benchmark Qwen3-TTS latency (TTFA/generation time/RTF) and VRAM.

Usage:
    uv run python scripts/benchmark_tts.py --ref-audio ref.wav --ref-text "..."  (see --help)

The model is loaded once per attention mode, warmed up, then measured. Warm-up
runs are excluded from the statistics. `--attention both` runs the default
attention and FlashAttention back to back and prints a comparison table.
"""

from __future__ import annotations

import argparse
import gc
import logging
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import torch

from qwen_tts_playground.config import Settings
from qwen_tts_playground.metrics import TTFA_UNAVAILABLE_REASON, Percentiles, summarize
from qwen_tts_playground.models import TTSResult
from qwen_tts_playground.runtime import check_flash_attention, diagnose_environment, select_dtype
from qwen_tts_playground.tts_service import QwenTTSService, TTSServiceError

TEXTS: dict[str, str] = {
    "SHORT": "Hola, vamos a comenzar.",
    "MEDIUM": "Hola, vamos a comenzar con tu proceso de verificación de identidad.",
    "LONG": (
        "Hola, gracias por comunicarte con nosotros. Para continuar con tu proceso de "
        "verificación de identidad, necesitamos confirmar algunos datos personales. "
        "Por favor, ten a la mano tu documento de identidad y ubícate en un lugar con "
        "buena iluminación antes de comenzar."
    ),
}


@dataclass
class RunStats:
    attention: str
    model: str
    gpu: str
    results: list[TTSResult] = field(default_factory=list)
    vram_initial_mb: float = 0.0
    vram_loaded_mb: float = 0.0
    peak_allocated_mb: float = 0.0
    peak_reserved_mb: float = 0.0

    @property
    def generation(self) -> Percentiles:
        return summarize([r.generation_time_seconds for r in self.results])

    @property
    def rtf(self) -> Percentiles:
        return summarize([r.real_time_factor for r in self.results])

    @property
    def ttfa(self) -> Percentiles | None:
        values = [r.ttfa_ms for r in self.results if r.ttfa_ms is not None]
        return summarize(values) if values else None


def _mb(num_bytes: int) -> float:
    return num_bytes / (1024**2)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--model", choices=["base", "voicedesign", "customvoice"], default="base")
    p.add_argument("--attention", choices=["auto", "flash", "default", "both"], default="auto")
    p.add_argument("--iterations", type=int, default=20, help="measured requests per text length")
    p.add_argument("--warmup", type=int, default=3, help="untimed requests before measuring")
    p.add_argument("--language", default="Spanish")
    p.add_argument("--ref-audio", help="reference audio (required for --model base)")
    p.add_argument("--ref-text", help="transcript of --ref-audio (in-context cloning)")
    p.add_argument("--x-vector-only", action="store_true", help="clone from speaker embedding only")
    p.add_argument("--speaker", default="Ryan", help="speaker for --model customvoice")
    p.add_argument(
        "--instruct",
        default="Female adult voice, professional and warm, natural pace.",
        help="voice description for --model voicedesign",
    )
    args = p.parse_args(argv)
    if args.iterations < 1 or args.warmup < 0:
        p.error("--iterations must be >= 1 and --warmup >= 0")
    if args.model == "base":
        if not args.ref_audio:
            p.error("--model base requires --ref-audio (a 3+ second clip of the voice to clone)")
        if not args.x_vector_only and not args.ref_text:
            p.error("--model base requires --ref-text unless --x-vector-only is set")
    return args


def _build_service(args: argparse.Namespace, attention: str, output_dir: Path) -> QwenTTSService:
    settings = Settings(qwen_tts_attention=attention, output_dir=output_dir)
    source = {
        "base": settings.resolve_voice_clone_model_source,
        "voicedesign": settings.resolve_model_source,
        "customvoice": settings.resolve_custom_voice_model_source,
    }[args.model]()
    return QwenTTSService(settings, model_source=source)


def _generate(service: QwenTTSService, args: argparse.Namespace, text: str) -> TTSResult:
    if args.model == "base":
        return service.synthesize_voice_clone(
            text,
            args.language,
            args.ref_audio,
            ref_text=args.ref_text,
            x_vector_only_mode=args.x_vector_only,
        )
    if args.model == "voicedesign":
        return service.synthesize(text, args.language, args.instruct)
    return service.synthesize_custom_voice(text, args.language, args.speaker)


def run_benchmark(args: argparse.Namespace, attention: str) -> RunStats | None:
    cuda = torch.cuda.is_available()
    if attention == "flash":
        flash = check_flash_attention(cuda, select_dtype(cuda))
        if not flash.usable:
            print(f"FlashAttention unavailable ({flash.reason}); skipping the flash run.")
            return None

    with tempfile.TemporaryDirectory(prefix="qwen_tts_bench_") as tmp:
        service = _build_service(args, attention, Path(tmp))
        stats = RunStats(attention=attention, model="", gpu="CPU")

        if cuda:
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            stats.vram_initial_mb = _mb(torch.cuda.memory_allocated())

        service.load()
        stats.model = service.model_name
        stats.attention = service.attention_in_use
        stats.gpu = torch.cuda.get_device_name() if cuda else "CPU"
        if cuda:
            stats.vram_loaded_mb = _mb(torch.cuda.memory_allocated())

        print(f"Warm-up: {args.warmup} request(s), not measured")
        for i in range(args.warmup):
            _generate(service, args, TEXTS["MEDIUM"] if i % 2 else TEXTS["SHORT"])

        for name, text in TEXTS.items():
            print(f"Measuring {name} ({len(text)} chars) x {args.iterations}")
            for _ in range(args.iterations):
                stats.results.append(_generate(service, args, text))

        if cuda:
            stats.peak_allocated_mb = _mb(torch.cuda.max_memory_allocated())
            stats.peak_reserved_mb = _mb(torch.cuda.max_memory_reserved())

        del service
        gc.collect()
        if cuda:
            torch.cuda.empty_cache()
        return stats


def print_report(stats: RunStats) -> None:
    print("\nQwen3-TTS Benchmark")
    print(f"GPU: {stats.gpu}")
    print(f"Attention: {stats.attention}")
    print(f"Model: {stats.model}")
    print(f"\nRequests: {len(stats.results)}\n")

    print("TTFA")
    if stats.ttfa is None:
        print(f"  N/A ({TTFA_UNAVAILABLE_REASON})")
    else:
        t = stats.ttfa
        print(f"  p50: {t.p50:.0f} ms\n  p95: {t.p95:.0f} ms\n  p99: {t.p99:.0f} ms")

    g, r = stats.generation, stats.rtf
    print("\nGeneration Time")
    print(f"  p50: {g.p50:.2f} s\n  p95: {g.p95:.2f} s\n  p99: {g.p99:.2f} s")
    print("\nRTF")
    print(f"  p50: {r.p50:.2f}\n  p95: {r.p95:.2f}\n  p99: {r.p99:.2f}")

    print("\nBy text length (p50 generation / p50 RTF)")
    per_len = len(stats.results) // len(TEXTS)
    for i, name in enumerate(TEXTS):
        chunk = stats.results[i * per_len : (i + 1) * per_len]
        gen = summarize([c.generation_time_seconds for c in chunk]).p50
        rtf = summarize([c.real_time_factor for c in chunk]).p50
        print(f"  {name:<7} {gen:6.2f} s   RTF {rtf:.2f}")

    print("\nVRAM (MB)")
    print(f"  initial:        {stats.vram_initial_mb:8.0f}")
    print(f"  after load:     {stats.vram_loaded_mb:8.0f}")
    print(f"  peak allocated: {stats.peak_allocated_mb:8.0f}")
    print(f"  peak reserved:  {stats.peak_reserved_mb:8.0f}")


def print_comparison(default: RunStats, flash: RunStats) -> None:
    def ttfa(s: RunStats, attr: str) -> str:
        return f"{getattr(s.ttfa, attr):.0f} ms" if s.ttfa else "N/A"

    rows = [
        ("TTFA p50", ttfa(default, "p50"), ttfa(flash, "p50")),
        ("TTFA p95", ttfa(default, "p95"), ttfa(flash, "p95")),
        ("RTF p50", f"{default.rtf.p50:.2f}", f"{flash.rtf.p50:.2f}"),
        ("RTF p95", f"{default.rtf.p95:.2f}", f"{flash.rtf.p95:.2f}"),
        ("Generation p50", f"{default.generation.p50:.2f} s", f"{flash.generation.p50:.2f} s"),
        ("Generation p95", f"{default.generation.p95:.2f} s", f"{flash.generation.p95:.2f} s"),
        ("Peak VRAM", f"{default.peak_allocated_mb:.0f} MB", f"{flash.peak_allocated_mb:.0f} MB"),
    ]
    print("\n" + f"{'':<16}{'DEFAULT':>14}{'FLASH ATTENTION':>20}")
    for label, a, b in rows:
        print(f"{label:<16}{a:>14}{b:>20}")


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.WARNING)
    args = parse_args(argv)
    print(diagnose_environment(), "\n")
    try:
        return _run(args)
    except TTSServiceError as exc:
        print(f"Benchmark aborted: {exc}", file=sys.stderr)
        return 1


def _run(args: argparse.Namespace) -> int:

    if args.attention == "both":
        default = run_benchmark(args, "default")
        flash = run_benchmark(args, "flash")
        if default:
            print_report(default)
        if flash:
            print_report(flash)
        if default and flash:
            print_comparison(default, flash)
        return 0 if default else 1

    stats = run_benchmark(args, args.attention)
    if stats is None:
        return 1
    print_report(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
