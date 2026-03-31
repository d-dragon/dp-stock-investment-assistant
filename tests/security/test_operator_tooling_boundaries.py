"""Security tests: Operator-only tooling boundary verification.

Validates that reconciliation functionality is operator-only and does NOT
leak through the public Flask REST surface.

Reference: specs/stm-phase-cde/tasks.md - T037 (US6), T048 (US8)
Run with: pytest tests/security/ -v
"""

import inspect
import json
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from web.api_server import DEFAULT_HTTP_ROUTE_FACTORIES, DEFAULT_SOCKETIO_REGISTRARS
from web.routes.shared_context import APIRouteContext
from web.routes.service_health_routes import create_health_blueprint
from web.routes.ai_chat_routes import create_chat_blueprint
from web.routes.models_routes import create_models_blueprint
from web.routes.user_routes import create_user_blueprint
from web.routes.workspace_routes import create_workspace_blueprint
from web.routes.session_routes import create_session_blueprint
from web.routes.conversation_routes import create_conversation_blueprint


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_service_factory():
    sf = MagicMock()
    sf.get_workspace_service.return_value = MagicMock()
    sf.get_session_service.return_value = MagicMock()
    sf.get_conversation_service.return_value = MagicMock()
    return sf


@pytest.fixture
def api_route_context(mock_service_factory):
    mock_logger = MagicMock()
    mock_logger.getChild = MagicMock(return_value=mock_logger)
    return APIRouteContext(
        app=Flask(__name__),
        agent=MagicMock(),
        config={},
        logger=mock_logger,
        model_registry=MagicMock(),
        service_factory=mock_service_factory,
    )


@pytest.fixture
def app(api_route_context):
    """Flask test app with all public management blueprints registered."""
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True
    for factory in (
        create_health_blueprint,
        create_workspace_blueprint,
        create_session_blueprint,
        create_conversation_blueprint,
    ):
        bp = factory(api_route_context)
        flask_app.register_blueprint(bp, url_prefix="/api")
    return flask_app


@pytest.fixture
def client(app, apply_management_headers):
    return apply_management_headers(app.test_client())


# ---------------------------------------------------------------------------
# Tests: No reconciliation routes in public surface
# ---------------------------------------------------------------------------

class TestNoReconciliationRoutes:
    """Reconciliation must NOT be exposed via Flask url_map."""

    def test_no_reconcil_route_in_url_map(self, app):
        """No rule matching /reconcil* should exist in the public url_map."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        reconcil_routes = [r for r in rules if "reconcil" in r.lower()]
        assert reconcil_routes == [], (
            f"Reconciliation routes MUST NOT appear in public API: {reconcil_routes}"
        )

    def test_no_scan_route_in_url_map(self, app):
        """No rule matching /scan* or */scan should exist in the public url_map."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        scan_routes = [
            r for r in rules
            if "/scan" in r.lower() and r != "/static/<path:filename>"
        ]
        assert scan_routes == [], (
            f"Scan routes MUST NOT appear in public API: {scan_routes}"
        )


# ---------------------------------------------------------------------------
# Tests: Management API responses don't leak reconciliation fields
# ---------------------------------------------------------------------------

