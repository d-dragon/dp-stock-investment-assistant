"""Service layer exceptions.

Custom exceptions for service layer error handling.
These exceptions are designed to be caught by route handlers
and converted to appropriate HTTP responses.

References:
- ADR-001: Conversation Immutability
- FR-3.1.5: Session Recall on Disconnection
- STM Domain Model: conversation_id is the primary identity
"""


class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass


class ArchivedConversationError(ServiceError):
    """Raised when attempting to write to an archived conversation.
    
    Per ADR-001, archived conversations are immutable. Any attempt
    to add new messages to an archived conversation should raise this error.
    
    Route handlers should catch this and return 409 Conflict.
    
    Attributes:
        conversation_id: The archived conversation ID that was accessed
        message: Human-readable error message
    """
    
    def __init__(self, conversation_id: str, message: str = None):
        self.conversation_id = conversation_id
        self.message = message or f"Conversation {conversation_id} is archived and cannot accept new messages"
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return self.message


# Backward-compatible alias (will be removed in a future release)
ArchivedSessionError = ArchivedConversationError


class ConversationNotFoundError(ServiceError):
    """Raised when a conversation cannot be found.
    
    Route handlers should catch this and return 404 Not Found.
    """
    
    def __init__(self, conversation_id: str, message: str = None):
        self.conversation_id = conversation_id
        self.message = message or f"Conversation {conversation_id} not found"
        super().__init__(self.message)


# Backward-compatible alias
SessionNotFoundError = ConversationNotFoundError


class InvalidLifecycleTransitionError(ServiceError):
    """Raised when an invalid status transition is attempted.
    
    E.g., trying to transition from 'archived' to 'active'.
    Route handlers should catch this and return 409 Conflict.
    """
    
    def __init__(self, entity_type: str, entity_id: str, current_status: str, target_status: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.current_status = current_status
        self.target_status = target_status
        self.message = (
            f"Invalid {entity_type} transition: {current_status} → {target_status} "
            f"(id: {entity_id})"
        )
        super().__init__(self.message)
