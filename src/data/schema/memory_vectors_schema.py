"""
Memory Vectors Collection Schema (Future Implementation)

Purpose: Store conversation embeddings for semantic search over past interactions.
This enables long-term memory retrieval based on semantic similarity.

Status: FUTURE IMPLEMENTATION (Phase 2A.2+)
This schema is defined for planning purposes but not yet active.

Reference: docs/langchain-agent/AGENT_MEMORY_TECHNICAL_DESIGN.md

Author: dp-stock-investment-assistant
Created: 2025-01-21
"""

from typing import Dict, Any, List

# -----------------------------------------------------------------------------
# Schema Definition
# -----------------------------------------------------------------------------

MEMORY_VECTORS_SCHEMA: Dict[str, Any] = {
    "bsonType": "object",
    "required": ["user_id", "content", "content_type", "embedding", "created_at"],
    "properties": {
        "_id": {
            "bsonType": "objectId",
            "description": "Unique identifier for the memory vector"
        },
        "user_id": {
            "bsonType": "objectId",
            "description": "User who owns this memory"
        },
        "session_id": {
            "bsonType": ["objectId", "null"],
            "description": "Source session (null for synthesized memories)"
        },
        "conversation_id": {
            "bsonType": ["objectId", "null"],
            "description": "Source conversation record"
        },
        "content": {
            "bsonType": "string",
            "description": "Text content that was embedded"
        },
        "content_type": {
            "bsonType": "string",
            "enum": ["user_query", "assistant_response", "summary", "insight", "preference"],
            "description": "Type of content for filtering"
        },
        "embedding": {
            "bsonType": "array",
            "items": {"bsonType": "double"},
            "description": "Vector embedding (1536 dimensions for OpenAI text-embedding-3-small)"
        },
        "embedding_model": {
            "bsonType": "string",
            "description": "Model used to generate embedding"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Additional context for the memory",
            "properties": {
                "symbols": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"},
                    "description": "Stock symbols mentioned"
                },
                "topics": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"},
                    "description": "Topics discussed (e.g., 'price', 'analysis', 'news')"
                },
                "sentiment": {
                    "bsonType": ["string", "null"],
                    "enum": ["positive", "negative", "neutral", None],
                    "description": "Sentiment of the content"
                },
                "importance_score": {
                    "bsonType": ["double", "null"],
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Importance weight for retrieval ranking"
                },
                "source_message_ids": {
                    "bsonType": "array",
                    "items": {"bsonType": "objectId"},
                    "description": "Source chat message IDs"
                }
            }
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        },
        "expires_at": {
            "bsonType": ["date", "null"],
            "description": "Optional expiration for temporary memories"
        }
    }
}

# -----------------------------------------------------------------------------
# Index Definitions
# -----------------------------------------------------------------------------

MEMORY_VECTORS_INDEXES: List[Dict[str, Any]] = [
    {
        "keys": [("user_id", 1), ("created_at", -1)],
        "options": {
            "name": "idx_memory_vectors_user_created",
            "background": True
        },
        "description": "User's memories by recency"
    },
    {
        "keys": [("session_id", 1)],
        "options": {
            "name": "idx_memory_vectors_session",
            "background": True
        },
        "description": "Memories from specific session"
    },
    {
        "keys": [("content_type", 1), ("user_id", 1)],
        "options": {
            "name": "idx_memory_vectors_type_user",
            "background": True
        },
        "description": "Filter by content type per user"
    },
    {
        "keys": [("metadata.symbols", 1)],
        "options": {
            "name": "idx_memory_vectors_symbols",
            "background": True,
            "sparse": True
        },
        "description": "Find memories by stock symbol"
    },
    {
        "keys": [("expires_at", 1)],
        "options": {
            "name": "idx_memory_vectors_expiry",
            "expireAfterSeconds": 0,
            "sparse": True
        },
        "description": "TTL index for auto-expiring temporary memories"
    }
]

# NOTE: Vector search index must be created separately via MongoDB Atlas
# See VECTOR_SEARCH_INDEX_DEFINITION below

# -----------------------------------------------------------------------------
# Vector Search Index Definition (MongoDB Atlas)
# -----------------------------------------------------------------------------

# This index definition is for MongoDB Atlas Vector Search
# It must be created via Atlas UI or Atlas Admin API, not pymongo

