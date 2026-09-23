"""Application configuration loaded from environment variables and `.env`."""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

DEFAULT_HF_REPO_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
DEFAULT_VOICE_CLONE_HF_REPO_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
DEFAULT_CUSTOM_VOICE_HF_REPO_ID = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"


def _resolve_source(local_path_str: str, hf_repo_id: str) -> str:
    """Return the local model directory if present, else the HF Hub repo id.

    A model must never be re-downloaded on every request: if a local snapshot
    exists at `local_path_str`, it is used as-is. If it does not exist (or is
    empty), the Hugging Face Hub repo id is returned instead and
    `from_pretrained` handles the (cached) download.
    """
    local_path = Path(local_path_str)
    if local_path.exists() and any(local_path.iterdir()):
        logger.info("Using local model snapshot at %s", local_path)
        return str(local_path)

    logger.info(
        "Local model path %s not found or empty; falling back to Hugging Face Hub repo %s",
        local_path,
        hf_repo_id,
    )
    return hf_repo_id


class Settings(BaseSettings):
    """Runtime configuration for the Qwen3-TTS playground."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    qwen_tts_model_path: str = "./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
    qwen_tts_voice_clone_model_path: str = "./models/Qwen3-TTS-12Hz-0.6B-Base"
    qwen_tts_custom_voice_model_path: str = "./models/Qwen3-TTS-12Hz-0.6B-CustomVoice"
    playground_host: str = "127.0.0.1"
    playground_port: int = 7860
    output_dir: Path = Path("outputs")

    def resolve_model_source(self) -> str:
        """Local snapshot or HF Hub repo id for the VoiceDesign model."""
        return _resolve_source(self.qwen_tts_model_path, DEFAULT_HF_REPO_ID)

    def resolve_voice_clone_model_source(self) -> str:
        """Local snapshot or HF Hub repo id for the voice-cloning Base model."""
        return _resolve_source(self.qwen_tts_voice_clone_model_path, DEFAULT_VOICE_CLONE_HF_REPO_ID)

    def resolve_custom_voice_model_source(self) -> str:
        """Local snapshot or HF Hub repo id for the CustomVoice model."""
        return _resolve_source(
            self.qwen_tts_custom_voice_model_path, DEFAULT_CUSTOM_VOICE_HF_REPO_ID
        )


def get_settings() -> Settings:
    """Build a fresh `Settings` instance from the current environment."""
    return Settings()
