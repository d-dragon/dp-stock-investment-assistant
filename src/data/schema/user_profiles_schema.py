"""
Schema definition for the user_profiles collection.
"""

USER_PROFILES_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id"],
    "properties": {
        "user_id": {
            "bsonType": "objectId",
            "description": "Reference to a user"
        },
        "risk_profile": {
            "bsonType": "string",
            "enum": ["conservative", "balanced", "aggressive"],
            "description": "Risk appetite classification"
        },
        "investment_horizon": {
            "bsonType": "string",
            "enum": ["short_term", "medium_term", "long_term"],
            "description": "Typical holding horizon"
        },
        "base_currency": {
            "bsonType": "string",
            "description": "Preferred reporting currency"
        },
        "constraints": {
            "bsonType": "object",
            "description": "Simple constraint settings",
            "properties": {
                "max_single_position_pct": {"bsonType": "double"},
                "max_sector_pct": {"bsonType": "double"}
            }
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        },
        "updated_at": {
            "bsonType": "date",
            "description": "Last update timestamp"
        }
    }
}

USER_PROFILES_INDEXES = [
    {
        "keys": [("user_id", 1)],
        "options": {"unique": True, "name": "idx_user_profiles_user"}
    }
]

def get_user_profiles_validation():
    """Return validation configuration for the user_profiles collection."""
    return {
        "validator": {"$jsonSchema": USER_PROFILES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
