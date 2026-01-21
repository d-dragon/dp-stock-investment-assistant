"""
Conversations Collection Schema

Purpose: Track conversation metadata and memory state for LangChain agent.
Maps 1:1 with sessions collection, storing memory-specific data.

Reference: docs/langchain-agent/AGENT_MEMORY_TECHNICAL_DESIGN.md

Author: dp-stock-investment-assistant
Created: 2025-01-21
"""

from typing import Dict, Any, List

# -----------------------------------------------------------------------------
# Schema Definition
# -----------------------------------------------------------------------------

CONVERSATIONS_SCHEMA: Dict[str, Any] = {
    "bsonType": "object",
    "required": ["session_id", "thread_id", "status", "created_at"],
    "properties": {
        "_id": {
            "bsonType": "objectId",
            "description": "Unique identifier for the conversation record"
        },
        "session_id": {
            "bsonType": "objectId",
            "description": "Reference to sessions collection (1:1 mapping)"
        },
        "thread_id": {
            "bsonType": "string",
            "description": "LangGraph thread identifier (string of session_id)"
        },
        "status": {
            "bsonType": "string",
            "enum": ["active", "summarized", "archived"],
            "description": "Conversation memory status"
        },
        "message_count": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Total messages in conversation"
        },
        "total_tokens": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Estimated token count for memory management"
        },
        "summary": {
            "bsonType": ["string", "null"],
            "description": "LLM-generated summary when conversation is long"
        },
        "summary_up_to_message": {
            "bsonType": ["int", "null"],
            "minimum": 0,
            "description": "Message index where summary ends (exclusive)"
        },
        "last_activity_at": {
            "bsonType": "date",
            "description": "Timestamp of last message"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        },
        "updated_at": {
            "bsonType": ["date", "null"],
            "description": "Last update timestamp"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Additional metadata (model used, tool calls count, etc.)",
            "properties": {
                "model_name": {
                    "bsonType": "string",
                    "description": "Primary model used in conversation"
                },
                "tool_calls_count": {
                    "bsonType": "int",
                    "description": "Number of tool invocations"
                },
                "last_model_used": {
                    "bsonType": "string",
                    "description": "Most recent model used"
                },
                "symbols_discussed": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"},
                    "description": "Stock symbols mentioned in conversation"
                }
            }
        }
    }
}

# -----------------------------------------------------------------------------
# Index Definitions
# -----------------------------------------------------------------------------

CONVERSATIONS_INDEXES: List[Dict[str, Any]] = [
    {
        "keys": [("session_id", 1)],
        "options": {
            "name": "idx_conversations_session",
            "unique": True,
            "background": True
        }
    },
    {
        "keys": [("thread_id", 1)],
        "options": {
            "name": "idx_conversations_thread",
            "unique": True,
            "background": True
        }
    },
    {
        "keys": [("status", 1), ("last_activity_at", -1)],
        "options": {
            "name": "idx_conversations_status_activity",
            "background": True
        }
    },
    {
        "keys": [("created_at", 1)],
        "options": {
            "name": "idx_conversations_created",
            "background": True,
            # Optional: TTL index for auto-expiration (30 days)
            # "expireAfterSeconds": 2592000
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
# Default Document Template
# -----------------------------------------------------------------------------

def get_default_conversation_document(session_id: str, thread_id: str) -> Dict[str, Any]:
    """
    Return a default document template for new conversation.
    
    Args:
        session_id: The session ObjectId as string
        thread_id: The LangGraph thread_id (typically same as session_id string)
    
    Returns:
        Dict with default field values for a new conversation.
    """
    from datetime import datetime, timezone
    from bson import ObjectId
    
    now = datetime.now(timezone.utc)
    
    return {
        "session_id": ObjectId(session_id),
        "thread_id": thread_id,
        "status": "active",
        "message_count": 0,
        "total_tokens": 0,
        "summary": None,
        "summary_up_to_message": None,
        "last_activity_at": now,
        "created_at": now,
        "updated_at": None,
        "metadata": {
            "model_name": None,
            "tool_calls_count": 0,
            "last_model_used": None,
            "symbols_discussed": []
        }
    }
