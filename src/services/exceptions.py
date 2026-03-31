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

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def to_dict(self) -> dict:
        """Serialize to the standard management error envelope body."""
        return {"message": str(self), "code": self.error_code}


class ArchivedConversationError(ServiceError):
    """Raised when attempting to write to an archived conversation.
    
    Per ADR-001, archived conversations are immutable. Any attempt
    to add new messages to an archived conversation should raise this error.
    
    Route handlers should catch this and return 409 Conflict.
    
    Attributes:
        conversation_id: The archived conversation ID that was accessed
        message: Human-readable error message
    """

    status_code = 409
    error_code = "CONFLICT"
    
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

    status_code = 404
    error_code = "NOT_FOUND"
    
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

    status_code = 409
    error_code = "CONFLICT"
    
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


# ---------------------------------------------------------------------------
# Management lifecycle and validation errors (Phase C-E)
# ---------------------------------------------------------------------------

class EntityNotFoundError(ServiceError):
    """Raised when a workspace, session, or conversation cannot be found.

    Route handlers should catch this and return 404 Not Found.
    """

    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, entity_type: str, entity_id: str, message: str = None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.message = message or f"{entity_type} {entity_id} not found"
        super().__init__(self.message)


class ParentNotFoundError(ServiceError):
    """Raised when a nested resource's parent does not exist.

    E.g., creating a session under a non-existent workspace.
    Route handlers should catch this and return 404 Not Found.
    """

    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, parent_type: str, parent_id: str, child_type: str, message: str = None):
        self.parent_type = parent_type
        self.parent_id = parent_id
        self.child_type = child_type
        self.message = message or (
            f"Cannot create {child_type}: parent {parent_type} {parent_id} not found"
        )
        super().__init__(self.message)


class OwnershipViolationError(ServiceError):
    """Raised when a user attempts to access a resource they do not own.

    Route handlers should catch this and return 403 Forbidden.
    The error intentionally avoids leaking whether the resource exists
    under a different owner.
    """

    status_code = 403
    error_code = "FORBIDDEN"

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        expected_owner: str,
        actual_owner: str,
        message: str = None,
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.expected_owner = expected_owner
        self.actual_owner = actual_owner
        self.message = message or f"Access denied for {entity_type} {entity_id}"
        super().__init__(self.message)


class StaleEntityError(ServiceError):
    """Raised on 409-style conflicts such as race conditions or stale updates.

    Route handlers should catch this and return 409 Conflict.
    """

    status_code = 409
    error_code = "CONFLICT"

    def __init__(self, entity_type: str, entity_id: str, message: str = None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.message = message or f"{entity_type} {entity_id} has been modified concurrently"
        super().__init__(self.message)


class ValidationError(ServiceError):
    """Raised for 400-level request validation failures.

    Route handlers should catch this and return 400 Bad Request.
    """

    status_code = 400
    error_code = "VALIDATION_ERROR"

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error on '{field}': {message}")
