"""
Schema definition for the strategies collection.
"""

STRATEGIES_SCHEMA = {
    "bsonType": "object",
    "required": ["name"],
    "properties": {
        "name": {
            "bsonType": "string",
            "description": "Strategy name"
        },
        "style_id": {
            "bsonType": ["objectId", "null"],
            "description": "Optional reference to an investment style"
        },
        "description": {
            "bsonType": "string",
            "description": "Strategy description"
        }
    }
}

STRATEGIES_INDEXES = [
    {
        "keys": [("name", 1)],
        "options": {"unique": True, "name": "idx_strategies_name"}
    },
    {
        "keys": [("style_id", 1)],
        "options": {"name": "idx_strategies_style"}
    }
]

def get_strategies_validation():
    """Return validation configuration for the strategies collection."""
    return {
        "validator": {"$jsonSchema": STRATEGIES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
