"""Tool Registry for centralized tool management.

Provides singleton pattern for registering, retrieving, and managing
LangChain tools across the application.

Reference: .github/instructions/backend-python.instructions.md § Service Layer
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type

from src.core.tools.base import CachingTool


# Module-level singleton
_registry_instance: Optional["ToolRegistry"] = None


class ToolRegistry:
    """Central registry for managing LangChain tools.
    
    Provides a singleton pattern for:
    - Registering tools by name
    - Retrieving tools by name
    - Listing all registered tools
    - Filtering enabled/disabled tools
    
    Example:
        >>> registry = ToolRegistry.get_instance()
        >>> registry.register(StockSymbolTool(cache=cache))
        >>> tool = registry.get("stock_symbol")
        >>> all_tools = registry.list_all()
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """Initialize ToolRegistry.
        
        Args:
            logger: Optional logger instance
        """
        self._tools: Dict[str, CachingTool] = {}
        self._enabled: Dict[str, bool] = {}
        self._logger = logger or logging.getLogger(self.__class__.__name__)
    
    @classmethod
    def get_instance(cls, logger: Optional[logging.Logger] = None) -> "ToolRegistry":
        """Get singleton instance of ToolRegistry.
        
        Args:
            logger: Optional logger (only used on first call)
            
        Returns:
            ToolRegistry singleton instance
        """
        global _registry_instance
        if _registry_instance is None:
            _registry_instance = cls(logger=logger)
        return _registry_instance
    
    def register(
        self,
        tool: CachingTool,
        *,
        enabled: bool = True,
        replace: bool = False,
    ) -> None:
        """Register a tool in the registry.
        
        Args:
            tool: CachingTool instance to register
            enabled: Whether the tool is enabled for use
            replace: Whether to replace existing tool with same name
            
        Raises:
            ValueError: If tool with same name exists and replace=False
        """
        name = tool.name
        
        if name in self._tools and not replace:
            raise ValueError(
                f"Tool '{name}' already registered. Use replace=True to override."
            )
        
        self._tools[name] = tool
        self._enabled[name] = enabled
        self._logger.info(
            f"Registered tool '{name}' (enabled={enabled}, replace={replace})"
        )
    
    def unregister(self, name: str) -> bool:
        """Remove a tool from the registry.
        
        Args:
            name: Tool name to unregister
            
        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            del self._enabled[name]
            self._logger.info(f"Unregistered tool '{name}'")
            return True
        return False
    
    def get(self, name: str) -> Optional[CachingTool]:
        """Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def is_enabled(self, name: str) -> bool:
        """Check if a tool is enabled.
        
        Args:
            name: Tool name
            
        Returns:
            True if tool exists and is enabled
        """
        return self._enabled.get(name, False)
    
    def set_enabled(self, name: str, enabled: bool) -> bool:
        """Enable or disable a tool.
        
        Args:
            name: Tool name
            enabled: New enabled status
            
        Returns:
            True if tool was found and updated
        """
        if name in self._tools:
            self._enabled[name] = enabled
            self._logger.info(f"Tool '{name}' enabled={enabled}")
            return True
        return False
    
    def list_all(self) -> List[CachingTool]:
        """List all registered tools.
        
        Returns:
            List of all registered tool instances
        """
        return list(self._tools.values())
    
    def list_names(self) -> List[str]:
        """List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def get_enabled_tools(self) -> List[CachingTool]:
        """Get all enabled tools.
        
        Returns:
            List of enabled tool instances
        """
        return [
            tool for name, tool in self._tools.items()
            if self._enabled.get(name, False)
        ]
    
    def get_disabled_tools(self) -> List[CachingTool]:
        """Get all disabled tools.
        
        Returns:
            List of disabled tool instances
        """
        return [
            tool for name, tool in self._tools.items()
            if not self._enabled.get(name, False)
        ]
    
    def clear(self) -> None:
        """Remove all registered tools."""
        self._tools.clear()
        self._enabled.clear()
        self._logger.info("Cleared all registered tools")
    
    def health_check(self) -> tuple[bool, Dict[str, Any]]:
        """Check health of all registered tools.
        
        Returns:
            Tuple of (all_healthy, details_dict)
        """
        tool_health: Dict[str, Dict[str, Any]] = {}
        all_healthy = True
        
        for name, tool in self._tools.items():
            try:
                healthy, details = tool.health_check()
                tool_health[name] = {
                    "healthy": healthy,
                    "enabled": self._enabled.get(name, False),
                    **details,
                }
                if not healthy and self._enabled.get(name, False):
                    all_healthy = False
            except Exception as e:
                tool_health[name] = {
                    "healthy": False,
                    "enabled": self._enabled.get(name, False),
                    "error": str(e),
                }
                if self._enabled.get(name, False):
                    all_healthy = False
        
        return all_healthy, {
            "component": "tool_registry",
            "status": "healthy" if all_healthy else "degraded",
            "total_tools": len(self._tools),
            "enabled_tools": len(self.get_enabled_tools()),
            "tools": tool_health,
        }
    
    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools


def get_tool_registry(logger: Optional[logging.Logger] = None) -> ToolRegistry:
    """Get the singleton ToolRegistry instance.
    
    Convenience function for accessing the registry.
    
    Args:
        logger: Optional logger (only used on first call)
        
    Returns:
        ToolRegistry singleton instance
    """
    return ToolRegistry.get_instance(logger=logger)


def reset_tool_registry() -> None:
    """Reset the ToolRegistry singleton.
    
    Useful for testing to ensure clean state between tests.
    """
    global _registry_instance
    if _registry_instance is not None:
        _registry_instance.clear()
    _registry_instance = None
