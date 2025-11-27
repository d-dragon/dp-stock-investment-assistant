"""
Schema definition for the chats collection.
"""

CHATS_SCHEMA = {
    "bsonType": "object",
    "required": ["session_id", "role", "content", "created_at"],
    "properties": {
        "session_id": {
            "bsonType": "objectId",
            "description": "Reference to the parent session"
        },
        "role": {
            "bsonType": "string",
            "enum": ["user", "assistant"],
            "description": "Message role"
        },
        "content": {
            "bsonType": "string",
            "description": "Chat message contents"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Message timestamp"
        }
    }
}

CHATS_INDEXES = [
    {
        "keys": [("session_id", 1), ("created_at", 1)],
        "options": {"name": "idx_chats_session_created"}
    }
]

def get_chats_validation():
    """Return validation configuration for the chats collection."""
    return {
        "validator": {"$jsonSchema": CHATS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
