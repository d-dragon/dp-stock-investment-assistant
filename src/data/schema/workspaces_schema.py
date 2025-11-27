"""
Schema definition for the workspaces collection.
"""

WORKSPACES_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id", "name"],
    "properties": {
        "user_id": {
            "bsonType": "objectId",
            "description": "Owner user reference"
        },
        "name": {
            "bsonType": "string",
            "description": "Workspace name"
        },
        "description": {
            "bsonType": "string",
            "description": "Optional description"
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

WORKSPACES_INDEXES = [
    {
        "keys": [("user_id", 1)],
        "options": {"name": "idx_workspaces_user"}
    },
    {
        "keys": [("user_id", 1), ("name", 1)],
        "options": {"unique": True, "name": "idx_workspaces_user_name"}
    }
]

def get_workspaces_validation():
    """Return validation configuration for the workspaces collection."""
    return {
        "validator": {"$jsonSchema": WORKSPACES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
