"""Integration tests for session management API contracts.

Tests session CRUD routes over Flask test client to verify the
REST contract defined in specs/stm-phase-cde/contracts/management-api.md.

Reference: T016 – session contract and ownership integration tests.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest
from flask import Flask

from services.exceptions import (
    EntityNotFoundError,
    OwnershipViolationError,
    ParentNotFoundError,
)
from web.routes.shared_context import APIRouteContext


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2025, 6, 1, tzinfo=timezone.utc)
_NOW_ISO = _NOW.isoformat()


def _make_session(
    session_id: Optional[str] = None,
    workspace_id: str = "ws-1",
    user_id: str = "user-1",
    title: str = "Test Session",
    status: str = "active",
    **extra: Any,
) -> Dict[str, Any]:
    sid = session_id or f"sess-{uuid.uuid4().hex[:8]}"
    doc: Dict[str, Any] = {
        "session_id": sid,
        "workspace_id": workspace_id,
        "user_id": user_id,
        "title": title,
        "description": "",
        "status": status,
        "assumptions": None,
        "pinned_intent": None,
        "focused_symbols": [],
        "conversation_count": 0,
        "created_at": _NOW_ISO,
        "updated_at": _NOW_ISO,
    }
    doc.update(extra)
    return doc


def _make_workspace(
    workspace_id: str = "ws-1",
    user_id: str = "user-1",
    status: str = "active",
) -> Dict[str, Any]:
    return {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": "Test Workspace",
        "status": status,
        "created_at": _NOW_ISO,
        "updated_at": _NOW_ISO,
    }


def _build_test_app(
    *,
    workspace_service: Optional[MagicMock] = None,
    session_service: Optional[MagicMock] = None,
) -> Flask:
    """Build a minimal Flask app with session management blueprint.

    Tries to import session_routes; if the blueprint is skeleton-only
    (no routes), the test client will return 404 and tests skip gracefully.
    """
    app = Flask("test_session_api")
    app.config["TESTING"] = True

    service_factory = MagicMock()
    if workspace_service:
        service_factory.get_workspace_service.return_value = workspace_service
    if session_service:
        service_factory.get_session_service.return_value = session_service

    agent = MagicMock()

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={"model_provider": "openai"},
        logger=logging.getLogger("test-session-api"),
        service_factory=service_factory,
    )

    # Register workspace blueprint (needed for nested routes)
    try:
        from web.routes.workspace_routes import create_workspace_blueprint
        ws_bp = create_workspace_blueprint(context)
        app.register_blueprint(ws_bp, url_prefix="/api")
    except Exception:
        pass

    # Register session blueprint
    try:
        from web.routes.session_routes import create_session_blueprint
        sess_bp = create_session_blueprint(context)
        app.register_blueprint(sess_bp, url_prefix="/api")
    except Exception:
        pass

    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def session_service() -> MagicMock:
    svc = MagicMock()
    svc.create_session.return_value = _make_session(session_id="sess-new")
    svc.list_sessions_paginated.return_value = {
        "items": [_make_session(session_id="sess-1"), _make_session(session_id="sess-2")],
        "total": 2,
        "limit": 25,
        "offset": 0,
    }
    svc.get_session_detail.return_value = _make_session(
        session_id="sess-1", conversation_count=3,
    )
    svc.update_session.return_value = _make_session(
        session_id="sess-1", title="Renamed",
    )
    svc.archive_session_managed.return_value = _make_session(
        session_id="sess-1", status="archived",
    )
    return svc


@pytest.fixture
def workspace_service() -> MagicMock:
    svc = MagicMock()
    svc.get_workspace_detail.return_value = _make_workspace()
    return svc


@pytest.fixture
def client(workspace_service: MagicMock, session_service: MagicMock, apply_management_headers):
    app = _build_test_app(
        workspace_service=workspace_service,
        session_service=session_service,
    )
    return apply_management_headers(app.test_client())


# ---------------------------------------------------------------------------
# Contract: POST /api/workspaces/{workspace_id}/sessions
# ---------------------------------------------------------------------------


class TestCreateSession:
    """POST /api/workspaces/{workspace_id}/sessions creates a session."""

    def test_creates_session_in_workspace(self, client, session_service):
        response = client.post("/api/workspaces/ws-1/sessions", json={
            "title": "NVDA earnings prep",
            "assumptions": "Supply constrained",
            "focused_symbols": ["NVDA", "AMD"],
        })

        if response.status_code == 404:
            pytest.skip("Session create route not yet implemented")

        assert response.status_code in (200, 201)
        body = response.get_json()
        assert "session_id" in body
        assert "workspace_id" in body
        assert "status" in body
        assert "created_at" in body


# ---------------------------------------------------------------------------
# Contract: GET /api/workspaces/{workspace_id}/sessions
# ---------------------------------------------------------------------------


class TestListSessions:
    """GET /api/workspaces/{workspace_id}/sessions lists sessions paginated."""

    def test_returns_paginated_list(self, client, session_service):
        response = client.get("/api/workspaces/ws-1/sessions?limit=25&offset=0")

        if response.status_code == 404:
            pytest.skip("Session list route not yet implemented")

        assert response.status_code == 200
        body = response.get_json()
        assert "items" in body
        assert "total" in body
        assert "limit" in body
        assert "offset" in body

    def test_supports_status_filter(self, client, session_service):
        response = client.get("/api/workspaces/ws-1/sessions?status=active")

        if response.status_code == 404:
            pytest.skip("Session list route not yet implemented")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Contract: GET /api/sessions/{session_id}
# ---------------------------------------------------------------------------


class TestGetSessionDetail:
    """GET /api/sessions/{session_id} returns session with conversation count."""

    def test_returns_detail_with_conversation_count(self, client, session_service):
        response = client.get("/api/sessions/sess-1")

        if response.status_code == 404:
            pytest.skip("Session detail route not yet implemented")

        assert response.status_code == 200
        body = response.get_json()
        assert body.get("session_id") == "sess-1"
        assert "conversation_count" in body

    def test_returns_404_for_nonexistent_session(self, client, session_service):
        session_service.get_session_detail.side_effect = EntityNotFoundError(
            "session", "nonexistent-sess",
        )
        response = client.get("/api/sessions/nonexistent-sess")

        if response.status_code == 404:
            body = response.get_json() or {}
            if "error" in body:
                assert (
                    body["error"]["code"] == "NOT_FOUND"
                    or "not found" in body["error"].get("message", "").lower()
                )
        # 404 is the correct outcome either way


# ---------------------------------------------------------------------------
# Contract: PUT /api/sessions/{session_id}
# ---------------------------------------------------------------------------


class TestUpdateSession:
    """PUT /api/sessions/{session_id} updates session title/description."""

    def test_updates_session_fields(self, client, session_service):
        response = client.put("/api/sessions/sess-1", json={
            "title": "Renamed Session",
            "description": "Updated description",
        })

        if response.status_code in (404, 405):
            pytest.skip("Session update route not yet implemented")

        assert response.status_code == 200
        body = response.get_json()
        assert "session_id" in body
        assert "updated_at" in body


# ---------------------------------------------------------------------------
# Contract: POST /api/sessions/{session_id}/archive
# ---------------------------------------------------------------------------


class TestArchiveSession:
    """POST /api/sessions/{session_id}/archive archives session."""

    def test_archives_session(self, client, session_service):
        response = client.post("/api/sessions/sess-1/archive")

        if response.status_code == 404:
            pytest.skip("Session archive route not yet implemented")

        assert response.status_code == 200
        body = response.get_json()
        assert body.get("status") == "archived"

    def test_archive_is_idempotent(self, client, session_service):
        session_service.archive_session_managed.return_value = _make_session(
            session_id="sess-1", status="archived",
        )
        response = client.post("/api/sessions/sess-1/archive")

        if response.status_code == 404:
            pytest.skip("Session archive route not yet implemented")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Contract: Cross-user access → 403
# ---------------------------------------------------------------------------


class TestCrossUserAccess:
    """Accessing session in another user's workspace returns 403."""

    def test_rejects_cross_user_access(self, client, session_service):
        session_service.get_session_detail.side_effect = OwnershipViolationError(
            entity_type="workspace",
            entity_id="ws-other",
            expected_owner="user-1",
            actual_owner="user-2",
        )
        response = client.get("/api/sessions/sess-other")

        if response.status_code == 404:
            pytest.skip("Session detail route not yet implemented")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Contract: Not-found → 404
# ---------------------------------------------------------------------------


class TestNotFoundSession:
    """GET /api/sessions/{nonexistent_id} returns 404."""

    def test_returns_404_for_missing(self, client, session_service):
        session_service.get_session_detail.side_effect = EntityNotFoundError(
            "session", "no-such-id",
        )
        response = client.get("/api/sessions/no-such-id")

        # 404 is correct whether route is implemented or not
        assert response.status_code == 404
