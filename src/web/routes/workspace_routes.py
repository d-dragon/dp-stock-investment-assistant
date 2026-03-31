"""Workspace management REST API endpoints."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request

from services.exceptions import (
    EntityNotFoundError,
    OwnershipViolationError,
    ParentNotFoundError,
    StaleEntityError,
    ValidationError,
)
from utils.service_utils import management_error_response, parse_list_params

from .shared_context import APIRouteContext

_VALID_STATUSES = {"active", "archived"}


def create_workspace_blueprint(context: APIRouteContext) -> Blueprint:
    """Create the workspace management blueprint."""

    blueprint = Blueprint("workspaces", __name__)
    logger = context.logger.getChild("workspaces")

    def _get_workspace_service():
        if context.service_factory is None:
            return None
        try:
            return context.service_factory.get_workspace_service()
        except Exception as exc:
            logger.error("Failed to get WorkspaceService", extra={"error": str(exc)})
            return None

    def _service_unavailable():
        logger.warning("Workspace service unavailable")
        return jsonify({"error": "Workspace service unavailable"}), 503

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

    @blueprint.route("/workspaces", methods=["POST"])
    def create_workspace():
        service = _get_workspace_service()
        if service is None:
            return _service_unavailable()

        payload = _parse_json_payload()
        if payload is None:
            return jsonify(management_error_response(
                "Request body must be a JSON object", 400, code="VALIDATION_ERROR",
            )), 400

        name = payload.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            return jsonify(management_error_response(
                "Field 'name' is required and must be a non-empty string",
                400, code="VALIDATION_ERROR",
            )), 400

        description = payload.get("description")
        user_id = _get_user_id()

        try:
            created = service.create_workspace(
                user_id, name=name, description=description,
            )
        except ValidationError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except ValueError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except Exception as e:
            logger.exception("Unexpected error creating workspace")
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        if not created:
            return jsonify(management_error_response(
                "Failed to create workspace", 500, code="INTERNAL_ERROR",
            )), 500

        response = jsonify(created)
        response.status_code = 201
        workspace_id = (
            created.get("workspace_id")
            or created.get("_id")
            or created.get("id")
        )
        if workspace_id:
            response.headers["Location"] = f"/api/workspaces/{workspace_id}"
        return response

    @blueprint.route("/workspaces", methods=["GET"])
    def list_workspaces():
        service = _get_workspace_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()
        try:
            params = parse_list_params(request.args, valid_statuses=_VALID_STATUSES)
        except ValueError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400

        try:
            result = service.list_workspaces_paginated(
                user_id,
                limit=params.limit,
                offset=params.offset,
                status=params.status,
            )
        except Exception as e:
            logger.exception("Unexpected error listing workspaces")
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/workspaces/<workspace_id>", methods=["GET"])
    def get_workspace(workspace_id: str):
        service = _get_workspace_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()

        try:
            result = service.get_workspace_detail(workspace_id, user_id)
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except Exception as e:
            logger.exception("Unexpected error fetching workspace", extra={"workspace_id": workspace_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/workspaces/<workspace_id>", methods=["PUT"])
    def update_workspace(workspace_id: str):
        service = _get_workspace_service()
        if service is None:
            return _service_unavailable()

        payload = _parse_json_payload()
        if payload is None:
            return jsonify(management_error_response(
                "Request body must be a JSON object", 400, code="VALIDATION_ERROR",
            )), 400

        user_id = _get_user_id()
        name = payload.get("name")
        description = payload.get("description")

        try:
            result = service.update_workspace(
                workspace_id, user_id, name=name, description=description,
            )
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except StaleEntityError as e:
            return jsonify(management_error_response(str(e), 409, code="CONFLICT")), 409
        except ValidationError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except Exception as e:
            logger.exception("Unexpected error updating workspace", extra={"workspace_id": workspace_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    @blueprint.route("/workspaces/<workspace_id>/archive", methods=["POST"])
    def archive_workspace(workspace_id: str):
        service = _get_workspace_service()
        if service is None:
            return _service_unavailable()

        user_id = _get_user_id()

        try:
            result = service.archive_workspace(workspace_id, user_id)
        except EntityNotFoundError as e:
            return jsonify(management_error_response(str(e), 404, code="NOT_FOUND")), 404
        except OwnershipViolationError as e:
            return jsonify(management_error_response(str(e), 403, code="FORBIDDEN")), 403
        except StaleEntityError as e:
            return jsonify(management_error_response(str(e), 409, code="CONFLICT")), 409
        except ValidationError as e:
            return jsonify(management_error_response(str(e), 400, code="VALIDATION_ERROR")), 400
        except Exception as e:
            logger.exception("Unexpected error archiving workspace", extra={"workspace_id": workspace_id})
            return jsonify(management_error_response(
                "Internal server error", 500, code="INTERNAL_ERROR",
            )), 500

        return jsonify(result), 200

    return blueprint
