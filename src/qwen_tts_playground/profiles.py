"""Static VoiceDesign profile data: accents, ages, speeds, emotions, presets.

IMPORTANT: accents below are *requested* through natural-language `instruct`
text sent to the VoiceDesign model. They are not guaranteed regional accents
and must be evaluated by ear, generation by generation. See the README for
details on the difference between `language` (sent literally to the model)
and `accent` (a style requested via instruction text).
"""

from __future__ import annotations

from dataclasses import dataclass

from qwen_tts_playground.models import AgeGroup, Emotion, Gender, Language, Speed

# ---------------------------------------------------------------------------
# Accents (requested via instruct, grouped by language)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AccentPreset:
    label: str
    language_variant: str
    accent_phrase: str


ACCENTS_BY_LANGUAGE: dict[str, dict[str, AccentPreset]] = {
    Language.SPANISH.value: {
        "Latin American Neutral": AccentPreset(
            "Latin American Neutral",
            "neutral Latin American Spanish",
            "with a natural, neutral pan-Latin American accent",
        ),
        "Peruvian": AccentPreset(
            "Peruvian",
            "Latin American Spanish",
            "with a subtle neutral Peruvian accent",
        ),
        "Mexican": AccentPreset(
            "Mexican",
            "Mexican Spanish",
            "with a natural Mexican accent",
        ),
        "Colombian": AccentPreset(
            "Colombian",
            "Latin American Spanish",
            "with a neutral Colombian accent",
        ),
        "Argentinian": AccentPreset(
            "Argentinian",
            "Argentine Spanish",
            "with a moderate Argentine accent, without exaggeration",
        ),
        "Spain": AccentPreset(
            "Spain",
            "European Spanish",
            "with a neutral Spanish accent from Spain",
        ),
    },
    Language.PORTUGUESE.value: {
        "Brazil Neutral": AccentPreset(
            "Brazil Neutral",
            "Brazilian Portuguese",
            "with a neutral Brazilian accent",
        ),
        "São Paulo": AccentPreset(
            "São Paulo",
            "Brazilian Portuguese",
            "with a subtle São Paulo accent, without exaggerating regional characteristics",
        ),
        "Rio de Janeiro": AccentPreset(
            "Rio de Janeiro",
            "Brazilian Portuguese",
            "with a subtle, warm and conversational Rio de Janeiro accent, "
            "without exaggerating regional characteristics",
        ),
        "Portugal": AccentPreset(
            "Portugal",
            "European Portuguese",
            "with a neutral Portuguese accent",
        ),
    },
    Language.ENGLISH.value: {
        "American": AccentPreset(
            "American",
            "American English",
            "with a neutral American accent",
        ),
        "British": AccentPreset(
            "British",
            "British English",
            "with a neutral British accent",
        ),
        "Australian": AccentPreset(
            "Australian",
            "Australian English",
            "with a natural Australian accent",
        ),
        "Indian": AccentPreset(
            "Indian",
            "Indian English",
            "with a natural Indian English accent",
        ),
        "Latin American": AccentPreset(
            "Latin American",
            "English",
            "with a subtle, light Latin American accent",
        ),
    },
}


def accent_choices(language: str) -> list[str]:
    return list(ACCENTS_BY_LANGUAGE.get(language, {}).keys())


def default_accent(language: str) -> str:
    choices = accent_choices(language)
    return choices[0] if choices else ""


# ---------------------------------------------------------------------------
# Gender
# ---------------------------------------------------------------------------

GENDER_INSTRUCTION: dict[str, str] = {
    Gender.FEMALE.value: "Female voice.",
    Gender.MALE.value: "Male voice.",
}

# ---------------------------------------------------------------------------
# Age
# ---------------------------------------------------------------------------

AGE_INSTRUCTION: dict[str, str] = {
    AgeGroup.YOUNG_ADULT.value: "approximately 25-30 years old",
    AgeGroup.ADULT.value: "approximately 30-45 years old",
    AgeGroup.MATURE.value: "mature adult voice, approximately 45-60 years old",
}

# ---------------------------------------------------------------------------
# Speed
# ---------------------------------------------------------------------------

SPEED_INSTRUCTION: dict[str, str] = {
    Speed.SLOW.value: "Speak slowly and clearly.",
    Speed.SLIGHTLY_SLOW.value: "Speak at a slightly slower than normal pace.",
    Speed.NORMAL.value: "Speak at a natural moderate pace.",
    Speed.SLIGHTLY_FAST.value: "Speak slightly faster than normal while remaining clear.",
    Speed.FAST.value: "Speak quickly but maintain clear articulation.",
}

# ---------------------------------------------------------------------------
# Emotion (kept controlled by default; banking tone stays professional)
# ---------------------------------------------------------------------------

