"""Gradio web playground for Qwen3-TTS VoiceDesign + voice cloning.

Two models, two tabs:
  - Voice Design (Qwen3-TTS-12Hz-1.7B-VoiceDesign): text + natural-language
    style instruction -> speech.
  - Voice Clone (Qwen3-TTS-12Hz-0.6B-Base): text + a reference audio
    (+ reference text) -> speech in the reference speaker's voice.

Run with:
    uv run python -m qwen_tts_playground.playground
"""

from __future__ import annotations

import logging
from datetime import datetime

import gradio as gr

from qwen_tts_playground.config import Settings, get_settings
from qwen_tts_playground.models import AgeGroup, Emotion, Gender, Language, Personality, Speed
from qwen_tts_playground.profiles import (
    BANKING_PRESET_NAMES,
    SAMPLE_TEXTS,
    VOICE_PRESET_NAMES,
    VOICE_PRESETS,
    accent_choices,
    banking_preset_text,
    default_accent,
)
from qwen_tts_playground.prompt_builder import VoicePromptBuilder
from qwen_tts_playground.tts_service import QwenTTSService, TTSServiceError, build_output_path

logger = logging.getLogger(__name__)

VOICE_DESIGN_MODEL_DISPLAY_NAME = "Qwen3-TTS-12Hz-1.7B-VoiceDesign"
VOICE_CLONE_MODEL_DISPLAY_NAME = "Qwen3-TTS-12Hz-0.6B-Base"

CLONE_MODE_ICL = "In-Context Learning (needs reference text)"
CLONE_MODE_X_VECTOR = "Speaker Embedding Only (x-vector)"
CLONE_MODE_CHOICES = [CLONE_MODE_ICL, CLONE_MODE_X_VECTOR]

LANGUAGE_CHOICES = [Language.SPANISH.value, Language.PORTUGUESE.value, Language.ENGLISH.value]
GENDER_CHOICES = [Gender.FEMALE.value, Gender.MALE.value]
AGE_CHOICES = [AgeGroup.YOUNG_ADULT.value, AgeGroup.ADULT.value, AgeGroup.MATURE.value]
PERSONALITY_CHOICES = [p.value for p in Personality]
EMOTION_CHOICES = [e.value for e in Emotion]
SPEED_CHOICES = [s.value for s in Speed]

DEFAULT_LANGUAGE = Language.SPANISH.value
DEFAULT_GENDER = Gender.FEMALE.value
DEFAULT_AGE = AgeGroup.ADULT.value
DEFAULT_PERSONALITY = [
    Personality.PROFESSIONAL.value,
    Personality.TRUSTWORTHY.value,
    Personality.CALM.value,
]
DEFAULT_EMOTION = Emotion.NEUTRAL.value
DEFAULT_SPEED = Speed.NORMAL.value

HISTORY_HEADERS = [
    "Timestamp",
    "Mode",
    "Language",
    "Accent",
    "Gender",
    "Voice Style",
    "Generation Time (s)",
    "Audio Duration (s)",
    "RTF",
    "Filename",
]

builder = VoicePromptBuilder()


def _char_count_label(text: str) -> str:
    return f"Characters: {len(text or '')}"


def _rebuild_prompt(language, accent, gender, age, personality, emotion, speed, custom_instruction):
    return builder.build(
        language=language,
        accent=accent,
        gender=gender,
        age=age,
        personality=personality,
        emotion=emotion,
        speed=speed,
        custom_instruction=custom_instruction,
    )


def _on_language_change(language: str, preset_guard: int):
    # `preset_guard` > 0 means this change was caused by loading a Voice Preset
    # (see `_on_voice_preset_change`), which already set the correct accent for
    # that preset. Skip resetting it to the language's default in that case.
    if preset_guard > 0:
        return gr.update(), gr.update(), gr.update()

    accents = accent_choices(language)
    accent_value = default_accent(language)
    sample_text = SAMPLE_TEXTS.get(language, "")
    return (
        gr.update(choices=accents, value=accent_value),
        sample_text,
        _char_count_label(sample_text),
    )


