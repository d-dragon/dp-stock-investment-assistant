"""
Socket.IO Chat Events Registration Pattern
===========================================

Demonstrates Socket.IO event handler registration using frozen context pattern.

Reference: backend-python.instructions.md § WebSocket Layer (Socket.IO)
Related: backend-python.instructions.md § Flask API Patterns (context pattern)
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping, Any
from flask import Flask
from flask_socketio import SocketIO, emit
import logging

if TYPE_CHECKING:
    from core.agent import StockAgent


# ============================================================================
# CONTEXT: Immutable Dependency Injection
# ============================================================================

@dataclass(frozen=True)
class SocketIOContext:
    """
    Immutable context for Socket.IO event handlers.
    
    Similar to APIRouteContext, provides dependencies to event handlers
    through closure pattern to prevent global state and mutation bugs.
    
    Attributes:
        socketio: Flask-SocketIO instance
        agent: AI agent for processing queries
        config: Application configuration (immutable Mapping)
        logger: Logger instance for event handlers
    """
    socketio: SocketIO
    agent: "StockAgent"
    config: Mapping[str, Any]
    logger: logging.Logger


# ============================================================================
# EVENT HANDLERS: Registration Function Pattern
# ============================================================================

def register_chat_events(context: SocketIOContext) -> None:
    """
    Register Socket.IO event handlers for chat functionality.
    
    Pattern Benefits:
    - Dependencies injected via closure (context)
    - Handlers can't mutate context (frozen=True)
    - All handlers share same logger hierarchy
    - Easy to test with mock context
    
    Args:
        context: Immutable SocketIOContext with dependencies
    
    Event Flow:
        Client                          Server
          |                               |
          |--- connect ------------------→|
          |←-- status (connected) --------|
          |                               |
          |--- chat_message -------------→|
          |     {"message": "Price of AAPL"}
          |                               |
          |←-- chat_response -------------|
          |     {"response": "AAPL is..."}
          |                               |
          |--- disconnect ---------------→|
          |                               |
    """
    socketio = context.socketio
    agent = context.agent
    logger = context.logger
    
    # Connection Events
    # -------------------------------------------------------------------------
    
    @socketio.on('connect')
    def handle_connect():
        """
        Handle client connection.
        
        Emits 'status' event to confirm connection established.
        """
        logger.info('Client connected')
        emit('status', {
            'message': 'Connected to stock assistant',
            'timestamp': _get_timestamp()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info('Client disconnected')
    
    # Chat Events
    # -------------------------------------------------------------------------
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        """
        Handle incoming chat message from client.
        
        Args:
            data: Dict with 'message' field
        
        Emits:
            - 'chat_response': On successful processing
            - 'error': On validation or processing failure
        
        Example:
            Client sends:  {"message": "What's the price of AAPL?"}
            Server emits:  {"response": "AAPL is trading at $150.25"}
        """
        try:
            # Validate input
            if not isinstance(data, dict):
                emit('error', {'message': 'Invalid data format'})
                return
            
            message = data.get('message', '').strip()
            
            if not message:
                emit('error', {'message': 'Message cannot be empty'})
                return
            
            # Log request
            logger.info(f"Processing chat message: {message[:50]}...")
            
            # Process query with agent
            response = agent.process_query(message)
            
            # Emit response
            emit('chat_response', {
                'response': response,
                'timestamp': _get_timestamp()
            })
            
            logger.info(f"Chat response sent ({len(response)} chars)")
        
        except Exception as exc:
            logger.error(f"Chat processing error: {exc}", exc_info=True)
            emit('error', {
                'message': 'Failed to process message. Please try again.',
                'timestamp': _get_timestamp()
            })
    
    # Streaming Events
    # -------------------------------------------------------------------------
    
    @socketio.on('chat_stream_start')
    def handle_chat_stream_start(data):
        """
        Handle streaming chat request.
        
        Emits multiple 'chat_chunk' events as response streams.
        Final 'chat_stream_end' signals completion.
        
        Args:
            data: Dict with 'message' field
        
        Example:
            Client sends:  {"message": "Latest news on AAPL"}
            Server emits:  {"chunk": "Apple"} (chat_chunk)
                          {"chunk": " Inc."} (chat_chunk)
                          {"chunk": " has"} (chat_chunk)
                          ...
                          {} (chat_stream_end)
        """
        try:
            message = data.get('message', '').strip()
            
            if not message:
                emit('error', {'message': 'Message cannot be empty'})
                return
            
            logger.info(f"Starting streaming response for: {message[:50]}...")
            
            # Stream response chunks
            for chunk in agent.process_query_streaming(message):
                emit('chat_chunk', {'chunk': chunk})
            
            # Signal completion
            emit('chat_stream_end', {'timestamp': _get_timestamp()})
            
            logger.info("Streaming response completed")
        
        except Exception as exc:
            logger.error(f"Streaming error: {exc}", exc_info=True)
            emit('error', {'message': 'Streaming interrupted'})


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_timestamp():
    """Get current timestamp in ISO format."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# ============================================================================
