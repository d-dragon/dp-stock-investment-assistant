"""
Memory Configuration Module for FR-3.1 Short-Term Memory (STM).

This module provides the MemoryConfig frozen dataclass with fail-fast validation
for all memory-related configuration parameters as specified in FR-3.1.9 and FR-3.1.10.

Key features:
- Immutable configuration (frozen dataclass)
- Fail-fast validation in __post_init__
- Factory method from_config() for YAML loading
- Range validation for all numeric parameters

Reference:
    - Spec: specs/spec-driven-development-pilot/plan.md § MemoryConfig Dataclass Pattern
    - FR-3.1.9: All operational parameters must be externally configurable
    - FR-3.1.10: Invalid configuration must fail immediately with clear error messages

Example:
    >>> from utils.memory_config import MemoryConfig
    >>> config = MemoryConfig.from_config(app_config)
    >>> print(config.summarize_threshold)
    4000
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


# Validation ranges per FR-3.1.10
VALIDATION_RANGES = {
    "summarize_threshold": (1000, 10000),
    "max_messages": (10, 200),
    "messages_to_keep": (5, 50),
    "max_content_size": (1024, 65536),
    "summary_max_length": (100, 2000),
    "context_load_timeout_ms": (100, 5000),
    "state_save_timeout_ms": (10, 500),
}


@dataclass(frozen=True)
class MemoryConfig:
    """
    Immutable configuration for Short-Term Memory (STM) feature.
    
    All parameters are validated on construction per FR-3.1.10 fail-fast requirements.
    Invalid configuration raises ValueError with actionable error message.
    
    Attributes:
        enabled: Master switch for memory functionality (FR-3.1.1)
        summarize_threshold: Token count triggering summarization (FR-3.1.6)
        max_messages: Maximum messages per session before pruning
        messages_to_keep: Messages preserved when pruning (must be < max_messages)
        max_content_size: Maximum bytes for single message content
        summary_max_length: Maximum tokens for generated summary
        context_load_timeout_ms: Performance timeout for context loading (SC-7)
        state_save_timeout_ms: Performance timeout for state persistence
        checkpoint_collection: MongoDB collection name for LangGraph checkpoints
        conversations_collection: MongoDB collection name for app-managed metadata
    
    Raises:
        ValueError: If any parameter is outside valid range or constraint violated
    """
    
    # Feature toggle
    enabled: bool = True
    
    # Summarization settings (FR-3.1.6)
    summarize_threshold: int = 4000  # Valid: 1000-10000
    max_messages: int = 50  # Valid: 10-200
    messages_to_keep: int = 10  # Valid: 5-50, must be < max_messages
    max_content_size: int = 32768  # Valid: 1024-65536
    summary_max_length: int = 500  # Valid: 100-2000
    
    # Performance settings (FR-3.1.9, SC-7)
    context_load_timeout_ms: int = 500  # Valid: 100-5000
    state_save_timeout_ms: int = 50  # Valid: 10-500
    
    # MongoDB collection names (FR-3.1.2)
    checkpoint_collection: str = "agent_checkpoints"
    conversations_collection: str = "conversations"
    
    def __post_init__(self) -> None:
        """
        Validate all parameters on construction (FR-3.1.10 fail-fast).
        
        Raises:
            ValueError: If any parameter is invalid with actionable message
        """
        # Validate enabled is boolean
        if not isinstance(self.enabled, bool):
            raise ValueError(
                f"Invalid 'enabled' value: {self.enabled!r}. "
                f"Must be a boolean (true/false)."
            )
        
        # Validate numeric ranges
        for field_name, (min_val, max_val) in VALIDATION_RANGES.items():
            value = getattr(self, field_name)
            self._validate_range(field_name, value, min_val, max_val)
        
        # Validate messages_to_keep < max_messages constraint
        if self.messages_to_keep >= self.max_messages:
            raise ValueError(
                f"Invalid 'messages_to_keep' value: {self.messages_to_keep}. "
                f"Must be less than 'max_messages' ({self.max_messages}). "
                f"Valid range: 5-50 and < max_messages."
            )
        
        # Validate collection names are non-empty strings
        self._validate_collection_name("checkpoint_collection", self.checkpoint_collection)
        self._validate_collection_name("conversations_collection", self.conversations_collection)
    
    def _validate_range(
        self,
        field_name: str,
        value: Any,
        min_val: int,
        max_val: int
    ) -> None:
        """
        Validate a numeric field is within valid range.
        
        Args:
            field_name: Name of the field for error messages
            value: Value to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
        
        Raises:
            ValueError: If value is not a valid integer or outside range
        """
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(
                f"Invalid '{field_name}' value: {value!r}. "
                f"Must be an integer. Valid range: {min_val}-{max_val}."
            )
        
        if value < min_val or value > max_val:
            raise ValueError(
                f"Invalid '{field_name}' value: {value}. "
                f"Must be between {min_val} and {max_val} (inclusive). "
                f"Current value is {'below' if value < min_val else 'above'} the valid range."
            )
    
    def _validate_collection_name(self, field_name: str, value: Any) -> None:
        """
        Validate a MongoDB collection name is a non-empty string.
        
        Args:
            field_name: Name of the field for error messages
            value: Value to validate
        
        Raises:
            ValueError: If value is not a non-empty string
        """
        if not isinstance(value, str):
            raise ValueError(
                f"Invalid '{field_name}' value: {value!r}. "
                f"Must be a non-empty string."
            )
        
        if not value.strip():
            raise ValueError(
                f"Invalid '{field_name}' value: '{value}'. "
                f"Must be a non-empty string (cannot be blank or whitespace only)."
            )
    
    @classmethod
    def from_config(cls, config_dict: Dict[str, Any]) -> "MemoryConfig":
        """
        Factory method to create MemoryConfig from YAML config dictionary.
        
        Extracts memory configuration from `langchain.memory` section of config.
        Falls back to defaults for missing parameters.
        
        Args:
            config_dict: Application configuration dictionary (from ConfigLoader)
        
        Returns:
            MemoryConfig instance with validated parameters
        
        Raises:
            ValueError: If any parameter is invalid (FR-3.1.10 fail-fast)
        
        Example:
            >>> config = ConfigLoader.load_config()
            >>> memory_config = MemoryConfig.from_config(config)
        """
        # Extract langchain.memory section, with nested fallbacks
        langchain_config = config_dict.get("langchain", {})
        memory_config = langchain_config.get("memory", {})
        
        # Build kwargs from config, using None for missing values (will use defaults)
        kwargs: Dict[str, Any] = {}
        
        # Map config keys to dataclass fields
        field_mappings = {
            "enabled": "enabled",
            "summarize_threshold": "summarize_threshold",
            "max_messages": "max_messages",
            "messages_to_keep": "messages_to_keep",
            "max_content_size": "max_content_size",
            "summary_max_length": "summary_max_length",
            "context_load_timeout_ms": "context_load_timeout_ms",
            "state_save_timeout_ms": "state_save_timeout_ms",
            "checkpoint_collection": "checkpoint_collection",
            "conversations_collection": "conversations_collection",
        }
        
        for config_key, field_name in field_mappings.items():
            value = memory_config.get(config_key)
            if value is not None:
                kwargs[field_name] = value
        
        return cls(**kwargs)
    
    @classmethod
    def disabled(cls) -> "MemoryConfig":
        """
        Factory method to create a disabled MemoryConfig.
        
        Returns:
            MemoryConfig with enabled=False and all default values
        
        Example:
            >>> memory_config = MemoryConfig.disabled()
            >>> assert memory_config.enabled is False
        """
        return cls(enabled=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert MemoryConfig to dictionary for serialization or logging.
        
        Returns:
            Dictionary with all configuration values
        """
        return {
            "enabled": self.enabled,
            "summarize_threshold": self.summarize_threshold,
            "max_messages": self.max_messages,
            "messages_to_keep": self.messages_to_keep,
            "max_content_size": self.max_content_size,
            "summary_max_length": self.summary_max_length,
            "context_load_timeout_ms": self.context_load_timeout_ms,
            "state_save_timeout_ms": self.state_save_timeout_ms,
            "checkpoint_collection": self.checkpoint_collection,
            "conversations_collection": self.conversations_collection,
        }


# Convenience type alias
MemoryConfigDict = Dict[str, Any]
