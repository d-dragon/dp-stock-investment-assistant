"""
Schema definition for the market_snapshots collection.
"""

MARKET_SNAPSHOTS_SCHEMA = {
    "bsonType": "object",
    "required": ["as_of"],
    "properties": {
        "as_of": {
            "bsonType": "date",
            "description": "Timestamp for the snapshot"
        },
        "data": {
            "bsonType": "object",
            "description": "Macro indicators payload"
        }
    }
}

MARKET_SNAPSHOTS_INDEXES = [
    {
        "keys": [("as_of", -1)],
        "options": {"name": "idx_market_snapshots_as_of"}
    }
]

def get_market_snapshots_validation():
    """Return validation configuration for the market_snapshots collection."""
    return {
        "validator": {"$jsonSchema": MARKET_SNAPSHOTS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
