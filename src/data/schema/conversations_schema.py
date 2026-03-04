"""
Conversations Collection Schema - FR-3.1 Short-Term Memory

Purpose: Application-managed metadata for conversation state, separate from
LangGraph's internal checkpoint storage (agent_checkpoints collection).

Maps 1:1 with sessions collection via session_id = thread_id.

Reference: specs/spec-driven-development-pilot/data-model.md

Author: dp-stock-investment-assistant
Updated: 2025-01-27 (FR-3.1 Implementation)
"""

from typing import Dict, Any, List, Optional

# -----------------------------------------------------------------------------
# Schema Definition (FR-3.1 Spec)
# -----------------------------------------------------------------------------

CONVERSATIONS_SCHEMA: Dict[str, Any] = {
    "bsonType": "object",
    "required": ["session_id", "status", "created_at", "updated_at"],
    "properties": {
        "_id": {
            "bsonType": "objectId",
            "description": "MongoDB auto-generated ID"
        },
        "session_id": {
            "bsonType": "string",
            "description": "FK to sessions.id, also used as thread_id for LangGraph",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        },
        "workspace_id": {
            "bsonType": ["string", "null"],
            "description": "FK to workspaces.id for isolation verification"
        },
        "user_id": {
            "bsonType": ["string", "null"],
            "description": "FK to users.id for authorization"
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
                "bsonType": "string",
                "pattern": "^[A-Z]{1,5}$"
            },
            "description": "Stock symbols mentioned (e.g., ['AAPL', 'MSFT'])"
        },
        "session_assumptions": {
            "bsonType": ["string", "null"],
            "description": "User's stated preferences/assumptions for session"
        },
        "pinned_intent": {
            "bsonType": ["string", "null"],
            "description": "Pinned analysis intent (e.g., 'long-term value investing')"
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
        }
    },
    "additionalProperties": False
}

# -----------------------------------------------------------------------------
# Index Definitions (FR-3.1 Spec)
# -----------------------------------------------------------------------------

CONVERSATIONS_INDEXES: List[Dict[str, Any]] = [
    # Primary lookup: session → conversation (1:1)
    {
        "keys": [("session_id", 1)],
        "options": {
            "name": "idx_conversations_session_id_unique",
            "unique": True,
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
    """
    Return MongoDB validation configuration for conversations collection.
    
    Returns:
        Dict with validator, validationLevel, and validationAction settings.
    """
    return {
        "validator": {
            "$jsonSchema": CONVERSATIONS_SCHEMA
        },
        "validationLevel": "moderate",
        "validationAction": "warn"
    }


def get_conversations_indexes() -> List[Dict[str, Any]]:
    """
    Return index definitions for conversations collection.
    
    Returns:
        List of index configurations with keys and options.
    """
    return CONVERSATIONS_INDEXES


# -----------------------------------------------------------------------------
# Default Document Template (FR-3.1)
# -----------------------------------------------------------------------------

def get_default_conversation_document(
    session_id: str,
    *,
    workspace_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Return a default document template for new conversation.
    
    Args:
        session_id: The session UUID string (also used as thread_id)
        workspace_id: Optional workspace ID for isolation
        user_id: Optional user ID for authorization
    
    Returns:
        Dict with default field values for a new conversation.
    
    Note:
        session_id = thread_id per FR-3.1 spec (1:1 mapping, no translation)
    """
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc)
    
    return {
        "session_id": session_id,  # UUID string, same as thread_id
        "workspace_id": workspace_id,
        "user_id": user_id,
        "status": "active",
        "message_count": 0,
        "total_tokens": 0,
        "summary": None,
        "focused_symbols": [],
        "session_assumptions": None,
        "pinned_intent": None,
        "last_activity_at": now,
        "created_at": now,
        "updated_at": now,
        "archived_at": None
    }
