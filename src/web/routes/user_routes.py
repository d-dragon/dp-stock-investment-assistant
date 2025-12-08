"""User-focused REST API endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request

from services.factory import ServiceFactory
from services.user_service import UserService

from .api_routes import APIRouteContext


def create_user_blueprint(context: APIRouteContext) -> Blueprint:
    """Create endpoints for user CRUD-style interactions."""

    blueprint = Blueprint("users", __name__)
    logger = context.logger.getChild("users")

    service_factory = context.service_factory
    user_service: Optional[UserService] = context.user_service

    def _get_user_service() -> Optional[UserService]:
        nonlocal service_factory, user_service
        if user_service is not None:
            return user_service

        if service_factory is None:
            try:
                service_factory = ServiceFactory(context.config, logger=logger.getChild("factory"))
            except Exception as exc:  # pragma: no cover - defensive log branch
                logger.error("Failed to initialize ServiceFactory", extra={"error": str(exc)})
                return None

        try:
            user_service = service_factory.get_user_service()
        except Exception as exc:
            logger.error("Failed to initialize UserService", extra={"error": str(exc)})
            user_service = None
        return user_service

    def _service_unavailable():
        logger.warning("User service unavailable")
        return jsonify({"error": "User service unavailable"}), 503

    def _parse_json_payload() -> Optional[Dict[str, Any]]:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return None
        return payload

    @blueprint.route("/users", methods=["GET"])
    def get_user():
        service = _get_user_service()
        if service is None:
            return _service_unavailable()

        user_id = request.args.get("id")
        email = request.args.get("email")

        if (not user_id and not email) or (user_id and email):
            return jsonify({"error": "Query with exactly one of 'id' or 'email'"}), 400

        try:
            if user_id:
                user = service.get_user_profile(user_id)
            else:
                user = service.get_user_by_email(email)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            logger.exception("Failed to fetch user", extra={"user_id": user_id, "email": email})
            return jsonify({"error": "Failed to fetch user"}), 500

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": user})

    @blueprint.route("/users", methods=["POST"])
    def create_user():
        service = _get_user_service()
        if service is None:
            return _service_unavailable()

        payload = _parse_json_payload()
        if payload is None:
            return jsonify({"error": "Request body must be a JSON object"}), 400

        try:
            created = service.create_or_update_user(payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            logger.exception("Failed to create user")
            return jsonify({"error": "Failed to create user"}), 500

        if not created:
            return jsonify({"error": "Failed to create user"}), 500

        response = jsonify({"user": created})
        response.status_code = 201
        location_id = created.get("_id")
        if location_id:
            response.headers["Location"] = f"/api/users/{location_id}"
        return response

    @blueprint.route("/users/<user_id>/profile", methods=["PATCH"])
    def update_user_profile(user_id: str):
        service = _get_user_service()
        if service is None:
            return _service_unavailable()

        payload = _parse_json_payload()
        if payload is None:
            return jsonify({"error": "Request body must be a JSON object"}), 400

        try:
            updated = service.update_user_profile(user_id, payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            logger.exception("Failed to update user profile", extra={"user_id": user_id})
            return jsonify({"error": "Failed to update user profile"}), 500

        if not updated:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": updated})

    return blueprint
