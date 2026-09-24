import sys
import types
from pathlib import Path

import numpy as np
import pytest
import torch

from qwen_tts_playground.config import Settings
from qwen_tts_playground.tts_service import (
    CudaOutOfMemoryError,
    GenerationError,
    InvalidLanguageError,
    InvalidReferenceAudioError,
    InvalidSpeakerError,
    InvalidTextError,
    QwenTTSService,
    build_output_path,
    sanitize_filename_component,
)

SAMPLE_RATE = 24000
AUDIO_SECONDS = 1.0


class FakeQwen3TTSModel:
    """Stand-in for qwen_tts.Qwen3TTSModel; no real weights are ever loaded."""

    def __init__(self):
        self.calls: list[dict] = []
        self.raise_oom = False
        self.raise_error = False

    @classmethod
    def from_pretrained(cls, path, **kwargs):
        return cls()

    def generate_voice_design(self, text, language, instruct, **kwargs):
        self.calls.append(
            {"text": text, "language": language, "instruct": instruct, "kwargs": kwargs}
        )
        if self.raise_oom:
            raise torch.cuda.OutOfMemoryError("simulated CUDA OOM")
        if self.raise_error:
            raise RuntimeError("simulated generation failure")

        wav = np.zeros(int(SAMPLE_RATE * AUDIO_SECONDS), dtype=np.float32)
        return [wav], SAMPLE_RATE

    def generate_voice_clone(
        self, text, language, ref_audio, ref_text, x_vector_only_mode, **kwargs
    ):
        self.calls.append(
            {
                "text": text,
                "language": language,
                "ref_audio": ref_audio,
                "ref_text": ref_text,
                "x_vector_only_mode": x_vector_only_mode,
                "kwargs": kwargs,
            }
        )
        if self.raise_oom:
            raise torch.cuda.OutOfMemoryError("simulated CUDA OOM")
        if self.raise_error:
            raise RuntimeError("simulated generation failure")

        wav = np.zeros(int(SAMPLE_RATE * AUDIO_SECONDS), dtype=np.float32)
        return [wav], SAMPLE_RATE

    def generate_custom_voice(self, text, language, speaker, instruct, **kwargs):
        self.calls.append(
            {
                "text": text,
                "language": language,
                "speaker": speaker,
                "instruct": instruct,
                "kwargs": kwargs,
            }
        )
        if self.raise_oom:
            raise torch.cuda.OutOfMemoryError("simulated CUDA OOM")
        if self.raise_error:
            raise RuntimeError("simulated generation failure")

        wav = np.zeros(int(SAMPLE_RATE * AUDIO_SECONDS), dtype=np.float32)
        return [wav], SAMPLE_RATE


@pytest.fixture
def fake_qwen_tts_module(monkeypatch):
    module = types.ModuleType("qwen_tts")
    module.Qwen3TTSModel = FakeQwen3TTSModel
    monkeypatch.setitem(sys.modules, "qwen_tts", module)
    return module


