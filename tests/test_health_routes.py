"""Unit tests for service health check routes."""

import logging
from flask import Flask

from web.routes.shared_context import APIRouteContext
from web.routes.service_health_routes import create_health_blueprint


def _make_test_app():
    """Create minimal Flask app with health blueprint for testing."""
    app = Flask("test_health_routes")
    
    context = APIRouteContext(
        app=app,
        agent=None,  # Health check doesn't need agent
        config={},
        logger=logging.getLogger("test-health-routes"),
        stream_chat_response=lambda m, p: iter([]),
        extract_meta=lambda r: ("provider", "model", False),
        strip_fallback_prefix=lambda r: r,
        get_timestamp=lambda: "2024-01-01T00:00:00Z",
    )
    
    blueprint = create_health_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    
    return app


def test_health_check_returns_200_status():
    """Test health endpoint returns 200 OK."""
    app = _make_test_app()
    client = app.test_client()
    
    response = client.get("/api/health")
    
    assert response.status_code == 200


def test_health_check_returns_healthy_status():
    """Test health endpoint returns healthy status in JSON."""
    app = _make_test_app()
    client = app.test_client()
    
    response = client.get("/api/health")
    payload = response.get_json()
    
    assert payload["status"] == "healthy"


def test_health_check_includes_message():
    """Test health endpoint includes descriptive message."""
    app = _make_test_app()
    client = app.test_client()
    
    response = client.get("/api/health")
    payload = response.get_json()
    
    assert "message" in payload
    assert len(payload["message"]) > 0


def test_health_check_content_type_is_json():
    """Test health endpoint returns JSON content type."""
    app = _make_test_app()
    client = app.test_client()
    
    response = client.get("/api/health")
    
    assert response.content_type == "application/json"
