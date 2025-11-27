"""
Schema definition for the investment_styles collection.
"""

INVESTMENT_STYLES_SCHEMA = {
    "bsonType": "object",
    "required": ["name"],
    "properties": {
        "name": {
            "bsonType": "string",
            "description": "Style name"
        },
        "description": {
            "bsonType": "string",
            "description": "Optional description"
        }
    }
}

INVESTMENT_STYLES_INDEXES = [
    {
        "keys": [("name", 1)],
        "options": {"unique": True, "name": "idx_investment_styles_name"}
    }
]

def get_investment_styles_validation():
    """Return validation configuration for the investment_styles collection."""
    return {
        "validator": {"$jsonSchema": INVESTMENT_STYLES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
