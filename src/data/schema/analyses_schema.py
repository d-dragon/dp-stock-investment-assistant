"""
Schema definition for the analyses collection.
"""

ANALYSES_SCHEMA = {
    "bsonType": "object",
    "required": ["session_id", "title"],
    "properties": {
        "session_id": {
            "bsonType": "objectId",
            "description": "Reference to the originating session"
        },
        "title": {
            "bsonType": "string",
            "description": "Analysis title"
        },
        "summary": {
            "bsonType": "string",
            "description": "Short summary"
        },
        "symbol_ids": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Related symbol tickers"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        }
    }
}

ANALYSES_INDEXES = [
    {
        "keys": [("session_id", 1)],
        "options": {"name": "idx_analyses_session"}
    }
]

def get_analyses_validation():
    """Return validation configuration for the analyses collection."""
    return {
        "validator": {"$jsonSchema": ANALYSES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
