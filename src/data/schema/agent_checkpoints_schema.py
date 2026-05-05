"""
Agent Checkpoints Collection Schema (Documentation Only)

Purpose: Document the schema used by LangGraph's MongoDBSaver checkpointer.
This collection is managed by langgraph-checkpoint-mongodb, not by our application.

IMPORTANT: This schema is for documentation purposes only.
The actual collection is created and managed by MongoDBSaver.

Reference: docs/domains/agent/AGENT_MEMORY_TECHNICAL_DESIGN.md

Author: dp-stock-investment-assistant
Created: 2025-01-21
"""

from typing import Dict, Any, List

# -----------------------------------------------------------------------------
# Schema Definition (Managed by LangGraph MongoDBSaver)
# -----------------------------------------------------------------------------

# NOTE: This schema reflects what MongoDBSaver creates.
# We do NOT enforce this schema via MongoDB validation since
# LangGraph manages the collection structure.

AGENT_CHECKPOINTS_SCHEMA_DOCUMENTATION: Dict[str, Any] = {
    "bsonType": "object",
    "description": "LangGraph checkpoint storage - managed by MongoDBSaver",
    "properties": {
        "_id": {
            "bsonType": "objectId",
            "description": "MongoDB document ID"
        },
        "thread_id": {
            "bsonType": "string",
            "description": "Conversation thread identifier (maps to session_id)"
        },
        "checkpoint_id": {
            "bsonType": "string",
            "description": "Unique checkpoint identifier within thread"
        },
        "parent_checkpoint_id": {
            "bsonType": ["string", "null"],
            "description": "Parent checkpoint for versioning/branching"
        },
        "checkpoint": {
            "bsonType": "object",
            "description": "Serialized agent state including messages and tool calls",
            "properties": {
                "channel_values": {
                    "bsonType": "object",
                    "description": "Channel data including messages"
                },
                "channel_versions": {
                    "bsonType": "object",
                    "description": "Version tracking for channels"
                },
                "versions_seen": {
                    "bsonType": "object",
                    "description": "Seen versions for each channel"
                }
            }
        },
        "metadata": {
            "bsonType": "object",
            "description": "Checkpoint metadata",
            "properties": {
                "source": {
                    "bsonType": "string",
                    "description": "Source node that created checkpoint"
                },
                "step": {
                    "bsonType": "int",
                    "description": "Step number in execution"
                },
                "writes": {
                    "bsonType": "object",
                    "description": "Writes made in this step"
                }
            }
        },
        "created_at": {
            "bsonType": "date",
            "description": "Checkpoint creation timestamp"
        }
    }
}

# -----------------------------------------------------------------------------
# Index Definitions (Created by MongoDBSaver)
# -----------------------------------------------------------------------------

# These indexes are typically created by MongoDBSaver automatically.
# Listed here for documentation and potential manual creation if needed.

AGENT_CHECKPOINTS_INDEXES_DOCUMENTATION: List[Dict[str, Any]] = [
    {
        "keys": [("thread_id", 1), ("checkpoint_id", 1)],
        "options": {
            "name": "idx_checkpoints_thread_checkpoint",
            "unique": True
        },
        "description": "Unique index for retrieving specific checkpoint"
    },
    {
        "keys": [("thread_id", 1), ("created_at", -1)],
        "options": {
            "name": "idx_checkpoints_thread_created"
        },
        "description": "For retrieving latest checkpoint per thread"
    }
]

# -----------------------------------------------------------------------------
# Configuration Constants
# -----------------------------------------------------------------------------

# Default collection name used by our application
AGENT_CHECKPOINTS_COLLECTION_NAME = "agent_checkpoints"

# TTL for old checkpoints (in days) - applied via scheduled job, not TTL index
AGENT_CHECKPOINTS_TTL_DAYS = 30


def get_collection_name() -> str:
    """
    Return the collection name for agent checkpoints.
    
    This should match the collection_name parameter passed to MongoDBSaver.
    
    Returns:
        Collection name string.
    """
    return AGENT_CHECKPOINTS_COLLECTION_NAME


def get_checkpointer_config(
    connection_string: str,
    database_name: str,
    collection_name: str = None
) -> Dict[str, Any]:
    """
    Return configuration dict for MongoDBSaver initialization.
    
    Args:
        connection_string: MongoDB connection URI
        database_name: Database name
        collection_name: Optional collection name override
    
    Returns:
        Dict with checkpointer configuration.
    
    Example:
        config = get_checkpointer_config(
            "mongodb://localhost:27017",
            "stock_assistant"
        )
        checkpointer = MongoDBSaver(**config)
    """
    return {
        "connection_string": connection_string,
        "db_name": database_name,
        "collection_name": collection_name or AGENT_CHECKPOINTS_COLLECTION_NAME
    }


# -----------------------------------------------------------------------------
# Usage Example (for documentation)
# -----------------------------------------------------------------------------

"""
Usage Example:

from langgraph.checkpoint.mongodb import MongoDBSaver
from data.schema.agent_checkpoints_schema import get_checkpointer_config

# Get configuration
config = get_checkpointer_config(
    connection_string=app_config["database"]["mongodb"]["connection_string"],
    database_name=app_config["database"]["mongodb"]["database_name"]
)

# Initialize checkpointer
checkpointer = MongoDBSaver(**config)

# Use with agent executor (langchain.agents.create_agent)
agent_executor = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=checkpointer
)

# Invoke with thread_id for memory
result = agent_executor.invoke(
    {"messages": [HumanMessage(content="query")]},
    config={"configurable": {"thread_id": session_id}}
)
"""
