"""
LangGraph Studio Bootstrap Module.

This module provides the entry point for LangGraph Studio/CLI which runs
from project root (where langgraph.json is located). It adds the 'src'
directory to sys.path before importing, allowing the project's standard
import pattern (from core.*, from utils.*, etc.) to work correctly.

Background:
-----------
The project uses PYTHONPATH-based imports where 'src' is added to the path:
    from core.agent import StockAgent
    from utils.config_loader import ConfigLoader

This works for:
    - python src/main.py (Python adds script dir to path)
    - gunicorn wsgi:app (PYTHONPATH=/app/src in Docker)
    - pytest tests/ (conftest.py adds src to path)

However, LangGraph CLI runs from project root:
    langgraph dev  # Runs in project root, not in src/

Without path setup, Python would try:
    from core.agent import StockAgent  # ModuleNotFoundError: No module named 'core'

This bootstrap module solves the issue by:
1. Adding 'src' to sys.path before any imports
2. Importing the agent from stock_assistant_agent
3. Re-exporting the agent graph for Studio

Usage in langgraph.json:
    {
      "graphs": {
        "stock_assistant": "./src/core/langgraph_bootstrap.py:agent"
      }
    }

STM Feature (FR-3.1):
--------------------
This module also provides the checkpointer factory for Short-Term Memory:
    - create_checkpointer(config) - Creates MongoDBSaver if memory enabled
    - Returns None if langchain.memory.enabled=false
    - Uses MemoryConfig for fail-fast validation

Reference: .github/instructions/backend-python.instructions.md
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def _setup_python_path() -> None:
    """Add 'src' directory to sys.path for project imports.
    
    This function is called at module load time to ensure the import
    context is correctly set up before any project imports occur.
    """
    # Determine paths
    # This file: src/core/langgraph_bootstrap.py
    # Project root: ../../ from this file
    bootstrap_dir = Path(__file__).resolve().parent  # src/core
    src_dir = bootstrap_dir.parent  # src
    project_root = src_dir.parent  # project root
    
    # Add 'src' to path if not already present
    src_path = str(src_dir)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Optionally log for debugging (disabled by default)
    if os.environ.get("LANGGRAPH_DEBUG"):
        print(f"[langgraph_bootstrap] Added to sys.path: {src_path}")
        print(f"[langgraph_bootstrap] sys.path: {sys.path[:5]}...")


# Setup path BEFORE any project imports
_setup_python_path()


# Now we can use project-standard imports
from core.stock_assistant_agent import create_stock_assistant_agent
from utils.memory_config import MemoryConfig

# Module-level logger
logger = logging.getLogger(__name__)


def create_checkpointer(config: Dict[str, Any]) -> Optional[Any]:
    """
    Create MongoDBSaver checkpointer if memory is enabled.
    
    This factory function creates a LangGraph MongoDBSaver checkpointer
    for Short-Term Memory (STM) persistence. It uses MemoryConfig for
    fail-fast validation of all configuration parameters.
    
    Args:
        config: Application configuration dict with 'langchain.memory' 
                and 'mongodb' sections.
    
    Returns:
        MongoDBSaver instance if memory enabled, None otherwise.
        
    Raises:
        ValueError: If MemoryConfig validation fails (FR-3.1.10 fail-fast)
        
    Note:
        Connection errors are logged but not raised, allowing the agent
        to operate without memory if MongoDB is temporarily unavailable.
        
    Example:
        >>> from utils.config_loader import ConfigLoader
        >>> config = ConfigLoader.load_config()
        >>> checkpointer = create_checkpointer(config)
        >>> if checkpointer:
        ...     print("Memory enabled")
        
    Reference:
        - FR-3.1.1: Multi-turn conversation context
        - FR-3.1.2: MongoDB-backed persistence
        - plan.md § MongoDBSaver Initialization Pattern
    """
    # Check if memory is enabled (quick exit path)
    memory_section = config.get("langchain", {}).get("memory", {})
    
    if not memory_section.get("enabled", False):
        logger.info("Short-Term Memory disabled (langchain.memory.enabled=false)")
        return None
    
    # Load and validate config with fail-fast semantics (FR-3.1.10)
    # This will raise ValueError if any parameter is invalid
    memory_config = MemoryConfig.from_config(config)
    
    # Get MongoDB connection details
    mongodb_config = config.get("mongodb", {})
    connection_string = mongodb_config.get("uri", "")
    db_name = mongodb_config.get("database", "stock_assistant")
    
    if not connection_string:
        logger.warning(
            "MongoDB connection string not configured. "
            "Short-Term Memory will be disabled."
        )
        return None
    
    try:
        # Import MongoDBSaver here to avoid import errors when package not installed
        from langgraph.checkpoint.mongodb import MongoDBSaver
        
        checkpointer = MongoDBSaver(
            connection_string=connection_string,
            db_name=db_name,
            collection_name=memory_config.checkpoint_collection
        )
        
        logger.info(
            f"MongoDBSaver checkpointer initialized "
            f"(collection={memory_config.checkpoint_collection})"
        )
        
        return checkpointer
        
    except ImportError as e:
        logger.error(
            f"Failed to import MongoDBSaver: {e}. "
            "Ensure langgraph-checkpoint-mongodb is installed."
        )
        return None
        
    except Exception as e:
        # Log connection errors but don't raise - allow agent to work without memory
        logger.error(
            f"Failed to create MongoDBSaver checkpointer: {e}. "
            "Short-Term Memory will be disabled for this session."
        )
        return None


def get_agent():
    """Create and return the stock assistant agent graph.
    
    This is the primary factory function for LangGraph Studio.
    It creates a new agent instance each time, allowing for
    configuration reloading during development.
    
    Returns:
        CompiledStateGraph: The agent executor for Studio
    """
    return create_stock_assistant_agent()


# Module-level export for LangGraph Studio
# Studio imports: "./src/core/langgraph_bootstrap.py:agent"
agent = get_agent()
