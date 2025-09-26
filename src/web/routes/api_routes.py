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

    @blueprint.route('/models/openai', methods=['GET'])
    def list_openai_models():
        """Return cached or live OpenAI model catalog."""
        if not model_registry:
            return jsonify({'error': 'OpenAI model registry unavailable'}), 503
        refresh = _parse_bool(request.args.get('refresh'))
        try:
            payload = model_registry.get_supported_models(force_refresh=refresh)
            return jsonify(payload)
        except RuntimeError as exc:
            logger.error(f"OpenAI model registry unavailable: {exc}")
            return jsonify({'error': str(exc)}), 503
        except Exception as exc:
            logger.error(f"Failed to retrieve OpenAI models: {exc}")
            return jsonify({'error': f'Failed to retrieve OpenAI models: {exc}'}), 500

    @blueprint.route('/models/openai/refresh', methods=['POST'])
    def refresh_openai_models():
        """Force a refresh of the OpenAI model catalog."""
        if not model_registry:
            return jsonify({'error': 'OpenAI model registry unavailable'}), 503
        try:
            payload = model_registry.refresh_supported_models()
            payload['source'] = 'live'
            return jsonify(payload)
        except RuntimeError as exc:
            logger.error(f"Unable to refresh OpenAI models: {exc}")
            return jsonify({'error': str(exc)}), 503
        except Exception as exc:
            logger.error(f"Failed to refresh OpenAI models: {exc}")
            return jsonify({'error': f'Failed to refresh OpenAI models: {exc}'}), 500

    @blueprint.route('/models/openai/default', methods=['PUT'])
    def set_default_openai_model():
        """Set the default OpenAI model used by the assistant."""
        if not model_registry or not set_active_model:
            return jsonify({'error': 'OpenAI model management unavailable'}), 503

        payload = request.get_json(silent=True) or {}
        model_name = payload.get('model') if isinstance(payload, dict) else None
        if not isinstance(model_name, str) or not model_name.strip():
            return jsonify({'error': 'model is required'}), 400
        model_name = model_name.strip()

        try:
            supported = model_registry.is_supported_model(model_name)
        except RuntimeError as exc:
            logger.error(f"OpenAI model validation unavailable: {exc}")
            return jsonify({'error': str(exc)}), 503
        except Exception as exc:
            logger.error(f"Failed to validate OpenAI model '{model_name}': {exc}")
            return jsonify({'error': f"Failed to validate model '{model_name}': {exc}"}), 500

        if not supported:
            return jsonify({'error': f"Model '{model_name}' is not supported"}), 400

        try:
            result = set_active_model('openai', model_name)
        except Exception as exc:
            logger.error(f"Failed to set active model '{model_name}': {exc}")
            return jsonify({'error': f"Failed to set active model: {exc}"}), 500

        model_registry.record_active_model(model_name)
        result['active_model'] = model_registry.get_active_model()
        return jsonify(result)

    return blueprint
