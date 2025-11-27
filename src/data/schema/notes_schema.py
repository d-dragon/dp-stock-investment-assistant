"""
Schema definition for the notes collection.
"""

NOTES_SCHEMA = {
    "bsonType": "object",
    "required": ["workspace_id", "content", "type"],
    "properties": {
        "workspace_id": {
            "bsonType": "objectId",
            "description": "Owning workspace reference"
        },
        "session_id": {
            "bsonType": ["objectId", "null"],
            "description": "Optional session reference"
        },
        "type": {
            "bsonType": "string",
            "description": "Note type identifier"
        },
        "title": {
            "bsonType": "string",
            "description": "Optional title"
        },
        "content": {
            "bsonType": "string",
            "description": "Markdown or plain-text body"
        },
        "symbol_ids": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Related ticker symbols"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        }
    }
}

NOTES_INDEXES = [
    {
        "keys": [("workspace_id", 1)],
        "options": {"name": "idx_notes_workspace"}
    },
    {
        "keys": [("session_id", 1)],
        "options": {"name": "idx_notes_session"}
    }
]

def get_notes_validation():
    """Return validation configuration for the notes collection."""
    return {
        "validator": {"$jsonSchema": NOTES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
