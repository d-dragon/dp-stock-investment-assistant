"""Core type definitions for the LangChain agent architecture.

This module defines structured response types and enums used throughout
the agent system. Using frozen dataclasses ensures immutability and
provides clear contracts for agent outputs.

Reference: .github/instructions/backend-python.instructions.md § Service Layer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ResponseStatus(Enum):
    """Status of agent response processing.
    
    Used to indicate the outcome of a query without parsing string prefixes.
    
    Values:
        SUCCESS: Query processed successfully with primary model
        FALLBACK: Query processed using fallback model after primary failed
        ERROR: Query processing failed completely
        PARTIAL: Query partially processed (e.g., some tools failed)
    """
    SUCCESS = "success"
    FALLBACK = "fallback"
    ERROR = "error"
    PARTIAL = "partial"


@dataclass(frozen=True)
class ToolCall:
    """Record of a tool invocation during agent processing.
    
    Captures tool execution details for debugging, logging, and analytics.
    
    Attributes:
        name: Tool name (e.g., 'stock_price', 'technical_analysis')
        input: Input parameters passed to the tool
        output: Tool execution result
        cached: Whether result was served from cache
        execution_time_ms: Tool execution time in milliseconds
    """
    name: str
    input: Dict[str, Any]
    output: Any
    cached: bool = False
    execution_time_ms: Optional[float] = None


@dataclass(frozen=True)
class TokenUsage:
    """Token usage statistics for an agent response.
    
    Tracks token consumption for cost monitoring and optimization.
    
    Attributes:
        prompt_tokens: Tokens used in the prompt/input
        completion_tokens: Tokens generated in the response
        total_tokens: Total tokens consumed (prompt + completion)
    """
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    @classmethod
    def from_openai_usage(cls, usage: Optional[Dict[str, Any]]) -> "TokenUsage":
        """Create TokenUsage from OpenAI API usage response.
        
        Args:
            usage: OpenAI usage dict with prompt_tokens, completion_tokens, total_tokens
            
        Returns:
            TokenUsage instance, or empty instance if usage is None
        """
        if not usage:
            return cls()
        return cls(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
        )


@dataclass(frozen=True)
class AgentResponse:
    """Structured response from agent query processing.
    
    Replaces string-based responses with '[fallback:]' prefixes.
    Provides clear contract for agent outputs with metadata.
    
    Attributes:
        content: The actual response text/content
        provider: Model provider used ('openai', 'grok')
        model: Specific model name (e.g., 'gpt-4', 'grok-beta')
        status: Processing status (SUCCESS, FALLBACK, ERROR, PARTIAL)
        tool_calls: List of tools invoked during processing
        token_usage: Token consumption statistics
        cached: Whether the entire response was served from cache
        error_message: Error details if status is ERROR
        metadata: Additional provider-specific metadata
    
    Example:
        >>> response = AgentResponse(
        ...     content="AAPL is trading at $150.25",
        ...     provider="openai",
        ...     model="gpt-4",
        ...     status=ResponseStatus.SUCCESS,
        ... )
        >>> response.is_success
        True
    """
    content: str
    provider: str
    model: str
    status: ResponseStatus = ResponseStatus.SUCCESS
    tool_calls: tuple[ToolCall, ...] = field(default_factory=tuple)
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    cached: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure tool_calls is always a tuple for immutability."""
        if isinstance(self.tool_calls, list):
            # Use object.__setattr__ since frozen=True
            object.__setattr__(self, 'tool_calls', tuple(self.tool_calls))
    
    @property
    def is_success(self) -> bool:
        """Check if response completed successfully (including fallback)."""
        return self.status in (ResponseStatus.SUCCESS, ResponseStatus.FALLBACK)
    
    @property
    def is_error(self) -> bool:
        """Check if response represents an error."""
        return self.status == ResponseStatus.ERROR
    
    @property
    def used_fallback(self) -> bool:
        """Check if fallback model was used."""
        return self.status == ResponseStatus.FALLBACK
    
    @classmethod
    def error(
        cls,
        message: str,
        provider: str = "unknown",
        model: str = "unknown",
    ) -> "AgentResponse":
        """Create an error response.
        
        Args:
            message: Error message describing what went wrong
            provider: Provider that was attempted
            model: Model that was attempted
            
        Returns:
            AgentResponse with ERROR status
        """
        return cls(
            content=message,
            provider=provider,
            model=model,
            status=ResponseStatus.ERROR,
            error_message=message,
        )
    
    @classmethod
    def success(
        cls,
        content: str,
        provider: str,
        model: str,
        **kwargs: Any,
    ) -> "AgentResponse":
        """Create a successful response.
        
        Args:
            content: Response content
            provider: Provider used
            model: Model used
            **kwargs: Additional attributes (tool_calls, token_usage, etc.)
            
        Returns:
            AgentResponse with SUCCESS status
        """
        return cls(
            content=content,
            provider=provider,
            model=model,
            status=ResponseStatus.SUCCESS,
            **kwargs,
        )
    
    @classmethod
    def fallback(
        cls,
        content: str,
        provider: str,
        model: str,
        **kwargs: Any,
    ) -> "AgentResponse":
        """Create a fallback response.
        
        Args:
            content: Response content from fallback model
            provider: Fallback provider used
            model: Fallback model used
            **kwargs: Additional attributes
            
        Returns:
            AgentResponse with FALLBACK status
        """
        return cls(
            content=content,
            provider=provider,
            model=model,
            status=ResponseStatus.FALLBACK,
            **kwargs,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the response
        """
        return {
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "status": self.status.value,
            "tool_calls": [
                {
                    "name": tc.name,
                    "input": tc.input,
                    "output": tc.output,
                    "cached": tc.cached,
                    "execution_time_ms": tc.execution_time_ms,
                }
                for tc in self.tool_calls
            ],
            "token_usage": {
                "prompt_tokens": self.token_usage.prompt_tokens,
                "completion_tokens": self.token_usage.completion_tokens,
                "total_tokens": self.token_usage.total_tokens,
            },
            "cached": self.cached,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


# Type alias for streaming responses
StreamingAgentResponse = tuple[AgentResponse, List[str]]
"""Tuple of (final_response, list_of_chunks) for streaming operations."""
