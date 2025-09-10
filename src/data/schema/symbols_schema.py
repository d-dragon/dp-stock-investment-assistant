"""
Schema definition for the symbols collection.
"""

# MongoDB JSON Schema for validation
SYMBOLS_SCHEMA = {
    "bsonType": "object",
    "required": ["symbol", "name"],
    "properties": {
        "symbol": {
            "bsonType": "string",
            "description": "Stock symbol, required"
        },
        "name": {
            "bsonType": "string",
            "description": "Company name, required"
        },
        "exchange": {
            "bsonType": "string",
            "description": "Stock exchange (e.g., 'NASDAQ')"
        },
        "sector": {
            "bsonType": "string",
            "description": "Business sector"
        },
        "industry": {
            "bsonType": "string",
            "description": "Industry category"
        },
        "market_cap_category": {
            "bsonType": "string",
            "description": "Market cap classification (e.g., 'Large Cap')"
        },
        "is_tracked": {
            "bsonType": "bool",
            "description": "Whether this symbol is actively tracked"
        },
        "tracking_start_date": {
            "bsonType": "date",
            "description": "When tracking began for this symbol"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Additional metadata",
            "properties": {
                "country": {
                    "bsonType": "string",
                    "description": "Country of incorporation"
                },
                "currency": {
                    "bsonType": "string",
                    "description": "Trading currency"
                },
                "isin": {
                    "bsonType": "string",
                    "description": "International Securities Identification Number"
                },
                "last_updated": {
                    "bsonType": "date",
                    "description": "Last time this record was updated"
                }
            }
        }
    }
}

# Index definitions
SYMBOLS_INDEXES = [
    {
        "keys": [("symbol", 1)],
        "options": {"unique": True, "name": "idx_symbol_unique"}
    },
    {
        "keys": [("sector", 1)],
        "options": {"name": "idx_sector"}
    },
    {
        "keys": [("industry", 1)],
        "options": {"name": "idx_industry"}
    },
    {
        "keys": [("market_cap_category", 1)],
        "options": {"name": "idx_market_cap"}
    }
]

def get_symbols_validation():
    """Returns the validation configuration for symbols collection"""
    return {
        "validator": {"$jsonSchema": SYMBOLS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }