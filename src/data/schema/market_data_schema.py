"""
Schema definition for the market_data time series collection.
"""

from datetime import datetime
from typing import Dict, Any

# MongoDB JSON Schema for validation
MARKET_DATA_SCHEMA = {
    "bsonType": "object",
    "required": ["symbol", "timestamp", "open", "high", "low", "close", "volume"],
    "properties": {
        "symbol": {
            "bsonType": "string",
            "description": "Stock symbol, required"
        },
        "timestamp": {
            "bsonType": "date",
            "description": "Data timestamp, required"
        },
        "open": {
            "bsonType": "double",
            "description": "Opening price, required"
        },
        "high": {
            "bsonType": "double",
            "description": "Highest price, required"
        },
        "low": {
            "bsonType": "double",
            "description": "Lowest price, required"
        },
        "close": {
            "bsonType": "double",
            "description": "Closing price, required"
        },
        "volume": {
            "bsonType": "int",
            "description": "Trading volume, required"
        },
        "adjusted_close": {
            "bsonType": "double",
            "description": "Adjusted closing price"
        },
        "technical_indicators": {
            "bsonType": "object",
            "description": "Technical indicators calculated for this data point"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Additional metadata",
            "properties": {
                "source": {
                    "bsonType": "string",
                    "description": "Data source (e.g., 'yahoo_finance')"
                },
                "data_quality": {
                    "bsonType": "string",
                    "description": "Quality indicator (e.g., 'verified', 'estimated')"
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
MARKET_DATA_INDEXES = [
    {
        "keys": [("symbol", 1), ("timestamp", 1)],
        "options": {"name": "idx_symbol_timestamp"}
    },
    {
        "keys": [("timestamp", 1)],
        "options": {"name": "idx_timestamp"}
    }
]

# Time-series collection options
MARKET_DATA_TIMESERIES_OPTIONS = {
    "timeField": "timestamp",
    "metaField": "symbol",
    "granularity": "minutes"
}

def get_market_data_validation():
    """Returns the validation configuration for market_data collection"""
    return {
        "validator": {"$jsonSchema": MARKET_DATA_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }