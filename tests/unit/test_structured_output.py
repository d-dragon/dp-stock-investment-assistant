"""Unit tests for Agent Structured Outputs and Control-Plane Response Tools.

Validates Pydantic v2 schemas, tool execution, AgentResponse serialization,
and ToolRegistry response tool registration.
"""

import pytest
from src.core.types import (
    ResponseStatus,
    StockAnalysisResponse,
    RecommendationResponse,
    GeneralChatResponse,
    ErrorResponse,
    AgentResponse,
)
from src.core.tools.response_tools import (
    SubmitStockAnalysisTool,
    SubmitRecommendationTool,
    SubmitGeneralChatTool,
)
from src.core.tools.registry import get_tool_registry, register_response_tools, reset_tool_registry
from src.core.tools.descriptors import RiskClass


def test_stock_analysis_response_schema():
    """Verify StockAnalysisResponse schema instantiation and default values."""
    res = StockAnalysisResponse(
        symbol="FPT",
        summary="FPT Corp demonstrates strong YoY tech growth.",
        sentiment="BULLISH",
        key_metrics={"pe_ratio": 18.5, "revenue_growth": 0.21},
        citations=["VNDirect", "Bloomberg"],
    )
    assert res.route_kind == "FUNDAMENTALS"
    assert res.symbol == "FPT"
    assert res.sentiment == "BULLISH"
    assert res.key_metrics["pe_ratio"] == 18.5
    assert len(res.citations) == 2


def test_recommendation_response_schema():
    """Verify RecommendationResponse schema and mandatory disclosure."""
    res = RecommendationResponse(
        recommendation="BUY",
        thesis="Strong quarterly earnings and market leadership.",
        time_horizon="LONG_TERM",
        risk_factors=["Regulatory shift", "FX fluctuation"],
    )
    assert res.route_kind == "IDEAS"
    assert res.recommendation == "BUY"
    assert "Not financial advice" in res.disclaimer
    assert len(res.risk_factors) == 2


def test_general_chat_response_schema():
    """Verify GeneralChatResponse schema and defaults."""
    res = GeneralChatResponse(
        message="Hello! I can assist you with Vietnam stock analysis.",
        topics_covered=["general_inquiry"],
        follow_up_suggestions=["Analyze FPT stock", "Market overview"],
    )
    assert res.route_kind == "GENERAL_CHAT"
    assert res.message.startswith("Hello!")
    assert len(res.follow_up_suggestions) == 2


def test_response_tools_execution():
    """Verify response tools return direct typed schema objects."""
    analysis_tool = SubmitStockAnalysisTool()
    assert analysis_tool.name == "submit_stock_analysis"
    assert analysis_tool.return_direct is True
    assert analysis_tool.risk_class == RiskClass.BOUNDED_NON_MUTATING

    out_analysis = analysis_tool._run(
        symbol="VNM",
        summary="Vinamilk stable dividend yield.",
        sentiment="NEUTRAL",
    )
    assert isinstance(out_analysis, StockAnalysisResponse)
    assert out_analysis.symbol == "VNM"

    rec_tool = SubmitRecommendationTool()
    out_rec = rec_tool._run(
        recommendation="HOLD",
        thesis="Consolidation phase near support level.",
    )
    assert isinstance(out_rec, RecommendationResponse)
    assert out_rec.recommendation == "HOLD"

    chat_tool = SubmitGeneralChatTool()
    out_chat = chat_tool._run(message="How can I help with your portfolio?")
    assert isinstance(out_chat, GeneralChatResponse)
    assert out_chat.message.startswith("How can I help")


def test_agent_response_structured_content_serialization():
    """Verify AgentResponse to_dict includes structured_content payload."""
    analysis_payload = StockAnalysisResponse(
        symbol="HPG",
        summary="Hoa Phat Group steel volume surge.",
        sentiment="BULLISH",
    )
    agent_res = AgentResponse(
        content="Analysis complete.",
        provider="openai",
        model="gpt-4o",
        status=ResponseStatus.SUCCESS,
        structured_content=analysis_payload,
    )
    assert agent_res.structured_content == analysis_payload
    d = agent_res.to_dict()
    assert d["structured_content"]["symbol"] == "HPG"
    assert d["structured_content"]["route_kind"] == "FUNDAMENTALS"


def test_tool_registry_register_response_tools():
    """Verify register_response_tools registers all 3 control-plane tools."""
    reset_tool_registry()
    reg = get_tool_registry()
    register_response_tools(reg)

    assert "submit_stock_analysis" in reg
    assert "submit_recommendation" in reg
    assert "submit_general_chat" in reg
    assert reg.is_enabled("submit_stock_analysis") is True
