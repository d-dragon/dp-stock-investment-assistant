"""Session management REST API endpoints."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request

from services.exceptions import (
    EntityNotFoundError,
    InvalidLifecycleTransitionError,
    OwnershipViolationError,
    ParentNotFoundError,
    StaleEntityError,
    ValidationError,
)
from utils.service_utils import management_error_response, normalize_document, parse_list_params

from .shared_context import APIRouteContext

_VALID_STATUSES = {"active", "closed", "archived"}


def create_session_blueprint(context: APIRouteContext) -> Blueprint:
    """Create the session management blueprint."""

    blueprint = Blueprint("sessions", __name__)
    logger = context.logger.getChild("sessions")

    def _get_session_service():
        if context.service_factory is None:
            return None
        try:
            return context.service_factory.get_session_service()
        except Exception as exc:
            logger.error("Failed to get SessionService", extra={"error": str(exc)})
            return None

    def _service_unavailable():
        logger.warning("Session service unavailable")
        return jsonify({"error": "Session service unavailable"}), 503

    def _get_user_id() -> Optional[str]:
        user_id = request.headers.get("X-User-ID")
        if user_id is None:
            return None
        return user_id.strip() or None

    @blueprint.before_request
    def _require_user_id_header():
        user_id = _get_user_id()
        if user_id is None:
            return jsonify(management_error_response(
                "X-User-ID header is required", 400, code="VALIDATION_ERROR",
            )), 400
        return None

    def _parse_json_payload() -> Optional[Dict[str, Any]]:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return None
        return payload

    # ── Nested under workspace ──────────────────────────────────

    @blueprint.route("/workspaces/<workspace_id>/sessions", methods=["POST"])
    def create_session(workspace_id: str):
        service = _get_session_service()
        if service is None:
            return _service_unavailable()

        payload = _parse_json_payload()
        if payload is None:
            return jsonify(management_error_response(
                "Request body must be a JSON object", 400, code="VALIDATION_ERROR",
            )), 400

        title = payload.get("title", "")
        user_id = _get_user_id()
        session_id = str(uuid.uuid4())

        try:
            created = service.create_session(
                session_id, workspace_id, user_id, title=title,
            )
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except ValidationError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except ValueError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except Exception as e:
            logger.exception("Unexpected error creating session")
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        if not created:
            return jsonify(management_error_response(
                "Failed to create session", 500, code="INTERNAL_ERROR",
            )), 500

        result = normalize_document(created)
        result.setdefault("conversation_count", 0)

        response = jsonify(result)
        response.status_code = 201
        response.headers["Location"] = f"/api/sessions/{session_id}"
        return response

    @blueprint.route("/workspaces/<workspace_id>/sessions", methods=["GET"])
    def list_sessions(workspace_id: str):
        service = _get_session_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()
        try:
            params = parse_list_params(request.args, valid_statuses=_VALID_STATUSES)
        except ValueError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400

        try:
            result = service.list_sessions_paginated(
                workspace_id, user_id,
                limit=params.limit,
                offset=params.offset,
                status=params.status,
            )
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except Exception as e:
            logger.exception("Unexpected error listing sessions")
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    # ── Flat session routes ─────────────────────────────────────

    @blueprint.route("/sessions/<session_id>", methods=["GET"])
    def get_session(session_id: str):
        service = _get_session_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()

        try:
            result = service.get_session_detail(session_id, user_id)
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except Exception as e:
            logger.exception("Unexpected error fetching session", extra={"session_id": session_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/sessions/<session_id>", methods=["PUT"])
    def update_session(session_id: str):
        service = _get_session_service()
        if service is None:
            return _service_unavailable()

        payload = _parse_json_payload()
        if payload is None:
            return jsonify(management_error_response(
                "Request body must be a JSON object", 400, code="VALIDATION_ERROR",
            )), 400

        user_id = _get_user_id()
        title = payload.get("title")
        description = payload.get("description")

        try:
            result = service.update_session(
                session_id, user_id, title=title, description=description,
            )
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except StaleEntityError as e:
            return jsonify(management_error_response(str(e), 409, code="CONFLICT")), 409
        except ValidationError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except Exception as e:
            logger.exception("Unexpected error updating session", extra={"session_id": session_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/sessions/<session_id>/close", methods=["POST"])
    def close_session(session_id: str):
        service = _get_session_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()

        try:
            result = service.close_session_managed(session_id, user_id)
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except InvalidLifecycleTransitionError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except Exception as e:
            logger.exception("Unexpected error closing session", extra={"session_id": session_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/sessions/<session_id>/archive", methods=["POST"])
    def archive_session(session_id: str):
        service = _get_session_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()

        try:
            result = service.archive_session_managed(session_id, user_id)
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except StaleEntityError as e:
            return jsonify(management_error_response(str(e), 409, code="CONFLICT")), 409
        except ValidationError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except Exception as e:
            logger.exception("Unexpected error archiving session", extra={"session_id": session_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    return blueprint
