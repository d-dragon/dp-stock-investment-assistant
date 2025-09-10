"""
Schema definition for the investment_reports collection.
"""

# MongoDB JSON Schema for validation
INVESTMENT_REPORTS_SCHEMA = {
    "bsonType": "object",
    "required": ["symbol", "timestamp", "report_type"],
    "properties": {
        "symbol": {
            "bsonType": "string",
            "description": "Stock symbol, required"
        },
        "timestamp": {
            "bsonType": "date",
            "description": "Report generation timestamp, required"
        },
        "report_type": {
            "bsonType": "string",
            "description": "Type of report (e.g., 'comprehensive_analysis'), required",
            "enum": ["comprehensive_analysis", "technical_analysis", "fundamental_analysis", "quick_overview", "market_sentiment"]
        },
        "time_horizon": {
            "bsonType": "string",
            "description": "Investment time horizon",
            "enum": ["short_term", "medium_term", "long_term"]
        },
        "recommendation": {
            "bsonType": "object",
            "description": "Investment recommendation",
            "properties": {
                "action": {
                    "bsonType": "string",
                    "enum": ["buy", "sell", "hold", "strong_buy", "strong_sell"]
                },
                "target_price": {"bsonType": "double"},
                "confidence": {
                    "bsonType": "double",
                    "minimum": 0,
                    "maximum": 1
                },
                "time_frame_months": {"bsonType": "int"}
            }
        },
        "analysis_sections": {
            "bsonType": "array",
            "description": "Report content sections",
            "items": {
                "bsonType": "object",
                "required": ["title", "content"],
                "properties": {
                    "title": {"bsonType": "string"},
                    "content": {"bsonType": "string"},
                    "key_indicators": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "key_metrics": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "sentiment_score": {"bsonType": "double"},
                    "risk_level": {"bsonType": "string"},
                    "risk_factors": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    }
                }
            }
        },
        "charts": {
            "bsonType": "array",
            "description": "Visualization references",
            "items": {
                "bsonType": "object",
                "required": ["title"],
                "properties": {
                    "title": {"bsonType": "string"},
                    "chart_data": {"bsonType": "object"}
                }
            }
        },
        "metadata": {
            "bsonType": "object",
            "description": "Report metadata",
            "properties": {
                "generated_by": {"bsonType": "string"},
                "model": {"bsonType": "string"},
                "prompt_tokens": {"bsonType": "int"},
                "completion_tokens": {"bsonType": "int"},
                "data_sources": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                },
                "data_as_of": {"bsonType": "date"}
            }
        }
    }
}

# Index definitions
INVESTMENT_REPORTS_INDEXES = [
    {
        "keys": [("symbol", 1)],
        "options": {"name": "idx_symbol"}
    },
    {
        "keys": [("symbol", 1), ("timestamp", -1)],
        "options": {"name": "idx_symbol_timestamp"}
    },
    {
        "keys": [("recommendation.action", 1)],
        "options": {"name": "idx_recommendation_action", "sparse": True}
    },
    {
        "keys": [("report_type", 1)],
        "options": {"name": "idx_report_type"}
    }
]

def get_investment_reports_validation():
    """Returns the validation configuration for investment_reports collection"""
    return {
        "validator": {"$jsonSchema": INVESTMENT_REPORTS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }