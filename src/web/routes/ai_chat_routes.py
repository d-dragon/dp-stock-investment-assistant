"""AI chat and configuration endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from flask import Blueprint, Response, jsonify, request, stream_with_context

if TYPE_CHECKING:
    from .shared_context import APIRouteContext


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
                "stream": bool (optional, default False)
            }
        
        Returns:
            - Streaming: SSE stream with incremental response chunks
            - Non-streaming: JSON with complete response and metadata
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

            if stream:
                logger.info(f"Streaming chat request: {user_message[:50]}...")
                return Response(
                    stream_with_context(stream_chat_response(user_message, provider_override)),
                    mimetype='text/event-stream',
                    headers=SSE_HEADERS
                )

            logger.info(f"Chat request: {user_message[:50]}...")
            raw_response = agent.process_query(user_message, provider=provider_override)
            provider_used, model_used, fallback_flag = extract_meta(raw_response)
            response_clean = strip_fallback_prefix(raw_response)

            return jsonify({
                'response': response_clean,
                'provider': provider_used,
                'model': model_used,
                'fallback': fallback_flag,
                'timestamp': get_timestamp()
            })
        except Exception as exc:
            logger.error(f"Error in chat endpoint: {exc}", exc_info=True)
            return jsonify({'error': f'Internal server error: {exc}'}), 500

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
