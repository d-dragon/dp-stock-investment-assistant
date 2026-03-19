"""
Schema definition for the sessions collection.

Sessions are business workflow containers within a workspace. Each session
owns many conversations and holds reusable analytical context (assumptions,
pinned_intent, focused_symbols) that child conversations inherit.

Lifecycle: active → closed → archived (no reverse transitions).

Reference: specs/agent-session-with-stm-wiring/spec.md (FR-004, FR-009, FR-009a)
"""

SESSIONS_SCHEMA = {
    "bsonType": "object",
    "required": ["session_id", "workspace_id", "title"],
    "properties": {
        "session_id": {
            "bsonType": "string",
            "description": "Explicit business identifier (UUID v4)",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        },
        "workspace_id": {
            "bsonType": "string",
            "description": "Reference to the workspace (string for cross-collection consistency)"
        },
        "user_id": {
            "bsonType": "string",
            "description": "Owner user reference"
        },
        "title": {
            "bsonType": "string",
            "description": "Session title"
        },
        "status": {
            "bsonType": "string",
            "enum": ["active", "closed", "archived"],
            "description": "Session lifecycle status"
        },
        "assumptions": {
            "bsonType": ["string", "null"],
            "description": "Session-level reusable assumptions for child conversations"
        },
        "pinned_intent": {
            "bsonType": ["string", "null"],
            "description": "Session-level pinned analysis intent"
        },
        "focused_symbols": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Session-level symbol focus inherited by conversations"
        },
        "linked_symbol_ids": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Symbols referenced in the session"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        },
        "updated_at": {
            "bsonType": "date",
            "description": "Last update timestamp"
        }
    }
}

SESSIONS_INDEXES = [
    {
        "keys": [("session_id", 1)],
        "options": {"name": "idx_sessions_session_id", "unique": True, "background": True}
    },
    {
        "keys": [("workspace_id", 1)],
        "options": {"name": "idx_sessions_workspace"}
    },
    {
        "keys": [("workspace_id", 1), ("status", 1)],
        "options": {"name": "idx_sessions_workspace_status"}
    }
]

def get_sessions_validation():
    """Return validation configuration for the sessions collection."""
    return {
        "validator": {"$jsonSchema": SESSIONS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }


def get_sessions_indexes():
    """Return index definitions for the sessions collection."""
    return SESSIONS_INDEXES
