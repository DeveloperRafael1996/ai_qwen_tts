"""Encapsulates loading and running the Qwen3-TTS VoiceDesign model.

The model is loaded exactly once (see `QwenTTSService.load`) and every
subsequent `synthesize()` call reuses the already-loaded weights. GPU
inference is protected by a lock so that concurrent UI clicks cannot launch
overlapping `generate()` calls on the same model instance.
"""

from __future__ import annotations

import logging
import re
import threading
import time
import traceback
from datetime import datetime
from importlib.util import find_spec
from pathlib import Path

import soundfile as sf
import torch

from qwen_tts_playground.config import Settings
from qwen_tts_playground.models import TTSResult

logger = logging.getLogger(__name__)


class TTSServiceError(Exception):
    """Base class for all playground/TTS service errors."""


class ModelNotFoundError(TTSServiceError):
    """Raised when neither a local model directory nor a valid repo id is usable."""


class MissingModelFilesError(TTSServiceError):
    """Raised when the local model directory exists but is missing required files."""


class InvalidTextError(TTSServiceError):
    """Raised when the text to synthesize is empty or invalid."""


class InvalidLanguageError(TTSServiceError):
    """Raised when the requested language is not one of the supported languages."""


class GenerationError(TTSServiceError):
    """Raised when the underlying model fails to generate audio."""


class CudaOutOfMemoryError(TTSServiceError):
    """Raised when CUDA runs out of memory during generation."""


SUPPORTED_LANGUAGES = {"spanish", "portuguese", "english"}

_FILENAME_UNSAFE_RE = re.compile(r"[^a-z0-9_]+")


