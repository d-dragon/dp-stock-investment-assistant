"""
Schema definition for the users collection.
"""

USERS_SCHEMA = {
    "bsonType": "object",
    "required": ["email"],
    "properties": {
        "email": {
            "bsonType": "string",
            "description": "Unique user email"
        },
        "name": {
            "bsonType": "string",
            "description": "Display name"
        },
        "group_id": {
            "bsonType": ["objectId", "null"],
            "description": "Reference to the owning team/group"
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

USERS_INDEXES = [
    {
        "keys": [("email", 1)],
        "options": {"unique": True, "name": "idx_users_email_unique"}
    },
    {
        "keys": [("group_id", 1)],
        "options": {"name": "idx_users_group"}
    }
]

def get_users_validation():
    """Return validation configuration for the users collection."""
    return {
        "validator": {"$jsonSchema": USERS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
