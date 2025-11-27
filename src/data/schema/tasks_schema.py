"""
Schema definition for the tasks collection.
"""

TASKS_SCHEMA = {
    "bsonType": "object",
    "required": ["workspace_id", "description", "status"],
    "properties": {
        "workspace_id": {
            "bsonType": "objectId",
            "description": "Owning workspace reference"
        },
        "session_id": {
            "bsonType": ["objectId", "null"],
            "description": "Optional session linkage"
        },
        "description": {
            "bsonType": "string",
            "description": "Task description"
        },
        "status": {
            "bsonType": "string",
            "enum": ["open", "in_progress", "done", "canceled"],
            "description": "Task state"
        },
        "priority": {
            "bsonType": "string",
            "enum": ["low", "medium", "high"],
            "description": "Priority hint"
        },
        "due_date": {
            "bsonType": "date",
            "description": "Optional due date"
        },
        "symbol_ids": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Related symbols"
        },
        "created_by": {
            "bsonType": "string",
            "description": "Actor that created the task"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        }
    }
}

TASKS_INDEXES = [
    {
        "keys": [("workspace_id", 1)],
        "options": {"name": "idx_tasks_workspace"}
    },
    {
        "keys": [("workspace_id", 1), ("status", 1)],
        "options": {"name": "idx_tasks_workspace_status"}
    }
]

def get_tasks_validation():
    """Return validation configuration for the tasks collection."""
    return {
        "validator": {"$jsonSchema": TASKS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
