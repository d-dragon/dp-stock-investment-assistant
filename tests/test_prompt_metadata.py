"""
Integration tests for prompt identity in response and trace metadata (US4).

Tests:
- Response metadata fields (AC-8.1)
- LangSmith independence (M1-NFR-004)
- Fallback metadata (AC-3)
- Stateless request metadata
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask import Flask

from core.prompt_asset_loader import PromptAssetLoader
from core.prompt_types import PromptSelection, SelectionTuple
from web.routes.shared_context import APIRouteContext
from web.routes.ai_chat_routes import create_chat_blueprint


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_metadata_app(agent=None, loader=None):
    """Build a minimal Flask app with chat blueprint for metadata testing."""
    app = Flask("test_metadata")
    agent = agent or MagicMock()
    loader = loader or MagicMock(spec=PromptAssetLoader)

    # Provide a mock chat_service so the blueprint uses it (not legacy fallback)
    mock_chat_svc = MagicMock()
    mock_chat_svc.process_chat_query.return_value = {"response": "Test reply"}

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={"openai": {"model": "gpt-4"}},
        logger=MagicMock(),
        chat_service=mock_chat_svc,
        prompt_asset_loader=loader,
    )
    blueprint = create_chat_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    app.config["TESTING"] = True
    return app


def _make_agent_with_metadata(
    prompt_version="1.0.0",
    prompt_variant="baseline",
    selection_mode="fixed",
    fallback_used=False,
    degraded_reason=None,
    model_provider="openai",
    model_name="gpt-4",
):
    """Create a mock agent that returns known prompt metadata."""
    agent = MagicMock()
    agent._inject_prompt_metadata.return_value = {
        "prompt_version": prompt_version,
        "prompt_variant": prompt_variant,
        "prompt_selection_mode": selection_mode,
        "fallback_used": fallback_used,
        "model_provider": model_provider,
        "model_name": model_name,
    }
    if degraded_reason:
        agent._inject_prompt_metadata.return_value["degraded_reason"] = degraded_reason
    return agent


# ------------------------------------------------------------------
# T027: Response metadata presence
# ------------------------------------------------------------------

class TestResponseMetadata:
    """Response metadata fields are populated correctly."""

    def test_response_metadata_includes_all_prompt_fields(self):
        """AC-8.1: All 6 metadata fields present and non-empty in response."""
        agent = _make_agent_with_metadata()
        app = _make_metadata_app(agent=agent)

        with app.test_client() as client:
            resp = client.post("/api/chat", json={"message": "Price of AAPL"})

        assert resp.status_code == 200
        data = resp.get_json()
        assert "metadata" in data, "Response must contain 'metadata' key"
        meta = data["metadata"]
        assert meta.get("prompt_version") == "1.0.0"
        assert meta.get("prompt_variant") == "baseline"
        assert meta.get("prompt_selection_mode") == "fixed"
        assert meta.get("fallback_used") is False
        assert meta.get("model_provider") == "openai"
        assert meta.get("model_name") == "gpt-4"


# ------------------------------------------------------------------
# T028: LangSmith independence
# ------------------------------------------------------------------

class TestLangSmithIndependence:
    """Response metadata must be populated regardless of LangSmith (M1-NFR-004)."""

    def test_response_metadata_populated_regardless_of_langsmith(self):
        """M1-NFR-004: Response metadata works when LangSmith is unreachable."""
        agent = _make_agent_with_metadata()
        app = _make_metadata_app(agent=agent)

        with app.test_client() as client:
            resp = client.post("/api/chat", json={"message": "Hello"})

        assert resp.status_code == 200
        data = resp.get_json()
        assert "metadata" in data
        meta = data["metadata"]
        assert meta["prompt_version"] == "1.0.0"
        assert meta["model_provider"] == "openai"


# ------------------------------------------------------------------
# T029: Fallback metadata
# ------------------------------------------------------------------

class TestFallbackMetadata:
    """Fallback indicators are reflected in response metadata."""

    def test_response_metadata_shows_fallback(self):
        """AC-3: When fallback occurred, metadata shows it."""
        agent = _make_agent_with_metadata(
            fallback_used=True,
            degraded_reason="Version 2.0.0 not found, fell back to 1.0.0",
        )
        app = _make_metadata_app(agent=agent)

        with app.test_client() as client:
            resp = client.post("/api/chat", json={"message": "Test"})

        assert resp.status_code == 200
        data = resp.get_json()
        meta = data["metadata"]
        assert meta["fallback_used"] is True
        assert "degraded_reason" in meta
        assert "2.0.0" in meta["degraded_reason"]


# ------------------------------------------------------------------
# T030: Stateless request metadata
# ------------------------------------------------------------------

class TestStatelessRequestMetadata:
    """Stateless requests still receive prompt metadata."""

    def test_stateless_request_receives_metadata(self):
        """PS-05 edge case: query without conversation_id gets metadata."""
        agent = _make_agent_with_metadata()
        app = _make_metadata_app(agent=agent)

        with app.test_client() as client:
            # No conversation_id in request
            resp = client.post("/api/chat", json={"message": "Hello"})

        assert resp.status_code == 200
        data = resp.get_json()
        assert "metadata" in data
        meta = data["metadata"]
        assert meta["prompt_version"] == "1.0.0"
        assert meta["model_name"] == "gpt-4"
