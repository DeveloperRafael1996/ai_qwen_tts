import inspect

from qwen_tts_playground.config import Settings
from qwen_tts_playground.playground import build_ui
from qwen_tts_playground.tts_service import QwenTTSService


def test_every_event_passes_as_many_inputs_as_its_handler_accepts():
    settings = Settings(cartesia_api_key="")
    services = [QwenTTSService(settings) for _ in range(3)]
    demo = build_ui(*services, settings)

    checked = 0
    for fn in demo.fns.values():
        if fn.fn is None or not fn.inputs:
            continue
        params = [
            p
            for p in inspect.signature(fn.fn).parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        required = [p for p in params if p.default is p.empty]
        assert len(required) <= len(fn.inputs) <= len(params), fn.fn.__name__
        checked += 1
    assert checked > 0
