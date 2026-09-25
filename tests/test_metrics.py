import math

import pytest

from qwen_tts_playground.metrics import (
    RequestMetrics,
    audio_duration_seconds,
    percentile,
    real_time_factor,
    summarize,
    ttfa_ms,
)


def test_audio_duration_from_samples():
    assert audio_duration_seconds(48000, 24000) == 2.0


def test_audio_duration_rejects_bad_sample_rate():
    with pytest.raises(ValueError):
        audio_duration_seconds(10, 0)


def test_rtf_matches_spec_example():
    assert real_time_factor(1.8, 10.0) == pytest.approx(0.18)


def test_rtf_zero_audio_is_infinite():
    assert math.isinf(real_time_factor(1.0, 0.0))


def test_ttfa_in_milliseconds():
    assert ttfa_ms(10.0, 10.2874) == pytest.approx(287.4)


def test_ttfa_is_none_without_streaming():
    assert ttfa_ms(10.0, None) is None


def test_ttfa_rejects_time_going_backwards():
    with pytest.raises(ValueError):
        ttfa_ms(10.0, 9.0)


def test_percentile_interpolates():
    values = [1.0, 2.0, 3.0, 4.0]
    assert percentile(values, 50) == pytest.approx(2.5)
    assert percentile(values, 0) == 1.0
    assert percentile(values, 100) == 4.0


def test_percentile_single_value_and_errors():
    assert percentile([7.0], 99) == 7.0
    with pytest.raises(ValueError):
        percentile([], 50)
    with pytest.raises(ValueError):
        percentile([1.0], 101)


def test_summarize_orders_percentiles():
    s = summarize(list(range(1, 101)))
    assert s.p50 < s.p95 < s.p99


def test_request_log_reports_ttfa_na_and_never_the_text():
    m = RequestMetrics("m", "gpu", "sdpa", 82, 1.4827, 8.23)
    log = m.format_log()
    assert "ttfa_ms=N/A" in log
    assert "model API does not expose first audio chunk" in log
    assert "rtf=0.180" in log
    assert "generation_time_ms=1482.7" in log
    assert "audio_duration_ms=8230" in log


def test_request_log_with_ttfa():
    log = RequestMetrics("m", "gpu", "sdpa", 5, 1.0, 2.0, ttfa_ms=285.34).format_log()
    assert "ttfa_ms=285.3" in log
    assert "ttfa_note" not in log
