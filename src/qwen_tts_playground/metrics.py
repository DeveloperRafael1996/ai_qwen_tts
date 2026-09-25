"""Pure helpers for TTS performance metrics (RTF, TTFA, percentiles)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

TTFA_UNAVAILABLE_REASON = "model API does not expose first audio chunk"


def audio_duration_seconds(num_samples: int, sample_rate: int) -> float:
    """Real duration of a PCM buffer: samples / sample_rate."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    if num_samples < 0:
        raise ValueError("num_samples must not be negative")
    return num_samples / sample_rate


def real_time_factor(generation_seconds: float, audio_seconds: float) -> float:
    """RTF = generation_time / audio_duration (< 1 is faster than real time)."""
    if audio_seconds <= 0:
        return math.inf
    return generation_seconds / audio_seconds


def ttfa_ms(start: float, first_chunk_at: float | None) -> float | None:
    """Milliseconds from `start` to the first audio chunk (both `perf_counter` values).

    Returns None when no first-chunk timestamp exists (no real streaming), so
    callers never report total generation time as if it were TTFA.
    """
    if first_chunk_at is None:
        return None
    if first_chunk_at < start:
        raise ValueError("first_chunk_at must not precede start")
    return (first_chunk_at - start) * 1000.0


def percentile(values: Sequence[float], pct: float) -> float:
    """Linear-interpolated percentile (numpy's default), pct in [0, 100]."""
    if not values:
        raise ValueError("percentile of an empty sequence")
    if not 0 <= pct <= 100:
        raise ValueError("pct must be within [0, 100]")
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct / 100
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)


@dataclass(frozen=True)
class Percentiles:
    p50: float
    p95: float
    p99: float


def summarize(values: Sequence[float]) -> Percentiles:
    return Percentiles(
        p50=percentile(values, 50),
        p95=percentile(values, 95),
        p99=percentile(values, 99),
    )


@dataclass(frozen=True)
class RequestMetrics:
    """Metrics of one generation. Holds only the text length, never the text."""

    model: str
    gpu: str
    attention: str
    text_characters: int
    generation_time_seconds: float
    audio_duration_seconds: float
    ttfa_ms: float | None = None

    @property
    def rtf(self) -> float:
        return real_time_factor(self.generation_time_seconds, self.audio_duration_seconds)

    def format_log(self) -> str:
        ttfa = f"{self.ttfa_ms:.1f}" if self.ttfa_ms is not None else "N/A"
        lines = [
            "TTS PERFORMANCE",
            f"model={self.model}",
            f"gpu={self.gpu}",
            f"attention={self.attention}",
            f"text_characters={self.text_characters}",
            f"ttfa_ms={ttfa}",
        ]
        if self.ttfa_ms is None:
            lines.append(f"ttfa_note={TTFA_UNAVAILABLE_REASON}")
        lines += [
            f"generation_time_ms={self.generation_time_seconds * 1000:.1f}",
            f"audio_duration_ms={self.audio_duration_seconds * 1000:.0f}",
            f"rtf={self.rtf:.3f}",
        ]
        return "\n".join(lines)
