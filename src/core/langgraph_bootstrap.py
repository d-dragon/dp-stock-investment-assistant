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

Reference: .github/instructions/backend-python.instructions.md
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


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
