"""
Schema definition for the user_preferences collection.
"""

# MongoDB JSON Schema for validation
USER_PREFERENCES_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id"],
    "properties": {
        "user_id": {
            "bsonType": "string",
            "description": "Unique user identifier"
        },
        "analysis_preferences": {
            "bsonType": "object",
            "description": "User's analysis preferences",
            "properties": {
                "target_symbols": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"},
                    "description": "Symbols the user is tracking"
                },
                "sectors_of_interest": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"},
                    "description": "Sectors the user is interested in"
                },
                "time_horizon": {
                    "bsonType": "string",
                    "enum": ["short_term", "medium_term", "long_term"],
                    "description": "User's investment time horizon"
                },
                "risk_tolerance": {
                    "bsonType": "string",
                    "enum": ["conservative", "moderate", "aggressive"],
                    "description": "User's risk tolerance"
                },
                "technical_indicators": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"},
                    "description": "Technical indicators the user prefers"
                },
                "fundamental_metrics": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"},
                    "description": "Fundamental metrics the user prefers"
                }
            }
        },
        "display_preferences": {
            "bsonType": "object",
            "description": "UI and display preferences",
            "properties": {
                "default_chart_timeframe": {"bsonType": "string"},
                "preferred_report_format": {"bsonType": "string"},
                "chart_colors": {"bsonType": "object"}
            }
        },
        "notification_settings": {
            "bsonType": "object",
            "description": "Notification preferences",
            "properties": {
                "price_alerts": {"bsonType": "bool"},
                "news_alerts": {"bsonType": "bool"},
                "report_generation": {"bsonType": "bool"},
                "email": {"bsonType": "string"}
            }
        },
        "last_updated": {
            "bsonType": "date",
            "description": "When preferences were last updated"
        }
    }
}

# Index definitions
USER_PREFERENCES_INDEXES = [
    {
        "keys": [("user_id", 1)],
        "options": {"unique": True, "name": "idx_user_id_unique"}
    }
]

def get_user_preferences_validation():
    """Returns the validation configuration for user_preferences collection"""
    return {
        "validator": {"$jsonSchema": USER_PREFERENCES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }