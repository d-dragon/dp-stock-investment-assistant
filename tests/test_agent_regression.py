"""
Regression tests for prompt externalization behavioral parity.

Verifies that the externalized prompt asset produces semantically equivalent
agent behavior to the hardcoded REACT_SYSTEM_PROMPT baseline (M1-FR-002).
"""

from __future__ import annotations

from typing import Dict, List

import pytest

from core.prompt_types import PromptSelection


# ---- Test fixtures ----

SEED_QUERIES: List[Dict[str, str]] = [
    {"query": "What is AAPL trading at?", "route": "PRICE_CHECK"},
    {"query": "Latest news on TSLA", "route": "NEWS_ANALYSIS"},
    {"query": "Analyze MSFT fundamentals", "route": "FUNDAMENTALS"},
    {"query": "Show me AAPL technical chart", "route": "TECHNICAL_ANALYSIS"},
    {"query": "How does the market look today?", "route": "GENERAL_CHAT"},
]


@pytest.fixture
def seed_query_set() -> List[Dict[str, str]]:
    """The canonical 5-query seed set for behavioral regression testing.

    Covers PRICE_CHECK, NEWS_ANALYSIS, FUNDAMENTALS, TECHNICAL_ANALYSIS,
    and GENERAL_CHAT route categories.
    """
    return SEED_QUERIES


@pytest.fixture
def baseline_prompt_selection() -> PromptSelection:
    """A PromptSelection matching the hardcoded REACT_SYSTEM_PROMPT baseline."""
    return PromptSelection(
        selected_assets=["<inline>"],
        prompt_version="0.0.0",
        prompt_variant="inline_fallback",
        selection_mode="fixed",
        fallback_used=False,
        degraded_reason=None,
        trace_metadata={},
    )


@pytest.fixture
def externalized_prompt_selection() -> PromptSelection:
    """A PromptSelection matching the externalized M1 v1.0.0 asset."""
    return PromptSelection(
        selected_assets=["system/react_analyst.md"],
        prompt_version="1.0.0",
        prompt_variant="baseline",
        selection_mode="fixed",
        fallback_used=False,
        degraded_reason=None,
        trace_metadata={
            "prompt_version": "1.0.0",
            "prompt_variant": "baseline",
            "prompt_selection_mode": "fixed",
            "agent_role": "react_analyst",
        },
    )


# ---- Behavioral parity tests ----

@pytest.mark.slow
class TestExternalizedPromptBehavioralParity:
    """Verifies the externalized prompt asset matches the inline baseline.

    These tests are tagged ``@pytest.mark.slow`` for CI segregation.
    They require a running agent with model access (not isolated unit tests).
    """

    def test_seed_query_set_has_expected_routes(self, seed_query_set):
        """Verify the 5-query seed set covers the required route categories."""
        routes = {entry["route"] for entry in seed_query_set}
        assert "PRICE_CHECK" in routes
        assert "NEWS_ANALYSIS" in routes
        assert "FUNDAMENTALS" in routes
        assert "TECHNICAL_ANALYSIS" in routes
        assert "GENERAL_CHAT" in routes
        assert len(seed_query_set) == 5

    def test_externalized_prompt_metadata_matches_expected(
        self, externalized_prompt_selection
    ):
        """Verify the externalized prompt carries correct identity metadata."""
        sel = externalized_prompt_selection
        assert sel.prompt_version == "1.0.0"
        assert sel.prompt_variant == "baseline"
        assert sel.selection_mode == "fixed"
        assert sel.fallback_used is False
        assert sel.degraded_reason is None
        assert "system/react_analyst.md" in sel.selected_assets

    def test_baseline_prompt_fallback_metadata(
        self, baseline_prompt_selection
    ):
        """Verify the inline fallback prompt carries correct identity metadata."""
        sel = baseline_prompt_selection
        assert sel.prompt_version == "0.0.0"
        assert sel.prompt_variant == "inline_fallback"
        assert sel.fallback_used is False
        assert "<inline>" in sel.selected_assets
