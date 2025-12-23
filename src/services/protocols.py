"""Protocol definitions for service contracts.

This module defines minimal interfaces (protocols) that services can depend on
without creating tight coupling to concrete implementations. This prevents
circular dependencies and improves testability.

Protocols use structural subtyping (duck typing) - any object that implements
the required methods automatically satisfies the protocol.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Protocol, Union, runtime_checkable

if TYPE_CHECKING:
    from core.types import AgentResponse


@runtime_checkable
class AgentProvider(Protocol):
    """Minimal interface for AI agent query processing.
    
    This protocol defines the agent-related methods that ChatService needs.
    By depending on the protocol instead of the concrete StockAgent,
    we avoid tight coupling and improve testability.
    
    Any object implementing these methods can be used as an AgentProvider,
    including the full StockAgent, test mocks, or alternative implementations.
    
    The protocol supports both legacy string responses and new structured
    AgentResponse objects for gradual migration.
    """
    
    def process_query(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
    ) -> str:
        """Process a query and return complete response.
        
        Args:
            query: User query to process
            provider: Optional provider override (e.g., 'openai', 'grok')
            
        Returns:
            Complete response text
        """
        ...
    
    def process_query_streaming(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Process a query and stream response chunks.
        
        Args:
            query: User query to process
            provider: Optional provider override (e.g., 'openai', 'grok')
            
        Yields:
            Response text chunks
        """
        ...
    
    def process_query_structured(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
    ) -> "AgentResponse":
        """Process a query and return structured response.
        
        This method returns a full AgentResponse with metadata,
        status, tool calls, and token usage information.
        
        Args:
            query: User query to process
            provider: Optional provider override (e.g., 'openai', 'grok')
            
        Returns:
            AgentResponse with content and metadata
        """
        ...


@runtime_checkable
class WorkspaceProvider(Protocol):
    """Minimal interface for workspace data access.
    
    This protocol defines the workspace-related methods that other services
    (like UserService) need to call. By depending on the protocol instead of
    the concrete WorkspaceService, we avoid circular dependencies.
    
    Any object implementing these methods can be used as a WorkspaceProvider,
    including the full WorkspaceService, test mocks, or alternative implementations.
    """
    
    def list_workspaces(
        self,
        user_id: str,
        *,
        limit: int,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """Return workspaces for a user.
        
        Args:
            user_id: The user identifier
            limit: Maximum number of workspaces to return
            use_cache: Whether to use cached data if available
            
        Returns:
            List of workspace dictionaries
        """
        ...


@runtime_checkable
class SymbolProvider(Protocol):
    """Minimal interface for symbol data access.
    
    This protocol defines the symbol-related methods that other services
    (like UserService) need to call. By depending on the protocol instead of
    the concrete SymbolsService, we avoid circular dependencies.
    
    Any object implementing these methods can be used as a SymbolProvider,
    including the full SymbolsService, test mocks, or alternative implementations.
    """
    
    def get_symbol(
        self,
        symbol: str,
        *,
        use_cache: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Return symbol metadata.
        
        Args:
            symbol: The ticker symbol (e.g., 'AAPL')
            use_cache: Whether to use cached data if available
            
        Returns:
            Symbol metadata dictionary, or None if not found
        """
        ...