def _on_clone_language_change(language: str):
    sample_text = SAMPLE_TEXTS.get(language, "")
    return sample_text, _char_count_label(sample_text)


def _on_banking_preset_change(preset_name: str, language: str):
    if not preset_name or preset_name == "Custom":
        return gr.update()
    text = banking_preset_text(preset_name, language)
    return text


def _on_voice_preset_change(
    preset_name: str, current_language: str, current_accent: str, current_gender: str
):
    """Apply a ready-made Voice Preset.

    Setting `language`/`accent`/`gender` here will also re-trigger their own
    `.change()` listeners (Gradio fires `.change()` on any value update, not
    just user interaction), which would otherwise immediately overwrite
    `preset.instruct` with a generic rebuilt prompt. `preset_guard` counts how
    many of those cascades are actually expected (only fields whose value is
    really changing) so each one can skip its rebuild exactly once.
    """
    if not preset_name or preset_name == "None":
        return gr.update(), gr.update(), gr.update(), gr.update(), 0

    preset = VOICE_PRESETS[preset_name]
    accents = accent_choices(preset.language)

    expected_cascades = 0
    if preset.language != current_language:
        expected_cascades += 1
    if preset.accent != current_accent:
        expected_cascades += 1
    if preset.gender != current_gender:
        expected_cascades += 1

    return (
        gr.update(value=preset.language),
        gr.update(choices=accents, value=preset.accent),
        gr.update(value=preset.gender),
        preset.instruct,
        expected_cascades,
    )


def _guarded_rebuild_prompt(
    preset_guard: int,
    language,
    accent,
    gender,
    age,
    personality,
    emotion,
    speed,
    custom_instruction,
):
    if preset_guard > 0:
        return gr.update(), preset_guard - 1
    rebuilt = _rebuild_prompt(
        language, accent, gender, age, personality, emotion, speed, custom_instruction
    )
    return rebuilt, 0


def _format_perf_markdown(
    result,
    model_name: str,
    language: str,
    accent: str,
    gender: str,
) -> str:
    return (
        f"**Model:** {model_name}\n\n"
        f"**Language:** {language}  \n"
        f"**Accent:** {accent}  \n"
        f"**Gender:** {gender}\n\n"
        f"**Generation:** {result.generation_time_seconds:.2f} s  \n"
        f"**Audio:** {result.audio_duration_seconds:.2f} s  \n"
        f"**RTF:** {result.real_time_factor:.3f}  \n"
        f"**Sample rate:** {result.sample_rate} Hz"
    )


def _format_gpu_markdown(service: QwenTTSService) -> str:
    metrics = service.gpu_metrics()
    return (
        f"**GPU:** {metrics['gpu']}  \n"
        f"**VRAM allocated:** {metrics['vram_allocated']}  \n"
        f"**VRAM reserved:** {metrics['vram_reserved']}"
    )


def _history_row(
    result, mode: str, language: str, accent: str, gender: str, voice_style: str
) -> list:
    return [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        mode,
        language,
        accent,
        gender,
        voice_style,
        round(result.generation_time_seconds, 3),
        round(result.audio_duration_seconds, 3),
        round(result.real_time_factor, 3),
        result.output_path.name,
    ]


