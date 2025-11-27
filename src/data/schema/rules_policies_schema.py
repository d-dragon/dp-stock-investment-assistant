"""
Schema definition for the rules_policies collection.
"""

RULES_POLICIES_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id", "name"],
    "properties": {
        "user_id": {
            "bsonType": "objectId",
            "description": "Owner reference"
        },
        "name": {
            "bsonType": "string",
            "description": "Rule or policy name"
        },
        "description": {
            "bsonType": "string",
            "description": "Rule details"
        },
        "active": {
            "bsonType": "bool",
            "description": "Whether the rule is active"
        }
    }
}

RULES_POLICIES_INDEXES = [
    {
        "keys": [("user_id", 1)],
        "options": {"name": "idx_rules_policies_user"}
    }
]

def get_rules_policies_validation():
    """Return validation configuration for the rules_policies collection."""
    return {
        "validator": {"$jsonSchema": RULES_POLICIES_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
