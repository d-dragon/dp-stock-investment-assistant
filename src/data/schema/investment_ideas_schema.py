"""
Schema definition for the investment_ideas collection.
"""

INVESTMENT_IDEAS_SCHEMA = {
    "bsonType": "object",
    "required": ["workspace_id", "title"],
    "properties": {
        "workspace_id": {
            "bsonType": "objectId",
            "description": "Owning workspace reference"
        },
        "title": {
            "bsonType": "string",
            "description": "Idea name or title"
        },
        "symbol_ids": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Related ticker symbols"
        },
        "status": {
            "bsonType": "string",
            "enum": ["watching", "active", "exited", "rejected"],
            "description": "Idea lifecycle status"
        },
        "conviction": {
            "bsonType": ["int", "double"],
            "description": "Simple conviction score"
        },
        "thesis_summary": {
            "bsonType": "string",
            "description": "Short thesis text"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        },
        "updated_at": {
            "bsonType": "date",
            "description": "Last updated timestamp"
        }
    }
}

INVESTMENT_IDEAS_INDEXES = [
    {
        "keys": [("workspace_id", 1)],
        "options": {"name": "idx_investment_ideas_workspace"}
    },
    {
        "keys": [("workspace_id", 1), ("status", 1)],
        "options": {"name": "idx_investment_ideas_workspace_status"}
    }
]

def get_investment_ideas_validation():
    """Return validation configuration for the investment_ideas collection."""
    return {
        "validator": {"$jsonSchema": INVESTMENT_IDEAS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
