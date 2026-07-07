"""M2B.2 tests for envelopes, normalized outputs, and prompt-safe context."""

from __future__ import annotations

import sys
import types

import pytest

from core.tools.context import assemble_tool_context_pack
from core.tools.gateway import ToolGateway
from core.tools.normalization import (
    AdmissionOutcome,
    DegradedReason,
    NormalizedOutput,
    NormalizedOutputKind,
    SourceMetadata,
    ToolExecutionEnvelope,
    contains_blocked_prompt_payload,
    make_degraded_output,
    make_system_record_output,
)
from tests.fixtures.tool_system_m2b2.payloads import DEGRADED_FIXTURES, RAW_PROVIDER_PAYLOAD
from tests.fixtures.tool_system_m2b2.symbols import SYMBOL_RECORDS
from tests.helpers.tool_system_m2b2_helpers import assert_no_raw_prompt_payload


def test_tool_execution_envelope_required_fields():
    output = make_system_record_output(SYMBOL_RECORDS[0])
    envelope = ToolExecutionEnvelope(
        route="price_check",
        selected_tool="stock_symbol",
        selected_adapter="internal_symbol_store",
        descriptor_identity="stock_symbol:m2b2",
        admission_outcome=AdmissionOutcome.ALLOWED,
        normalized_output=output,
        cache_status="not_applicable",
        freshness_status="current",
        trace_metadata={"raw_trace": "blocked", "safe": "kept"},
    )
    payload = envelope.to_dict()

    assert payload["route"] == "price_check"
    assert payload["selected_tool"] == "stock_symbol"
    assert payload["normalized_output_ref"] == output.output_id
    assert "raw_trace" not in payload["trace_metadata"]


@pytest.mark.parametrize("kind", list(NormalizedOutputKind))
def test_exactly_one_normalized_output_kind(kind):
    if kind == NormalizedOutputKind.DEGRADED_STATE:
        output = make_degraded_output(
            code="validation_failed",
            safe_message="Validation failed.",
            reason=DegradedReason.VALIDATION_FAILED,
        )
    else:
        output = NormalizedOutput(kind=kind, content={"value": kind.value})

    assert output.kind == kind
    assert output.to_dict()["kind"] == kind.value


def test_raw_provider_payloads_are_excluded_from_prompt_context():
    assert contains_blocked_prompt_payload(RAW_PROVIDER_PAYLOAD)
    safe_output = NormalizedOutput(
        kind=NormalizedOutputKind.EVIDENCE_FACT,
        content={"symbol": "FPT", "value": 100000},
        source_metadata=SourceMetadata(provider_id="fixture", provider_class="official"),
    )
    pack = assemble_tool_context_pack(
        request_id="request-1",
        route="price_check",
        normalized_outputs=(safe_output,),
    )

    projection = pack.prompt_projection()
    assert_no_raw_prompt_payload(projection)


@pytest.mark.parametrize("reason", DEGRADED_FIXTURES)
def test_degraded_states_are_machine_detectable(reason):
    output = make_degraded_output(
        code=reason,
        safe_message=f"{reason} occurred.",
        reason=reason,
        route="price_check",
        tool_name="stock_symbol",
    )

    assert output.kind == NormalizedOutputKind.DEGRADED_STATE
    assert output.degraded_state.code == reason
    assert output.prompt_projection()["degraded_state"]["user_visible"] is True


def test_safe_public_metadata_separates_trace_internals():
    output = make_system_record_output(SYMBOL_RECORDS[0])
    envelope = ToolExecutionEnvelope(
        route="price_check",
        selected_tool="stock_symbol",
        descriptor_identity="stock_symbol:m2b2",
        admission_outcome=AdmissionOutcome.ALLOWED,
        normalized_output=output,
        trace_metadata={"descriptor_hash": "internal", "credential": "secret"},
    )
    public = envelope.public_metadata()

    assert "trace_metadata" not in public
    assert "descriptor_hash" not in public
    assert public["normalized_output_kind"] == "SystemRecord"


def test_gateway_can_build_envelope_from_normalized_tool_result():
    gateway = ToolGateway(registry=__import__("core.tools.registry", fromlist=["ToolRegistry"]).ToolRegistry())
    tool_result = {"normalized_output": make_system_record_output(SYMBOL_RECORDS[0]).to_dict()}

    envelope = gateway.build_execution_envelope(
        route=__import__("core.routes", fromlist=["StockQueryRoute"]).StockQueryRoute.PRICE_CHECK,
        tool_name="stock_symbol",
        result=tool_result,
    )

    assert envelope.normalized_output.kind == NormalizedOutputKind.SYSTEM_RECORD
    assert envelope.selected_tool == "stock_symbol"


def test_agent_exposes_prompt_safe_context_projection_helper(monkeypatch):
    class StubHumanMessage:
        def __init__(self, content):
            self.content = content

    class StubAIMessage:
        def __init__(self, content=""):
            self.content = content

    messages_module = types.ModuleType("langchain_core.messages")
    messages_module.HumanMessage = StubHumanMessage
    messages_module.SystemMessage = type("StubSystemMessage", (), {})
    messages_module.AIMessage = StubAIMessage

    openai_module = types.ModuleType("langchain_openai")
    openai_module.ChatOpenAI = type("StubChatOpenAI", (), {})

    monkeypatch.setitem(sys.modules, "langchain_core.messages", messages_module)
    monkeypatch.setitem(sys.modules, "langchain_openai", openai_module)

    from core.stock_assistant_agent import StockAssistantAgent

    output = make_system_record_output(SYMBOL_RECORDS[0])
    agent = StockAssistantAgent.__new__(StockAssistantAgent)
    agent._tool_gateway = type("Gateway", (), {"trace_records": []})()

    projection = StockAssistantAgent._build_prompt_safe_tool_context_projection(
        agent,
        request_id="request-1",
        route="price_check",
        normalized_outputs=[output],
    )

    assert projection["request_id"] == "request-1"
    assert projection["route"] == "price_check"
    assert projection["normalized_outputs"][0]["kind"] == "SystemRecord"
    assert_no_raw_prompt_payload(projection)
