"""Schema definition for the reports collection."""

REPORTS_SCHEMA = {
    "bsonType": "object",
    "required": ["workspace_id", "title", "report_type", "status"],
    "properties": {
        "workspace_id": {
            "bsonType": "objectId",
            "description": "Owning workspace reference"
        },
        "session_id": {
            "bsonType": ["objectId", "null"],
            "description": "Optional session linkage"
        },
        "analysis_id": {
            "bsonType": ["objectId", "null"],
            "description": "Optional analysis linkage"
        },
        "title": {
            "bsonType": "string",
            "description": "Human readable report title"
        },
        "summary": {
            "bsonType": "string",
            "description": "Abstract or executive summary"
        },
        "report_type": {
            "bsonType": "string",
            "enum": [
                "workspace_snapshot",
                "idea_deep_dive",
                "portfolio_update",
                "risk_monitor",
                "custom"
            ],
            "description": "Report template or intent"
        },
        "status": {
            "bsonType": "string",
            "enum": ["draft", "in_review", "approved", "published", "archived"],
            "description": "Workflow state"
        },
        "symbol_tickers": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Ticker symbols referenced by the report (e.g., 'AAPL', 'MSFT')"
        },
        "sections": {
            "bsonType": "array",
            "description": "Structured report sections",
            "items": {
                "bsonType": "object",
                "required": ["title", "content"],
                "properties": {
                    "title": {"bsonType": "string"},
                    "content": {"bsonType": "string"},
                    "order": {"bsonType": "int"},
                    "section_type": {"bsonType": "string"}
                }
            }
        },
        "insights": {
            "bsonType": "array",
            "description": "Bullet insights or highlights",
            "items": {
                "bsonType": "object",
                "properties": {
                    "text": {"bsonType": "string"},
                    "category": {"bsonType": "string"},
                    "priority": {"bsonType": "string"}
                }
            }
        },
        "distribution": {
            "bsonType": "object",
            "description": "Distribution tracking",
            "properties": {
                "channels": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                },
                "recipients": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                },
                "last_sent_at": {"bsonType": "date"}
            }
        },
        "attachments": {
            "bsonType": "array",
            "description": "Supplementary files or exports",
            "items": {
                "bsonType": "object",
                "properties": {
                    "name": {"bsonType": "string"},
                    "type": {"bsonType": "string"},
                    "uri": {"bsonType": "string"}
                }
            }
        },
        "generated_by": {
            "bsonType": "string",
            "enum": ["user", "agent", "system"],
            "description": "Producer of the report"
        },
        "generated_at": {
            "bsonType": "date",
            "description": "Timestamp of creation"
        },
        "updated_at": {
            "bsonType": "date",
            "description": "Last modification timestamp"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Format and template metadata",
            "properties": {
                "format": {"bsonType": "string"},
                "template_id": {"bsonType": "string"},
                "version": {"bsonType": "string"}
            }
        },
        "tags": {
            "bsonType": "array",
            "items": {"bsonType": "string"},
            "description": "Searchable labels"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp (system)"
        }
    }
}

REPORTS_INDEXES = [
    {
        "keys": [("workspace_id", 1), ("report_type", 1), ("status", 1)],
        "options": {"name": "idx_reports_workspace_type_status"}
    },
    {
        "keys": [("session_id", 1)],
        "options": {"name": "idx_reports_session", "sparse": True}
    },
    {
        "keys": [("analysis_id", 1)],
        "options": {"name": "idx_reports_analysis", "sparse": True}
    },
    {
        "keys": [("symbol_tickers", 1)],
        "options": {"name": "idx_reports_tickers"}
    },
    {
        "keys": [("generated_at", -1)],
        "options": {"name": "idx_reports_generated_at"}
    }
]


def get_reports_validation():
    """Return validation configuration for the reports collection."""
    return {
        "validator": {"$jsonSchema": REPORTS_SCHEMA},
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