class TestNoReconciliationFieldLeakage:
    """Public API JSON responses must not contain reconciliation-internal fields."""

    _FORBIDDEN_KEYS = {
        "anomalies",
        "anomaly_count",
        "correlation_id",
        "scan_scope",
        "reconciliation",
    }

    def _assert_no_forbidden_keys(self, data):
        """Recursively check that no forbidden key appears in *data*."""
        if isinstance(data, dict):
            leaked = self._FORBIDDEN_KEYS & set(data.keys())
            assert not leaked, f"Response leaks reconciliation fields: {leaked}"
            for v in data.values():
                self._assert_no_forbidden_keys(v)
        elif isinstance(data, list):
            for item in data:
                self._assert_no_forbidden_keys(item)

    def test_health_endpoint_clean(self, client):
        """GET /api/health must not expose reconciliation fields."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        self._assert_no_forbidden_keys(resp.get_json())

    def test_workspace_list_clean(self, client, mock_service_factory):
        """GET /api/workspaces must not expose reconciliation fields."""
        mock_service_factory.get_workspace_service.return_value.list_workspaces_paginated.return_value = {
            "items": [], "total": 0, "limit": 50, "offset": 0,
        }
        resp = client.get("/api/workspaces?user_id=u1")
        if resp.status_code == 200:
            self._assert_no_forbidden_keys(resp.get_json())

    def test_session_list_clean(self, client, mock_service_factory):
        """GET /api/sessions must not expose reconciliation fields."""
        mock_service_factory.get_session_service.return_value.list_sessions.return_value = []
        resp = client.get("/api/sessions?workspace_id=ws1")
        if resp.status_code == 200:
            self._assert_no_forbidden_keys(resp.get_json())

    def test_conversation_list_clean(self, client, mock_service_factory):
        """GET /api/conversations must not expose reconciliation fields."""
        mock_service_factory.get_conversation_service.return_value.list_conversations.return_value = []
        resp = client.get("/api/conversations?session_id=s1")
        if resp.status_code == 200:
            self._assert_no_forbidden_keys(resp.get_json())


# ---------------------------------------------------------------------------
# Tests: Error messages don't expose scan internals
# ---------------------------------------------------------------------------

class TestNoScanInternalLeakage:
    """Error responses must not reveal reconciliation implementation details."""

    _LEAK_PATTERNS = [
        "reconciliation",
        "anomaly_detected",
        "scan_started",
        "scan_completed",
        "orphaned_thread",
        "metadata_drift",
        "stale_conversation",
        "missing_thread",
        "correlation_id",
    ]

    def test_404_does_not_leak_scan_internals(self, client):
        """A 404 on a non-existent route must not mention scan internals."""
        resp = client.get("/api/reconciliation/scan")
        body = resp.get_data(as_text=True).lower()
        for pattern in self._LEAK_PATTERNS:
            # 404 body should not contain internal terminology
            # (the word may appear in the URL echo, so only check non-URL part)
            if pattern not in "reconciliation":
                assert pattern not in body, (
                    f"404 response leaks scan internal: '{pattern}'"
                )

    def test_workspace_error_does_not_leak(self, client, mock_service_factory):
        """Workspace service error must not reveal reconciliation internals."""
        mock_service_factory.get_workspace_service.return_value.get_workspace_detail.side_effect = (
            Exception("Internal error during reconciliation scan_started")
        )
        resp = client.get("/api/workspaces/ws-missing")
        body = resp.get_data(as_text=True).lower()
        for pattern in self._LEAK_PATTERNS:
            assert pattern not in body, (
                f"Error response leaks scan internal: '{pattern}'"
            )


# ---------------------------------------------------------------------------
# Tests: Migration routes not in public surface (T041)
# ---------------------------------------------------------------------------

class TestNoMigrationRoutes:
    """Migration must NOT be exposed via Flask url_map."""

    def test_no_migration_route_in_url_map(self, app):
        """No rule matching /migrat* should exist in the public url_map."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        migration_routes = [r for r in rules if "migrat" in r.lower()]
        assert migration_routes == [], (
            f"Migration routes MUST NOT appear in public API: {migration_routes}"
        )

    def test_no_legacy_promote_route(self, app):
        """No rule matching /legacy or /promote should exist."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        legacy_routes = [
            r for r in rules
            if "legacy" in r.lower() or "promote" in r.lower()
        ]
        assert legacy_routes == [], (
            f"Legacy/promote routes MUST NOT appear in public API: {legacy_routes}"
        )


class TestNoMigrationFieldLeakage:
    """Public API responses must not contain migration-internal fields."""

    _MIGRATION_FORBIDDEN_KEYS = {
        "audit_log",
        "last_processed_source_id",
        "resume_cursor",
        "to_create",
        "to_skip",
        "writes_performed",
    }

    def _assert_no_migration_keys(self, data):
        if isinstance(data, dict):
            leaked = self._MIGRATION_FORBIDDEN_KEYS & set(data.keys())
            assert not leaked, f"Response leaks migration fields: {leaked}"
            for v in data.values():
                self._assert_no_migration_keys(v)
        elif isinstance(data, list):
            for item in data:
                self._assert_no_migration_keys(item)

    def test_health_endpoint_no_migration_fields(self, client):
        """GET /api/health must not expose migration fields."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        self._assert_no_migration_keys(resp.get_json())


