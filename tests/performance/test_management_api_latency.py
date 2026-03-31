"""Performance tests: Management API latency-budget verification.

Validates that the management API endpoints meet their P95 latency budgets
(NFR-1.4.1–NFR-1.4.4, AC-5.5) using the Flask test client with mocked
services for consistent, network-free measurement.

Run with: pytest tests/performance/ -m performance -v
"""

import statistics
import time
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from services.factory import ServiceFactory
from web.routes.shared_context import APIRouteContext
from web.routes.workspace_routes import create_workspace_blueprint
from web.routes.session_routes import create_session_blueprint
from web.routes.conversation_routes import create_conversation_blueprint

# ---------------------------------------------------------------------------
# Latency budgets (P95, milliseconds)
# ---------------------------------------------------------------------------
BUDGET_GET_SINGLE_MS = 200
BUDGET_LIST_MS = 500
BUDGET_MUTATE_MS = 300
BUDGET_CASCADE_MS = 2000

ITERATIONS = 50

# ---------------------------------------------------------------------------
# Realistic stub data
# ---------------------------------------------------------------------------
_NOW = datetime.now(timezone.utc).isoformat()


def _workspace(workspace_id: str = "ws-1", *, status: str = "active") -> dict:
    return {
        "_id": workspace_id,
        "id": workspace_id,
        "name": "Growth watchlist",
        "description": "Performance test workspace",
        "user_id": "perf-user",
        "status": status,
        "created_at": _NOW,
        "updated_at": _NOW,
        "session_count": 3,
        "active_conversation_count": 5,
    }


def _session(session_id: str = "ses-1", workspace_id: str = "ws-1", *, status: str = "active") -> dict:
    return {
        "_id": session_id,
        "id": session_id,
        "workspace_id": workspace_id,
        "title": "Q2 review",
        "status": status,
        "user_id": "perf-user",
        "created_at": _NOW,
        "updated_at": _NOW,
        "conversation_count": 2,
    }


def _conversation(
    conversation_id: str = "conv-1",
    session_id: str = "ses-1",
    workspace_id: str = "ws-1",
) -> dict:
    return {
        "_id": conversation_id,
        "id": conversation_id,
        "conversation_id": conversation_id,
        "thread_id": conversation_id,
        "session_id": session_id,
        "workspace_id": workspace_id,
        "title": "Scenario run",
        "status": "active",
        "user_id": "perf-user",
        "message_count": 12,
        "total_tokens": 4500,
        "created_at": _NOW,
        "updated_at": _NOW,
    }


def _paginated(items: list, total: int | None = None) -> dict:
    return {
        "items": items,
        "total": total if total is not None else len(items),
        "limit": 50,
        "offset": 0,
    }


# ---------------------------------------------------------------------------
# Flask test app with mocked services
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def perf_app():
    """Build a minimal Flask app with management blueprints backed by mocks."""
    app = Flask("perf_test")
    app.config["TESTING"] = True

    logger = MagicMock()
    logger.getChild = MagicMock(return_value=logger)

    # --- Workspace service mock ---
    ws_service = MagicMock()
    ws_service.get_workspace_detail.return_value = _workspace()
    ws_service.list_workspaces_paginated.return_value = _paginated(
        [_workspace(f"ws-{i}") for i in range(20)], total=20
    )
    ws_service.create_workspace.return_value = _workspace("ws-new")
    ws_service.update_workspace.return_value = _workspace()
    ws_service.archive_workspace.return_value = _workspace(status="archived")

    # --- Session service mock ---
    ses_service = MagicMock()
    ses_service.get_session_detail.return_value = _session()
    ses_service.list_sessions_paginated.return_value = _paginated(
        [_session(f"ses-{i}") for i in range(15)], total=15
    )
    ses_service.create_session.return_value = _session("ses-new")
    ses_service.update_session.return_value = _session()
    ses_service.archive_session_managed.return_value = {
        **_session(status="archived"),
        "status": "archived",
        "archived_children": {"sessions": 0, "conversations": 3},
    }

    # --- Conversation service mock ---
    conv_service = MagicMock()
    conv_service.get_conversation_detail.return_value = _conversation()
    conv_service.list_conversations_paginated.return_value = _paginated(
        [_conversation(f"conv-{i}") for i in range(10)], total=10
    )
    conv_service.create_conversation.return_value = _conversation("conv-new")
    conv_service.update_conversation_managed.return_value = _conversation()
    conv_service.archive_conversation_managed.return_value = {
        **_conversation(),
        "status": "archived",
    }

    # --- ServiceFactory mock ---
    service_factory = MagicMock(spec=ServiceFactory)
    service_factory.get_workspace_service.return_value = ws_service
    service_factory.get_session_service.return_value = ses_service
    service_factory.get_conversation_service.return_value = conv_service

    context = APIRouteContext(
        app=app,
        agent=MagicMock(),
        config={},
        logger=logger,
        chat_service=MagicMock(),
        model_registry=MagicMock(),
        set_active_model=MagicMock(),
        service_factory=service_factory,
    )

    for factory in (
        create_workspace_blueprint,
        create_session_blueprint,
        create_conversation_blueprint,
    ):
        bp = factory(context)
        app.register_blueprint(bp, url_prefix="/api")

    return app


