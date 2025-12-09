import json
import os
from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from web.routes.shared_context import APIRouteContext
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
        model_registry=None,  # Will be mocked in individual tests as needed
        set_active_model=None,  # Will be mocked in individual tests as needed
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
    data = json.loads(r.data)
    assert data["error"] == "Field 'name' is required"


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


def test_set_default_model_missing_registry(context):
    """Test PUT /models/openai/default without model_registry in context."""
    # Remove model_registry from context and create new app
    context = replace(context, model_registry=None, app=Flask(__name__))
    app = context.app
    app.register_blueprint(create_models_blueprint(context), url_prefix="/api")
    client = app.test_client()
    
    r = client.put("/api/models/openai/default", json={"model": "gpt-4o"})
    assert r.status_code == 503
    data = json.loads(r.data)
    assert data["error"] == "OpenAI model management unavailable"


def test_set_default_model_missing_model_name(context):
    """Test PUT /models/openai/default with missing model parameter."""
    # Add model_registry and set_active_model to context with new app
    mock_registry = MagicMock()
    mock_set_active = MagicMock()
    context = replace(context, model_registry=mock_registry, set_active_model=mock_set_active, app=Flask(__name__))
    
    app = context.app
    app.register_blueprint(create_models_blueprint(context), url_prefix="/api")
    client = app.test_client()
    
    r = client.put("/api/models/openai/default", json={})
    assert r.status_code == 400
    data = json.loads(r.data)
    assert data["error"] == "model is required"


def test_set_default_model_success(context):
    """Test PUT /models/openai/default with successful model setting."""
    # Mock the registry and set_active_model with new app
    mock_registry = MagicMock()
    mock_registry.is_supported_model.return_value = True
    mock_registry.get_active_model.return_value = "gpt-4o"
    mock_set_active = MagicMock(return_value={"model": "gpt-4o", "provider": "openai"})
    
    context = replace(context, model_registry=mock_registry, set_active_model=mock_set_active, app=Flask(__name__))
    app = context.app
    app.register_blueprint(create_models_blueprint(context), url_prefix="/api")
    client = app.test_client()
    
    r = client.put("/api/models/openai/default", json={"model": "gpt-4o"})
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["model"] == "gpt-4o"
    assert data["active_model"] == "gpt-4o"
    
    # Verify calls
    mock_registry.is_supported_model.assert_called_once_with("gpt-4o")
    mock_set_active.assert_called_once_with("openai", "gpt-4o")
    mock_registry.record_active_model.assert_called_once_with("gpt-4o")