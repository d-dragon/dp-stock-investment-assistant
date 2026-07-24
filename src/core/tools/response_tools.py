"""Control-plane response tools for route-adapted structured output delivery.

Implements ADR-AGENT-005 response tools (submit_stock_analysis, submit_recommendation,
submit_general_chat) bound under RiskClass.BOUNDED_NON_MUTATING with return_direct=True.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field

from .base import AgentTool
from .descriptors import RiskClass
from ..types import (
    StockAnalysisResponse,
    RecommendationResponse,
    GeneralChatResponse,
)


class SubmitStockAnalysisInput(BaseModel):
    """Input parameters for submitting structured stock fundamental/technical analysis."""
    symbol: str = Field(..., description="Target stock ticker symbol (e.g. AAPL, FPT)")
    summary: str = Field(..., description="High-level analytical summary")
    sentiment: str = Field(default="NEUTRAL", description="Market sentiment: BULLISH, BEARISH, or NEUTRAL")
    key_metrics: Dict[str, Any] = Field(default_factory=dict, description="Key fundamental/technical metrics dictionary")
    citations: List[str] = Field(default_factory=list, description="List of data provider citations and references")


class SubmitStockAnalysisTool(AgentTool):
    """Control-plane tool for submitting structured stock analysis."""
    name: str = "submit_stock_analysis"
    description: str = "Submit structured stock fundamental & technical analysis matching schema contract."
    args_schema: Type[BaseModel] = SubmitStockAnalysisInput
    return_direct: bool = True
    risk_class: RiskClass = RiskClass.BOUNDED_NON_MUTATING

    def _execute(
        self,
        symbol: str,
        summary: str,
        sentiment: str = "NEUTRAL",
        key_metrics: Optional[Dict[str, Any]] = None,
        citations: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> StockAnalysisResponse:
        return StockAnalysisResponse(
            symbol=symbol,
            summary=summary,
            sentiment=sentiment,
            key_metrics=key_metrics or {},
            citations=citations or [],
        )


class SubmitRecommendationInput(BaseModel):
    """Input parameters for submitting structured investment recommendations."""
    recommendation: str = Field(..., description="Actionable recommendation: BUY, SELL, HOLD, or WATCH")
    time_horizon: str = Field(default="MEDIUM_TERM", description="Target investment horizon: SHORT_TERM, MEDIUM_TERM, LONG_TERM")
    thesis: str = Field(..., description="Core investment rationale and thesis")
    risk_factors: List[str] = Field(default_factory=list, description="Primary risk factors to monitor")
    disclaimer: str = Field(default="Not financial advice. For informational purposes only.", description="Mandatory financial disclosure")


class SubmitRecommendationTool(AgentTool):
    """Control-plane tool for submitting structured recommendations."""
    name: str = "submit_recommendation"
    description: str = "Submit structured investment ideas & recommendations matching schema contract."
    args_schema: Type[BaseModel] = SubmitRecommendationInput
    return_direct: bool = True
    risk_class: RiskClass = RiskClass.BOUNDED_NON_MUTATING

    def _execute(
        self,
        recommendation: str,
        thesis: str,
        time_horizon: str = "MEDIUM_TERM",
        risk_factors: Optional[List[str]] = None,
        disclaimer: str = "Not financial advice. For informational purposes only.",
        **kwargs: Any,
    ) -> RecommendationResponse:
        return RecommendationResponse(
            recommendation=recommendation,
            thesis=thesis,
            time_horizon=time_horizon,
            risk_factors=risk_factors or [],
            disclaimer=disclaimer,
        )


class SubmitGeneralChatInput(BaseModel):
    """Input parameters for submitting structured general chat commentary."""
    message: str = Field(..., description="Natural language response text")
    topics_covered: List[str] = Field(default_factory=list, description="Key discussion topics identified")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up queries for the user")


class SubmitGeneralChatTool(AgentTool):
    """Control-plane tool for submitting structured general chat commentary."""
    name: str = "submit_general_chat"
    description: str = "Submit structured general chat commentary & suggestions matching schema contract."
    args_schema: Type[BaseModel] = SubmitGeneralChatInput
    return_direct: bool = True
    risk_class: RiskClass = RiskClass.BOUNDED_NON_MUTATING

    def _execute(
        self,
        message: str,
        topics_covered: Optional[List[str]] = None,
        follow_up_suggestions: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> GeneralChatResponse:
        return GeneralChatResponse(
            message=message,
            topics_covered=topics_covered or [],
            follow_up_suggestions=follow_up_suggestions or [],
        )
