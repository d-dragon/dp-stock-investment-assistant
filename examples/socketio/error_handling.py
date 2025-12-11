"""
Socket.IO Error Handling Patterns

Demonstrates comprehensive error handling for Socket.IO event handlers,
including validation, exception handling, and user-friendly error responses.

Reference: backend-python.instructions.md § WebSocket Layer > Error Handling
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
from flask_socketio import SocketIO, emit
import logging
from functools import wraps


# ============================================================================
# ERROR RESPONSE PATTERNS
# ============================================================================

def emit_error(message: str, event: str = "error", **kwargs) -> None:
    """
    Send error message to client via Socket.IO.
    
    Args:
        message: User-friendly error message
        event: Event name to emit (default: "error")
        **kwargs: Additional data to include in error response
    """
    error_data = {
        "message": message,
        "type": "error",
        **kwargs
    }
    emit(event, error_data)


def emit_validation_error(field: str, message: str) -> None:
    """Send validation error for specific field."""
    emit_error(
        message=f"Validation failed: {message}",
        field=field,
        validation_error=True
    )


def emit_server_error(operation: str) -> None:
    """Send generic server error (hide internal details)."""
    emit_error(
        message=f"Failed to {operation}. Please try again.",
        server_error=True
    )


# ============================================================================
# INPUT VALIDATION DECORATORS
# ============================================================================

def validate_required_fields(*required_fields: str):
    """
    Decorator to validate required fields in Socket.IO event data.
    
    Usage:
        @validate_required_fields("message", "user_id")
        def handle_chat(data):
            # data guaranteed to have 'message' and 'user_id'
            pass
    """
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(data: Dict[str, Any]) -> Any:
            # Check for missing fields
            missing = [field for field in required_fields if field not in data]
            
            if missing:
                emit_validation_error(
                    field=missing[0],
                    message=f"Required field '{missing[0]}' is missing"
                )
                return None
            
            # Check for empty string values
            empty = [
                field for field in required_fields
                if isinstance(data.get(field), str) and not data[field].strip()
            ]
            
            if empty:
                emit_validation_error(
                    field=empty[0],
                    message=f"Field '{empty[0]}' cannot be empty"
                )
                return None
            
            return handler(data)
        
        return wrapper
    return decorator


def validate_types(**field_types: type):
    """
    Decorator to validate field types in Socket.IO event data.
    
    Usage:
        @validate_types(message=str, quantity=int)
        def handle_trade(data):
            # message is str, quantity is int
            pass
    """
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(data: Dict[str, Any]) -> Any:
            for field, expected_type in field_types.items():
                if field in data and not isinstance(data[field], expected_type):
                    emit_validation_error(
                        field=field,
                        message=f"Field '{field}' must be {expected_type.__name__}, got {type(data[field]).__name__}"
                    )
                    return None
            
            return handler(data)
        
        return wrapper
    return decorator


# ============================================================================
# EXCEPTION HANDLING DECORATOR
# ============================================================================

def handle_socket_errors(operation: str, logger: Optional[logging.Logger] = None):
    """
    Decorator to catch and handle exceptions in Socket.IO handlers.
    
    Args:
        operation: User-facing operation name (e.g., "process message")
        logger: Optional logger for error logging
    """
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return handler(*args, **kwargs)
            
            except ValueError as e:
                # Validation or business logic errors (safe to show user)
                if logger:
                    logger.warning(f"{operation} validation error: {e}")
                emit_error(str(e), validation_error=True)
            
            except PermissionError as e:
                # Authorization errors
                if logger:
                    logger.warning(f"{operation} permission denied: {e}")
                emit_error("You don't have permission to perform this action", permission_error=True)
            
            except Exception as e:
                # Unexpected errors (log full details, hide from user)
                if logger:
                    logger.error(f"{operation} failed: {e}", exc_info=True)
                emit_server_error(operation)
        
        return wrapper
    return decorator


# ============================================================================
# EXAMPLE USAGE: CHAT EVENT HANDLERS WITH ERROR HANDLING
# ============================================================================

@dataclass(frozen=True)
class SocketIOContext:
    """Immutable context for Socket.IO event handlers."""
    socketio: SocketIO
    logger: logging.Logger


def register_chat_events_with_error_handling(context: SocketIOContext) -> None:
    """
    Register Socket.IO chat events with comprehensive error handling.
    
    Demonstrates:
    1. Input validation decorators
    2. Exception handling decorator
    3. User-friendly error responses
    4. Logging for debugging
    """
    socketio = context.socketio
    logger = context.logger.getChild("chat_events")
    
    
    @socketio.on('connect')
    def handle_connect():
        """Connection established - minimal error handling needed."""
        logger.info('Client connected')
        emit('status', {'message': 'Connected to chat server'})
    
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Disconnection - cleanup, minimal error handling."""
        logger.info('Client disconnected')
    
    
    @socketio.on('chat_message')
    @handle_socket_errors("send chat message", logger)
    @validate_required_fields("message")
    @validate_types(message=str)
    def handle_chat_message(data: Dict[str, Any]):
        """
        Handle chat message with full error handling.
        
        Validation:
        - 'message' field required and non-empty
        - 'message' must be string type
        
        Error handling:
        - Validation errors → emit_validation_error
        - Business logic errors → emit_error (user-friendly)
        - Unexpected errors → emit_server_error (generic)
        """
        message = data['message'].strip()
        
        # Business logic validation
        if len(message) > 1000:
            raise ValueError("Message too long (max 1000 characters)")
        
        # Simulate processing (could raise exceptions)
        response = process_chat_message(message)
        
        # Success response
        emit('chat_response', {'response': response})
    
    
    @socketio.on('trade_order')
    @handle_socket_errors("place trade order", logger)
    @validate_required_fields("symbol", "quantity")
    @validate_types(symbol=str, quantity=int)
    def handle_trade_order(data: Dict[str, Any]):
        """
        Handle trade order with validation and error handling.
        
        Demonstrates:
        - Multiple required fields
        - Type validation
        - Business logic validation
        - Permission checks
        """
        symbol = data['symbol'].upper()
        quantity = data['quantity']
        
        # Validate symbol format
        if not symbol.isalpha() or len(symbol) > 5:
            raise ValueError("Invalid stock symbol format")
        
        # Validate quantity
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if quantity > 10000:
            raise ValueError("Quantity exceeds maximum order size (10,000)")
        
        # Check user permissions (example)
        user_id = data.get('user_id')
        if not has_trading_permission(user_id):
            raise PermissionError("Trading not enabled for your account")
        
        # Place order (could raise exceptions)
        order_id = place_order(symbol, quantity)
        
        # Success response
        emit('trade_confirmation', {
            'status': 'success',
            'order_id': order_id,
            'symbol': symbol,
            'quantity': quantity
        })
    
    
    @socketio.on('subscribe_updates')
    @handle_socket_errors("subscribe to updates", logger)
    @validate_required_fields("symbols")
    @validate_types(symbols=list)
    def handle_subscribe(data: Dict[str, Any]):
        """
        Handle subscription with list validation.
        
        Demonstrates:
        - List type validation
        - List content validation
        - Array length validation
        """
        symbols = data['symbols']
        
        # Validate list content
        if not all(isinstance(s, str) for s in symbols):
            raise ValueError("All symbols must be strings")
        
        # Validate list length
        if len(symbols) == 0:
            raise ValueError("At least one symbol required")
        
        if len(symbols) > 50:
            raise ValueError("Maximum 50 symbols per subscription")
        
        # Subscribe (could raise exceptions)
        subscription_id = subscribe_to_symbols(symbols)
        
        # Success response
        emit('subscription_confirmed', {
            'subscription_id': subscription_id,
            'symbols': symbols,
            'count': len(symbols)
        })