@pytest.fixture
def service(tmp_path, fake_qwen_tts_module, monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    settings = Settings(
        qwen_tts_model_path=str(tmp_path / "does-not-exist"),
        output_dir=tmp_path / "outputs",
    )
    svc = QwenTTSService(settings)
    svc.load()
    return svc


def test_load_is_idempotent(service):
    model_instance = service._model
    service.load()
    assert service._model is model_instance


def test_synthesize_success_writes_wav_and_computes_metrics(service):
    result = service.synthesize(text="Hello there", language="English", instruct="Some instruct")

    assert result.sample_rate == SAMPLE_RATE
    assert result.audio_duration_seconds == pytest.approx(AUDIO_SECONDS)
    assert result.generation_time_seconds >= 0
    assert Path(result.output_path).exists()


def test_rtf_calculation_matches_definition(service):
    result = service.synthesize(text="Hi", language="Spanish", instruct="x")
    expected_rtf = result.generation_time_seconds / result.audio_duration_seconds
    assert result.real_time_factor == pytest.approx(expected_rtf)


def test_synthesize_empty_text_raises(service):
    with pytest.raises(InvalidTextError):
        service.synthesize(text="   ", language="English", instruct="x")


def test_synthesize_invalid_language_raises(service):
    with pytest.raises(InvalidLanguageError):
        service.synthesize(text="Hello", language="French", instruct="x")


def test_synthesize_cuda_oom_is_wrapped(service):
    service._model.raise_oom = True
    with pytest.raises(CudaOutOfMemoryError):
        service.synthesize(text="Hello", language="English", instruct="x")


def test_synthesize_generic_failure_is_wrapped(service):
    service._model.raise_error = True
    with pytest.raises(GenerationError):
        service.synthesize(text="Hello", language="English", instruct="x")


def test_synthesize_passes_generation_kwargs(service):
    service.synthesize(
        text="Hello",
        language="English",
        instruct="x",
        temperature=0.5,
        top_p=0.8,
        top_k=10,
        seed=42,
    )
    call = service._model.calls[-1]
    assert call["kwargs"] == {"temperature": 0.5, "top_p": 0.8, "top_k": 10}


def test_sanitize_filename_component_strips_accents_and_spaces():
    assert sanitize_filename_component("Latin American") == "latin_american"
    assert sanitize_filename_component("São Paulo") == "s_o_paulo"
    assert sanitize_filename_component("  ") == "unknown"


def test_build_output_path_matches_expected_format(tmp_path):
    path = build_output_path(tmp_path, "Spanish", "Peruvian", "Female")
    assert path.parent == tmp_path
    assert path.suffix == ".wav"
    assert path.name.startswith("spanish_peruvian_female_")


def test_build_output_path_never_overwrites(tmp_path):
    first = build_output_path(tmp_path, "Spanish", "Peruvian", "Female")
    first.write_bytes(b"existing-data")

    second = build_output_path(tmp_path, "Spanish", "Peruvian", "Female")

    assert first != second
    assert not second.exists()


def test_synthesize_voice_clone_icl_mode_success(service):
    result = service.synthesize_voice_clone(
        text="Hello there",
        language="English",
        ref_audio="/tmp/ref.wav",
        ref_text="This is what the reference audio says.",
    )

    assert result.sample_rate == SAMPLE_RATE
    assert Path(result.output_path).exists()
    call = service._model.calls[-1]
    assert call["ref_audio"] == "/tmp/ref.wav"
    assert call["ref_text"] == "This is what the reference audio says."
    assert call["x_vector_only_mode"] is False


def test_synthesize_voice_clone_x_vector_mode_does_not_need_ref_text(service):
    result = service.synthesize_voice_clone(
        text="Hello there",
        language="English",
        ref_audio="/tmp/ref.wav",
        ref_text=None,
        x_vector_only_mode=True,
    )
    assert result.sample_rate == SAMPLE_RATE
    call = service._model.calls[-1]
    assert call["x_vector_only_mode"] is True


def test_synthesize_voice_clone_missing_ref_audio_raises(service):
    with pytest.raises(InvalidReferenceAudioError):
        service.synthesize_voice_clone(text="Hello", language="English", ref_audio="")


def test_synthesize_voice_clone_icl_mode_without_ref_text_raises(service):
    with pytest.raises(InvalidReferenceAudioError):
        service.synthesize_voice_clone(
            text="Hello",
            language="English",
            ref_audio="/tmp/ref.wav",
            ref_text=None,
            x_vector_only_mode=False,
        )


def test_synthesize_voice_clone_empty_text_raises(service):
    with pytest.raises(InvalidTextError):
        service.synthesize_voice_clone(
            text="  ", language="English", ref_audio="/tmp/ref.wav", ref_text="hi"
        )


def test_synthesize_voice_clone_cuda_oom_is_wrapped(service):
    service._model.raise_oom = True
    with pytest.raises(CudaOutOfMemoryError):
        service.synthesize_voice_clone(
            text="Hello", language="English", ref_audio="/tmp/ref.wav", ref_text="hi"
        )


def test_resolve_voice_clone_model_source_prefers_local_dir(tmp_path):
    local_dir = tmp_path / "clone-model"
    local_dir.mkdir()
    (local_dir / "config.json").write_text("{}")

    settings = Settings(qwen_tts_voice_clone_model_path=str(local_dir))
    assert settings.resolve_voice_clone_model_source() == str(local_dir)


def test_resolve_voice_clone_model_source_falls_back_to_hf_repo(tmp_path):
    settings = Settings(qwen_tts_voice_clone_model_path=str(tmp_path / "does-not-exist"))
    assert settings.resolve_voice_clone_model_source() == "Qwen/Qwen3-TTS-12Hz-0.6B-Base"


def test_qwen_tts_service_respects_model_source_override(
    tmp_path, fake_qwen_tts_module, monkeypatch
):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    settings = Settings(
        qwen_tts_model_path=str(tmp_path / "voice-design-not-used"),
        output_dir=tmp_path / "outputs",
    )
    svc = QwenTTSService(settings, model_source=str(tmp_path / "explicit-override"))
    svc.load()
    assert svc._model_source == str(tmp_path / "explicit-override")


def test_resolve_custom_voice_model_source_prefers_local_dir(tmp_path):
    local_dir = tmp_path / "custom-voice-model"
    local_dir.mkdir()
    (local_dir / "config.json").write_text("{}")

    settings = Settings(qwen_tts_custom_voice_model_path=str(local_dir))
    assert settings.resolve_custom_voice_model_source() == str(local_dir)


def test_resolve_custom_voice_model_source_falls_back_to_hf_repo(tmp_path):
    settings = Settings(qwen_tts_custom_voice_model_path=str(tmp_path / "does-not-exist"))
    assert settings.resolve_custom_voice_model_source() == "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"


def test_synthesize_custom_voice_success(service):
    result = service.synthesize_custom_voice(text="Hello there", language="English", speaker="Ryan")
    assert result.sample_rate == SAMPLE_RATE
    assert Path(result.output_path).exists()
    call = service._model.calls[-1]
    assert call["speaker"] == "Ryan"
    assert call["instruct"] is None


def test_synthesize_custom_voice_forwards_instruct(service):
    service.synthesize_custom_voice(
        text="Hello", language="English", speaker="Ryan", instruct="Speak happily"
    )
    call = service._model.calls[-1]
    assert call["instruct"] == "Speak happily"


def test_synthesize_custom_voice_missing_speaker_raises(service):
    with pytest.raises(InvalidSpeakerError):
        service.synthesize_custom_voice(text="Hello", language="English", speaker="")


def test_synthesize_custom_voice_empty_text_raises(service):
    with pytest.raises(InvalidTextError):
        service.synthesize_custom_voice(text="  ", language="English", speaker="Ryan")


def test_synthesize_custom_voice_invalid_language_raises(service):
    with pytest.raises(InvalidLanguageError):
        service.synthesize_custom_voice(text="Hello", language="French", speaker="Ryan")


def test_synthesize_custom_voice_cuda_oom_is_wrapped(service):
    service._model.raise_oom = True
    with pytest.raises(CudaOutOfMemoryError):
        service.synthesize_custom_voice(text="Hello", language="English", speaker="Ryan")


def test_gradio_auth_disabled_by_default():
    assert Settings(app_username="", app_password="").gradio_auth() is None
    assert Settings(app_username="admin", app_password="").gradio_auth() is None


def test_gradio_auth_enabled_when_both_set():
    assert Settings(app_username="admin", app_password="s3cret").gradio_auth() == (
        "admin",
        "s3cret",
    )
