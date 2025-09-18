import json
import os
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from web.routes.api_routes import APIRouteContext
from web.routes.models_routes import create_models_blueprint


@pytest.fixture(autouse=True)
def set_env_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    yield
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture
def context():
    app = Flask(__name__)
    agent = MagicMock()
    config = {
        "model": {"provider": "openai", "name": "gpt-4"},
        "cache": {"ttl_seconds": 60},
        "openai": {},
    }
    logger = MagicMock()
    # Provide minimal functions to satisfy APIRouteContext, not used here
    return APIRouteContext(
        app=app,
        agent=agent,
        config=config,
        logger=logger,
        stream_chat_response=lambda *_: [],
        extract_meta=lambda s: ("openai", "gpt-4", False),
        strip_fallback_prefix=lambda s: s,
        get_timestamp=lambda: "2025-09-18T00:00:00Z",
    )


@pytest.fixture
def client(context):
    app = context.app
    app.register_blueprint(create_models_blueprint(context), url_prefix="/api")
    return app.test_client()


def mock_openai_models():
    return {
        "data": [
            {"id": "gpt-4o-mini", "created": 1714000000, "owned_by": "openai", "object": "model"},
            {"id": "gpt-4o", "created": 1713000000, "owned_by": "openai", "object": "model"},
        ]
    }


@patch("web.routes.models_routes.requests.get")
def test_list_models_refresh_and_cached(mock_get, client):
    # First: refresh=true fetches from OpenAI
    mock_get.return_value = MagicMock(status_code=200, json=mock_openai_models)
    mock_get.return_value.raise_for_status = lambda: None

    r1 = client.get("/api/models/openai?refresh=true")
    assert r1.status_code == 200
    j1 = json.loads(r1.data)
    assert j1["cached"] is False
    assert j1["source"] == "openai"
    assert any(m["id"] == "gpt-4o-mini" for m in j1["models"])

    # Second: cached read
    r2 = client.get("/api/models/openai")
    assert r2.status_code == 200
    j2 = json.loads(r2.data)
    assert j2["cached"] is True
    assert j2["source"] == "cache"
    assert any(m["id"] == "gpt-4o-mini" for m in j2["models"])


@patch("web.routes.models_routes.requests.get")
def test_refresh_endpoint(mock_get, client):
    mock_get.return_value = MagicMock(status_code=200, json=mock_openai_models)
    mock_get.return_value.raise_for_status = lambda: None

    r = client.post("/api/models/openai/refresh")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["cached"] is False
    assert data["source"] == "openai"
    assert len(data["models"]) >= 1


def test_get_selected_model(client, context):
    r = client.get("/api/models/openai/selected")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["provider"] == "openai"
    assert data["name"] == "gpt-4"


def test_select_model_missing_name(client):
    r = client.post("/api/models/openai/select", json={})
    assert r.status_code == 400
    assert json.loads(r.data)["error"]


def test_select_model_success_updates_agent(client, context):
    # Provide set_active_model on agent and verify it's called
    context.agent.set_active_model = MagicMock()
    r = client.post("/api/models/openai/select", json={"name": "gpt-4o-mini"})
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data == {"provider": "openai", "name": "gpt-4o-mini"}
    context.agent.set_active_model.assert_called_once_with(provider="openai", name="gpt-4o-mini")


@patch("web.routes.models_routes.requests.get")
def test_models_missing_api_key_returns_500(mock_get, client, monkeypatch):
    # Remove API key to simulate configuration error
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    r = client.get("/api/models/openai?refresh=true")
    assert r.status_code == 500
    data = json.loads(r.data)
    assert "Missing OpenAI API key" in data["error"]