"""
Conversations Collection Schema - STM Domain Model Refactor

Purpose: Application-managed metadata for conversation state, separate from
LangGraph's internal checkpoint storage (agent_checkpoints collection).

Each conversation maps 1:1 to a LangGraph checkpoint thread via
conversation_id == thread_id. Multiple conversations can exist under
one session (session_id is a non-unique FK).

Reference: specs/agent-session-with-stm-wiring/spec.md (FR-002, FR-005)
"""

from typing import Dict, Any, List, Optional

# -----------------------------------------------------------------------------
# Schema Definition
# -----------------------------------------------------------------------------

CONVERSATIONS_SCHEMA: Dict[str, Any] = {
    "bsonType": "object",
    "required": [
        "conversation_id", "thread_id", "session_id",
        "workspace_id", "user_id", "status", "created_at", "updated_at"
    ],
    "properties": {
        "_id": {
            "bsonType": "objectId",
            "description": "MongoDB auto-generated ID"
        },
        "conversation_id": {
            "bsonType": "string",
            "description": "Primary business key (UUID v4)",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        },
        "thread_id": {
            "bsonType": "string",
            "description": "LangGraph checkpoint thread_id (== conversation_id)"
        },
        "session_id": {
            "bsonType": "string",
            "description": "FK to sessions.session_id (non-unique, 1:N)",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        },
        "workspace_id": {
            "bsonType": "string",
            "description": "FK to workspaces._id for isolation verification"
        },
        "user_id": {
            "bsonType": "string",
            "description": "FK to users._id for authorization"
        },
        "status": {
            "enum": ["active", "summarized", "archived"],
            "description": "Conversation lifecycle state"
        },
        "message_count": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Number of human messages exchanged"
        },
        "total_tokens": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Estimated token count for summarization trigger"
        },
        "summary": {
            "bsonType": ["string", "null"],
            "maxLength": 500,
            "description": "LLM-generated summary when status=summarized"
        },
        "focused_symbols": {
            "bsonType": "array",
            "items": {
                "bsonType": "string"
            },
            "description": "Thread-local symbol refinement (inherits from session, overrides replace)"
        },
        "context_overrides": {
            "bsonType": ["object", "null"],
            "description": "Thread-local refinement of inherited session context (shallow key overwrite)"
        },
        "conversation_intent": {
            "bsonType": ["string", "null"],
            "description": "Conversation-specific intent override"
        },
        "last_activity_at": {
            "bsonType": "date",
            "description": "Last user interaction timestamp"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Conversation creation timestamp"
        },
        "updated_at": {
            "bsonType": "date",
            "description": "Last update timestamp"
        },
        "archived_at": {
            "bsonType": ["date", "null"],
            "description": "Archive timestamp if status=archived"
        },
        "archive_reason": {
            "bsonType": ["string", "null"],
            "enum": ["user_closed", "inactivity", "workspace_archived", "session_archived", None],
            "description": "Reason for archival"
        }
    },
    "additionalProperties": False
}

# -----------------------------------------------------------------------------
# Index Definitions
# -----------------------------------------------------------------------------

CONVERSATIONS_INDEXES: List[Dict[str, Any]] = [
    # Primary lookup: conversation_id (unique business key)
    {
        "keys": [("conversation_id", 1)],
        "options": {
            "name": "idx_conversations_conversation_id",
            "unique": True,
            "background": True
        }
    },
    # LangGraph thread mapping (1:1 with conversation_id)
    {
        "keys": [("thread_id", 1)],
        "options": {
            "name": "idx_conversations_thread_id",
            "unique": True,
            "background": True
        }
    },
    # Parent session lookup (non-unique FK, 1:N)
    {
        "keys": [("session_id", 1)],
        "options": {
            "name": "idx_conversations_session_id",
            "background": True
        }
    },
    # Compound index for hierarchy + status queries
    {
        "keys": [("workspace_id", 1), ("session_id", 1), ("status", 1)],
        "options": {
            "name": "idx_conversations_hierarchy_status",
            "background": True
        }
    },
    # Authorization queries
    {
        "keys": [("user_id", 1), ("status", 1)],
        "options": {
            "name": "idx_conversations_user_status",
            "background": True
        }
    },
    # Workspace isolation
    {
        "keys": [("workspace_id", 1), ("status", 1)],
        "options": {
            "name": "idx_conversations_workspace_status",
            "background": True
        }
    },
    # Archive job queries
    {
        "keys": [("status", 1), ("last_activity_at", 1)],
        "options": {
            "name": "idx_conversations_status_activity",
            "background": True
        }
    },
    # Symbol lookup
    {
        "keys": [("focused_symbols", 1)],
        "options": {
            "name": "idx_conversations_symbols",
            "background": True
        }
    }
]

# -----------------------------------------------------------------------------
# Validation Config Helper
# -----------------------------------------------------------------------------

def get_conversations_validation() -> Dict[str, Any]:
    """Return MongoDB validation configuration for conversations collection."""
    return {
        "validator": {
            "$jsonSchema": CONVERSATIONS_SCHEMA
        },
        "validationLevel": "moderate",
        "validationAction": "warn"
    }


def get_conversations_indexes() -> List[Dict[str, Any]]:
    """Return index definitions for conversations collection."""
    return CONVERSATIONS_INDEXES


# -----------------------------------------------------------------------------
# Default Document Template
# -----------------------------------------------------------------------------

def get_default_conversation_document(
    conversation_id: str,
    thread_id: str,
    session_id: str,
    *,
    workspace_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """
    Return a default document template for new conversation.
    
    Args:
        conversation_id: The conversation UUID string (primary business key)
        thread_id: LangGraph thread_id (must equal conversation_id)
        session_id: Parent session UUID string
        workspace_id: Workspace ID for isolation
        user_id: User ID for authorization
    
    Returns:
        Dict with default field values for a new conversation.
    """
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc)
    
    return {
        "conversation_id": conversation_id,
        "thread_id": thread_id,
        "session_id": session_id,
        "workspace_id": workspace_id,
        "user_id": user_id,
        "status": "active",
        "message_count": 0,
        "total_tokens": 0,
        "summary": None,
        "focused_symbols": [],
        "context_overrides": None,
        "conversation_intent": None,
        "last_activity_at": now,
        "created_at": now,
        "updated_at": now,
        "archived_at": None,
        "archive_reason": None
    }
