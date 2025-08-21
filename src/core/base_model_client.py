"""Base model client abstraction for multi-provider support."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Generator, Optional


class BaseModelClient(ABC):
    """Abstract base class for model providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, *, context: Optional[str] = None) -> str:
        """Synchronous text generation."""
        ...

    @abstractmethod
    def generate_stream(self, prompt: str, *, context: Optional[str] = None) -> Generator[str, None, None]:
        """Streaming generation yielding chunks."""
        ...

    @property
    @abstractmethod
    def provider(self) -> str:
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...

    def supports_web_search(self) -> bool:
        """Optional capability flag."""
        return False

    def generate_with_search(self, prompt: str, *, context: Optional[str] = None) -> str:
        """Override if provider implements native web/search tooling."""
        return self.generate(prompt, context=context)