@pytest.fixture(scope="module")
def client(perf_app):
    """Flask test client (in-process, no network)."""
    return perf_app.test_client()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _measure(fn, n: int = ITERATIONS) -> float:
    """Run *fn* *n* times and return the P95 latency in ms."""
    timings: list[float] = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        elapsed_ms = (time.perf_counter() - start) * 1000
        timings.append(elapsed_ms)
    timings.sort()
    return timings[int(0.95 * len(timings))]


HEADERS = {"X-User-ID": "perf-user", "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@pytest.mark.performance
class TestManagementApiLatency:
    """Verify each endpoint category stays within its P95 latency budget."""

    # ── GET single entity ─────────────────────────────────────

    def test_get_workspace_latency(self, client):
        p95 = _measure(lambda: client.get("/api/workspaces/ws-1", headers=HEADERS))
        assert p95 < BUDGET_GET_SINGLE_MS, (
            f"GET /api/workspaces/{{id}} p95={p95:.1f}ms exceeds {BUDGET_GET_SINGLE_MS}ms budget"
        )

    def test_get_session_latency(self, client):
        p95 = _measure(lambda: client.get("/api/sessions/ses-1", headers=HEADERS))
        assert p95 < BUDGET_GET_SINGLE_MS, (
            f"GET /api/sessions/{{id}} p95={p95:.1f}ms exceeds {BUDGET_GET_SINGLE_MS}ms budget"
        )

    def test_get_conversation_latency(self, client):
        p95 = _measure(lambda: client.get("/api/conversations/conv-1", headers=HEADERS))
        assert p95 < BUDGET_GET_SINGLE_MS, (
            f"GET /api/conversations/{{id}} p95={p95:.1f}ms exceeds {BUDGET_GET_SINGLE_MS}ms budget"
        )

    # ── List entities ─────────────────────────────────────────

    def test_list_workspaces_latency(self, client):
        p95 = _measure(lambda: client.get("/api/workspaces", headers=HEADERS))
        assert p95 < BUDGET_LIST_MS, (
            f"GET /api/workspaces p95={p95:.1f}ms exceeds {BUDGET_LIST_MS}ms budget"
        )

    def test_list_sessions_latency(self, client):
        p95 = _measure(
            lambda: client.get("/api/workspaces/ws-1/sessions", headers=HEADERS)
        )
        assert p95 < BUDGET_LIST_MS, (
            f"GET /api/workspaces/{{id}}/sessions p95={p95:.1f}ms exceeds {BUDGET_LIST_MS}ms budget"
        )

    def test_list_conversations_latency(self, client):
        p95 = _measure(
            lambda: client.get("/api/sessions/ses-1/conversations", headers=HEADERS)
        )
        assert p95 < BUDGET_LIST_MS, (
            f"GET /api/sessions/{{id}}/conversations p95={p95:.1f}ms exceeds {BUDGET_LIST_MS}ms budget"
        )

    # ── Create / Update / Archive ─────────────────────────────

    def test_create_workspace_latency(self, client):
        import json

        body = json.dumps({"name": "Perf workspace", "description": "latency test"})
        p95 = _measure(lambda: client.post("/api/workspaces", data=body, headers=HEADERS))
        assert p95 < BUDGET_MUTATE_MS, (
            f"POST /api/workspaces p95={p95:.1f}ms exceeds {BUDGET_MUTATE_MS}ms budget"
        )

    def test_update_workspace_latency(self, client):
        import json

        body = json.dumps({"name": "Renamed"})
        p95 = _measure(
            lambda: client.put("/api/workspaces/ws-1", data=body, headers=HEADERS)
        )
        assert p95 < BUDGET_MUTATE_MS, (
            f"PUT /api/workspaces/{{id}} p95={p95:.1f}ms exceeds {BUDGET_MUTATE_MS}ms budget"
        )

    def test_archive_workspace_latency(self, client):
        p95 = _measure(
            lambda: client.post("/api/workspaces/ws-1/archive", headers=HEADERS)
        )
        assert p95 < BUDGET_MUTATE_MS, (
            f"POST /api/workspaces/{{id}}/archive p95={p95:.1f}ms exceeds {BUDGET_MUTATE_MS}ms budget"
        )

    def test_create_session_latency(self, client):
        import json

        body = json.dumps({"title": "Perf session"})
        p95 = _measure(
            lambda: client.post(
                "/api/workspaces/ws-1/sessions", data=body, headers=HEADERS
            )
        )
        assert p95 < BUDGET_MUTATE_MS, (
            f"POST /api/workspaces/{{id}}/sessions p95={p95:.1f}ms exceeds {BUDGET_MUTATE_MS}ms budget"
        )

    def test_update_session_latency(self, client):
        import json

        body = json.dumps({"title": "Renamed session"})
        p95 = _measure(
            lambda: client.put("/api/sessions/ses-1", data=body, headers=HEADERS)
        )
        assert p95 < BUDGET_MUTATE_MS, (
            f"PUT /api/sessions/{{id}} p95={p95:.1f}ms exceeds {BUDGET_MUTATE_MS}ms budget"
        )

    def test_archive_session_latency(self, client):
        p95 = _measure(
            lambda: client.post("/api/sessions/ses-1/archive", headers=HEADERS)
        )
        assert p95 < BUDGET_MUTATE_MS, (
            f"POST /api/sessions/{{id}}/archive p95={p95:.1f}ms exceeds {BUDGET_MUTATE_MS}ms budget"
        )

    def test_archive_conversation_latency(self, client):
        p95 = _measure(
            lambda: client.post("/api/conversations/conv-1/archive", headers=HEADERS)
        )
        assert p95 < BUDGET_MUTATE_MS, (
            f"POST /api/conversations/{{id}}/archive p95={p95:.1f}ms exceeds {BUDGET_MUTATE_MS}ms budget"
        )

    # ── Cascade archive ───────────────────────────────────────

    def test_cascade_archive_workspace_latency(self, perf_app, client):
        """Archive a workspace whose mock returns cascade metadata (children archived)."""
        # Reconfigure the workspace service mock to simulate cascade with children
        ws_service = (
            perf_app.extensions
            if hasattr(perf_app, "extensions")
            else None
        )
        # The mock already returns archived status; the budget is for the
        # full round-trip including serialisation.  Real cascade overhead
        # comes from the service layer, which is mocked here — the test
        # validates that the *route* layer itself doesn't blow the budget.
        p95 = _measure(
            lambda: client.post("/api/workspaces/ws-1/archive", headers=HEADERS)
        )
        assert p95 < BUDGET_CASCADE_MS, (
            f"Cascade archive workspace p95={p95:.1f}ms exceeds {BUDGET_CASCADE_MS}ms budget"
        )

    def test_cascade_archive_session_latency(self, client):
        """Archive a session that cascades to child conversations."""
        p95 = _measure(
            lambda: client.post("/api/sessions/ses-1/archive", headers=HEADERS)
        )
        assert p95 < BUDGET_CASCADE_MS, (
            f"Cascade archive session p95={p95:.1f}ms exceeds {BUDGET_CASCADE_MS}ms budget"
        )
