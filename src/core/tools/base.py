"""Base tool class with caching support.

Provides CachingTool abstract base class that extends LangChain's BaseTool
with Redis/in-memory caching integration.

Reference: .github/instructions/backend-python.instructions.md § Cache Backend
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from abc import abstractmethod
from typing import Any, Dict, Optional, Type, Callable

from langchain_core.tools import BaseTool
from pydantic import Field

from src.core.types import ToolCall
from src.utils.cache import CacheBackend


class CachingTool(BaseTool):
    """Abstract base class for tools with caching support.
    
    Extends LangChain's BaseTool to provide:
    - Automatic caching via Redis/in-memory CacheBackend
    - Configurable TTL per tool type
    - ToolCall tracking for analytics
    - Async wrapper that delegates to sync implementation
    
    Subclasses must implement:
    - _execute(): The actual tool logic
    - name: Tool name for LangChain
    - description: Tool description for LLM
    
    Attributes:
        cache: Optional CacheBackend for result caching
        cache_ttl_seconds: Cache TTL in seconds (default 60)
        enable_cache: Whether caching is enabled (default True)
    
    Example:
        >>> class MyTool(CachingTool):
        ...     name = "my_tool"
        ...     description = "Does something useful"
        ...     
        ...     def _execute(self, query: str) -> str:
        ...         return f"Result for {query}"
    """
    
    # Pydantic fields (serializable)
    cache_ttl_seconds: int = Field(default=60, description="Cache TTL in seconds")
    enable_cache: bool = Field(default=True, description="Whether caching is enabled")
    
    # Class variable for non-serializable cache backend
    _cache: Optional[CacheBackend] = None
    _logger: Optional[logging.Logger] = None
    
    class Config:
        """Pydantic config to allow arbitrary types."""
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        cache: Optional[CacheBackend] = None,
        cache_ttl_seconds: int = 60,
        enable_cache: bool = True,
        logger: Optional[logging.Logger] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CachingTool.
        
        Args:
            cache: CacheBackend instance for caching (Redis or in-memory)
            cache_ttl_seconds: TTL for cached results in seconds
            enable_cache: Whether to enable caching
            logger: Optional logger instance
            **kwargs: Additional BaseTool arguments
        """
        super().__init__(
            cache_ttl_seconds=cache_ttl_seconds,
            enable_cache=enable_cache,
            **kwargs,
        )
        # Store non-serializable objects as class attributes
        object.__setattr__(self, '_cache', cache)
        object.__setattr__(self, '_logger', logger or logging.getLogger(self.__class__.__name__))
    
    @property
    def cache(self) -> Optional[CacheBackend]:
        """Get the cache backend."""
        return self._cache
    
    @property
    def logger(self) -> logging.Logger:
        """Get the logger."""
        return self._logger or logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def _execute(self, **kwargs: Any) -> Any:
        """Execute the tool logic.
        
        Subclasses must implement this method with the actual tool logic.
        
        Args:
            **kwargs: Tool-specific input arguments
            
        Returns:
            Tool execution result
            
        Raises:
            Exception: If tool execution fails
        """
        pass
    
    def _generate_cache_key(self, **kwargs: Any) -> str:
        """Generate a cache key from input arguments.
        
        Creates a deterministic hash key based on tool name and inputs.
        
        Args:
            **kwargs: Input arguments to hash
            
        Returns:
            Cache key string in format 'tool:{name}:{hash}'
        """
        # Sort kwargs for deterministic hashing
        sorted_args = json.dumps(kwargs, sort_keys=True, default=str)
        hash_digest = hashlib.md5(sorted_args.encode()).hexdigest()[:12]
        return f"tool:{self.name}:{hash_digest}"
    
    def _cached_run(self, **kwargs: Any) -> tuple[Any, bool]:
        """Execute tool with caching support.
        
        Checks cache first, then executes and caches result.
        
        Args:
            **kwargs: Tool input arguments
            
        Returns:
            Tuple of (result, was_cached)
        """
        cache_key = self._generate_cache_key(**kwargs)
        
        # Check cache
        if self.enable_cache and self._cache:
            cached_result = self._cache.get_json(cache_key)
            if cached_result is not None:
                self.logger.debug(f"Cache HIT for {self.name}: {cache_key}")
                return cached_result, True
        
        # Execute and cache
        result = self._execute(**kwargs)
        
        if self.enable_cache and self._cache and result is not None:
            try:
                self._cache.set_json(cache_key, result, ttl_seconds=self.cache_ttl_seconds)
                self.logger.debug(f"Cached result for {self.name}: {cache_key} (TTL={self.cache_ttl_seconds}s)")
            except Exception as e:
                self.logger.warning(f"Failed to cache result for {self.name}: {e}")
        
        return result, False
    
    def _run(self, **kwargs: Any) -> Any:
        """LangChain sync execution entry point.
        
        This method is called by LangChain when invoking the tool.
        Uses caching wrapper and tracks execution metrics.
        
        Args:
            **kwargs: Tool input arguments (parsed from LLM)
            
        Returns:
            Tool execution result
        """
        start_time = time.perf_counter()
        
        try:
            result, was_cached = self._cached_run(**kwargs)
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            self.logger.info(
                f"Tool {self.name} executed: cached={was_cached}, "
                f"time={execution_time_ms:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool {self.name} failed: {e}", exc_info=True)
            raise
    
    async def _arun(self, **kwargs: Any) -> Any:
        """LangChain async execution entry point.
        
        Wraps sync implementation for now. Can be optimized later
        with true async implementations in subclasses.
        
        Args:
            **kwargs: Tool input arguments
            
        Returns:
            Tool execution result
        """
        # Run sync version in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._run(**kwargs))
    
    def create_tool_call(
        self,
        input_args: Dict[str, Any],
        output: Any,
        cached: bool,
        execution_time_ms: float,
    ) -> ToolCall:
        """Create a ToolCall record for tracking.
        
        Args:
            input_args: Input arguments passed to tool
            output: Tool execution result
            cached: Whether result was from cache
            execution_time_ms: Execution time in milliseconds
            
        Returns:
            ToolCall dataclass instance
        """
        return ToolCall(
            name=self.name,
            input=input_args,
            output=output,
            cached=cached,
            execution_time_ms=execution_time_ms,
        )
    
    def health_check(self) -> tuple[bool, Dict[str, Any]]:
        """Check tool health status.
        
        Returns:
            Tuple of (healthy, details_dict)
        """
        details = {
            "component": f"tool:{self.name}",
            "cache_enabled": self.enable_cache,
            "cache_available": self._cache is not None,
            "cache_ttl_seconds": self.cache_ttl_seconds,
        }
        
        if self._cache:
            try:
                cache_healthy = self._cache.ping()
                details["cache_status"] = "connected" if cache_healthy else "disconnected"
            except Exception as e:
                details["cache_status"] = f"error: {e}"
                cache_healthy = False
        else:
            cache_healthy = True  # No cache required
            details["cache_status"] = "not_configured"
        
        # Tool is healthy if either cache is not required or cache is working
        healthy = not self.enable_cache or cache_healthy
        details["status"] = "ready" if healthy else "degraded"
        
        return healthy, details
