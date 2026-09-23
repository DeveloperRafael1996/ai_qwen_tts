"""Pydantic models and enums shared across the playground."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class Language(StrEnum):
    SPANISH = "Spanish"
    PORTUGUESE = "Portuguese"
    ENGLISH = "English"


class Gender(StrEnum):
    FEMALE = "Female"
    MALE = "Male"


class AgeGroup(StrEnum):
    YOUNG_ADULT = "Young Adult"
    ADULT = "Adult"
    MATURE = "Mature"


class Personality(StrEnum):
    PROFESSIONAL = "Professional"
    WARM = "Warm"
    TRUSTWORTHY = "Trustworthy"
    CALM = "Calm"
    FIRM = "Firm"
    FRIENDLY = "Friendly"
    SERIOUS = "Serious"
    EMPATHETIC = "Empathetic"


class Emotion(StrEnum):
    NEUTRAL = "Neutral"
    WARM = "Warm"
    REASSURING = "Reassuring"
    POSITIVE = "Positive"
    SERIOUS = "Serious"
    CONCERNED = "Concerned"
    EMPATHETIC = "Empathetic"
    CONFIDENT = "Confident"


class Speed(StrEnum):
    SLOW = "Slow"
    SLIGHTLY_SLOW = "Slightly Slow"
    NORMAL = "Normal"
    SLIGHTLY_FAST = "Slightly Fast"
    FAST = "Fast"


class TTSResult(BaseModel):
    """Result of a single VoiceDesign synthesis call."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    output_path: Path
    sample_rate: int
    generation_time_seconds: float
    audio_duration_seconds: float
    real_time_factor: float


class HistoryEntry(BaseModel):
    """One row of the in-memory session generation history."""

    timestamp: str
    language: str
    accent: str
    gender: str
    voice_style: str
    generation_time_seconds: float
    audio_duration_seconds: float
    real_time_factor: float
    filename: str
