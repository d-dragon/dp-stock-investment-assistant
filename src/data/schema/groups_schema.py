"""
Schema definition for the groups collection.
"""

GROUPS_SCHEMA = {
    "bsonType": "object",
    "required": ["name"],
    "properties": {
        "name": {
            "bsonType": "string",
            "description": "Group or team name"
        },
        "description": {
            "bsonType": "string",
            "description": "Optional description"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        }
    }
}

GROUPS_INDEXES = [
    {
        "keys": [("name", 1)],
        "options": {"unique": True, "name": "idx_groups_name_unique"}
    }
]

def get_groups_validation():
    """Return validation configuration for the groups collection."""
    return {
        "validator": {"$jsonSchema": GROUPS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