EMOTION_TONE_PHRASE: dict[str, str] = {
    Emotion.NEUTRAL.value: "neutral and professional",
    Emotion.WARM.value: "warm and professional",
    Emotion.REASSURING.value: "reassuring but professional",
    Emotion.POSITIVE.value: "positive and professional",
    Emotion.SERIOUS.value: "serious and composed",
    Emotion.CONCERNED.value: "concerned but composed",
    Emotion.EMPATHETIC.value: "empathetic and professional",
    Emotion.CONFIDENT.value: "confident and professional",
}

# ---------------------------------------------------------------------------
# Sample texts per language
# ---------------------------------------------------------------------------

SAMPLE_TEXTS: dict[str, str] = {
    Language.SPANISH.value: (
        "Hola, soy tu asistente. Vamos a verificar tu identidad de forma segura. "
        "¿Puedes decirme tu nombre?"
    ),
    Language.PORTUGUESE.value: (
        "Olá, sou seu assistente. Vamos verificar sua identidade com segurança. "
        "Pode me dizer seu nome?"
    ),
    Language.ENGLISH.value: (
        "Hello, I'm your assistant. We're going to verify your identity securely. "
        "Could you please tell me your name?"
    ),
}

# ---------------------------------------------------------------------------
# Banking presets: preset name -> {language: text}
# ---------------------------------------------------------------------------

BANKING_PRESETS: dict[str, dict[str, str]] = {
    "Welcome": {
        Language.SPANISH.value: SAMPLE_TEXTS[Language.SPANISH.value],
        Language.PORTUGUESE.value: SAMPLE_TEXTS[Language.PORTUGUESE.value],
        Language.ENGLISH.value: SAMPLE_TEXTS[Language.ENGLISH.value],
    },
    "Identity Verification": {
        Language.SPANISH.value: (
            "Antes de continuar, necesitamos verificar tu identidad. "
            "Por favor, ten a la mano tu documento de identidad."
        ),
        Language.PORTUGUESE.value: (
            "Antes de continuar, precisamos verificar sua identidade. "
            "Por favor, tenha seu documento de identidade em mãos."
        ),
        Language.ENGLISH.value: (
            "Before we continue, we need to verify your identity. "
            "Please have your identity document ready."
        ),
    },
    "Document Capture": {
        Language.SPANISH.value: (
            "Coloca tu documento de identidad dentro del marco y asegúrate "
            "de que se vea con claridad."
        ),
        Language.PORTUGUESE.value: (
            "Coloque seu documento de identidade dentro do quadro e "
            "certifique-se de que esteja bem visível."
        ),
        Language.ENGLISH.value: (
            "Place your identity document inside the frame and make sure it is clearly visible."
        ),
    },
    "Face Capture": {
        Language.SPANISH.value: (
            "Mira directamente a la cámara y mantén tu rostro dentro del marco."
        ),
        Language.PORTUGUESE.value: (
            "Olhe diretamente para a câmera e mantenha seu rosto dentro do enquadramento."
        ),
        Language.ENGLISH.value: (
            "Look directly at the camera and keep your face inside the frame."
        ),
    },
    "Retry": {
        Language.SPANISH.value: (
            "No pudimos completar la verificación. Vamos a intentarlo nuevamente."
        ),
        Language.PORTUGUESE.value: (
            "Não conseguimos concluir a verificação. Vamos tentar novamente."
        ),
        Language.ENGLISH.value: ("We were unable to complete the verification. Let's try again."),
    },
    "Security Warning": {
        Language.SPANISH.value: (
            "Por tu seguridad, nunca compartas tus claves ni códigos de verificación con nadie."
        ),
        Language.PORTUGUESE.value: (
            "Para sua segurança, nunca compartilhe suas senhas ou códigos "
            "de verificação com ninguém."
        ),
        Language.ENGLISH.value: (
            "For your security, never share your passwords or verification codes with anyone."
        ),
    },
    "Success": {
        Language.SPANISH.value: "Perfecto. Tu identidad fue verificada correctamente.",
        Language.PORTUGUESE.value: "Perfeito. Sua identidade foi verificada com sucesso.",
        Language.ENGLISH.value: "Perfect. Your identity has been verified successfully.",
    },
    "Error": {
        Language.SPANISH.value: (
            "Ocurrió un problema durante el proceso. Por favor, inténtalo "
            "de nuevo en unos momentos."
        ),
        Language.PORTUGUESE.value: (
            "Ocorreu um problema durante o processo. Por favor, tente "
            "novamente em alguns instantes."
        ),
        Language.ENGLISH.value: (
            "Something went wrong during the process. Please try again in a few moments."
        ),
    },
    "Remove Glasses": {
        Language.SPANISH.value: "Retira tus lentes para continuar con la verificación.",
        Language.PORTUGUESE.value: "Retire seus óculos para continuar com a verificação.",
        Language.ENGLISH.value: "Please remove your glasses to continue with the verification.",
    },
    "Improve Lighting": {
        Language.SPANISH.value: "Busca un lugar con mejor iluminación y vuelve a intentarlo.",
        Language.PORTUGUESE.value: "Procure um local com melhor iluminação e tente novamente.",
        Language.ENGLISH.value: "Move to a better-lit area and try again.",
    },
}

