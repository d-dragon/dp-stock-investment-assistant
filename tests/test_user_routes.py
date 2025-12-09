"""Unit tests for user-focused HTTP API blueprint."""

from __future__ import annotations

import logging
from typing import Iterable, Tuple

from flask import Flask

from web.routes.shared_context import APIRouteContext
from web.routes.user_routes import create_user_blueprint


class DummyAgent:
    """Minimal agent stub required by APIRouteContext."""

    def process_query_streaming(self, *_args, **_kwargs) -> Iterable[str]:  # pragma: no cover - unused
        return iter(())


class DummyUserService:
    """Simple in-memory user service stub for route tests."""

    def __init__(self) -> None:
        self.create_calls = []
        self.update_calls = []
        self.profile_calls = []
        self.email_calls = []
        self.user_profiles = {}
        self.users_by_email = {}

    def create_or_update_user(self, payload):
        self.create_calls.append(payload)
        if payload.get("invalid"):
            raise ValueError("invalid user payload")
        result = dict(payload)
        result.setdefault("_id", "user-123")
        return result

    def update_user_profile(self, user_id, payload):
        self.update_calls.append((user_id, payload))
        if payload.get("invalid"):
            raise ValueError("invalid profile")
        if payload.get("missing") or user_id == "missing":
            return None
        updated = {"_id": user_id}
        updated.update(payload)
        return updated

    def get_user_profile(self, user_id):
        self.profile_calls.append(user_id)
        return self.user_profiles.get(user_id)

    def get_user_by_email(self, email):
        self.email_calls.append(email)
        return self.users_by_email.get(email)


class ExplodingFactory:
    """Service factory stub that simulates wiring failures."""

    def get_user_service(self):
        raise RuntimeError("boom")


def _make_app(*, user_service=None, service_factory=None) -> Tuple[Flask, DummyUserService]:
    app = Flask("test_user_routes")
    provided_service = user_service or DummyUserService()

    def _stream_sentinel(message, provider_override):  # pragma: no cover - blueprint compatibility
        return iter(())

    context = APIRouteContext(
        app=app,
        agent=DummyAgent(),
        config={},
        logger=logging.getLogger("test-user-routes"),
        stream_chat_response=_stream_sentinel,
        extract_meta=lambda raw: ("provider", "model", False),
        strip_fallback_prefix=lambda raw: raw,
        get_timestamp=lambda: "2024-01-01T00:00:00Z",
        model_registry=None,
        set_active_model=None,
        service_factory=service_factory,
        user_service=provided_service if service_factory is None else user_service,
    )
    blueprint = create_user_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    return app, provided_service


def test_create_user_returns_201_and_location_header():
    app, service = _make_app()
    client = app.test_client()

    response = client.post("/api/users", json={"email": "user@example.com"})

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["user"]["email"] == "user@example.com"
    assert response.headers["Location"] == "/api/users/user-123"
    assert service.create_calls == [{"email": "user@example.com"}]


def test_create_user_rejects_non_object_payload():
    app, service = _make_app()
    client = app.test_client()

    response = client.post("/api/users", json=["invalid"])

    assert response.status_code == 400
    assert service.create_calls == []


def test_update_user_profile_returns_404_when_missing():
    app, service = _make_app()
    client = app.test_client()

    response = client.patch("/api/users/missing/profile", json={"missing": True})

    assert response.status_code == 404
    assert service.update_calls == [("missing", {"missing": True})]


def test_update_user_profile_returns_400_on_validation_error():
    app, service = _make_app()
    client = app.test_client()

    response = client.patch("/api/users/abc/profile", json={"invalid": True})

    assert response.status_code == 400
    assert service.update_calls == [("abc", {"invalid": True})]


def test_routes_return_503_when_service_factory_fails():
    factory = ExplodingFactory()
    app, _ = _make_app(user_service=None, service_factory=factory)
    client = app.test_client()

    response = client.post("/api/users", json={"email": "user@example.com"})

    assert response.status_code == 503


def test_get_user_by_id_returns_payload():
    app, service = _make_app()
    client = app.test_client()
    service.user_profiles["abc"] = {"_id": "abc", "email": "abc@example.com"}

    response = client.get("/api/users", query_string={"id": "abc"})

    assert response.status_code == 200
    assert response.get_json()["user"]["_id"] == "abc"
    assert service.profile_calls == ["abc"]


def test_get_user_by_email_returns_payload():
    app, service = _make_app()
    client = app.test_client()
    service.users_by_email["alex@example.com"] = {
        "_id": "user-999",
        "email": "alex@example.com",
    }

    response = client.get("/api/users", query_string={"email": "alex@example.com"})

    assert response.status_code == 200
    assert response.get_json()["user"]["_id"] == "user-999"
    assert service.email_calls == ["alex@example.com"]


def test_get_user_requires_exactly_one_filter():
    app, _ = _make_app()
    client = app.test_client()

    response_missing = client.get("/api/users")
    response_both = client.get("/api/users", query_string={"id": "a", "email": "b@example.com"})

    assert response_missing.status_code == 400
    assert response_both.status_code == 400


def test_get_user_returns_404_when_not_found():
    app, service = _make_app()
    client = app.test_client()

    response = client.get("/api/users", query_string={"id": "unknown"})

    assert response.status_code == 404
    assert service.profile_calls == ["unknown"]


def test_get_user_returns_503_when_service_factory_fails():
    factory = ExplodingFactory()
    app, _ = _make_app(user_service=None, service_factory=factory)
    client = app.test_client()

    response = client.get("/api/users", query_string={"id": "abc"})

    assert response.status_code == 503
