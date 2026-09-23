"""Compose a single VoiceDesign `instruct` string from independent axes."""

from __future__ import annotations

from qwen_tts_playground.models import AgeGroup, Emotion, Gender, Language, Personality, Speed
from qwen_tts_playground.profiles import (
    ACCENTS_BY_LANGUAGE,
    AGE_INSTRUCTION,
    EMOTION_TONE_PHRASE,
    GENDER_INSTRUCTION,
    SPEED_INSTRUCTION,
)


def _join_traits(traits: list[str]) -> str:
    """Join personality traits into a natural sentence: 'Warm, calm and trustworthy.'"""
    if not traits:
        return ""
    words = [t.lower() for t in traits]
    sentence = words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]
    return sentence[0].upper() + sentence[1:] + "."


class VoicePromptBuilder:
    """Builds a natural-language VoiceDesign `instruct` from discrete controls."""

    def build(
        self,
        language: str,
        accent: str,
        gender: str,
        age: str,
        personality: list[str],
        emotion: str,
        speed: str,
        custom_instruction: str | None = None,
    ) -> str:
        traits = list(personality) if personality else [Personality.PROFESSIONAL.value]
        primary_trait = traits[0]
        remaining_traits = traits[1:]

        gender_sentence = GENDER_INSTRUCTION.get(gender, GENDER_INSTRUCTION[Gender.FEMALE.value])
        age_phrase = AGE_INSTRUCTION.get(age, AGE_INSTRUCTION[AgeGroup.ADULT.value])
        speed_phrase = SPEED_INSTRUCTION.get(speed, SPEED_INSTRUCTION[Speed.NORMAL.value])
        tone_phrase = EMOTION_TONE_PHRASE.get(emotion, EMOTION_TONE_PHRASE[Emotion.NEUTRAL.value])

        accent_preset = ACCENTS_BY_LANGUAGE.get(language, {}).get(accent)
        if accent_preset is not None:
            accent_line = f"Speak {accent_preset.language_variant} {accent_preset.accent_phrase}."
        else:
            accent_line = f"Speak {language}."

        age_sentence = age_phrase[0].upper() + age_phrase[1:] + "."

        paragraphs: list[str] = []

        paragraphs.append(f"{primary_trait} banking assistant.\n{gender_sentence}\n{age_sentence}")
        paragraphs.append(accent_line)

        personality_and_tone: list[str] = []
        traits_sentence = _join_traits(remaining_traits)
        if traits_sentence:
            personality_and_tone.append(traits_sentence)
        personality_and_tone.append(
            f"Use a {tone_phrase} tone. Professional and emotionally controlled."
        )
        paragraphs.append("\n".join(personality_and_tone))

        paragraphs.append(f"{speed_phrase} Use clear articulation and natural intonation.")

        paragraphs.append("Avoid sounding robotic, overly enthusiastic or authoritarian.")

        if custom_instruction and custom_instruction.strip():
            paragraphs.append(custom_instruction.strip())

        return "\n\n".join(paragraphs)


def default_language() -> str:
    return Language.SPANISH.value
