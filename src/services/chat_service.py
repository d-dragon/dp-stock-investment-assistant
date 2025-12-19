"""Chat orchestration service for SSE streaming and response metadata."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generator, Mapping, Optional, Tuple

from core.model_factory import ModelClientFactory
from services.base import BaseService
from services.protocols import AgentProvider
from utils.cache import CacheBackend


class ChatService(BaseService):
    """Orchestrates chat streaming, fallback detection, and metadata extraction.
    
    Responsibilities:
    - Stream chat responses in SSE format with metadata events
    - Extract provider/model metadata from agent responses
    - Detect and strip fallback prefixes from responses
    - Generate consistent timestamps for chat events
    
    This service encapsulates chat-specific logic that was previously
    in APIServer, improving separation of concerns and testability.
    """
    
    MODEL_METADATA_CACHE_TTL = 60  # Cache model selection briefly
    
    def __init__(
        self,
        *,
        agent_provider: AgentProvider,
        config: Mapping[str, Any],
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize ChatService.
        
        Args:
            agent_provider: Agent implementing AgentProvider protocol
            config: Application configuration (for model defaults)
            cache: Optional cache backend
            time_provider: Optional time provider for testing
            logger: Optional logger instance
        """
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._agent = agent_provider
        self._config = config
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """Check service health.
        
        Service is healthy if agent dependency is available.
        
        Returns:
            Tuple of (healthy: bool, details: dict)
        """
        return self._dependencies_health_report(
            required={"agent": self._agent},
        )
    
    def stream_chat_response(
        self, user_message: str, provider_override: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream chat response in real-time (SSE format).
        
        Emits SSE events in sequence:
        1. Meta event with provider/model info
        2. Content chunks as they arrive
        3. Done event with completion metadata
        4. [DONE] terminator
        
        Args:
            user_message: User's query to process
            provider_override: Optional provider override
            
        Yields:
            SSE-formatted strings (data: {...}\n\n)
        """
        try:
            self.logger.info(f"Starting streaming response: {user_message[:50]}...")
            
            # Emit model metadata first
            client = (
                ModelClientFactory.get_client(self._config, provider=provider_override)
                if provider_override
                else self._select_default_client()
            )
            meta = {
                "event": "meta",
                "provider": client.provider,
                "model": client.model_name,
            }
            yield f"data: {json.dumps(meta)}\n\n"
            
            # Stream response chunks
            chunk_count = 0
            full_text_parts = []
            for chunk in self._agent.process_query_streaming(
                user_message, provider=provider_override
            ):
                if chunk:
                    chunk_count += 1
                    full_text_parts.append(chunk)
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Emit completion metadata
            full_text = "".join(full_text_parts)
            provider_used, model_used, fallback_flag = self.extract_meta(full_text)
            completion = {
                "event": "done",
                "fallback": fallback_flag,
                "provider": provider_used,
                "model": model_used,
            }
            yield f"data: {json.dumps(completion)}\n\n"
            yield "data: [DONE]\n\n"
            
            self.logger.info(f"Streaming complete chunks={chunk_count}")
        
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
    
    def extract_meta(self, raw: str) -> Tuple[str, str, bool]:
        """Extract provider/model metadata from response, detecting fallback prefix.
        
        Inspects response for fallback prefix pattern: [fallback:provider]
        Returns the provider name from config if no fallback detected.
        
        Args:
            raw: Raw response text from agent
            
        Returns:
            Tuple of (provider: str, model: str, fallback_flag: bool)
        """
        fallback_flag = False
        provider = self._config.get("model", {}).get("provider", "openai")
        model = self._config.get("model", {}).get("name") or self._config.get(
            "openai", {}
        ).get("model", "gpt-4")
        
        if raw.startswith("[fallback:"):
            fallback_flag = True
            try:
                closing = raw.find("]")
                if closing == -1:
                    return provider, model, fallback_flag
                tag = raw[1:closing]
                provider = tag.split(":", 1)[1]
            except Exception:
                pass
        
        return provider, model, fallback_flag
    
    def strip_fallback_prefix(self, raw: str) -> str:
        """Remove [fallback:provider] prefix if present.
        
        Args:
            raw: Raw response text from agent
            
        Returns:
            Cleaned response text without fallback prefix
        """
        if raw.startswith("[fallback:"):
            closing = raw.find("]")
            if closing != -1:
                return raw[closing + 1 :].lstrip()
        return raw
    
    def get_timestamp(self) -> str:
        """Return current UTC timestamp (ISO 8601 with Z suffix).
        
        Delegates to injectable time provider for testability.
        
        Returns:
            ISO 8601 timestamp string (e.g., '2024-01-01T00:00:00Z')
        """
        return self._utc_now()
    
    def _select_default_client(self):
        """Select default model client from config.
        
        Returns:
            Model client instance
        """
        return ModelClientFactory.get_client(self._config)
