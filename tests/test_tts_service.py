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
