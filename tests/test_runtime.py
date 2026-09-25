import torch

from qwen_tts_playground import runtime
from qwen_tts_playground.runtime import FLASH_IMPL, FlashAttentionStatus, resolve_attention

USABLE = FlashAttentionStatus(True, True, "2.8.3")
MISSING = FlashAttentionStatus(False, False, None, "flash-attn package not installed")


def _patch(monkeypatch, status):
    monkeypatch.setattr(runtime, "check_flash_attention", lambda *a, **k: status)


def test_auto_uses_flash_when_usable(monkeypatch):
    _patch(monkeypatch, USABLE)
    choice = resolve_attention("auto", True, torch.bfloat16)
    assert choice.implementation == FLASH_IMPL
    assert choice.label == "FlashAttention 2"


def test_auto_falls_back_when_unavailable(monkeypatch):
    _patch(monkeypatch, MISSING)
    choice = resolve_attention("auto", True, torch.bfloat16)
    assert choice.implementation is None
    assert "not installed" in choice.reason


def test_default_never_uses_flash(monkeypatch):
    _patch(monkeypatch, USABLE)
    assert resolve_attention("default", True, torch.bfloat16).implementation is None


def test_flash_request_warns_and_falls_back(monkeypatch, caplog):
    _patch(monkeypatch, MISSING)
    with caplog.at_level("WARNING"):
        choice = resolve_attention("flash", True, torch.bfloat16)
    assert choice.implementation is None
    assert "FlashAttention requested but unavailable" in caplog.text


def test_cpu_dtype_is_float32():
    assert runtime.select_dtype(False) == torch.float32
