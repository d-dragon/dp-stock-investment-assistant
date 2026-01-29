"""Service layer exceptions.

Custom exceptions for service layer error handling.
These exceptions are designed to be caught by route handlers
and converted to appropriate HTTP responses.

References:
- ADR-001: Conversation Immutability
- FR-3.1.5: Session Recall on Disconnection
"""


class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass


class ArchivedSessionError(ServiceError):
    """Raised when attempting to use an archived session for writes.
    
    Per ADR-001, archived conversations are immutable. Any attempt
    to add new messages to an archived session should raise this error.
    
    Route handlers should catch this and return 409 Conflict.
    
    Attributes:
        session_id: The archived session ID that was accessed
        message: Human-readable error message
    """
    
    def __init__(self, session_id: str, message: str = None):
        self.session_id = session_id
        self.message = message or f"Session {session_id} is archived and cannot accept new messages"
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return self.message


class SessionNotFoundError(ServiceError):
    """Raised when a session cannot be found.
    
    This is different from ArchivedSessionError - this indicates
    the session doesn't exist at all.
    
    Route handlers should catch this and return 404 Not Found.
    """
    
    def __init__(self, session_id: str, message: str = None):
        self.session_id = session_id
        self.message = message or f"Session {session_id} not found"
        super().__init__(self.message)