VECTOR_SEARCH_INDEX_DEFINITION: Dict[str, Any] = {
    "name": "memory_vectors_search",
    "type": "vectorSearch",
    "definition": {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 1536,  # OpenAI text-embedding-3-small
                "similarity": "cosine"
            },
            {
                "type": "filter",
                "path": "user_id"
            },
            {
                "type": "filter",
                "path": "content_type"
            },
            {
                "type": "filter",
                "path": "metadata.symbols"
            }
        ]
    }
}

# -----------------------------------------------------------------------------
# Validation Config Helper
# -----------------------------------------------------------------------------

def get_memory_vectors_validation() -> Dict[str, Any]:
    """
    Return MongoDB validation configuration for memory_vectors collection.
    
    Returns:
        Dict with validator, validationLevel, and validationAction settings.
    """
    return {
        "validator": {
            "$jsonSchema": MEMORY_VECTORS_SCHEMA
        },
        "validationLevel": "moderate",
        "validationAction": "warn"
    }


def get_memory_vectors_indexes() -> List[Dict[str, Any]]:
    """
    Return index definitions for memory_vectors collection.
    
    Note: Does NOT include vector search index which must be created
    separately via MongoDB Atlas.
    
    Returns:
        List of index configurations with keys and options.
    """
    return MEMORY_VECTORS_INDEXES


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Embedding dimensions by model
EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}

# Default embedding model
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

# Content type weights for retrieval ranking
CONTENT_TYPE_WEIGHTS = {
    "user_query": 1.0,
    "assistant_response": 0.8,
    "summary": 0.9,
    "insight": 1.0,
    "preference": 1.2,  # Higher weight for learned preferences
}


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_default_memory_vector_document(
    user_id: str,
    content: str,
    content_type: str,
    embedding: List[float],
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    session_id: str = None,
    conversation_id: str = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Return a default document template for new memory vector.
    
    Args:
        user_id: User ObjectId as string
        content: Text content that was embedded
        content_type: Type of content (user_query, assistant_response, etc.)
        embedding: Vector embedding list
        embedding_model: Model used to generate embedding
        session_id: Optional source session ID
        conversation_id: Optional source conversation ID
        metadata: Optional additional metadata
    
    Returns:
        Dict with default field values for a new memory vector.
    """
    from datetime import datetime, timezone
    from bson import ObjectId
    
    now = datetime.now(timezone.utc)
    
    doc = {
        "user_id": ObjectId(user_id),
        "session_id": ObjectId(session_id) if session_id else None,
        "conversation_id": ObjectId(conversation_id) if conversation_id else None,
        "content": content,
        "content_type": content_type,
        "embedding": embedding,
        "embedding_model": embedding_model,
        "metadata": metadata or {
            "symbols": [],
            "topics": [],
            "sentiment": None,
            "importance_score": None,
            "source_message_ids": []
        },
        "created_at": now,
        "expires_at": None
    }
    
    return doc


def build_vector_search_query(
    query_embedding: List[float],
    user_id: str,
    limit: int = 10,
    content_types: List[str] = None,
    symbols: List[str] = None,
    min_score: float = 0.7
) -> Dict[str, Any]:
    """
    Build MongoDB Atlas Vector Search aggregation pipeline.
    
    Args:
        query_embedding: Query vector embedding
        user_id: User to search within
        limit: Maximum results to return
        content_types: Optional filter by content types
        symbols: Optional filter by stock symbols
        min_score: Minimum similarity score threshold
    
    Returns:
        Aggregation pipeline for vector search.
    """
    from bson import ObjectId
    
    # Build filter
    filter_conditions = {
        "user_id": ObjectId(user_id)
    }
    
    if content_types:
        filter_conditions["content_type"] = {"$in": content_types}
    
    if symbols:
        filter_conditions["metadata.symbols"] = {"$in": symbols}
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "memory_vectors_search",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": limit * 10,  # Oversample for filtering
                "limit": limit,
                "filter": filter_conditions
            }
        },
        {
            "$addFields": {
                "score": {"$meta": "vectorSearchScore"}
            }
        },
        {
            "$match": {
                "score": {"$gte": min_score}
            }
        },
        {
            "$project": {
                "embedding": 0  # Exclude large embedding field
            }
        }
    ]
    
    return pipeline


# -----------------------------------------------------------------------------
# Implementation Status
# -----------------------------------------------------------------------------

"""
IMPLEMENTATION STATUS: FUTURE (Phase 2A.2+)

This schema is designed and documented but not yet implemented.
Implementation requires:

1. MongoDB Atlas cluster with Vector Search enabled
2. Embedding generation service integration
3. Memory extraction pipeline from conversations
4. Vector search retrieval tool for agent

See PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md for timeline.
"""
