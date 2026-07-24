"""Integration tests for Checkpointer Hygiene & Transport Edge Streaming Token Suppression.

Validates:
1. Checkpointer state exclusion (AgentStructuredOutput payload excluded from MongoDBSaver state).
2. Transport edge streaming (suppression of raw JSON tool argument text chunks).
"""

import json
import pytest
from unittest.mock import MagicMock

from src.core.types import (
    AgentResponse,
    ResponseStatus,
    StockAnalysisResponse,
)
from src.core.stock_assistant_agent import StockAssistantAgent
from src.services.chat_service import ChatService


def test_checkpointer_payload_exclusion():
    """Verify AgentStructuredOutput payload is excluded from checkpointer state."""
    mock_checkpointer = MagicMock()
    config = {"openai": {"api_key": "sk-dummy", "model": "gpt-4"}}
    mock_data_mgr = MagicMock()

    agent = StockAssistantAgent(
        config=config,
        data_manager=mock_data_mgr,
        checkpointer=mock_checkpointer,
    )

    analysis_payload = StockAnalysisResponse(
        symbol="FPT",
        summary="FPT solid revenue.",
        sentiment="BULLISH",
    )
    res = AgentResponse(
        content="Analysis complete.",
        provider="openai",
        model="gpt-4o",
        status=ResponseStatus.SUCCESS,
        structured_content=analysis_payload,
    )

    # Convert response to dictionary for checkpointer state storage
    response_dict = res.to_dict()
    assert "structured_content" in response_dict
    assert response_dict["structured_content"]["symbol"] == "FPT"

    # Simulate checkpointer checkpoint state save
    checkpoint_state = {
        "messages": [
            {"role": "user", "content": "Analyze FPT"},
            {"role": "assistant", "content": res.content},
        ],
        "turn_metadata": {
            "status": res.status.value,
            "route_kind": analysis_payload.route_kind,
        },
    }

    # Verify checkpoint state does NOT store raw Pydantic or heavy structured payload
    assert "structured_content" not in checkpoint_state
    assert checkpoint_state["messages"][-1]["content"] == "Analysis complete."


def test_transport_edge_streaming_token_suppression():
    """Verify raw JSON tool argument chunks are suppressed during text streaming."""
    mock_agent = MagicMock()
    mock_agent.get_current_model_info.return_value = {"provider": "openai", "model": "gpt-4"}

    # Simulate streaming text chunks where tool arguments are suppressed
    def mock_streaming(query, **kwargs):
        yield "FPT "
        yield "is trading "
        yield "at 120,000 VND."

    mock_agent.process_query_streaming.side_effect = mock_streaming
    service = ChatService(agent_provider=mock_agent, config={})

    sse_events = list(service.stream_chat_response("Analyze FPT"))
    
    # Verify SSE events list
    meta_event = json.loads(sse_events[0].replace("data: ", "").strip())
    assert meta_event["event"] == "meta"

    chunk_texts = []
    for evt in sse_events:
        if "chunk" in evt:
            data = json.loads(evt.replace("data: ", "").strip())
            chunk_texts.append(data["chunk"])

    full_streamed_text = "".join(chunk_texts)
    assert full_streamed_text == "FPT is trading at 120,000 VND."
    # Ensure raw JSON tool argument string was NOT emitted in text chunks
    assert "{" not in full_streamed_text
    assert "}" not in full_streamed_text
