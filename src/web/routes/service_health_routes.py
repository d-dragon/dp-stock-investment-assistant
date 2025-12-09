"""Health check and service status endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint, jsonify

if TYPE_CHECKING:
    from .shared_context import APIRouteContext


def create_health_blueprint(context: "APIRouteContext") -> Blueprint:
    """
    Create and return the health check blueprint.
    
    Provides endpoints for monitoring service health and availability.
    Minimal dependencies - only uses logger from context.
    """
    blueprint = Blueprint("health", __name__)
    logger = context.logger.getChild("health")

    @blueprint.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint for monitoring and load balancers.
        
        Returns:
            200 OK with status message
        """
        logger.debug("Health check requested")
        return jsonify({
            'status': 'healthy',
            'message': 'Stock Investment Assistant API is running'
        })

    return blueprint
