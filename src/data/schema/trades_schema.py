"""
Schema definition for the trades collection.
"""

TRADES_SCHEMA = {
    "bsonType": "object",
    "required": ["portfolio_id", "symbol_id", "side", "quantity", "price", "executed_at"],
    "properties": {
        "portfolio_id": {
            "bsonType": "objectId",
            "description": "Reference to the portfolio"
        },
        "symbol_id": {
            "bsonType": "objectId",
            "description": "Reference to the symbol"
        },
        "side": {
            "bsonType": "string",
            "enum": ["buy", "sell"],
            "description": "Buy or sell"
        },
        "quantity": {
            "bsonType": ["double", "int"],
            "description": "Trade quantity"
        },
        "price": {
            "bsonType": ["double", "int"],
            "description": "Execution price"
        },
        "executed_at": {
            "bsonType": "date",
            "description": "Execution timestamp"
        }
    }
}

TRADES_INDEXES = [
    {
        "keys": [("portfolio_id", 1)],
        "options": {"name": "idx_trades_portfolio"}
    },
    {
        "keys": [("symbol_id", 1)],
        "options": {"name": "idx_trades_symbol"}
    }
]

def get_trades_validation():
    """Return validation configuration for the trades collection."""
    return {
        "validator": {"$jsonSchema": TRADES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
