"""Unit tests for ChatService two-stage fallback formatter and execution timeout budget.

Validates Stage 1 direct extraction, Stage 2 fallback formatting, and 10.0s timeout degradation.
"""

import time
import pytest
from unittest.mock import MagicMock

from src.core.types import (
    AgentResponse,
    ResponseStatus,
    StockAnalysisResponse,
    ErrorResponse,
)
from src.services.chat_service import ChatService


def test_fallback_formatter_stage1_direct_extraction():
    """Verify Stage 1 directly returns AgentResponse.structured_content when present."""
    mock_agent = MagicMock()
    service = ChatService(agent_provider=mock_agent, config={})

    payload = StockAnalysisResponse(
        symbol="FPT",
        summary="FPT fundamental growth report.",
        sentiment="BULLISH",
    )
    res = AgentResponse(
        content="Report complete.",
        provider="openai",
        model="gpt-4o",
        status=ResponseStatus.SUCCESS,
        structured_content=payload,
    )

    out_payload, status = service._extract_structured_response(res, timeout_seconds=10.0)
    assert out_payload == payload
    assert status == ResponseStatus.SUCCESS


def test_fallback_formatter_stage2_timeout_degradation():
    """Verify Stage 2 degrades to PARTIAL status when timeout is exceeded."""
    mock_agent = MagicMock()
    service = ChatService(agent_provider=mock_agent, config={})

    # Response with no direct structured payload
    res = AgentResponse(
        content="Raw unstructured text from LLM.",
        provider="openai",
        model="gpt-4o",
        status=ResponseStatus.SUCCESS,
        structured_content=None,
    )

    # Force 0.001s timeout to simulate timeout limit hit
    out_payload, status = service._extract_structured_response(res, timeout_seconds=0.001)
    assert getattr(out_payload, "error_code", "") == "FALLBACK_EXTRACTION_TIMEOUT"
    assert getattr(out_payload, "route_kind", "") == "ERROR"
    assert status.value == ResponseStatus.PARTIAL.value
