"""Socket.IO chat events for the Stock Investment Assistant."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Tuple, TYPE_CHECKING

from flask_socketio import SocketIO, emit

# UUID v4 regex pattern for conversation_id validation
UUID_V4_REGEX = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
)

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
        """
        Handle real-time chat messages.
        
        Accepts optional conversation_id (UUID v4) for conversation memory.
        """
        try:
            payload = data or {}
            message = payload.get('message', '').strip()
            provider_override = payload.get('provider')
            conversation_id = payload.get('conversation_id')
            
            if not message:
                emit('error', {'message': 'Message cannot be empty'})
                return

            # Validate conversation_id format if provided
            if conversation_id is not None:
                if not isinstance(conversation_id, str) or not UUID_V4_REGEX.match(conversation_id):
                    emit('error', {'message': 'conversation_id must be a valid UUID v4'})
                    return

            logger.debug(f"Processing chat message with conversation_id={conversation_id}")
            raw_response = agent.process_query(message, provider=provider_override, conversation_id=conversation_id)
            provider_used, model_used, fallback_flag = extract_meta(raw_response)
            response_clean = strip_fallback_prefix(raw_response)

            response_data = {
                'response': response_clean,
                'provider': provider_used,
                'model': model_used,
                'fallback': fallback_flag,
                'timestamp': get_timestamp()
            }
            
            # Echo conversation_id back if provided
            if conversation_id:
                response_data['conversation_id'] = conversation_id

            emit('chat_response', response_data)
        except Exception as exc:
            import traceback
            logger.error(f"Error in chat_message handler: {exc}\n{traceback.format_exc()}")
            emit('error', {'message': 'An error occurred while processing your message. Please try again later.'})
