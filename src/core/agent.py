"""
Stock Investment Agent - Legacy module for backward compatibility.

DEPRECATED: This module re-exports StockAssistantAgent as StockAgent for 
backward compatibility. New code should import from stock_assistant_agent.

Example:
    # Old way (still works):
    from core.agent import StockAgent
    
    # New way (recommended):
    from core.stock_assistant_agent import StockAssistantAgent
"""

import warnings
from typing import TYPE_CHECKING

# Re-export the new agent with legacy name
from .stock_assistant_agent import StockAssistantAgent

# Alias for backward compatibility
StockAgent = StockAssistantAgent

# Also re-export for convenience
from .stock_assistant_agent import StockAssistantAgent as _Agent


def __getattr__(name: str):
    """Emit deprecation warning when using legacy imports."""
    if name == "StockAgent":
        warnings.warn(
            "StockAgent is deprecated. Use StockAssistantAgent from "
            "core.stock_assistant_agent instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return StockAssistantAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

