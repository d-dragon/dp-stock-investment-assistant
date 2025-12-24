"""Chat orchestration service for SSE streaming and response metadata."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generator, Mapping, Optional, Tuple

from core.types import AgentResponse, ResponseStatus
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
            
            # Emit model metadata first (delegate to agent)
            model_info = self._agent.get_current_model_info(provider=provider_override)
            meta = {
                "event": "meta",
                "provider": model_info["provider"],
                "model": model_info["model"],
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
    
    def process_chat_query(
        self, user_message: str, provider_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process chat query and return structured response (non-streaming).
        
        This method provides a non-streaming alternative to stream_chat_response,
        returning a complete response dict with metadata.
        
        Args:
            user_message: User's query to process
            provider_override: Optional provider override
            
        Returns:
            Dict with keys:
                - response: str - The cleaned response text
                - provider: str - Provider used
                - model: str - Model used
                - fallback: bool - Whether fallback was used
                - timestamp: str - ISO 8601 timestamp
        """
        # Get response from agent
        raw_response = self._agent.process_query(user_message, provider=provider_override)
        
        # Get model info from agent
        model_info = self._agent.get_current_model_info(provider=provider_override)
        
        # Extract metadata from response
        provider, model, fallback = self.extract_meta(raw_response)
        
        # Use model_info as fallback if extract_meta didn't find metadata
        if model_info:
            provider = provider or model_info.get("provider")
            model = model or model_info.get("model")
        
        # Strip fallback prefix from response
        cleaned_response = self.strip_fallback_prefix(raw_response)
        
        return {
            "response": cleaned_response,
            "provider": provider,
            "model": model,
            "fallback": fallback,
            "timestamp": self.get_timestamp(),
        }
    
    def process_chat_query_structured(
        self, user_message: str, provider_override: Optional[str] = None
    ) -> AgentResponse:
        """Process chat query and return structured AgentResponse.
        
        This method uses the agent's structured response API to get
        full metadata including tool calls and token usage.
        
        Args:
            user_message: User's query to process
            provider_override: Optional provider override
            
        Returns:
            AgentResponse with content, provider, model, status, tool_calls, etc.
        """
        try:
            # Use agent's structured response method
            response = self._agent.process_query_structured(
                user_message, provider=provider_override
            )
            
            self.logger.info(
                f"Structured query processed: status={response.status.value}, "
                f"tools_used={len(response.tool_calls)}"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Structured query error: {e}")
            return AgentResponse.error(
                message=str(e),
                provider="unknown",
                model="unknown",
            )
    
    def stream_chat_response_structured(
        self, user_message: str, provider_override: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream chat response with enhanced metadata (SSE format).
        
        Similar to stream_chat_response but uses AgentResponse for
        richer completion metadata including tool calls and token usage.
        
        Emits SSE events in sequence:
        1. Meta event with provider/model info
        2. Content chunks as they arrive
        3. Done event with full completion metadata
        4. [DONE] terminator
        
        Args:
            user_message: User's query to process
            provider_override: Optional provider override
            
        Yields:
            SSE-formatted strings (data: {...}\n\n)
        """
        try:
            self.logger.info(f"Starting structured streaming: {user_message[:50]}...")
            
            # Emit model metadata first
            model_info = self._agent.get_current_model_info(provider=provider_override)
            meta = {
                "event": "meta",
                "provider": model_info["provider"],
                "model": model_info["model"],
            }
            yield f"data: {json.dumps(meta)}\n\n"
            
            # Stream response chunks
            chunk_count = 0
            for chunk in self._agent.process_query_streaming(
                user_message, provider=provider_override
            ):
                if chunk:
                    chunk_count += 1
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Get structured response for completion metadata
            # (Note: This makes an additional call, so only use when rich metadata is needed)
            response = self._agent.process_query_structured(
                user_message, provider=provider_override
            )
            
            completion = {
                "event": "done",
                "status": response.status.value,
                "fallback": response.used_fallback,
                "provider": response.provider,
                "model": response.model,
                "tools_used": len(response.tool_calls),
                "tool_names": [tc.name for tc in response.tool_calls],
                "token_usage": {
                    "prompt_tokens": response.token_usage.prompt_tokens,
                    "completion_tokens": response.token_usage.completion_tokens,
                    "total_tokens": response.token_usage.total_tokens,
                },
            }
            yield f"data: {json.dumps(completion)}\n\n"
            yield "data: [DONE]\n\n"
            
            self.logger.info(
                f"Structured streaming complete: chunks={chunk_count}, "
                f"tools_used={len(response.tool_calls)}"
            )
        
        except Exception as e:
            self.logger.error(f"Structured streaming error: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
    