# REGISTRATION: App Factory Integration
# ============================================================================

def create_app_with_socketio(agent, config):
    """
    Example Flask app factory with Socket.IO integration.
    
    Used in: src/web/api_server.py
    
    Args:
        agent: StockAgent instance
        config: Application configuration dict
    
    Returns:
        Tuple of (Flask app, SocketIO instance)
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.get('secret_key', 'dev-secret-key')
    
    # Initialize Socket.IO
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",  # Configure for production
        async_mode='eventlet'      # Or 'gevent', 'threading'
    )
    
    # Create context
    logger = logging.getLogger(__name__)
    context = SocketIOContext(
        socketio=socketio,
        agent=agent,
        config=config,
        logger=logger
    )
    
    # Register events
    register_chat_events(context)
    
    # Optional: Register additional event modules
    # from web.sockets.trading_events import register_trading_events
    # register_trading_events(context)
    
    return app, socketio


# ============================================================================
# ERROR HANDLING: Best Practices
# ============================================================================

def register_events_with_comprehensive_error_handling(context: SocketIOContext):
    """
    Example showing comprehensive error handling patterns.
    
    Key Principles:
    1. Never let exceptions crash the Socket.IO server
    2. Always emit 'error' event on failure
    3. Log with context (user ID, message preview, error details)
    4. Distinguish client errors (400) from server errors (500)
    """
    socketio = context.socketio
    agent = context.agent
    logger = context.logger
    
    @socketio.on('trade_order')
    def handle_trade_order(data):
        """Example: Trade order with validation and error handling."""
        try:
            # 1. Validate schema
            if not isinstance(data, dict):
                emit('error', {
                    'code': 'INVALID_FORMAT',
                    'message': 'Request must be a JSON object'
                })
                return
            
            # 2. Validate required fields
            required_fields = ['symbol', 'quantity', 'order_type']
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                emit('error', {
                    'code': 'MISSING_FIELDS',
                    'message': f"Missing required fields: {', '.join(missing)}"
                })
                return
            
            # 3. Validate business logic
            if data['quantity'] <= 0:
                emit('error', {
                    'code': 'INVALID_QUANTITY',
                    'message': 'Quantity must be positive'
                })
                return
            
            # 4. Process order (with error handling)
            logger.info(f"Processing trade: {data['symbol']} x {data['quantity']}")
            
            # Simulated processing
            order_id = _process_trade_order(data)
            
            emit('trade_confirmation', {
                'order_id': order_id,
                'status': 'pending',
                'timestamp': _get_timestamp()
            })
        
        except ValueError as e:
            # Client error (400-level)
            logger.warning(f"Trade validation error: {e}")
            emit('error', {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            })
        
        except Exception as e:
            # Server error (500-level)
            logger.error(f"Trade processing error: {e}", exc_info=True)
            emit('error', {
                'code': 'SERVER_ERROR',
                'message': 'Order processing failed. Please try again.'
            })


def _process_trade_order(data):
    """Simulated trade processing."""
    import uuid
    return str(uuid.uuid4())


# ============================================================================
# TESTING: Mock Context Pattern
# ============================================================================

def create_test_context():
    """
    Create mock SocketIOContext for testing.
    
    Used in: tests/test_chat_events.py
    """
    from unittest.mock import MagicMock
    
    mock_socketio = MagicMock()
    mock_agent = MagicMock()
    mock_agent.process_query.return_value = "Test response"
    mock_agent.process_query_streaming.return_value = iter(["chunk1", "chunk2"])
    
    config = {'secret_key': 'test-key'}
    logger = logging.getLogger('test')
    
    return SocketIOContext(
        socketio=mock_socketio,
        agent=mock_agent,
        config=config,
        logger=logger
    )


# ============================================================================
# FRONTEND INTEGRATION: Event Names Configuration
# ============================================================================

def show_frontend_config():
    """
    Event names should be centralized in frontend config.
    
    File: frontend/src/config.ts
    """
    typescript_config = """
    export const API_CONFIG = {
        WEBSOCKET: {
            URL: process.env.REACT_APP_WS_URL || 'http://localhost:5000',
            EVENTS: {
                // Connection
                CONNECT: 'connect',
                DISCONNECT: 'disconnect',
                STATUS: 'status',
                
                // Chat
                CHAT_MESSAGE: 'chat_message',
                CHAT_RESPONSE: 'chat_response',
                CHAT_STREAM_START: 'chat_stream_start',
                CHAT_CHUNK: 'chat_chunk',
                CHAT_STREAM_END: 'chat_stream_end',
                
                // Errors
                ERROR: 'error',
                
                // Trading (example)
                TRADE_ORDER: 'trade_order',
                TRADE_CONFIRMATION: 'trade_confirmation',
            }
        }
    };
    """
    print("Frontend Configuration (TypeScript):")
    print(typescript_config)


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    print("=" * 80)
    print("Socket.IO Chat Events Registration Pattern")
    print("=" * 80)
    
    print("\n1. Creating Mock Context:")
    print("-" * 80)
    test_context = create_test_context()
    print(f"   SocketIO: {test_context.socketio}")
    print(f"   Agent: {test_context.agent}")
    print(f"   Config: {test_context.config}")
    
    print("\n2. Registering Event Handlers:")
    print("-" * 80)
    register_chat_events(test_context)
    print("   ✅ Connected: connect → emit 'status'")
    print("   ✅ Disconnected: disconnect → log event")
    print("   ✅ Chat Message: chat_message → agent.process_query() → emit 'chat_response'")
    print("   ✅ Streaming: chat_stream_start → agent.process_query_streaming() → emit 'chat_chunk'")
    
    print("\n3. Event Flow Example:")
    print("-" * 80)
    print("   Client: socket.emit('chat_message', {message: 'Price of AAPL'})")
    print("   Server: agent.process_query('Price of AAPL')")
    print("   Server: socket.emit('chat_response', {response: 'AAPL is $150.25'})")
    
    print("\n4. Error Handling Example:")
    print("-" * 80)
    print("   Client: socket.emit('chat_message', {})  # Missing 'message'")
    print("   Server: socket.emit('error', {message: 'Message cannot be empty'})")
    
    print("\n5. Frontend Configuration:")
    print("-" * 80)
    show_frontend_config()
    
    print("\n" + "=" * 80)
    print("Key Patterns:")
    print("=" * 80)
    print("✅ Use frozen dataclass for context (prevents mutation)")
    print("✅ Register all handlers in single function (register_chat_events)")
    print("✅ Always emit 'error' event on failures (never silent)")
    print("✅ Log with context (message preview, error details)")
    print("✅ Centralize event names in frontend config")
    print("✅ Clean up listeners on client unmount (useEffect return)")
    print("=" * 80)