def build_ui(
    service: QwenTTSService, voice_clone_service: QwenTTSService, settings: Settings
) -> gr.Blocks:
    def generate_audio(
        text: str,
        language: str,
        accent: str,
        gender: str,
        voice_prompt: str,
        seed: float | None,
        temperature: float | None,
        top_p: float | None,
        top_k: float | None,
        history_rows: list,
    ):
        try:
            output_path = build_output_path(settings.output_dir, language, accent, gender)
            result = service.synthesize(
                text=text,
                language=language,
                instruct=voice_prompt,
                output_path=output_path,
                temperature=float(temperature) if temperature else None,
                top_p=float(top_p) if top_p else None,
                top_k=int(top_k) if top_k else None,
                seed=int(seed) if seed else None,
            )
        except TTSServiceError as exc:
            logger.warning("Synthesis rejected: %s", exc)
            return (
                None,
                gr.update(),
                _format_gpu_markdown(service),
                f"Error: {exc}",
                history_rows,
                history_rows,
            )
        except Exception:
            logger.exception("Unexpected error during synthesis")
            return (
                None,
                gr.update(),
                _format_gpu_markdown(service),
                "Error: an unexpected error occurred. Check server logs for details.",
                history_rows,
                history_rows,
            )

        perf_md = _format_perf_markdown(
            result, VOICE_DESIGN_MODEL_DISPLAY_NAME, language, accent, gender
        )
        gpu_md = _format_gpu_markdown(service)
        row = _history_row(result, "Voice Design", language, accent, gender, "Main")
        new_rows = [*history_rows, row]

        return (
            str(result.output_path),
            perf_md,
            gpu_md,
            "Audio generated successfully.",
            new_rows,
            new_rows,
        )

    def generate_comparison(
        text: str,
        language: str,
        gender_a: str,
        accent_a: str,
        personality_a: list,
        speed_a: str,
        gender_b: str,
        accent_b: str,
        personality_b: list,
        speed_b: str,
        history_rows: list,
    ):
        instruct_a = builder.build(
            language=language,
            accent=accent_a,
            gender=gender_a,
            age=DEFAULT_AGE,
            personality=personality_a,
            emotion=DEFAULT_EMOTION,
            speed=speed_a,
        )
        instruct_b = builder.build(
            language=language,
            accent=accent_b,
            gender=gender_b,
            age=DEFAULT_AGE,
            personality=personality_b,
            emotion=DEFAULT_EMOTION,
            speed=speed_b,
        )

        rows = list(history_rows)
        outputs = []
        for label, gender, accent, instruct in (
            ("Voice A", gender_a, accent_a, instruct_a),
            ("Voice B", gender_b, accent_b, instruct_b),
        ):
            try:
                output_path = build_output_path(settings.output_dir, language, accent, gender)
                result = service.synthesize(
                    text=text,
                    language=language,
                    instruct=instruct,
                    output_path=output_path,
                )
                rows.append(_history_row(result, "Voice Design", language, accent, gender, label))
                outputs.append(str(result.output_path))
            except TTSServiceError as exc:
                logger.warning("Comparison synthesis (%s) rejected: %s", label, exc)
                outputs.append(None)
            except Exception:
                logger.exception("Unexpected error during comparison synthesis (%s)", label)
                outputs.append(None)

        return outputs[0], outputs[1], rows, rows

    def generate_voice_clone(
        text: str,
        language: str,
        ref_audio_path: str | None,
        ref_text: str,
        clone_mode: str,
        seed: float | None,
        temperature: float | None,
        top_p: float | None,
        top_k: float | None,
        history_rows: list,
    ):
        x_vector_only_mode = clone_mode == CLONE_MODE_X_VECTOR

        try:
            if not voice_clone_service.is_loaded:
                logger.info("Lazily loading voice-clone model (first use this session)...")
                voice_clone_service.load()

            output_path = build_output_path(settings.output_dir, language, "clone", "voice")
            result = voice_clone_service.synthesize_voice_clone(
                text=text,
                language=language,
                ref_audio=ref_audio_path or "",
                ref_text=ref_text,
                x_vector_only_mode=x_vector_only_mode,
                output_path=output_path,
                temperature=float(temperature) if temperature else None,
                top_p=float(top_p) if top_p else None,
                top_k=int(top_k) if top_k else None,
                seed=int(seed) if seed else None,
            )
        except TTSServiceError as exc:
            logger.warning("Voice-clone synthesis rejected: %s", exc)
            return (
                None,
                gr.update(),
                _format_gpu_markdown(voice_clone_service),
                f"Error: {exc}",
                history_rows,
                history_rows,
            )
        except Exception:
            logger.exception("Unexpected error during voice-clone synthesis")
            return (
                None,
                gr.update(),
                _format_gpu_markdown(voice_clone_service),
                "Error: an unexpected error occurred. Check server logs for details.",
                history_rows,
                history_rows,
            )

        voice_style = "X-Vector" if x_vector_only_mode else "In-Context Learning"
        perf_md = _format_perf_markdown(result, VOICE_CLONE_MODEL_DISPLAY_NAME, language, "-", "-")
        gpu_md = _format_gpu_markdown(voice_clone_service)
        row = _history_row(result, "Voice Clone", language, "-", "-", voice_style)
        new_rows = [*history_rows, row]

        return (
            str(result.output_path),
            perf_md,
            gpu_md,
            "Audio generated successfully.",
            new_rows,
            new_rows,
        )

    with gr.Blocks(title="Qwen3-TTS VoiceDesign Playground") as demo:
        gr.Markdown("# Qwen3-TTS VoiceDesign Playground")
        gr.Markdown(
            "Local multilingual TTS playground for voice, accent and style experimentation."
        )

        history_state = gr.State([])
        preset_guard_state = gr.State(0)

        with gr.Tab("Voice Design"):
            with gr.Row():
                with gr.Column(scale=1):
                    language = gr.Dropdown(
                        LANGUAGE_CHOICES, value=DEFAULT_LANGUAGE, label="Language"
                    )
                    accent = gr.Dropdown(
                        accent_choices(DEFAULT_LANGUAGE),
                        value=default_accent(DEFAULT_LANGUAGE),
                        label="Accent",
                    )
                    gender = gr.Radio(GENDER_CHOICES, value=DEFAULT_GENDER, label="Gender")
                    age = gr.Dropdown(AGE_CHOICES, value=DEFAULT_AGE, label="Age")
                    personality = gr.CheckboxGroup(
                        PERSONALITY_CHOICES, value=DEFAULT_PERSONALITY, label="Personality"
                    )
                    emotion = gr.Dropdown(EMOTION_CHOICES, value=DEFAULT_EMOTION, label="Emotion")
                    speed = gr.Dropdown(SPEED_CHOICES, value=DEFAULT_SPEED, label="Speaking Pace")

                    gr.Markdown("---")
                    banking_preset = gr.Dropdown(
                        ["Custom", *BANKING_PRESET_NAMES],
                        value="Custom",
                        label="Banking Preset (fills text below)",
                    )
                    text_input = gr.Textbox(
                        value=SAMPLE_TEXTS[DEFAULT_LANGUAGE],
                        label="Text to synthesize",
                        lines=4,
                    )
                    char_count = gr.Markdown(_char_count_label(SAMPLE_TEXTS[DEFAULT_LANGUAGE]))

                    voice_prompt = gr.Textbox(
                        value=_rebuild_prompt(
                            DEFAULT_LANGUAGE,
                            default_accent(DEFAULT_LANGUAGE),
                            DEFAULT_GENDER,
                            DEFAULT_AGE,
                            DEFAULT_PERSONALITY,
                            DEFAULT_EMOTION,
                            DEFAULT_SPEED,
                            "",
                        ),
                        label="Voice Design Instruction",
                        lines=10,
                    )
                    reset_prompt_btn = gr.Button("Reset Voice Prompt")

                    custom_instruction = gr.Textbox(
                        label="Additional Voice Instruction",
                        placeholder=(
                            "Make security instructions slightly more serious, but never alarming."
                        ),
                        lines=2,
                    )

                    voice_preset_dropdown = gr.Dropdown(
                        ["None", *VOICE_PRESET_NAMES],
                        value="None",
                        label="Load Voice Preset (overrides Voice Design Instruction)",
                    )

                    with gr.Accordion("Advanced Settings", open=False):
                        seed = gr.Number(label="Seed (optional)", value=None, precision=0)
                        temperature = gr.Slider(0.1, 1.5, value=0.9, step=0.05, label="Temperature")
                        top_p = gr.Slider(0.1, 1.0, value=1.0, step=0.05, label="Top P")
                        top_k = gr.Slider(0, 100, value=50, step=1, label="Top K")

                    generate_btn = gr.Button("Generate Audio", variant="primary")

                with gr.Column(scale=1):
                    audio_output = gr.Audio(label="Generated Audio", autoplay=False)
                    status = gr.Markdown("")
                    perf_info = gr.Markdown("")
                    gpu_info = gr.Markdown(_format_gpu_markdown(service))

            gr.Markdown("## Voice Comparison")
            gr.Markdown("Compare two voice configurations for the same text and language.")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Voice A")
                    gender_a = gr.Radio(GENDER_CHOICES, value=Gender.FEMALE.value, label="Gender A")
                    accent_a = gr.Dropdown(
                        accent_choices(DEFAULT_LANGUAGE),
                        value=default_accent(DEFAULT_LANGUAGE),
                        label="Accent A",
                    )
                    personality_a = gr.CheckboxGroup(
                        PERSONALITY_CHOICES, value=[Personality.WARM.value], label="Personality A"
                    )
                    speed_a = gr.Dropdown(SPEED_CHOICES, value=Speed.NORMAL.value, label="Speed A")
                    audio_a = gr.Audio(label="Voice A Output", autoplay=False)
                with gr.Column():
                    gr.Markdown("### Voice B")
                    gender_b = gr.Radio(GENDER_CHOICES, value=Gender.MALE.value, label="Gender B")
                    accent_b = gr.Dropdown(
                        accent_choices(DEFAULT_LANGUAGE),
                        value=default_accent(DEFAULT_LANGUAGE),
                        label="Accent B",
                    )
                    personality_b = gr.CheckboxGroup(
                        PERSONALITY_CHOICES, value=[Personality.CALM.value], label="Personality B"
                    )
                    speed_b = gr.Dropdown(
                        SPEED_CHOICES, value=Speed.SLIGHTLY_SLOW.value, label="Speed B"
                    )
                    audio_b = gr.Audio(label="Voice B Output", autoplay=False)

            compare_btn = gr.Button("Generate Comparison")

        with gr.Tab("Voice Clone"):
            gr.Markdown(
                "Clone a voice from a short reference audio clip (3+ seconds recommended) "
                "using the smaller **Qwen3-TTS-12Hz-0.6B-Base** model. This model is loaded "
                "lazily, on the first click below, to avoid holding two large models in VRAM "
                "at once."
            )
            with gr.Row():
                with gr.Column(scale=1):
                    clone_language = gr.Dropdown(
                        LANGUAGE_CHOICES, value=DEFAULT_LANGUAGE, label="Language"
                    )
                    clone_text_input = gr.Textbox(
                        value=SAMPLE_TEXTS[DEFAULT_LANGUAGE],
                        label="Text to synthesize",
                        lines=4,
                    )
                    clone_char_count = gr.Markdown(
                        _char_count_label(SAMPLE_TEXTS[DEFAULT_LANGUAGE])
                    )

                    ref_audio = gr.Audio(
                        sources=["upload", "microphone"],
                        type="filepath",
                        label="Reference Audio",
                    )
                    clone_mode = gr.Radio(
                        CLONE_MODE_CHOICES,
                        value=CLONE_MODE_ICL,
                        label="Cloning Mode",
                    )
                    ref_text = gr.Textbox(
                        label="Reference Text (what is said in the reference audio)",
                        lines=2,
                        visible=True,
                    )

                    with gr.Accordion("Advanced Settings", open=False):
                        clone_seed = gr.Number(label="Seed (optional)", value=None, precision=0)
                        clone_temperature = gr.Slider(
                            0.1, 1.5, value=0.9, step=0.05, label="Temperature"
                        )
                        clone_top_p = gr.Slider(0.1, 1.0, value=1.0, step=0.05, label="Top P")
                        clone_top_k = gr.Slider(0, 100, value=50, step=1, label="Top K")

                    generate_clone_btn = gr.Button("Generate Cloned Audio", variant="primary")

                with gr.Column(scale=1):
                    clone_audio_output = gr.Audio(label="Generated Audio", autoplay=False)
                    clone_status = gr.Markdown("")
                    clone_perf_info = gr.Markdown("")
                    clone_gpu_info = gr.Markdown(_format_gpu_markdown(voice_clone_service))

        gr.Markdown("## Session History")
        history_table = gr.Dataframe(headers=HISTORY_HEADERS, value=[], wrap=True)

        # --- Wiring -----------------------------------------------------

        prompt_axis_inputs = [
            language,
            accent,
            gender,
            age,
            personality,
            emotion,
            speed,
            custom_instruction,
        ]

        guarded_rebuild_inputs = [preset_guard_state, *prompt_axis_inputs]

        language.change(
            fn=_on_language_change,
            inputs=[language, preset_guard_state],
            outputs=[accent, text_input, char_count],
        ).then(
            fn=_guarded_rebuild_prompt,
            inputs=guarded_rebuild_inputs,
            outputs=[voice_prompt, preset_guard_state],
        )

        # `accent` and `gender` can also be set programmatically by a Voice
        # Preset load, so they go through the same guard as `language`.
        for control in (accent, gender):
            control.change(
                fn=_guarded_rebuild_prompt,
                inputs=guarded_rebuild_inputs,
                outputs=[voice_prompt, preset_guard_state],
            )

        # These are never touched by preset loading, so no guard is needed.
        for control in (age, personality, emotion, speed, custom_instruction):
            control.change(fn=_rebuild_prompt, inputs=prompt_axis_inputs, outputs=[voice_prompt])

        reset_prompt_btn.click(
            fn=_rebuild_prompt, inputs=prompt_axis_inputs, outputs=[voice_prompt]
        )

        text_input.change(fn=_char_count_label, inputs=[text_input], outputs=[char_count])

        banking_preset.change(
            fn=_on_banking_preset_change,
            inputs=[banking_preset, language],
            outputs=[text_input],
        )

        voice_preset_dropdown.change(
            fn=_on_voice_preset_change,
            inputs=[voice_preset_dropdown, language, accent, gender],
            outputs=[language, accent, gender, voice_prompt, preset_guard_state],
        )

        generate_btn.click(
            fn=generate_audio,
            inputs=[
                text_input,
                language,
                accent,
                gender,
                voice_prompt,
                seed,
                temperature,
                top_p,
                top_k,
                history_state,
            ],
            outputs=[audio_output, perf_info, gpu_info, status, history_state, history_table],
        )

        compare_btn.click(
            fn=generate_comparison,
            inputs=[
                text_input,
                language,
                gender_a,
                accent_a,
                personality_a,
                speed_a,
                gender_b,
                accent_b,
                personality_b,
                speed_b,
                history_state,
            ],
            outputs=[audio_a, audio_b, history_state, history_table],
        )

        clone_language.change(
            fn=_on_clone_language_change,
            inputs=[clone_language],
            outputs=[clone_text_input, clone_char_count],
        )

        clone_text_input.change(
            fn=_char_count_label, inputs=[clone_text_input], outputs=[clone_char_count]
        )

        clone_mode.change(
            fn=lambda mode: gr.update(visible=mode != CLONE_MODE_X_VECTOR),
            inputs=[clone_mode],
            outputs=[ref_text],
        )

        generate_clone_btn.click(
            fn=generate_voice_clone,
            inputs=[
                clone_text_input,
                clone_language,
                ref_audio,
                ref_text,
                clone_mode,
                clone_seed,
                clone_temperature,
                clone_top_p,
                clone_top_k,
                history_state,
            ],
            outputs=[
                clone_audio_output,
                clone_perf_info,
                clone_gpu_info,
                clone_status,
                history_state,
                history_table,
            ],
        )

    return demo


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    settings = get_settings()

    service = QwenTTSService(settings, model_source=settings.resolve_model_source())
    service.load()

    # The voice-clone (Base) model is loaded lazily on first use of that tab,
    # so a GPU that can only fit one model at a time (e.g. a 4-6GB laptop
    # GPU) doesn't fail at startup just because both models are configured.
    voice_clone_service = QwenTTSService(
        settings, model_source=settings.resolve_voice_clone_model_source()
    )

    demo = build_ui(service, voice_clone_service, settings)
    demo.launch(server_name=settings.playground_host, server_port=settings.playground_port)


if __name__ == "__main__":
    main()
