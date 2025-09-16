"""Socket.IO chat events for the Stock Investment Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Tuple, TYPE_CHECKING

from flask_socketio import SocketIO, emit

if TYPE_CHECKING:
    from logging import Logger
    from core.agent import StockAgent


@dataclass(frozen=True)
class SocketIOContext:
    socketio: SocketIO
    agent: "StockAgent"
    config: Mapping[str, Any]
    logger: "Logger"
    extract_meta: Callable[[str], Tuple[str, str, bool]]
    strip_fallback_prefix: Callable[[str], str]
    get_timestamp: Callable[[], str]


def register_chat_events(context: SocketIOContext) -> None:
    """Register chat-related Socket.IO event handlers."""
    socketio = context.socketio
    agent = context.agent
    logger = context.logger
    extract_meta = context.extract_meta
    strip_fallback_prefix = context.strip_fallback_prefix
    get_timestamp = context.get_timestamp

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info('Client connected')
        emit('status', {'message': 'Connected to Stock Investment Assistant'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info('Client disconnected')

    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle real-time chat messages."""
        try:
            payload = data or {}
            message = payload.get('message', '').strip()
            provider_override = payload.get('provider')
            if not message:
                emit('error', {'message': 'Message cannot be empty'})
                return

            raw_response = agent.process_query(message, provider=provider_override)
            provider_used, model_used, fallback_flag = extract_meta(raw_response)
            response_clean = strip_fallback_prefix(raw_response)

            emit('chat_response', {
                'response': response_clean,
                'provider': provider_used,
                'model': model_used,
                'fallback': fallback_flag,
                'timestamp': get_timestamp()
            })
        except Exception as exc:
            import traceback
            logger.error(f"Error in chat_message handler: {exc}\n{traceback.format_exc()}")
            emit('error', {'message': 'An error occurred while processing your message. Please try again later.'})
