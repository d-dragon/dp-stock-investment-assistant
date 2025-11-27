"""
Schema definition for the technical_indicators collection.
"""

TECHNICAL_INDICATORS_SCHEMA = {
    "bsonType": "object",
    "required": ["symbol_id", "as_of"],
    "properties": {
        "symbol_id": {
            "bsonType": "objectId",
            "description": "Reference to the symbol"
        },
        "as_of": {
            "bsonType": "date",
            "description": "Timestamp for the indicator snapshot"
        },
        "data": {
            "bsonType": "object",
            "description": "Dynamic indicator payload"
        }
    }
}

TECHNICAL_INDICATORS_INDEXES = [
    {
        "keys": [("symbol_id", 1)],
        "options": {"name": "idx_technical_indicators_symbol"}
    },
    {
        "keys": [("symbol_id", 1), ("as_of", -1)],
        "options": {"name": "idx_technical_indicators_symbol_as_of"}
    }
]

def get_technical_indicators_validation():
    """Return validation configuration for the technical_indicators collection."""
    return {
        "validator": {"$jsonSchema": TECHNICAL_INDICATORS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
