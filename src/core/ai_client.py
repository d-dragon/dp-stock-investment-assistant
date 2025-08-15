"""
Backward-compatible AIClient wrapper.
Redirects to OpenAIModelClient. Will be deprecated.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Generator
import logging
from .openai_model_client import OpenAIModelClient


class AIClient:
    """Legacy interface retained to avoid breaking imports."""

    def __init__(self, config: Dict[str, Any]):
        self._delegate = OpenAIModelClient(config)
        self.logger = logging.getLogger(__name__)
        self.logger.warning("AIClient is deprecated; use ModelClientFactory / OpenAIModelClient.")

    def web_search_response(self, query: str, context: Optional[str] = None) -> str:
        if self._delegate.supports_web_search():
            return self._delegate.generate_with_search(query, context=context)
        return self._delegate.generate(query, context=context)

    def web_search_response_streaming(self, query: str, context: Optional[str] = None):
        return self._delegate.generate_stream(query, context=context)

    def generate_response(self, query: str, context: Optional[str] = None) -> str:
        return self._delegate.generate(query, context=context)
