"""
Core package for DP Stock-Investment Assistant.
"""

# package marker for `core`
# (can be empty)

from .agent import StockAgent
from .ai_client import AIClient
from .data_manager import DataManager

__all__ = ['StockAgent', 'AIClient', 'DataManager']


