"""HTTP API routes for the Stock Investment Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Optional, Tuple, TYPE_CHECKING, Dict

from flask import Blueprint, Response, jsonify, request, stream_with_context

if TYPE_CHECKING:
    from logging import Logger
    from flask import Flask
    from core.agent import StockAgent
    from core.model_registry import OpenAIModelRegistry

SSE_HEADERS = {
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'
}


@dataclass(frozen=True)
class APIRouteContext:
    app: "Flask"
    agent: "StockAgent"
    config: Mapping[str, Any]
    logger: "Logger"
    stream_chat_response: Callable[[str, Optional[str]], Iterable[str]]
    extract_meta: Callable[[str], Tuple[str, str, bool]]
    strip_fallback_prefix: Callable[[str], str]
    get_timestamp: Callable[[], str]
    model_registry: Optional["OpenAIModelRegistry"] = None
    set_active_model: Optional[Callable[[str, str], Dict[str, Any]]] = None


def _parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def create_api_blueprint(context: APIRouteContext) -> Blueprint:
    """Create and return the core REST API blueprint."""
    blueprint = Blueprint("api", __name__)

    agent = context.agent
    config = context.config
    logger = context.logger
    stream_chat_response = context.stream_chat_response
    extract_meta = context.extract_meta
    strip_fallback_prefix = context.strip_fallback_prefix
    get_timestamp = context.get_timestamp
    model_registry = context.model_registry
    set_active_model = context.set_active_model

    @blueprint.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'message': 'Stock Investment Assistant API is running'
        })

    @blueprint.route('/chat', methods=['POST'])
    def chat():
        """Chat endpoint for stock investment queries."""
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
                return Response(
                    stream_with_context(stream_chat_response(user_message, provider_override)),
                    mimetype='text/event-stream',
                    headers=SSE_HEADERS
                )

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
            logger.error(f"Error in chat endpoint: {exc}")
            return jsonify({'error': f'Internal server error: {exc}'}), 500

    @blueprint.route('/config', methods=['GET'])
    def get_config():
        """Get safe configuration info (no sensitive data)."""
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

    # Model management endpoints are now handled by models_routes.py to avoid duplication

    return blueprint
