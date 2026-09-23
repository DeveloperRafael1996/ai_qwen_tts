from qwen_tts_playground.models import AgeGroup, Emotion, Gender, Language, Personality, Speed
from qwen_tts_playground.prompt_builder import VoicePromptBuilder

builder = VoicePromptBuilder()


def test_spanish_peruvian_female_prompt():
    prompt = builder.build(
        language=Language.SPANISH.value,
        accent="Peruvian",
        gender=Gender.FEMALE.value,
        age=AgeGroup.ADULT.value,
        personality=[
            Personality.PROFESSIONAL.value,
            Personality.WARM.value,
            Personality.TRUSTWORTHY.value,
        ],
        emotion=Emotion.REASSURING.value,
        speed=Speed.NORMAL.value,
    )
    assert "Female voice." in prompt
    assert "Latin American Spanish" in prompt
    assert "Peruvian accent" in prompt
    assert "Speak at a natural moderate pace." in prompt
    assert "reassuring but professional" in prompt
    assert "Approximately 30-45 years old." in prompt


def test_portuguese_brazilian_male_prompt():
    prompt = builder.build(
        language=Language.PORTUGUESE.value,
        accent="Brazil Neutral",
        gender=Gender.MALE.value,
        age=AgeGroup.MATURE.value,
        personality=[Personality.CALM.value],
        emotion=Emotion.NEUTRAL.value,
        speed=Speed.SLIGHTLY_SLOW.value,
    )
    assert "Male voice." in prompt
    assert "Brazilian Portuguese" in prompt
    assert "neutral Brazilian accent" in prompt
    assert "Speak at a slightly slower than normal pace." in prompt
    assert "Mature adult voice, approximately 45-60 years old." in prompt


def test_english_american_prompt_with_custom_instruction():
    prompt = builder.build(
        language=Language.ENGLISH.value,
        accent="American",
        gender=Gender.FEMALE.value,
        age=AgeGroup.YOUNG_ADULT.value,
        personality=[Personality.FRIENDLY.value],
        emotion=Emotion.POSITIVE.value,
        speed=Speed.FAST.value,
        custom_instruction="Make it sound upbeat but still professional.",
    )
    assert "neutral American accent" in prompt
    assert "Speak quickly but maintain clear articulation." in prompt
    assert "Make it sound upbeat but still professional." in prompt


def test_male_vs_female_sentence_differs():
    common_kwargs = dict(
        language=Language.ENGLISH.value,
        accent="American",
        age=AgeGroup.ADULT.value,
        personality=[Personality.CALM.value],
        emotion=Emotion.NEUTRAL.value,
        speed=Speed.NORMAL.value,
    )
    female_prompt = builder.build(gender=Gender.FEMALE.value, **common_kwargs)
    male_prompt = builder.build(gender=Gender.MALE.value, **common_kwargs)
    assert "Female voice." in female_prompt
    assert "Male voice." in male_prompt
    assert female_prompt != male_prompt


def test_empty_personality_falls_back_to_professional():
    prompt = builder.build(
        language=Language.ENGLISH.value,
        accent="American",
        gender=Gender.MALE.value,
        age=AgeGroup.ADULT.value,
        personality=[],
        emotion=Emotion.NEUTRAL.value,
        speed=Speed.NORMAL.value,
    )
    assert prompt.startswith("Professional banking assistant.")


def test_closing_safety_sentence_always_present():
    prompt = builder.build(
        language=Language.SPANISH.value,
        accent="Mexican",
        gender=Gender.FEMALE.value,
        age=AgeGroup.ADULT.value,
        personality=[Personality.FIRM.value],
        emotion=Emotion.SERIOUS.value,
        speed=Speed.NORMAL.value,
    )
    assert "Avoid sounding robotic, overly enthusiastic or authoritarian." in prompt