# ============================================================================
# MOCK FUNCTIONS (simulate business logic)
# ============================================================================

def process_chat_message(message: str) -> str:
    """Mock chat processing."""
    if "error" in message.lower():
        raise RuntimeError("Simulated processing error")
    return f"Processed: {message}"


def has_trading_permission(user_id: Optional[str]) -> bool:
    """Mock permission check."""
    return user_id is not None and user_id != "restricted_user"


def place_order(symbol: str, quantity: int) -> str:
    """Mock order placement."""
    if symbol == "INVALID":
        raise RuntimeError("Order placement failed")
    return f"ORDER_{symbol}_{quantity}"


def subscribe_to_symbols(symbols: list) -> str:
    """Mock subscription."""
    if "ERROR" in symbols:
        raise RuntimeError("Subscription failed")
    return f"SUB_{len(symbols)}"


# ============================================================================
# ERROR HANDLING PATTERNS SUMMARY
# ============================================================================

def show_error_handling_patterns():
    """Display summary of Socket.IO error handling patterns."""
    
    print("=" * 60)
    print("SOCKET.IO ERROR HANDLING PATTERNS")
    print("=" * 60)
    
    patterns = [
        {
            "pattern": "Validation Decorators",
            "use_case": "Input validation before handler execution",
            "decorators": ["@validate_required_fields", "@validate_types"],
            "benefit": "Consistent validation, DRY principle"
        },
        {
            "pattern": "Exception Handling Decorator",
            "use_case": "Catch and handle exceptions uniformly",
            "decorators": ["@handle_socket_errors"],
            "benefit": "User-friendly errors, safe internal details"
        },
        {
            "pattern": "Error Emission Functions",
            "use_case": "Send structured error responses",
            "functions": ["emit_error", "emit_validation_error", "emit_server_error"],
            "benefit": "Consistent error format for frontend"
        },
        {
            "pattern": "Business Logic Validation",
            "use_case": "Domain-specific validation in handler",
            "example": "if len(message) > 1000: raise ValueError",
            "benefit": "Context-specific validation logic"
        },
    ]
    
    for i, item in enumerate(patterns, 1):
        print(f"\n{i}. {item['pattern']}")
        print(f"   Use Case: {item['use_case']}")
        if 'decorators' in item:
            print(f"   Decorators: {', '.join(item['decorators'])}")
        if 'functions' in item:
            print(f"   Functions: {', '.join(item['functions'])}")
        if 'example' in item:
            print(f"   Example: {item['example']}")
        print(f"   Benefit: {item['benefit']}")
    
    print("\n" + "=" * 60)
    print("BEST PRACTICES")
    print("=" * 60)
    
    best_practices = [
        "✅ Always validate required fields before processing",
        "✅ Emit user-friendly error messages (hide internal details)",
        "✅ Log exceptions with full context for debugging",
        "✅ Use decorators for reusable validation logic",
        "✅ Distinguish validation, permission, and server errors",
        "✅ Never expose stack traces to clients",
        "✅ Provide specific field names in validation errors",
        "✅ Use consistent error response format",
    ]
    
    for practice in best_practices:
        print(f"  {practice}")


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("Socket.IO Error Handling Patterns")
    print("=" * 60)
    print("\nThis module demonstrates comprehensive error handling for")
    print("Socket.IO event handlers with validation decorators,")
    print("exception handling, and user-friendly error responses.\n")
    
    show_error_handling_patterns()
    
    print("\n" + "=" * 60)
    print("USAGE EXAMPLE")
    print("=" * 60)
    print("""
# Register events with error handling
from flask_socketio import SocketIO
from flask import Flask
import logging

app = Flask(__name__)
socketio = SocketIO(app)
logger = logging.getLogger(__name__)

context = SocketIOContext(socketio=socketio, logger=logger)
register_chat_events_with_error_handling(context)

# Frontend error handling
socket.on('error', (data) => {
    if (data.validation_error) {
        showFieldError(data.field, data.message);
    } else if (data.server_error) {
        showToast('Server error: ' + data.message);
    } else {
        showToast('Error: ' + data.message);
    }
});
    """)
    
    print("\n📖 Reference: backend-python.instructions.md")
    print("   § WebSocket Layer (Socket.IO) > Error Handling Best Practices")
