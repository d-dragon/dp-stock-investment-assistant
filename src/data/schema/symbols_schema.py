"""Schema definition for the symbols collection."""

# MongoDB JSON Schema for validation
SYMBOLS_SCHEMA = {
    "bsonType": "object",
    "required": ["symbol", "name", "asset_type", "listing"],
    "properties": {
        "symbol": {
            "bsonType": "string",
            "description": "Canonical trading symbol"
        },
        "name": {
            "bsonType": "string",
            "description": "Company or instrument name"
        },
        "asset_type": {
            "bsonType": "string",
            "description": "Instrument classification (equity, etf, adr, bond, crypto, other)",
            "enum": [
                "equity", "etf", "adr", "bond", "fund", "crypto", "index", "other"
            ]
        },
        "aliases": {
            "bsonType": "array",
            "description": "Alternate tickers or mnemonics (e.g., [\"AAPL.O\", \"AAPL:US\"])",
            "items": {"bsonType": "string"}
        },
        "identifiers": {
            "bsonType": "object",
            "description": "Global identifier codes",
            "properties": {
                "cusip": {"bsonType": "string"},
                # ISIN is optional, but if present, must be unique across all documents due to a unique sparse index.
                "isin": {"bsonType": "string"},
                "sedol": {"bsonType": "string"},
                "cik": {"bsonType": "string"},
                "figi": {"bsonType": "string"},
                "ric": {"bsonType": "string"}
            }
        },
        "listing": {
            "bsonType": "object",
            "description": "Primary listing context",
            "required": ["exchange", "country", "currency"],
            "properties": {
                "exchange": {"bsonType": "string", "description": "Primary exchange (e.g. NASDAQ)"},
                "mic": {"bsonType": "string", "description": "Market Identifier Code"},
                "country": {"bsonType": "string", "description": "Listing country"},
                "currency": {"bsonType": "string", "description": "Trading currency"},
                "primary": {"bsonType": "bool", "description": "Whether this is the primary listing"},
                "status": {
                    "bsonType": "string",
                    "enum": ["listed", "delisted", "suspended"],
                    "description": "Exchange status"
                },
                "listing_date": {"bsonType": "date"},
                "delisting_date": {"bsonType": "date"}
            }
        },
        "classification": {
            "bsonType": "object",
            "description": "Sector/industry groupings",
            "properties": {
                "sector": {"bsonType": "string"},
                "industry": {"bsonType": "string"},
                "sub_industry": {"bsonType": "string"},
                "gics_code": {"bsonType": "string"},
                "sic_code": {"bsonType": "string"},
                "market_cap_category": {"bsonType": "string"},
                "style_factor": {"bsonType": "string"}
            }
        },
        "coverage": {
            "bsonType": "object",
            "description": "Internal coverage metadata",
            "properties": {
                "is_tracked": {"bsonType": "bool"},
                "coverage_status": {
                    "bsonType": "string",
                    "enum": ["active", "pending", "paused", "retired"]
                },
                "coverage_level": {"bsonType": "string"},
                "tracking_start_date": {"bsonType": "date"},
                "tracking_end_date": {"bsonType": "date"},
                "assigned_analyst_id": {"bsonType": "objectId"},
                "last_reviewed_at": {"bsonType": "date"},
                "notes": {"bsonType": "string"},
                "tags": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                }
            }
        },
        "fundamentals_snapshot": {
            "bsonType": "object",
            "description": "Lightweight valuation snapshot for search",
            "properties": {
                "currency": {"bsonType": "string"},
                "market_cap": {"bsonType": "double"},
                "enterprise_value": {"bsonType": "double"},
                "shares_outstanding": {"bsonType": "double"},
                "free_float": {"bsonType": "double"},
                "beta": {"bsonType": "double"},
                "pe_ratio": {"bsonType": "double"},
                "dividend_yield": {"bsonType": "double"},
                "last_updated": {"bsonType": "date"}
            }
        },
        "price_snapshot": {
            "bsonType": "object",
            "description": "Recent trading metrics for quick displays",
            "properties": {
                "currency": {"bsonType": "string"},
                "last_price": {"bsonType": "double"},
                "previous_close": {"bsonType": "double"},
                "change_percent": {"bsonType": "double"},
                "volume": {"bsonType": "double"},
                "as_of": {"bsonType": "date"}
            }
        },
        "tags": {
            "bsonType": "array",
            "description": "Free-form labels used for filtering",
            "items": {"bsonType": "string"}
        },
        "metadata": {
            "bsonType": "object",
            "description": "Ingestion metadata",
            "properties": {
                "data_source": {"bsonType": "string"},
                "ingested_at": {"bsonType": "date"},
                "last_updated": {"bsonType": "date"}
            }
        },
        "created_at": {"bsonType": "date"},
        "updated_at": {"bsonType": "date"}
    }
}

# Index definitions aligned to the richer schema
SYMBOLS_INDEXES = [
    {
        "keys": [("symbol", 1)],
        "options": {"unique": True, "name": "idx_symbol_unique"}
    },
    # Unique sparse index: ISIN must be unique if present; documents without ISIN are allowed.
    {
        "keys": [("identifiers.isin", 1)],
        "options": {"unique": True, "name": "idx_isin_unique", "sparse": True}
    },
    {
        "keys": [("identifiers.cusip", 1)],
        "options": {"name": "idx_cusip", "sparse": True}
    },
    {
        "keys": [("listing.exchange", 1), ("listing.primary", 1)],
        "options": {"name": "idx_listing_exchange"}
    },
    {
        "keys": [("classification.sector", 1), ("classification.industry", 1)],
        "options": {"name": "idx_sector_industry"}
    },
    {
        "keys": [("classification.market_cap_category", 1)],
        "options": {"name": "idx_market_cap"}
    },
    {
        "keys": [("coverage.coverage_status", 1)],
        "options": {"name": "idx_coverage_status"}
    },
    {
        "keys": [("coverage.assigned_analyst_id", 1)],
        "options": {"name": "idx_assigned_analyst", "sparse": True}
    },
    {
        "keys": [("tags", 1)],
        "options": {"name": "idx_symbol_tags"}
    }
]

def get_symbols_validation():
    """Returns the validation configuration for symbols collection"""
    return {
        "validator": {"$jsonSchema": SYMBOLS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }