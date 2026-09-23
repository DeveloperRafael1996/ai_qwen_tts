from qwen_tts_playground.models import Language
from qwen_tts_playground.profiles import (
    BANKING_PRESETS,
    GENDER_INSTRUCTION,
    SAMPLE_TEXTS,
    SPEED_INSTRUCTION,
    VOICE_PRESETS,
    accent_choices,
    default_accent,
)


def test_spanish_accents_present():
    accents = accent_choices(Language.SPANISH.value)
    assert {"Peruvian", "Mexican", "Colombian", "Argentinian", "Spain"}.issubset(set(accents))


def test_portuguese_accents_present():
    accents = accent_choices(Language.PORTUGUESE.value)
    assert set(accents) == {"Brazil Neutral", "São Paulo", "Rio de Janeiro", "Portugal"}


def test_english_accents_present():
    accents = accent_choices(Language.ENGLISH.value)
    assert set(accents) == {"American", "British", "Australian", "Indian", "Latin American"}


def test_default_accent_is_first_choice():
    assert default_accent(Language.SPANISH.value) == accent_choices(Language.SPANISH.value)[0]


def test_unknown_language_has_no_accents():
    assert accent_choices("Klingon") == []
    assert default_accent("Klingon") == ""


def test_gender_instruction_literal_sentences():
    assert GENDER_INSTRUCTION["Female"] == "Female voice."
    assert GENDER_INSTRUCTION["Male"] == "Male voice."


def test_speed_instruction_exact_text():
    assert SPEED_INSTRUCTION["Slow"] == "Speak slowly and clearly."
    assert SPEED_INSTRUCTION["Slightly Slow"] == "Speak at a slightly slower than normal pace."
    assert SPEED_INSTRUCTION["Normal"] == "Speak at a natural moderate pace."
    assert SPEED_INSTRUCTION["Slightly Fast"] == (
        "Speak slightly faster than normal while remaining clear."
    )
    assert SPEED_INSTRUCTION["Fast"] == "Speak quickly but maintain clear articulation."


def test_sample_texts_all_languages_present_and_nonempty():
    for lang in (Language.SPANISH.value, Language.PORTUGUESE.value, Language.ENGLISH.value):
        assert SAMPLE_TEXTS[lang]


def test_banking_presets_cover_required_names_in_all_languages():
    required = [
        "Welcome",
        "Identity Verification",
        "Document Capture",
        "Face Capture",
        "Retry",
        "Security Warning",
        "Success",
        "Error",
    ]
    for name in required:
        assert name in BANKING_PRESETS
        for lang in (Language.SPANISH.value, Language.PORTUGUESE.value, Language.ENGLISH.value):
            assert BANKING_PRESETS[name][lang]


def test_voice_presets_language_and_gender_metadata():
    preset = VOICE_PRESETS["Spanish - Peruvian - Female"]
    assert preset.language == Language.SPANISH.value
    assert preset.gender == "Female"
    assert "Peruvian" in preset.instruct

    preset_male = VOICE_PRESETS["Portuguese - Brazilian - Male"]
    assert preset_male.language == Language.PORTUGUESE.value
    assert preset_male.gender == "Male"
