"""Client for Cartesia's hosted Sonic-3.6 TTS API (`POST /tts/bytes`).

Sonic-3.6 is API-only: there are no downloadable weights. The response is
streamed, so the time to the first audio chunk is a real TTFA measurement.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import httpx
import numpy as np
import soundfile as sf

from qwen_tts_playground.metrics import audio_duration_seconds, real_time_factor, ttfa_ms
from qwen_tts_playground.models import TTSResult
from qwen_tts_playground.tts_service import (
    GenerationError,
    InvalidLanguageError,
    InvalidTextError,
    TTSServiceError,
)

logger = logging.getLogger(__name__)

CARTESIA_API_URL = "https://api.cartesia.ai/tts/bytes"
CARTESIA_API_VERSION = "2026-08-14"
CARTESIA_MODEL_ID = "sonic-3.6"
SAMPLE_RATE = 24000
LANGUAGE_CODES = {"spanish": "es", "portuguese": "pt", "english": "en"}
# Accent presets sent as the API's `locale` (mutually exclusive with `language`).
ACCENT_LOCALES: dict[str, list[str]] = {
    "spanish": ["es-MX", "es-ES", "es-US"],
    "portuguese": ["pt-BR", "pt-PT"],
    "english": ["en-US", "en-GB", "en-AU", "en-IN", "en-CA", "en-ZA"],
}
DEFAULT_ACCENT = "Voice default"
# (label, voice id) recommended per language; ids come from Cartesia's public voice library.
CARTESIA_VOICES: dict[str, list[tuple[str, str]]] = {
    "spanish": [
        ("Ximena - Latina female", "3597a26f-80ef-4bd5-8101-9699bc764917"),
        ("Fernanda - Mexican female", "b4b8e2af-6139-466e-a93a-30c20d2e1fc5"),
        ("Mateo - Mexican male", "2fc4f1ec-bfd0-46f1-8e6d-d4279eaaf838"),
        ("Marcos - Spain male", "13ff5deb-2591-42ad-a356-63a04e524411"),
    ],
    "portuguese": [
        ("Helena - female", "8a6d0b8e-8cd8-4952-a41e-b7af18662135"),
        ("Felipe - male", "616c64d7-f541-436b-9b8d-e79cfbe19ef9"),
    ],
    "english": [
        ("Skylar - American female", "db6b0ed5-d5d3-463d-ae85-518a07d3c2b4"),
        ("Daniel - male", "47c38ca4-5f35-497b-b1a3-415245fb35e1"),
        ("Gemma - British female", "62ae83ad-4f6a-430b-af41-a9bede9286ca"),
        ("Archie - British male", "ef191366-f52f-447a-a398-ed8c0f2943a1"),
        ("Arlo - Australian male", "12e85709-099c-480a-ba3e-875c41a9611a"),
    ],
}


class CartesiaConfigError(TTSServiceError):
    """Raised when the API key or voice id is missing."""


class CartesiaClient:
    def __init__(
        self,
        api_key: str,
        model_id: str = CARTESIA_MODEL_ID,
        timeout: float = 60.0,
        url: str = CARTESIA_API_URL,
    ) -> None:
        self._api_key = api_key
        self._model_id = model_id
        self._timeout = timeout
        self._url = url

    @property
    def model_id(self) -> str:
        return self._model_id

    def synthesize(
        self,
        text: str,
        language: str,
        voice_id: str,
        output_path: Path,
        speed: float | None = None,
        locale: str | None = None,
    ) -> TTSResult:
        if not self._api_key:
            raise CartesiaConfigError("CARTESIA_API_KEY is not set.")
        if not voice_id.strip():
            raise CartesiaConfigError("A Cartesia voice id is required.")
        if not text or not text.strip():
            raise InvalidTextError("Text to synthesize must not be empty.")
        code = LANGUAGE_CODES.get(language.lower())
        if code is None:
            raise InvalidLanguageError(f"Unsupported language '{language}'.")

        payload: dict = {
            "model_id": self._model_id,
            "transcript": text,
            "voice": {"mode": "id", "id": voice_id.strip()},
            "output_format": {
                "container": "raw",
                "encoding": "pcm_s16le",
                "sample_rate": SAMPLE_RATE,
            },
        }
        if locale:
            if not locale.lower().startswith(code + "-"):
                raise InvalidLanguageError(
                    f"Locale '{locale}' does not match language '{language}'."
                )
            payload["locale"] = locale
        else:
            payload["language"] = code
        if speed is not None:
            payload["generation_config"] = {"speed": speed}
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Cartesia-Version": CARTESIA_API_VERSION,
        }

        pcm = bytearray()
        first_chunk_at: float | None = None
        start = time.perf_counter()
        try:
            with httpx.stream(
                "POST", self._url, json=payload, headers=headers, timeout=self._timeout
            ) as response:
                if response.status_code >= 400:
                    body = response.read().decode("utf-8", errors="replace")[:300]
                    raise GenerationError(f"Cartesia API error {response.status_code}: {body}")
                for chunk in response.iter_bytes():
                    if chunk and first_chunk_at is None:
                        first_chunk_at = time.perf_counter()
                    pcm.extend(chunk)
        except httpx.HTTPError as exc:
            raise GenerationError(f"Cartesia request failed: {type(exc).__name__}") from exc
        generation_time = time.perf_counter() - start

        samples = np.frombuffer(bytes(pcm[: len(pcm) // 2 * 2]), dtype="<i2")
        if samples.size == 0:
            raise GenerationError("Cartesia returned no audio.")
        sf.write(str(output_path), samples, SAMPLE_RATE, subtype="PCM_16")

        duration = audio_duration_seconds(samples.size, SAMPLE_RATE)
        logger.info(
            "Cartesia %s | chars=%d | ttfa_ms=%.1f | generation_ms=%.1f | audio_ms=%.0f",
            self._model_id,
            len(text),
            ttfa_ms(start, first_chunk_at) or 0.0,
            generation_time * 1000,
            duration * 1000,
        )
        return TTSResult(
            output_path=output_path,
            sample_rate=SAMPLE_RATE,
            generation_time_seconds=generation_time,
            audio_duration_seconds=duration,
            real_time_factor=real_time_factor(generation_time, duration),
            ttfa_ms=ttfa_ms(start, first_chunk_at),
        )
