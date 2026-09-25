import contextlib

import numpy as np
import pytest

from qwen_tts_playground import cartesia_client
from qwen_tts_playground.cartesia_client import CartesiaClient, CartesiaConfigError
from qwen_tts_playground.tts_service import GenerationError, InvalidLanguageError, InvalidTextError


class FakeResponse:
    def __init__(self, status_code=200, chunks=(), body=b""):
        self.status_code = status_code
        self._chunks = chunks
        self._body = body

    def read(self):
        return self._body

    def iter_bytes(self):
        yield from self._chunks


def _patch_stream(monkeypatch, response, captured=None):
    @contextlib.contextmanager
    def fake_stream(method, url, json, headers, timeout):
        if captured is not None:
            captured.update(json=json, headers=headers)
        yield response

    monkeypatch.setattr(cartesia_client.httpx, "stream", fake_stream)


def _client():
    return CartesiaClient("secret-key")


def test_synthesize_writes_wav_and_measures_ttfa(monkeypatch, tmp_path):
    pcm = np.zeros(24000, dtype="<i2").tobytes()
    captured: dict = {}
    _patch_stream(monkeypatch, FakeResponse(chunks=[pcm[:1001], pcm[1001:]]), captured)

    result = _client().synthesize("Hola", "Spanish", "voice-1", tmp_path / "o.wav", speed=1.1)

    assert result.audio_duration_seconds == pytest.approx(1.0)
    assert result.ttfa_ms is not None and result.ttfa_ms <= result.generation_time_seconds * 1000
    assert (tmp_path / "o.wav").exists()
    assert captured["json"]["model_id"] == "sonic-3.6"
    assert captured["json"]["language"] == "es"
    assert captured["json"]["generation_config"] == {"speed": 1.1}
    assert captured["headers"]["Authorization"] == "Bearer secret-key"


def test_http_error_does_not_leak_key(monkeypatch, tmp_path):
    _patch_stream(monkeypatch, FakeResponse(status_code=401, body=b"unauthorized"))
    with pytest.raises(GenerationError, match="401") as exc:
        _client().synthesize("Hola", "Spanish", "v", tmp_path / "o.wav")
    assert "secret-key" not in str(exc.value)


def test_empty_audio_raises(monkeypatch, tmp_path):
    _patch_stream(monkeypatch, FakeResponse(chunks=[]))
    with pytest.raises(GenerationError):
        _client().synthesize("Hola", "Spanish", "v", tmp_path / "o.wav")


def test_validation_errors(tmp_path):
    out = tmp_path / "o.wav"
    with pytest.raises(CartesiaConfigError):
        CartesiaClient("").synthesize("Hi", "English", "v", out)
    with pytest.raises(CartesiaConfigError):
        _client().synthesize("Hi", "English", " ", out)
    with pytest.raises(InvalidTextError):
        _client().synthesize(" ", "English", "v", out)
    with pytest.raises(InvalidLanguageError):
        _client().synthesize("Hi", "French", "v", out)
