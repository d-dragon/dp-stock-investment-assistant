"""
Schema definition for the watchlists collection.
"""

WATCHLISTS_SCHEMA = {
    "bsonType": "object",
    "required": ["workspace_id", "name"],
    "properties": {
        "workspace_id": {
            "bsonType": "objectId",
            "description": "Owning workspace reference"
        },
        "name": {
            "bsonType": "string",
            "description": "Watchlist name"
        },
        "symbol_ids": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Array of ticker symbols"
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

WATCHLISTS_INDEXES = [
    {
        "keys": [("workspace_id", 1)],
        "options": {"name": "idx_watchlists_workspace"}
    }
]

def get_watchlists_validation():
    """Return validation configuration for the watchlists collection."""
    return {
        "validator": {"$jsonSchema": WATCHLISTS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
