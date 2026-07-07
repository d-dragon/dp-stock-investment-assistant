"""Shared M2B.2 test assertions."""

from __future__ import annotations

from core.tools.normalization import NormalizedOutputKind, contains_blocked_prompt_payload


def assert_normalized_kind(payload, expected):
    assert payload["kind"] == (expected.value if isinstance(expected, NormalizedOutputKind) else expected)


def assert_no_raw_prompt_payload(payload):
    assert contains_blocked_prompt_payload(payload) is False


def assert_degraded(payload, code):
    assert payload["kind"] == NormalizedOutputKind.DEGRADED_STATE.value
    assert payload["degraded_state"]["code"] == code