# ---------------------------------------------------------------------------
# Tests: DEFAULT_HTTP_ROUTE_FACTORIES content assertion (T048)
# ---------------------------------------------------------------------------

class TestDefaultRouteFactoriesContent:
    """DEFAULT_HTTP_ROUTE_FACTORIES must contain exactly the public blueprints."""

    #: Authoritative set of public route factories — update on new blueprints.
    _EXPECTED_FACTORIES = frozenset({
        create_health_blueprint,
        create_chat_blueprint,
        create_models_blueprint,
        create_user_blueprint,
        create_workspace_blueprint,
        create_session_blueprint,
        create_conversation_blueprint,
    })

    #: Operator-forbidden substrings in factory/module names.
    _OPERATOR_PATTERNS = (
        "reconcil", "migration", "migrate", "operator",
        "scan", "anomal", "legacy", "promote",
    )

    def test_factories_match_expected_set(self):
        """DEFAULT_HTTP_ROUTE_FACTORIES contains exactly the public factories."""
        actual = frozenset(DEFAULT_HTTP_ROUTE_FACTORIES)
        assert actual == self._EXPECTED_FACTORIES, (
            f"Unexpected difference.\n"
            f"  Extra: {actual - self._EXPECTED_FACTORIES}\n"
            f"  Missing: {self._EXPECTED_FACTORIES - actual}"
        )

    def test_no_operator_factory_in_defaults(self):
        """No factory with an operator-related name appears in the defaults."""
        for factory in DEFAULT_HTTP_ROUTE_FACTORIES:
            name = factory.__name__.lower()
            module = (factory.__module__ or "").lower()
            for pat in self._OPERATOR_PATTERNS:
                assert pat not in name, (
                    f"Operator factory '{factory.__name__}' found in DEFAULT_HTTP_ROUTE_FACTORIES"
                )
                assert pat not in module, (
                    f"Operator module '{factory.__module__}' found in DEFAULT_HTTP_ROUTE_FACTORIES"
                )

    def test_no_operator_socketio_registrar(self):
        """No SocketIO registrar with an operator-related name appears in defaults."""
        for registrar in DEFAULT_SOCKETIO_REGISTRARS:
            name = registrar.__name__.lower()
            module = (registrar.__module__ or "").lower()
            for pat in self._OPERATOR_PATTERNS:
                assert pat not in name, (
                    f"Operator registrar '{registrar.__name__}' found in DEFAULT_SOCKETIO_REGISTRARS"
                )
                assert pat not in module, (
                    f"Operator module '{registrar.__module__}' found in DEFAULT_SOCKETIO_REGISTRARS"
                )


# ---------------------------------------------------------------------------
# Tests: Complete URL-map audit (T048)
# ---------------------------------------------------------------------------

