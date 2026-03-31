"""Conversation management REST API endpoints."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request

from services.exceptions import (
    EntityNotFoundError,
    OwnershipViolationError,
    ParentNotFoundError,
    StaleEntityError,
    ValidationError,
)
from utils.service_utils import management_error_response, normalize_document, parse_list_params

from .shared_context import APIRouteContext

_VALID_STATUSES = {"active", "summarized", "archived"}


def create_conversation_blueprint(context: APIRouteContext) -> Blueprint:
    """Create the conversation management blueprint."""

    blueprint = Blueprint("conversations", __name__)
    logger = context.logger.getChild("conversations")

    def _get_conversation_service():
        if context.service_factory is None:
            return None
        try:
            return context.service_factory.get_conversation_service()
        except Exception as exc:
            logger.error("Failed to get ConversationService", extra={"error": str(exc)})
            return None

    def _get_session_service():
        if context.service_factory is None:
            return None
        try:
            return context.service_factory.get_session_service()
        except Exception as exc:
            logger.error("Failed to get SessionService", extra={"error": str(exc)})
            return None

    def _service_unavailable():
        logger.warning("Conversation service unavailable")
        return jsonify({"error": "Conversation service unavailable"}), 503

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

    # ── Nested under session ────────────────────────────────────

    @blueprint.route("/sessions/<session_id>/conversations", methods=["POST"])
    def create_conversation(session_id: str):
        service = _get_conversation_service()
        if service is None:
            return _service_unavailable()
        session_service = _get_session_service()
        if session_service is None:
            logger.warning("Session service unavailable while creating conversation")
            return jsonify(management_error_response(
                "Session service unavailable", 503, code="SERVICE_UNAVAILABLE",
            )), 503

        payload = _parse_json_payload() or {}
        user_id = _get_user_id()
        conversation_id = str(uuid.uuid4())
        thread_id = conversation_id  # 1:1 mapping

        try:
            # Validate parent session exists and user owns it
            service.list_conversations_paginated(session_id, user_id, limit=1, offset=0)
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except Exception as e:
            logger.exception("Unexpected error validating session for conversation create")
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        try:
            session_detail = session_service.get_session_detail(session_id, user_id)
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except Exception:
            logger.exception("Unexpected error resolving parent session")
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        session_status = session_detail.get("status", "active")
        if session_status in {"closed", "archived"}:
            return jsonify(management_error_response(
                f"Cannot create conversation for session in '{session_status}' state",
                400,
                code="VALIDATION_ERROR",
            )), 400

        workspace_id = session_detail.get("workspace_id")
        if not workspace_id:
            return jsonify(management_error_response(
                "Parent session is missing workspace_id", 500, code="INTERNAL_ERROR",
            )), 500

        try:
            created = service.create_conversation(
                conversation_id=conversation_id,
                thread_id=thread_id,
                session_id=session_id,
                workspace_id=workspace_id,
                user_id=user_id,
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
            logger.exception("Unexpected error creating conversation")
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        if not created:
            return jsonify(management_error_response(
                "Failed to create conversation", 500, code="INTERNAL_ERROR",
            )), 500

        result = normalize_document(created)

        response = jsonify(result)
        response.status_code = 201
        response.headers["Location"] = f"/api/conversations/{conversation_id}"
        return response

    @blueprint.route("/sessions/<session_id>/conversations", methods=["GET"])
    def list_conversations(session_id: str):
        service = _get_conversation_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()
        try:
            params = parse_list_params(request.args, valid_statuses=_VALID_STATUSES)
        except ValueError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400

        try:
            result = service.list_conversations_paginated(
                session_id, user_id,
                limit=params.limit,
                offset=params.offset,
                status=params.status,
            )
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except Exception as e:
            logger.exception("Unexpected error listing conversations")
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    # ── Flat conversation routes ────────────────────────────────

    @blueprint.route("/conversations/<conversation_id>", methods=["GET"])
    def get_conversation(conversation_id: str):
        service = _get_conversation_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()

        try:
            result = service.get_conversation_detail(conversation_id, user_id)
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except Exception as e:
            logger.exception("Unexpected error fetching conversation", extra={"conversation_id": conversation_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/conversations/<conversation_id>", methods=["PUT"])
    def update_conversation(conversation_id: str):
        service = _get_conversation_service()
        if service is None:
            return _service_unavailable()

        payload = _parse_json_payload()
        if payload is None:
            return jsonify(management_error_response(
                "Request body must be a JSON object", 400, code="VALIDATION_ERROR",
            )), 400

        user_id = _get_user_id()
        title = payload.get("title")

        try:
            result = service.update_conversation_managed(
                conversation_id, user_id, title=title,
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
            logger.exception("Unexpected error updating conversation", extra={"conversation_id": conversation_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/conversations/<conversation_id>/summary", methods=["GET"])
    def get_conversation_summary(conversation_id: str):
        service = _get_conversation_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()

        try:
            result = service.get_conversation_summary(conversation_id, user_id)
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except ParentNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except Exception as e:
            logger.exception("Unexpected error fetching conversation summary", extra={"conversation_id": conversation_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/conversations/<conversation_id>/archive", methods=["POST"])
    def archive_conversation(conversation_id: str):
        service = _get_conversation_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()

        try:
            result = service.archive_conversation_managed(conversation_id, user_id)
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
            logger.exception("Unexpected error archiving conversation", extra={"conversation_id": conversation_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    return blueprint
