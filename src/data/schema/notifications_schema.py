"""
Schema definition for the notifications collection.
"""

NOTIFICATIONS_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id", "type", "message", "created_at"],
    "properties": {
        "user_id": {
            "bsonType": "objectId",
            "description": "Notification recipient"
        },
        "type": {
            "bsonType": "string",
            "description": "Notification category"
        },
        "message": {
            "bsonType": "string",
            "description": "User-visible message"
        },
        "symbol_id": {
            "bsonType": ["objectId", "null"],
            "description": "Optional symbol reference"
        },
        "read": {
            "bsonType": "bool",
            "description": "Read/unread status"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        }
    }
}

NOTIFICATIONS_INDEXES = [
    {
        "keys": [("user_id", 1)],
        "options": {"name": "idx_notifications_user"}
    },
    {
        "keys": [("user_id", 1), ("read", 1)],
        "options": {"name": "idx_notifications_user_read"}
    }
]

def get_notifications_validation():
    """Return validation configuration for the notifications collection."""
    return {
        "validator": {"$jsonSchema": NOTIFICATIONS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