class TestPublicUrlMapAudit:
    """Every registered URL rule must be accounted for — no unexpected routes."""

    #: Known-good route prefixes produced by the default factories + Flask builtins.
    _ALLOWED_ROUTE_PREFIXES = (
        "/api/health",
        "/api/chat",
        "/api/config",   # served by ai_chat_routes blueprint
        "/api/models",
        "/api/users",
        "/api/workspaces",
        "/api/sessions",
        "/api/conversations",
        "/static/",  # Flask built-in
    )

    #: Operator-forbidden substrings that must never appear in any route.
    _OPERATOR_PATTERNS = (
        "reconcil", "migration", "migrate", "operator",
        "scan", "anomal", "legacy", "promote",
    )

    @pytest.fixture
    def full_app(self, api_route_context):
        """Flask app with ALL default public blueprints registered."""
        flask_app = Flask(__name__)
        flask_app.config["TESTING"] = True
        for factory in DEFAULT_HTTP_ROUTE_FACTORIES:
            bp = factory(api_route_context)
            if bp is not None:
                flask_app.register_blueprint(bp, url_prefix="/api")
        return flask_app

    def test_all_routes_accounted_for(self, full_app):
        """Every url_map rule must start with a known prefix."""
        rules = [rule.rule for rule in full_app.url_map.iter_rules()]
        unexpected = [
            r for r in rules
            if not any(r.startswith(p) for p in self._ALLOWED_ROUTE_PREFIXES)
        ]
        assert unexpected == [], (
            f"Unexpected routes in public url_map: {unexpected}"
        )

    def test_no_operator_pattern_in_any_route(self, full_app):
        """No operator-related substring should appear in any registered route."""
        rules = [rule.rule for rule in full_app.url_map.iter_rules()]
        for rule in rules:
            lower = rule.lower()
            for pat in self._OPERATOR_PATTERNS:
                assert pat not in lower, (
                    f"Operator pattern '{pat}' found in route: {rule}"
                )

    def test_no_anomaly_route_in_url_map(self, app):
        """No rule matching /anomal* should exist in the public url_map."""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        anomaly_routes = [r for r in rules if "anomal" in r.lower()]
        assert anomaly_routes == [], (
            f"Anomaly routes MUST NOT appear in public API: {anomaly_routes}"
        )


# ---------------------------------------------------------------------------
# Tests: SocketIO events don't expose operator patterns (T048)
# ---------------------------------------------------------------------------

class TestNoOperatorSocketIOEvents:
    """Socket.IO event names must not include operator-internal patterns."""

    _OPERATOR_PATTERNS = (
        "reconcil", "migration", "migrate", "operator",
        "scan", "anomal", "legacy", "promote",
    )

    def test_chat_events_source_has_no_operator_event_names(self):
        """Inspect the register_chat_events function source for operator event strings."""
        from web.sockets.chat_events import register_chat_events
        source = inspect.getsource(register_chat_events)
        for pat in self._OPERATOR_PATTERNS:
            # Look for @socketio.on('...operator_pattern...')
            assert f"'{pat}" not in source.lower() and f'"{pat}' not in source.lower(), (
                f"Operator event pattern '{pat}' found in register_chat_events source"
            )

    def test_default_registrars_have_no_operator_events(self):
        """Every default SocketIO registrar's source is free of operator event patterns."""
        for registrar in DEFAULT_SOCKETIO_REGISTRARS:
            source = inspect.getsource(registrar)
            for pat in self._OPERATOR_PATTERNS:
                assert f"'{pat}" not in source.lower() and f'"{pat}' not in source.lower(), (
                    f"Operator pattern '{pat}' in registrar '{registrar.__name__}'"
                )


# ---------------------------------------------------------------------------
# Tests: Operator services not instantiated during route registration (T048)
# ---------------------------------------------------------------------------

class TestOperatorServiceIsolation:
    """Operator services must only be instantiated via explicit factory calls,
    not as a side-effect of route/blueprint registration."""

    def test_reconciliation_service_not_called_during_blueprint_registration(
        self, api_route_context
    ):
        """Registering all default blueprints must NOT call get_reconciliation_service."""
        sf = api_route_context.service_factory
        sf.get_reconciliation_service = MagicMock(
            side_effect=AssertionError(
                "get_reconciliation_service was called during route registration"
            )
        )

        flask_app = Flask(__name__)
        flask_app.config["TESTING"] = True
        for factory in DEFAULT_HTTP_ROUTE_FACTORIES:
            bp = factory(api_route_context)
            if bp is not None:
                flask_app.register_blueprint(bp, url_prefix="/api")

        # If we get here without AssertionError, the service was not called.
        sf.get_reconciliation_service.assert_not_called()
