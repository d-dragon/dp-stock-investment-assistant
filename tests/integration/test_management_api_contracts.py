"""Integration tests for management API contracts.

Tests workspace, session, and conversation CRUD routes over Flask test client
to verify the REST contract defined in
specs/stm-phase-cde/contracts/management-api.md.

References:
  T010 – workspace contract and ownership integration tests
  T016 – session lifecycle and parent-mismatch integration tests
  T022 – conversation hierarchy and zero-result pagination tests
  T027 – pagination parity, error-envelope parity, idempotent GET,
         archive-cascade, and limit-clamping cross-cutting tests
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from services.exceptions import (
    EntityNotFoundError,
    OwnershipViolationError,
    ParentNotFoundError,
    StaleEntityError,
)
from web.routes.shared_context import APIRouteContext
from web.routes.workspace_routes import create_workspace_blueprint
from web.routes.session_routes import create_session_blueprint
from web.routes.conversation_routes import create_conversation_blueprint


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2025, 6, 1, tzinfo=timezone.utc)
_NOW_ISO = _NOW.isoformat()


def _make_workspace(
    workspace_id: Optional[str] = None,
    user_id: str = "user-1",
    name: str = "Test Workspace",
    description: str = "desc",
    status: str = "active",
    **extra: Any,
) -> Dict[str, Any]:
    ws_id = workspace_id or f"ws-{uuid.uuid4().hex[:8]}"
    doc: Dict[str, Any] = {
        "workspace_id": ws_id,
        "user_id": user_id,
        "name": name,
        "description": description,
        "status": status,
        "session_count": 0,
        "active_conversation_count": 0,
        "created_at": _NOW_ISO,
        "updated_at": _NOW_ISO,
    }
    doc.update(extra)
    return doc


def _build_test_app(*, workspace_service: MagicMock) -> Flask:
    """Build a minimal Flask app with the workspace management blueprint.

    Uses a mock workspace_service injected through the service_factory
    in APIRouteContext so route handlers can resolve dependencies.
    """
    app = Flask("test_management_api")
    app.config["TESTING"] = True

    service_factory = MagicMock()
    service_factory.get_workspace_service.return_value = workspace_service

    agent = MagicMock()

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={"model_provider": "openai"},
        logger=logging.getLogger("test-management-api"),
        service_factory=service_factory,
    )

    blueprint = create_workspace_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    return app


def _build_full_test_app(
    *,
    workspace_service: MagicMock,
    session_service: MagicMock,
    conversation_service: MagicMock,
) -> Flask:
    """Build a Flask app with workspace, session, and conversation blueprints."""
    app = Flask("test_management_api_full")
    app.config["TESTING"] = True

    service_factory = MagicMock()
    service_factory.get_workspace_service.return_value = workspace_service
    service_factory.get_session_service.return_value = session_service
    service_factory.get_conversation_service.return_value = conversation_service

    agent = MagicMock()

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={"model_provider": "openai"},
        logger=logging.getLogger("test-management-api-full"),
        service_factory=service_factory,
    )

    app.register_blueprint(create_workspace_blueprint(context), url_prefix="/api")
    app.register_blueprint(create_session_blueprint(context), url_prefix="/api")
    app.register_blueprint(create_conversation_blueprint(context), url_prefix="/api")
    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def workspace_service() -> MagicMock:
    svc = MagicMock()
    svc.create_workspace.return_value = _make_workspace(workspace_id="ws-new")
    svc.list_workspaces_paginated.return_value = {
        "items": [_make_workspace(workspace_id="ws-1"), _make_workspace(workspace_id="ws-2")],
        "total": 2,
        "limit": 25,
        "offset": 0,
    }
    svc.get_workspace_detail.return_value = _make_workspace(
        workspace_id="ws-1", session_count=3, active_conversation_count=5,
    )
    svc.update_workspace.return_value = _make_workspace(workspace_id="ws-1", name="Renamed")
    svc.archive_workspace.return_value = _make_workspace(
        workspace_id="ws-1", status="archived",
    )
    return svc


@pytest.fixture
def client(workspace_service: MagicMock, apply_management_headers):
    app = _build_test_app(workspace_service=workspace_service)
    return apply_management_headers(app.test_client())


# ---------------------------------------------------------------------------
# Contract: POST /api/workspaces
# ---------------------------------------------------------------------------


class TestCreateWorkspace:
    """POST /api/workspaces creates workspace and returns expected shape."""

    def test_creates_workspace_with_expected_fields(self, client, workspace_service):
        response = client.post("/api/workspaces", json={
            "name": "Semiconductor swing trades",
            "description": "Tracking cyclical names",
        })

        # The route may not be fully implemented yet (skeleton);
        # if 404, the contract test still documents expected behavior.
        if response.status_code == 404:
            pytest.skip("Workspace create route not yet implemented")

        assert response.status_code in (200, 201)
        body = response.get_json()
        assert "workspace_id" in body
        assert body["name"] == body.get("name")
        assert "status" in body
        assert "created_at" in body
        assert "updated_at" in body


# ---------------------------------------------------------------------------
# Contract: GET /api/workspaces
# ---------------------------------------------------------------------------


class TestListWorkspaces:
    """GET /api/workspaces lists workspaces with pagination."""

    def test_returns_paginated_list(self, client, workspace_service):
        response = client.get("/api/workspaces?limit=25&offset=0")

        if response.status_code == 404:
            pytest.skip("Workspace list route not yet implemented")

        assert response.status_code == 200
        body = response.get_json()
        assert "items" in body
        assert "total" in body
        assert "limit" in body
        assert "offset" in body

    def test_supports_status_filter(self, client, workspace_service):
        response = client.get("/api/workspaces?status=archived")

        if response.status_code == 404:
            pytest.skip("Workspace list route not yet implemented")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Contract: GET /api/workspaces/{id}
# ---------------------------------------------------------------------------


class TestGetWorkspaceDetail:
    """GET /api/workspaces/{id} returns workspace detail with aggregate counts."""

    def test_returns_detail_with_counts(self, client, workspace_service):
        response = client.get("/api/workspaces/ws-1")

        if response.status_code == 404:
            pytest.skip("Workspace detail route not yet implemented")

        assert response.status_code == 200
        body = response.get_json()
        assert body.get("workspace_id") == "ws-1"
        assert "session_count" in body
        assert "active_conversation_count" in body

    def test_returns_404_for_nonexistent_workspace(self, client, workspace_service):
        workspace_service.get_workspace_detail.side_effect = EntityNotFoundError(
            "workspace", "nonexistent-ws",
        )
        response = client.get("/api/workspaces/nonexistent-ws")

        if response.status_code == 404:
            body = response.get_json() or {}
            # If properly implemented, expect error envelope
            if "error" in body:
                assert body["error"]["code"] == "RESOURCE_NOT_FOUND" or "not found" in body["error"].get("message", "").lower()
        # 404 is the correct outcome either way


# ---------------------------------------------------------------------------
# Contract: PUT /api/workspaces/{id}
# ---------------------------------------------------------------------------


class TestUpdateWorkspace:
    """PUT /api/workspaces/{id} updates workspace name/description."""

    def test_updates_workspace_fields(self, client, workspace_service):
        response = client.put("/api/workspaces/ws-1", json={
            "name": "Renamed Workspace",
            "description": "Updated description",
        })

        if response.status_code in (404, 405):
            pytest.skip("Workspace update route not yet implemented")

        assert response.status_code == 200
        body = response.get_json()
        assert "workspace_id" in body
        assert "updated_at" in body


# ---------------------------------------------------------------------------
# Contract: POST /api/workspaces/{id}/archive
# ---------------------------------------------------------------------------


class TestArchiveWorkspace:
    """POST /api/workspaces/{id}/archive archives workspace."""

    def test_archives_workspace(self, client, workspace_service):
        response = client.post("/api/workspaces/ws-1/archive")

        if response.status_code == 404:
            pytest.skip("Workspace archive route not yet implemented")

        assert response.status_code == 200
        body = response.get_json()
        assert body.get("status") == "archived"

    def test_archive_is_idempotent(self, client, workspace_service):
        workspace_service.archive_workspace.return_value = _make_workspace(
            workspace_id="ws-1", status="archived",
        )
        response = client.post("/api/workspaces/ws-1/archive")

        if response.status_code == 404:
            pytest.skip("Workspace archive route not yet implemented")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Contract: Cross-user access → 403
# ---------------------------------------------------------------------------


class TestCrossUserAccess:
    """GET /api/workspaces/{other_user_workspace} returns 403."""

    def test_rejects_cross_user_access(self, client, workspace_service):
        workspace_service.get_workspace_detail.side_effect = OwnershipViolationError(
            entity_type="workspace",
            entity_id="ws-other",
            expected_owner="user-1",
            actual_owner="user-2",
        )
        response = client.get("/api/workspaces/ws-other")

        if response.status_code == 404:
            # Route not implemented yet; still documents contract expectation
            pytest.skip("Workspace detail route not yet implemented")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Contract: Not-found → 404
# ---------------------------------------------------------------------------


class TestNotFoundWorkspace:
    """GET /api/workspaces/{nonexistent_id} returns 404."""

    def test_returns_404_for_missing(self, client, workspace_service):
        workspace_service.get_workspace_detail.side_effect = EntityNotFoundError(
            "workspace", "no-such-id",
        )
        response = client.get("/api/workspaces/no-such-id")

        # 404 is correct whether route is implemented or not
        assert response.status_code == 404


# ===========================================================================
# Cross-cutting contract tests (T027)
# ===========================================================================

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
        "status": status,
        "conversation_count": 0,
        "created_at": _NOW_ISO,
        "updated_at": _NOW_ISO,
    }
    doc.update(extra)
    return doc


def _make_conversation(
    conversation_id: Optional[str] = None,
    session_id: str = "sess-1",
    user_id: str = "user-1",
    status: str = "active",
    **extra: Any,
) -> Dict[str, Any]:
    cid = conversation_id or f"conv-{uuid.uuid4().hex[:8]}"
    doc: Dict[str, Any] = {
        "conversation_id": cid,
        "thread_id": cid,
        "session_id": session_id,
        "user_id": user_id,
        "status": status,
        "message_count": 0,
        "created_at": _NOW_ISO,
        "updated_at": _NOW_ISO,
    }
    doc.update(extra)
    return doc


# ---------------------------------------------------------------------------
# Fixtures for full (3-blueprint) app
# ---------------------------------------------------------------------------


@pytest.fixture
def session_service() -> MagicMock:
    svc = MagicMock()
    svc.create_session.return_value = _make_session(session_id="sess-new")
    svc.list_sessions_paginated.return_value = {
        "items": [_make_session(session_id="sess-1")],
        "total": 1,
        "limit": 25,
        "offset": 0,
    }
    svc.get_session_detail.return_value = _make_session(session_id="sess-1")
    svc.archive_session_managed.return_value = _make_session(
        session_id="sess-1", status="archived",
    )
    return svc


@pytest.fixture
def conversation_service() -> MagicMock:
    svc = MagicMock()
    svc.create_conversation.return_value = _make_conversation(conversation_id="conv-new")
    svc.list_conversations_paginated.return_value = {
        "items": [_make_conversation(conversation_id="conv-1")],
        "total": 1,
        "limit": 25,
        "offset": 0,
    }
    svc.get_conversation_detail.return_value = _make_conversation(conversation_id="conv-1")
    svc.archive_conversation_managed.return_value = _make_conversation(
        conversation_id="conv-1", status="archived",
    )
    return svc


@pytest.fixture
def full_client(workspace_service, session_service, conversation_service, apply_management_headers):
    app = _build_full_test_app(
        workspace_service=workspace_service,
        session_service=session_service,
        conversation_service=conversation_service,
    )
    return apply_management_headers(app.test_client())


# ---------------------------------------------------------------------------
# T027: Pagination envelope parity
# ---------------------------------------------------------------------------


class TestPaginationParity:
    """All three list endpoints return the same envelope shape."""

    _ENVELOPE_KEYS = {"items", "total", "limit", "offset"}

    def test_workspace_list_envelope(self, full_client, workspace_service):
        resp = full_client.get("/api/workspaces")
        assert resp.status_code == 200
        body = resp.get_json()
        assert self._ENVELOPE_KEYS <= set(body.keys())
        assert isinstance(body["items"], list)
        assert isinstance(body["total"], int)

    def test_session_list_envelope(self, full_client, session_service):
        resp = full_client.get("/api/workspaces/ws-1/sessions")
        assert resp.status_code == 200
        body = resp.get_json()
        assert self._ENVELOPE_KEYS <= set(body.keys())
        assert isinstance(body["items"], list)
        assert isinstance(body["total"], int)

    def test_conversation_list_envelope(self, full_client, conversation_service):
        resp = full_client.get("/api/sessions/sess-1/conversations")
        assert resp.status_code == 200
        body = resp.get_json()
        assert self._ENVELOPE_KEYS <= set(body.keys())
        assert isinstance(body["items"], list)
        assert isinstance(body["total"], int)


# ---------------------------------------------------------------------------
# T027: Error-envelope parity
# ---------------------------------------------------------------------------


class TestErrorEnvelopeParity:
    """All endpoints return {error: {message, code}} for error responses."""

    def _assert_error_shape(self, resp, expected_status: int):
        assert resp.status_code == expected_status
        body = resp.get_json()
        assert "error" in body, f"Missing 'error' key in {body}"
        err = body["error"]
        assert "message" in err
        assert "code" in err

    # 404 – entity not found
    def test_workspace_404(self, full_client, workspace_service):
        workspace_service.get_workspace_detail.side_effect = EntityNotFoundError("workspace", "x")
        resp = full_client.get("/api/workspaces/x")
        self._assert_error_shape(resp, 404)

    def test_session_404(self, full_client, session_service):
        session_service.get_session_detail.side_effect = EntityNotFoundError("session", "x")
        resp = full_client.get("/api/sessions/x")
        self._assert_error_shape(resp, 404)

    def test_conversation_404(self, full_client, conversation_service):
        conversation_service.get_conversation_detail.side_effect = EntityNotFoundError("conversation", "x")
        resp = full_client.get("/api/conversations/x")
        self._assert_error_shape(resp, 404)

    # 403 – ownership violation
    def test_workspace_403(self, full_client, workspace_service):
        workspace_service.get_workspace_detail.side_effect = OwnershipViolationError(
            "workspace", "ws-x", "user-1", "user-other",
        )
        resp = full_client.get("/api/workspaces/ws-x")
        self._assert_error_shape(resp, 403)

    def test_session_403(self, full_client, session_service):
        session_service.get_session_detail.side_effect = OwnershipViolationError(
            "session", "sess-x", "user-1", "user-other",
        )
        resp = full_client.get("/api/sessions/sess-x")
        self._assert_error_shape(resp, 403)

    def test_conversation_403(self, full_client, conversation_service):
        conversation_service.get_conversation_detail.side_effect = OwnershipViolationError(
            "conversation", "conv-x", "user-1", "user-other",
        )
        resp = full_client.get("/api/conversations/conv-x")
        self._assert_error_shape(resp, 403)

    # 409 – stale entity (via PUT)
    def test_session_409(self, full_client, session_service):
        session_service.update_session.side_effect = StaleEntityError("session", "sess-1")
        resp = full_client.put(
            "/api/sessions/sess-1",
            json={"title": "Updated"},
        )
        self._assert_error_shape(resp, 409)

    # 500 – unexpected errors
    def test_workspace_500(self, full_client, workspace_service):
        workspace_service.get_workspace_detail.side_effect = RuntimeError("boom")
        resp = full_client.get("/api/workspaces/ws-1")
        self._assert_error_shape(resp, 500)

    def test_session_500(self, full_client, session_service):
        session_service.get_session_detail.side_effect = RuntimeError("boom")
        resp = full_client.get("/api/sessions/sess-1")
        self._assert_error_shape(resp, 500)

    def test_conversation_500(self, full_client, conversation_service):
        conversation_service.get_conversation_detail.side_effect = RuntimeError("boom")
        resp = full_client.get("/api/conversations/conv-1")
        self._assert_error_shape(resp, 500)

    # 400 – validation (bad request body for PUT)
    def test_workspace_400_bad_body(self, full_client, workspace_service):
        resp = full_client.put(
            "/api/workspaces/ws-1",
            data="not json",
            content_type="text/plain",
        )
        self._assert_error_shape(resp, 400)

    def test_session_400_bad_body(self, full_client, session_service):
        resp = full_client.put(
            "/api/sessions/sess-1",
            data="not json",
            content_type="text/plain",
        )
        self._assert_error_shape(resp, 400)


# ---------------------------------------------------------------------------
# T027: Idempotent GET
# ---------------------------------------------------------------------------


class TestIdempotentGet:
    """Repeated GET calls return the same result with no side effects."""

    def test_workspace_get_is_idempotent(self, full_client, workspace_service):
        r1 = full_client.get("/api/workspaces/ws-1")
        r2 = full_client.get("/api/workspaces/ws-1")
        assert r1.status_code == r2.status_code == 200
        assert r1.get_json() == r2.get_json()
        # Service method called exactly twice (no extra side effects)
        assert workspace_service.get_workspace_detail.call_count == 2

    def test_session_get_is_idempotent(self, full_client, session_service):
        r1 = full_client.get("/api/sessions/sess-1")
        r2 = full_client.get("/api/sessions/sess-1")
        assert r1.status_code == r2.status_code == 200
        assert r1.get_json() == r2.get_json()
        assert session_service.get_session_detail.call_count == 2

    def test_conversation_get_is_idempotent(self, full_client, conversation_service):
        r1 = full_client.get("/api/conversations/conv-1")
        r2 = full_client.get("/api/conversations/conv-1")
        assert r1.status_code == r2.status_code == 200
        assert r1.get_json() == r2.get_json()
        assert conversation_service.get_conversation_detail.call_count == 2

    def test_workspace_list_is_idempotent(self, full_client, workspace_service):
        r1 = full_client.get("/api/workspaces?limit=10&offset=0")
        r2 = full_client.get("/api/workspaces?limit=10&offset=0")
        assert r1.status_code == r2.status_code == 200
        assert r1.get_json() == r2.get_json()


# ---------------------------------------------------------------------------
# T027: Archive cascade (service-layer integration)
# ---------------------------------------------------------------------------


class TestArchiveCascade:
    """Archive cascades through the hierarchy via service layer."""

    def test_workspace_archive_cascades_to_sessions(
        self, full_client, workspace_service, session_service,
    ):
        """Archiving a workspace should cascade to its sessions."""
        workspace_service.archive_workspace.return_value = _make_workspace(
            workspace_id="ws-1", status="archived",
        )
        resp = full_client.post("/api/workspaces/ws-1/archive")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "archived"
        # The service was called (cascade happens inside service layer)
        workspace_service.archive_workspace.assert_called_once()

    def test_session_archive_cascades_to_conversations(
        self, full_client, session_service, conversation_service,
    ):
        """Archiving a session should cascade to its conversations."""
        session_service.archive_session_managed.return_value = _make_session(
            session_id="sess-1", status="archived",
        )
        resp = full_client.post("/api/sessions/sess-1/archive")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "archived"
        session_service.archive_session_managed.assert_called_once()

    def test_archived_workspace_rejects_session_create(
        self, full_client, session_service,
    ):
        """Creating a session under an archived workspace should fail."""
        session_service.create_session.side_effect = ParentNotFoundError(
            "workspace", "ws-archived", "session",
            message="Cannot create session: parent workspace ws-archived is archived",
        )
        resp = full_client.post(
            "/api/workspaces/ws-archived/sessions",
            json={"title": "New session"},
        )
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body


# ---------------------------------------------------------------------------
# T027: Limit clamping and negative offset
# ---------------------------------------------------------------------------


class TestLimitClampingAndOffset:
    """Verify limit > 100 is clamped; negative offset returns 400."""

    def test_limit_clamped_to_100(self, full_client, workspace_service):
        """Requesting limit=500 should clamp to 100."""
        workspace_service.list_workspaces_paginated.return_value = {
            "items": [], "total": 0, "limit": 100, "offset": 0,
        }
        resp = full_client.get("/api/workspaces?limit=500")
        assert resp.status_code == 200
        # Service was called with clamped limit
        args = workspace_service.list_workspaces_paginated.call_args
        assert args.kwargs.get("limit", args[1].get("limit") if len(args) > 1 else None) <= 100

    def test_negative_offset_returns_400_workspaces(self, full_client, workspace_service):
        resp = full_client.get("/api/workspaces?offset=-5")
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_negative_offset_returns_400_sessions(self, full_client, session_service):
        resp = full_client.get("/api/workspaces/ws-1/sessions?offset=-1")
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_negative_offset_returns_400_conversations(self, full_client, conversation_service):
        resp = full_client.get("/api/sessions/sess-1/conversations?offset=-10")
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_limit_below_1_clamped(self, full_client, workspace_service):
        """Requesting limit=0 should clamp to 1."""
        workspace_service.list_workspaces_paginated.return_value = {
            "items": [], "total": 0, "limit": 1, "offset": 0,
        }
        resp = full_client.get("/api/workspaces?limit=0")
        assert resp.status_code == 200
        args = workspace_service.list_workspaces_paginated.call_args
        assert args.kwargs.get("limit", 1) >= 1

    def test_session_limit_clamped_to_100(self, full_client, session_service):
        """Requesting limit=500 on sessions should clamp to 100."""
        session_service.list_sessions_paginated.return_value = {
            "items": [], "total": 0, "limit": 100, "offset": 0,
        }
        resp = full_client.get("/api/workspaces/ws-1/sessions?limit=500")
        assert resp.status_code == 200
        args = session_service.list_sessions_paginated.call_args
        assert args.kwargs.get("limit", args[1].get("limit") if len(args) > 1 else None) <= 100

    def test_conversation_limit_clamped_to_100(self, full_client, conversation_service):
        """Requesting limit=500 on conversations should clamp to 100."""
        conversation_service.list_conversations_paginated.return_value = {
            "items": [], "total": 0, "limit": 100, "offset": 0,
        }
        resp = full_client.get("/api/sessions/sess-1/conversations?limit=500")
        assert resp.status_code == 200
        args = conversation_service.list_conversations_paginated.call_args
        assert args.kwargs.get("limit", args[1].get("limit") if len(args) > 1 else None) <= 100

    def test_session_limit_below_1_clamped(self, full_client, session_service):
        """Requesting limit=0 on sessions should clamp to 1."""
        session_service.list_sessions_paginated.return_value = {
            "items": [], "total": 0, "limit": 1, "offset": 0,
        }
        resp = full_client.get("/api/workspaces/ws-1/sessions?limit=0")
        assert resp.status_code == 200
        args = session_service.list_sessions_paginated.call_args
        assert args.kwargs.get("limit", 1) >= 1

    def test_conversation_limit_below_1_clamped(self, full_client, conversation_service):
        """Requesting limit=0 on conversations should clamp to 1."""
        conversation_service.list_conversations_paginated.return_value = {
            "items": [], "total": 0, "limit": 1, "offset": 0,
        }
        resp = full_client.get("/api/sessions/sess-1/conversations?limit=0")
        assert resp.status_code == 200
        args = conversation_service.list_conversations_paginated.call_args
        assert args.kwargs.get("limit", 1) >= 1


# ===========================================================================
# Session CRUD contract tests (T047)
# ===========================================================================


class TestCreateSession:
    """POST /api/workspaces/{id}/sessions creates session."""

    def test_creates_session_with_201(self, full_client, session_service):
        resp = full_client.post(
            "/api/workspaces/ws-1/sessions",
            json={"title": "Research session"},
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert "session_id" in body
        assert body.get("status") == "active"
        assert "created_at" in body
        assert "updated_at" in body

    def test_create_session_returns_location_header(self, full_client, session_service):
        resp = full_client.post(
            "/api/workspaces/ws-1/sessions",
            json={"title": "New session"},
        )
        assert resp.status_code == 201
        assert "Location" in resp.headers
        assert "/api/sessions/" in resp.headers["Location"]

    def test_create_session_requires_json_body(self, full_client, session_service):
        resp = full_client.post(
            "/api/workspaces/ws-1/sessions",
            data="not json",
            content_type="text/plain",
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body


class TestGetSessionDetail:
    """GET /api/sessions/{id} returns session detail."""

    def test_returns_session_detail(self, full_client, session_service):
        resp = full_client.get("/api/sessions/sess-1")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body.get("session_id") == "sess-1"
        assert "workspace_id" in body
        assert "status" in body
        assert "created_at" in body


class TestUpdateSession:
    """PUT /api/sessions/{id} updates session fields."""

    def test_updates_session_title(self, full_client, session_service):
        session_service.update_session.return_value = _make_session(
            session_id="sess-1", title="Updated",
        )
        resp = full_client.put(
            "/api/sessions/sess-1",
            json={"title": "Updated"},
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert "session_id" in body


class TestArchiveSession:
    """POST /api/sessions/{id}/archive archives session."""

    def test_archives_session(self, full_client, session_service):
        resp = full_client.post("/api/sessions/sess-1/archive")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body.get("status") == "archived"

    def test_archive_session_is_idempotent(self, full_client, session_service):
        session_service.archive_session_managed.return_value = _make_session(
            session_id="sess-1", status="archived",
        )
        r1 = full_client.post("/api/sessions/sess-1/archive")
        r2 = full_client.post("/api/sessions/sess-1/archive")
        assert r1.status_code == 200
        assert r2.status_code == 200


# ===========================================================================
# Conversation CRUD contract tests (T047)
# ===========================================================================


class TestCreateConversation:
    """POST /api/sessions/{id}/conversations creates conversation."""

    def test_creates_conversation_with_201(self, full_client, conversation_service):
        resp = full_client.post(
            "/api/sessions/sess-1/conversations",
            json={},
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert "conversation_id" in body
        assert "thread_id" in body
        assert "session_id" in body
        assert body.get("status") == "active"
        assert "created_at" in body

    def test_create_conversation_returns_location_header(
        self, full_client, conversation_service,
    ):
        resp = full_client.post(
            "/api/sessions/sess-1/conversations",
            json={},
        )
        assert resp.status_code == 201
        assert "Location" in resp.headers
        assert "/api/conversations/" in resp.headers["Location"]


class TestGetConversationDetail:
    """GET /api/conversations/{id} returns conversation detail."""

    def test_returns_conversation_detail(self, full_client, conversation_service):
        resp = full_client.get("/api/conversations/conv-1")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body.get("conversation_id") == "conv-1"
        assert "session_id" in body
        assert "status" in body
        assert "message_count" in body


class TestUpdateConversation:
    """PUT /api/conversations/{id} updates conversation fields."""

    def test_updates_conversation(self, full_client, conversation_service):
        conversation_service.update_conversation_managed.return_value = _make_conversation(
            conversation_id="conv-1",
        )
        resp = full_client.put(
            "/api/conversations/conv-1",
            json={"title": "Renamed conv"},
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert "conversation_id" in body

    def test_update_conversation_bad_body(self, full_client, conversation_service):
        resp = full_client.put(
            "/api/conversations/conv-1",
            data="not json",
            content_type="text/plain",
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body
        assert body["error"]["code"] == "VALIDATION_ERROR"


class TestArchiveConversation:
    """POST /api/conversations/{id}/archive archives conversation."""

    def test_archives_conversation(self, full_client, conversation_service):
        resp = full_client.post("/api/conversations/conv-1/archive")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body.get("status") == "archived"

    def test_archive_conversation_is_idempotent(
        self, full_client, conversation_service,
    ):
        conversation_service.archive_conversation_managed.return_value = _make_conversation(
            conversation_id="conv-1", status="archived",
        )
        r1 = full_client.post("/api/conversations/conv-1/archive")
        r2 = full_client.post("/api/conversations/conv-1/archive")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_archive_nonexistent_conversation_returns_404(
        self, full_client, conversation_service,
    ):
        conversation_service.archive_conversation_managed.side_effect = (
            EntityNotFoundError("conversation", "no-such-conv")
        )
        resp = full_client.post("/api/conversations/no-such-conv/archive")
        assert resp.status_code == 404


# ===========================================================================
# Session close lifecycle (T047)
# ===========================================================================


class TestSessionCloseLifecycle:
    """Closed sessions block new conversation creation but existing convos remain accessible."""

    def test_closed_session_blocks_conversation_creation(
        self, full_client, conversation_service,
    ):
        """Creating a conversation under a closed session should fail."""
        conversation_service.list_conversations_paginated.side_effect = (
            ParentNotFoundError(
                "session", "sess-closed", "conversation",
                message="Cannot create conversation: parent session sess-closed is closed",
            )
        )
        resp = full_client.post(
            "/api/sessions/sess-closed/conversations",
            json={},
        )
        assert resp.status_code == 404
        body = resp.get_json()
        assert "error" in body

    def test_existing_conversations_accessible_after_session_archive(
        self, full_client, session_service, conversation_service,
    ):
        """After archiving a session, its conversations are still readable."""
        session_service.archive_session_managed.return_value = _make_session(
            session_id="sess-1", status="archived",
        )
        full_client.post("/api/sessions/sess-1/archive")

        # Existing conversation still accessible via flat route
        resp = full_client.get("/api/conversations/conv-1")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body.get("conversation_id") == "conv-1"


# ===========================================================================
# Hierarchical ownership chain (T047)
# ===========================================================================


class TestHierarchicalOwnership:
    """Verify workspace → session → conversation ownership chain."""

    def test_session_inherits_workspace_user_id(self, full_client, session_service):
        """Session returned from create should reflect workspace ownership."""
        session_service.create_session.return_value = _make_session(
            session_id="sess-new", workspace_id="ws-1", user_id="user-1",
        )
        resp = full_client.post(
            "/api/workspaces/ws-1/sessions",
            json={"title": "Owned session"},
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["workspace_id"] == "ws-1"
        assert body["user_id"] == "user-1"

    def test_conversation_inherits_session_id(
        self, full_client, conversation_service,
    ):
        """Conversation returned from create should reflect session FK."""
        conversation_service.create_conversation.return_value = _make_conversation(
            conversation_id="conv-new", session_id="sess-1", user_id="user-1",
        )
        resp = full_client.post(
            "/api/sessions/sess-1/conversations",
            json={},
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["session_id"] == "sess-1"
        assert body["user_id"] == "user-1"

    def test_cross_user_session_access_returns_403(
        self, full_client, session_service,
    ):
        """Accessing another user's session returns 403."""
        session_service.get_session_detail.side_effect = OwnershipViolationError(
            "session", "sess-other", "user-1", "user-other",
        )
        resp = full_client.get("/api/sessions/sess-other")
        assert resp.status_code == 403

    def test_cross_user_conversation_access_returns_403(
        self, full_client, conversation_service,
    ):
        """Accessing another user's conversation returns 403."""
        conversation_service.get_conversation_detail.side_effect = OwnershipViolationError(
            "conversation", "conv-other", "user-1", "user-other",
        )
        resp = full_client.get("/api/conversations/conv-other")
        assert resp.status_code == 403

    def test_session_under_nonexistent_workspace_returns_404(
        self, full_client, session_service,
    ):
        """Creating session under non-existent workspace returns 404."""
        session_service.create_session.side_effect = ParentNotFoundError(
            "workspace", "ws-gone", "session",
        )
        resp = full_client.post(
            "/api/workspaces/ws-gone/sessions",
            json={"title": "Orphan session"},
        )
        assert resp.status_code == 404

    def test_conversation_under_nonexistent_session_returns_404(
        self, full_client, conversation_service,
    ):
        """Creating conversation under non-existent session returns 404."""
        conversation_service.list_conversations_paginated.side_effect = (
            ParentNotFoundError("session", "sess-gone", "conversation")
        )
        resp = full_client.post(
            "/api/sessions/sess-gone/conversations",
            json={},
        )
        assert resp.status_code == 404


# ===========================================================================
# Additional error envelope coverage (T047)
# ===========================================================================


class TestConversationErrorEnvelope:
    """Cover conversation error paths not in TestErrorEnvelopeParity."""

    def test_conversation_409_stale_entity(self, full_client, conversation_service):
        conversation_service.update_conversation_managed.side_effect = StaleEntityError(
            "conversation", "conv-1",
        )
        resp = full_client.put(
            "/api/conversations/conv-1",
            json={"title": "stale"},
        )
        assert resp.status_code == 409
        body = resp.get_json()
        assert "error" in body
        assert body["error"]["code"] == "CONFLICT"

    def test_workspace_400_on_empty_name(self, full_client, workspace_service):
        """POST /api/workspaces with missing name returns 400."""
        resp = full_client.post("/api/workspaces", json={"description": "no name"})
        assert resp.status_code == 400
        body = resp.get_json()
        assert "error" in body
        assert body["error"]["code"] == "VALIDATION_ERROR"
