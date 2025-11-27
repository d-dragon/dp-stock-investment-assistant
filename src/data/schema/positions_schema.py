"""
Schema definition for the positions collection.
"""

POSITIONS_SCHEMA = {
    "bsonType": "object",
    "required": ["portfolio_id", "symbol_id", "quantity"],
    "properties": {
        "portfolio_id": {
            "bsonType": "objectId",
            "description": "Reference to the portfolio"
        },
        "symbol_id": {
            "bsonType": "objectId",
            "description": "Reference to the symbol"
        },
        "quantity": {
            "bsonType": ["double", "int"],
            "description": "Number of shares/contracts held"
        },
        "avg_cost": {
            "bsonType": ["double", "int"],
            "description": "Average cost basis"
        },
        "last_updated": {
            "bsonType": "date",
            "description": "Last modification timestamp"
        }
    }
}

POSITIONS_INDEXES = [
    {
        "keys": [("portfolio_id", 1)],
        "options": {"name": "idx_positions_portfolio"}
    },
    {
        "keys": [("portfolio_id", 1), ("symbol_id", 1)],
        "options": {"unique": True, "name": "idx_positions_portfolio_symbol"}
    }
]

def get_positions_validation():
    """Return validation configuration for the positions collection."""
    return {
        "validator": {"$jsonSchema": POSITIONS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
