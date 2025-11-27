"""
Schema definition for the sessions collection.
"""

SESSIONS_SCHEMA = {
    "bsonType": "object",
    "required": ["workspace_id", "title"],
    "properties": {
        "workspace_id": {
            "bsonType": "objectId",
            "description": "Reference to the workspace"
        },
        "title": {
            "bsonType": "string",
            "description": "Session title"
        },
        "status": {
            "bsonType": "string",
            "enum": ["open", "closed"],
            "description": "Session lifecycle status"
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
