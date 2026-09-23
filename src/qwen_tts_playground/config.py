"""Application configuration loaded from environment variables and `.env`."""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

DEFAULT_HF_REPO_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"


class Settings(BaseSettings):
    """Runtime configuration for the Qwen3-TTS VoiceDesign playground."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    qwen_tts_model_path: str = "./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
    playground_host: str = "127.0.0.1"
    playground_port: int = 7860
    output_dir: Path = Path("outputs")

    def resolve_model_source(self) -> str:
        """Return the local model directory if present, else the HF Hub repo id.

        The model must never be re-downloaded on every request: if a local
        snapshot exists under `qwen_tts_model_path`, it is used as-is. If it
        does not exist (or is empty), the Hugging Face Hub repo id is
        returned instead and `from_pretrained` handles the (cached) download.
        """
        local_path = Path(self.qwen_tts_model_path)
        if local_path.exists() and any(local_path.iterdir()):
            logger.info("Using local model snapshot at %s", local_path)
            return str(local_path)

        logger.info(
            "Local model path %s not found or empty; falling back to Hugging Face Hub repo %s",
            local_path,
            DEFAULT_HF_REPO_ID,
        )
        return DEFAULT_HF_REPO_ID


def get_settings() -> Settings:
    """Build a fresh `Settings` instance from the current environment."""
    return Settings()