BANKING_PRESET_NAMES: list[str] = list(BANKING_PRESETS.keys())


def banking_preset_text(preset_name: str, language: str) -> str:
    return BANKING_PRESETS.get(preset_name, {}).get(language, "")


# ---------------------------------------------------------------------------
# Ready-made VoiceDesign instruction presets (section 36)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VoicePreset:
    name: str
    language: str
    accent: str
    gender: str
    instruct: str


VOICE_PRESETS: dict[str, VoicePreset] = {
    "Spanish - Peruvian - Female": VoicePreset(
        name="Spanish - Peruvian - Female",
        language=Language.SPANISH.value,
        accent="Peruvian",
        gender=Gender.FEMALE.value,
        instruct=(
            "A professional female banking assistant,\n"
            "approximately 30-40 years old.\n\n"
            "Speak neutral Latin American Spanish\n"
            "with a subtle Peruvian accent.\n\n"
            "Warm, calm and trustworthy.\n"
            "Clear articulation and natural intonation.\n\n"
            "Speak at a moderate pace.\n\n"
            "Avoid sounding robotic,\n"
            "overly enthusiastic or authoritarian."
        ),
    ),
    "Spanish - Peruvian - Male": VoicePreset(
        name="Spanish - Peruvian - Male",
        language=Language.SPANISH.value,
        accent="Peruvian",
        gender=Gender.MALE.value,
        instruct=(
            "A professional male banking assistant,\n"
            "approximately 35-45 years old.\n\n"
            "Speak neutral Latin American Spanish\n"
            "with a subtle Peruvian accent.\n\n"
            "Calm, confident and trustworthy.\n"
            "Clear articulation.\n\n"
            "Moderate speaking pace."
        ),
    ),
    "Spanish - Mexican - Female": VoicePreset(
        name="Spanish - Mexican - Female",
        language=Language.SPANISH.value,
        accent="Mexican",
        gender=Gender.FEMALE.value,
        instruct=(
            "A professional female banking assistant\n"
            "speaking Mexican Spanish.\n\n"
            "Natural Mexican accent.\n"
            "Warm, professional and trustworthy.\n\n"
            "Moderate speaking pace."
        ),
    ),
    "Spanish - Colombian - Female": VoicePreset(
        name="Spanish - Colombian - Female",
        language=Language.SPANISH.value,
        accent="Colombian",
        gender=Gender.FEMALE.value,
        instruct=(
            "A professional female banking assistant\n"
            "with a neutral Colombian Spanish accent.\n\n"
            "Warm, calm and clear.\n"
            "Professional banking tone."
        ),
    ),
    "Portuguese - Brazilian - Female": VoicePreset(
        name="Portuguese - Brazilian - Female",
        language=Language.PORTUGUESE.value,
        accent="Brazil Neutral",
        gender=Gender.FEMALE.value,
        instruct=(
            "A professional female banking assistant\n"
            "speaking Brazilian Portuguese.\n\n"
            "Neutral Brazilian accent.\n"
            "Warm, calm and trustworthy.\n\n"
            "Clear articulation and moderate speaking pace."
        ),
    ),
    "Portuguese - Brazilian - Male": VoicePreset(
        name="Portuguese - Brazilian - Male",
        language=Language.PORTUGUESE.value,
        accent="Brazil Neutral",
        gender=Gender.MALE.value,
        instruct=(
            "A professional male banking assistant\n"
            "speaking Brazilian Portuguese.\n\n"
            "Neutral Brazilian accent.\n"
            "Calm, mature and trustworthy."
        ),
    ),
    "English - US - Female": VoicePreset(
        name="English - US - Female",
        language=Language.ENGLISH.value,
        accent="American",
        gender=Gender.FEMALE.value,
        instruct=(
            "A professional female banking assistant.\n\n"
            "Neutral American English accent.\n"
            "Warm, calm and trustworthy.\n\n"
            "Natural speaking pace\n"
            "with clear articulation."
        ),
    ),
    "English - US - Male": VoicePreset(
        name="English - US - Male",
        language=Language.ENGLISH.value,
        accent="American",
        gender=Gender.MALE.value,
        instruct=(
            "A professional male banking assistant.\n\n"
            "Neutral American English accent.\n"
            "Mature, calm and trustworthy.\n\n"
            "Clear articulation and moderate pace."
        ),
    ),
    "English - UK - Female": VoicePreset(
        name="English - UK - Female",
        language=Language.ENGLISH.value,
        accent="British",
        gender=Gender.FEMALE.value,
        instruct=(
            "A professional female banking assistant\n"
            "with a neutral British English accent.\n\n"
            "Polished, calm and trustworthy."
        ),
    ),
}

VOICE_PRESET_NAMES: list[str] = list(VOICE_PRESETS.keys())
