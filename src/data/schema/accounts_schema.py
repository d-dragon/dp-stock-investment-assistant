"""
Schema definition for the accounts collection.
"""

ACCOUNTS_SCHEMA = {
    "bsonType": "object",
    "required": ["user_id", "name"],
    "properties": {
        "user_id": {
            "bsonType": "objectId",
            "description": "Owner reference"
        },
        "name": {
            "bsonType": "string",
            "description": "Account nickname"
        },
        "provider": {
            "bsonType": "string",
            "description": "Brokerage or custodian"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        }
    }
}

ACCOUNTS_INDEXES = [
    {
        "keys": [("user_id", 1)],
        "options": {"name": "idx_accounts_user"}
    }
]

def get_accounts_validation():
    """Return validation configuration for the accounts collection."""
    return {
        "validator": {"$jsonSchema": ACCOUNTS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
