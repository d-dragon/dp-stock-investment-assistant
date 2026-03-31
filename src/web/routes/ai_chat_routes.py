"""AI chat and configuration endpoints."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

from flask import Blueprint, Response, jsonify, request, stream_with_context

from services.exceptions import ArchivedConversationError

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
                "conversation_id": str (optional, UUID v4 for conversation-aware memory)
            }
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
            
            # Extract conversation identifier (optional).
            # Backward compatibility: accept deprecated `session_id` alias.
            # Migration-window dual-path (FR-D15 / SC-012): legacy stateless
            # requests omit this field entirely; ChatService guard clauses
            # skip conversation validation/metadata when None.
            conversation_id = data.get('conversation_id')
            if conversation_id is None and data.get('session_id') is not None:
                conversation_id = data.get('session_id')
                logger.info("chat.request using deprecated session_id alias")
            if conversation_id is not None:
                if not isinstance(conversation_id, str) or not UUID_V4_REGEX.match(conversation_id):
                    return jsonify({'error': 'conversation_id must be a valid UUID v4'}), 400

            if stream:
                logger.info(f"Streaming chat request: {user_message[:50]}..." + 
                           (f" conversation={conversation_id}" if conversation_id else ""))
                return Response(
                    stream_with_context(stream_chat_response(
                        user_message, provider_override, conversation_id=conversation_id
                    )),
                    mimetype='text/event-stream',
                    headers=SSE_HEADERS
                )

            logger.info(f"Chat request: {user_message[:50]}..." + 
                       (f" conversation={conversation_id}" if conversation_id else ""))
            result = chat_service.process_chat_query(
                user_message, provider_override=provider_override, conversation_id=conversation_id
            )
            
            if conversation_id:
                result['conversation_id'] = conversation_id

            return jsonify(result), 200
        except ArchivedConversationError as exc:
            logger.warning(f"Rejected message to archived conversation: {exc.conversation_id}")
            return jsonify({
                'error': 'Conversation is archived and cannot accept new messages',
                'code': 'CONVERSATION_ARCHIVED',
                'conversation_id': exc.conversation_id
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
