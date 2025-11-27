"""
Schema definition for the portfolios collection.
"""

PORTFOLIOS_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id", "name"],
    "properties": {
        "user_id": {
            "bsonType": "objectId",
            "description": "Portfolio owner reference"
        },
        "account_id": {
            "bsonType": ["objectId", "null"],
            "description": "Optional brokerage account reference"
        },
        "name": {
            "bsonType": "string",
            "description": "Portfolio name"
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

PORTFOLIOS_INDEXES = [
    {
        "keys": [("user_id", 1)],
        "options": {"name": "idx_portfolios_user"}
    }
]

def get_portfolios_validation():
    """Return validation configuration for the portfolios collection."""
    return {
        "validator": {"$jsonSchema": PORTFOLIOS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