def sanitize_filename_component(value: str) -> str:
    """Lowercase, replace spaces/accents-unsafe chars, collapse repeats."""
    value = value.strip().lower().replace(" ", "_")
    value = _FILENAME_UNSAFE_RE.sub("_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown"


def build_output_path(output_dir: Path, language: str, accent: str, gender: str) -> Path:
    """Build a unique, sanitized output path under `output_dir`.

    Filename format: `{language}_{accent}_{gender}_{timestamp}.wav`.
    If the exact path already exists (same-second collision), a numeric
    suffix is appended instead of overwriting.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    lang_part = sanitize_filename_component(language)
    accent_part = sanitize_filename_component(accent)
    gender_part = sanitize_filename_component(gender)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    base_name = f"{lang_part}_{accent_part}_{gender_part}_{timestamp}"
    candidate = output_dir / f"{base_name}.wav"

    counter = 1
    while candidate.exists():
        candidate = output_dir / f"{base_name}_{counter}.wav"
        counter += 1

    return candidate


def _flash_attention_available() -> bool:
    return find_spec("flash_attn") is not None


def _gpu_summary() -> str:
    if not torch.cuda.is_available():
        return "No CUDA GPU detected; running on CPU."
    idx = torch.cuda.current_device()
    name = torch.cuda.get_device_name(idx)
    free_bytes, total_bytes = torch.cuda.mem_get_info(idx)
    free_gb = free_bytes / (1024**3)
    total_gb = total_bytes / (1024**3)
    return f"{name} ({free_gb:.2f} GiB free / {total_gb:.2f} GiB total)"


class QwenTTSService:
    """Loads Qwen3-TTS VoiceDesign once and serves thread-safe synthesis calls."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._lock = threading.Lock()
        self._model = None
        self._device: str = "cpu"
        self._dtype: torch.dtype = torch.float32
        self._model_source: str = ""

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def device(self) -> str:
        return self._device

    def load(self) -> None:
        """Load the VoiceDesign model once. Safe to call multiple times (no-op after first)."""
        if self._model is not None:
            return

        from qwen_tts import Qwen3TTSModel

        model_source = self._settings.resolve_model_source()
        self._model_source = model_source

        local_path = Path(model_source)
        if local_path.exists():
            required_files = ["config.json"]
            missing = [f for f in required_files if not (local_path / f).exists()]
            if missing:
                raise MissingModelFilesError(
                    f"Model directory {local_path} is missing required files: {missing}"
                )

        use_cuda = torch.cuda.is_available()
        self._device = "cuda:0" if use_cuda else "cpu"
        self._dtype = torch.bfloat16 if use_cuda else torch.float32

        load_kwargs: dict = {
            "device_map": self._device,
            "dtype": self._dtype,
        }

        use_flash_attn = use_cuda and _flash_attention_available()
        attn_implementation = "flash_attention_2" if use_flash_attn else None
        if attn_implementation:
            load_kwargs["attn_implementation"] = attn_implementation

        logger.info("Loading Qwen3-TTS VoiceDesign model from %s", model_source)
        try:
            try:
                self._model = Qwen3TTSModel.from_pretrained(model_source, **load_kwargs)
            except (TypeError, ValueError, ImportError) as exc:
                if attn_implementation:
                    logger.warning(
                        "attn_implementation=%s unavailable (%s); retrying with default attention",
                        attn_implementation,
                        exc,
                    )
                    load_kwargs.pop("attn_implementation", None)
                    self._model = Qwen3TTSModel.from_pretrained(model_source, **load_kwargs)
                else:
                    raise
        except torch.cuda.OutOfMemoryError as exc:
            torch.cuda.empty_cache()
            logger.error("CUDA OOM while loading model:\n%s", traceback.format_exc())
            raise CudaOutOfMemoryError(
                f"CUDA ran out of memory while loading the model onto {self._device}. "
                "This GPU may not have enough VRAM for this model in bfloat16. Try freeing "
                "VRAM from other processes, or force CPU mode by setting "
                'CUDA_VISIBLE_DEVICES="" before starting the app (much slower).'
            ) from exc
        except OSError as exc:
            raise ModelNotFoundError(f"Could not load model from '{model_source}': {exc}") from exc

        logger.info(
            "Model loaded | device=%s | dtype=%s | model_path=%s | GPU=%s",
            self._device,
            self._dtype,
            model_source,
            _gpu_summary(),
        )

    def gpu_metrics(self) -> dict[str, str]:
        """Return current GPU/VRAM metrics; never raises if CUDA is unavailable."""
        if not torch.cuda.is_available():
            return {"gpu": "N/A (CPU mode)", "vram_allocated": "N/A", "vram_reserved": "N/A"}

        idx = torch.cuda.current_device()
        allocated = torch.cuda.memory_allocated(idx) / (1024**3)
        reserved = torch.cuda.memory_reserved(idx) / (1024**3)
        return {
            "gpu": torch.cuda.get_device_name(idx),
            "vram_allocated": f"{allocated:.2f} GiB",
            "vram_reserved": f"{reserved:.2f} GiB",
        }

    def synthesize(
        self,
        text: str,
        language: str,
        instruct: str,
        output_path: Path | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        seed: int | None = None,
    ) -> TTSResult:
        """Run one VoiceDesign generation and write the result WAV to disk."""
        if not text or not text.strip():
            raise InvalidTextError("Text to synthesize must not be empty.")

        if language.lower() not in SUPPORTED_LANGUAGES:
            raise InvalidLanguageError(
                f"Unsupported language '{language}'. Supported: Spanish, Portuguese, English."
            )

        if self._model is None:
            raise ModelNotFoundError("Model is not loaded. Call load() before synthesize().")

        if output_path is None:
            output_path = build_output_path(self._settings.output_dir, language, "custom", "voice")

        with self._lock:
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)

            gen_kwargs: dict = {}
            if temperature is not None:
                gen_kwargs["temperature"] = temperature
            if top_p is not None:
                gen_kwargs["top_p"] = top_p
            if top_k is not None:
                gen_kwargs["top_k"] = top_k

            start = time.perf_counter()
            try:
                wavs, sample_rate = self._model.generate_voice_design(
                    text=text,
                    language=language,
                    instruct=instruct,
                    **gen_kwargs,
                )
            except torch.cuda.OutOfMemoryError as exc:
                torch.cuda.empty_cache()
                logger.error("CUDA OOM during generation:\n%s", traceback.format_exc())
                raise CudaOutOfMemoryError(
                    "CUDA ran out of memory during generation. Try shorter text, "
                    "reduce max_new_tokens, or free VRAM from other processes."
                ) from exc
            except Exception as exc:
                logger.error("Generation failed:\n%s", traceback.format_exc())
                raise GenerationError(f"Generation failed: {exc}") from exc

            generation_time = time.perf_counter() - start

        if not wavs:
            raise GenerationError("Model returned no audio.")

        wav = wavs[0]
        audio_duration = len(wav) / float(sample_rate)
        real_time_factor = generation_time / audio_duration if audio_duration > 0 else float("inf")

        sf.write(str(output_path), wav, sample_rate)

        return TTSResult(
            output_path=output_path,
            sample_rate=sample_rate,
            generation_time_seconds=generation_time,
            audio_duration_seconds=audio_duration,
            real_time_factor=real_time_factor,
        )
