"""AI chat and configuration endpoints."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

from flask import Blueprint, Response, jsonify, request, stream_with_context

from services.exceptions import ArchivedSessionError

if TYPE_CHECKING:
    from .shared_context import APIRouteContext


# UUID v4 validation regex (8-4-4-4-12 format, version 4)
UUID_V4_REGEX = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
)

SSE_HEADERS = {
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'
}


def create_chat_blueprint(context: "APIRouteContext") -> Blueprint:
    """
    Create and return the AI chat blueprint.
    
    Provides endpoints for:
    - Chat interaction with AI agent (streaming and non-streaming)
    - Configuration retrieval (safe, non-sensitive settings)
    """
    blueprint = Blueprint("chat", __name__)

    # Unpack context dependencies
    agent = context.agent
    config = context.config
    logger = context.logger.getChild("chat")
    
    # Prefer chat_service if available (new pattern), fallback to functions (legacy)
    chat_service = context.chat_service
    if chat_service:
        stream_chat_response = chat_service.stream_chat_response
        extract_meta = chat_service.extract_meta
        strip_fallback_prefix = chat_service.strip_fallback_prefix
        get_timestamp = chat_service.get_timestamp
    else:
        # Legacy fallback for backward compatibility during migration
        stream_chat_response = context.stream_chat_response
        extract_meta = context.extract_meta
        strip_fallback_prefix = context.strip_fallback_prefix
        get_timestamp = context.get_timestamp

    @blueprint.route('/chat', methods=['POST'])
    def chat():
        """
        Chat endpoint for stock investment queries.
        
        Supports both streaming (SSE) and non-streaming responses.
        
        Request JSON:
            {
                "message": str (required),
                "provider": str (optional),
                "stream": bool (optional, default False),
                "session_id": str (optional, UUID v4 for session-aware memory)
            }
        
        Returns:
            - Streaming: SSE stream with incremental response chunks
            - Non-streaming: JSON with complete response and metadata
              If session_id provided, it's included in the response.
        """
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({'error': 'Message is required'}), 400

            user_message = data['message'].strip()
            if not user_message:
                return jsonify({'error': 'Message cannot be empty'}), 400

            provider_override = data.get('provider') or request.args.get('provider')
            stream = data.get('stream', False)
            
            # Extract and validate session_id (optional)
            session_id = data.get('session_id')
            if session_id is not None:
                if not isinstance(session_id, str) or not UUID_V4_REGEX.match(session_id):
                    return jsonify({'error': 'session_id must be a valid UUID v4'}), 400

            if stream:
                logger.info(f"Streaming chat request: {user_message[:50]}..." + 
                           (f" session={session_id}" if session_id else ""))
                return Response(
                    stream_with_context(stream_chat_response(
                        user_message, provider_override, session_id=session_id
                    )),
                    mimetype='text/event-stream',
                    headers=SSE_HEADERS
                )

            logger.info(f"Chat request: {user_message[:50]}..." + 
                       (f" session={session_id}" if session_id else ""))
            result = chat_service.process_chat_query(
                user_message, provider_override=provider_override, session_id=session_id
            )
            
            # Include session_id in response if provided
            if session_id:
                result['session_id'] = session_id

            return jsonify(result), 200
        except ArchivedSessionError as exc:
            logger.warning(f"Rejected message to archived session: {exc.session_id}")
            return jsonify({
                'error': 'Session is archived and cannot accept new messages',
                'code': 'SESSION_ARCHIVED',
                'session_id': exc.session_id
            }), 409
        except Exception as exc:
            logger.error(f"Error in chat endpoint: {exc}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500

    @blueprint.route('/config', methods=['GET'])
    def get_config():
        """
        Get safe configuration info (no sensitive data).
        
        Returns public configuration settings for frontend use.
        Never exposes API keys, passwords, or other secrets.
        
        Returns:
            JSON with model configuration and feature flags
        """
        logger.debug("Config request")
        model_cfg = config.get('model', {})
        legacy = config.get('openai', {})
        safe_config = {
            'model': {
                'provider': model_cfg.get('provider') or 'openai',
                'name': model_cfg.get('name') or legacy.get('model') or 'gpt-4'
            },
            'features': {
                'yahoo_finance': config.get('financial_apis', {}).get('yahoo_finance', {}).get('enabled', False),
                'alpha_vantage': config.get('financial_apis', {}).get('alpha_vantage', {}).get('enabled', False)
            }
        }
        return jsonify(safe_config)

    return blueprint
