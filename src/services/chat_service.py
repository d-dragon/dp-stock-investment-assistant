"""Chat orchestration service for SSE streaming and response metadata."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generator, List, Mapping, Optional, Tuple

from core.types import AgentResponse, ResponseStatus
from services.base import BaseService
from services.exceptions import ArchivedConversationError
from services.protocols import AgentProvider, ConversationProvider, SessionProvider
from utils.cache import CacheBackend


class ChatService(BaseService):
    """Orchestrates chat streaming, fallback detection, and metadata extraction.
    
    Validates conversation status before processing. Uses conversation_id
    as the primary identity for STM memory binding.
    
    Migration-window dual-path contract (FR-D15 / SC-012):
        Both legacy stateless requests (conversation_id=None) and
        hierarchy-aware requests (with conversation_id) are supported
        simultaneously. Guard clauses in _validate_conversation_active,
        _ensure_conversation_exists, _record_message_metadata, and
        _load_conversation_context all return early when conversation_id
        is None, preserving the stateless path without reintroducing the
        deprecated session_id == thread_id caller model.
    """
    
    MODEL_METADATA_CACHE_TTL = 60
    
    def __init__(
        self,
        *,
        agent_provider: AgentProvider,
        config: Mapping[str, Any],
        cache: Optional[CacheBackend] = None,
        conversation_provider: Optional[ConversationProvider] = None,
        session_provider: Optional["SessionProvider"] = None,
        time_provider: Optional[Callable[[], str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._agent = agent_provider
        self._config = config
        self._conversation_provider = conversation_provider
        self._session_provider = session_provider
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        return self._dependencies_health_report(
            required={"agent": self._agent},
            optional={
                "conversation_provider": self._conversation_provider,
                "session_provider": self._session_provider,
            },
        )
    
    def _validate_conversation_active(self, conversation_id: Optional[str]) -> None:
        """Validate that a conversation is not archived.
        
        Raises:
            ArchivedConversationError: If the conversation exists and is archived
        """
        if conversation_id is None:
            return
        if self._conversation_provider is None:
            self.logger.debug("No conversation provider for validation")
            return
        conversation = self._conversation_provider.get_conversation(conversation_id)
        if conversation is None:
            return  # will be created on first message
        status = conversation.get("status", "active")
        if status == "archived":
            self.logger.warning(f"Rejected message to archived conversation: {conversation_id}")
            raise ArchivedConversationError(conversation_id)
    
    def _ensure_conversation_exists(self, conversation_id: Optional[str]) -> None:
        """Auto-create conversation record if it doesn't exist (FR-D01).
        
        Non-blocking: logs warning on failure to avoid disrupting chat flow.
        """
        if not conversation_id or not self._conversation_provider:
            return
        try:
            self._conversation_provider.ensure_conversation_exists(conversation_id)
        except Exception as e:
            self.logger.warning(
                f"Auto-create conversation failed for {conversation_id}: {e}"
            )
    
    def _record_message_metadata(
        self,
        conversation_id: Optional[str],
        *,
        tokens_used: int = 0,
        symbols: Optional[List[str]] = None,
    ) -> None:
        """Record per-turn metadata after agent response (FR-D02/FR-D03).
        
        Non-blocking: logs warning on failure so the chat response is
        never disrupted by a metadata-write error.
        """
        if not conversation_id or not self._conversation_provider:
            return
        try:
            self._conversation_provider.record_message_metadata(
                conversation_id, tokens_used=tokens_used, symbols=symbols,
            )
        except Exception as e:
            self.logger.warning(
                f"Metadata recording failed for {conversation_id}: {e}"
            )
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token estimate (~4 chars per token)."""
        return max(len(text) // 4, 1) if text else 0
    
    def _load_conversation_context(
        self, conversation_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Load session context and merge with conversation overrides.
        
        Returns merged context dict or None if unavailable.
        """
        if not conversation_id or not self._conversation_provider or not self._session_provider:
            return None
        conversation = self._conversation_provider.get_conversation(conversation_id)
        if not conversation:
            return None
        session_id = conversation.get("session_id")
        if not session_id:
            return None
        session_ctx = self._session_provider.get_session_context(session_id)
        if not session_ctx:
            return None
        # Merge: conversation overrides shallow-replace session context keys
        overrides = conversation.get("context_overrides") or {}
        merged = {**session_ctx, **overrides}
        return merged
    
    def stream_chat_response(
        self, user_message: str, provider_override: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream chat response in SSE format.
        
        Raises:
            ArchivedConversationError: If the conversation is archived
        """
        self._validate_conversation_active(conversation_id)
        self._ensure_conversation_exists(conversation_id)
        
        try:
            self.logger.info(f"Starting streaming response: {user_message[:50]}...")
            
            # Load session context for this conversation (FR-012a)
            context = self._load_conversation_context(conversation_id)
            if context:
                self.logger.debug(f"Loaded session context for conversation={conversation_id}")
            
            model_info = self._agent.get_current_model_info(provider=provider_override)
            meta = {
                "event": "meta",
                "provider": model_info["provider"],
                "model": model_info["model"],
            }
            yield f"data: {json.dumps(meta)}\n\n"
            
            chunk_count = 0
            full_text_parts = []
            for chunk in self._agent.process_query_streaming(
                user_message, provider=provider_override, conversation_id=conversation_id
            ):
                if chunk:
                    chunk_count += 1
                    full_text_parts.append(chunk)
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
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
            
            # Non-blocking metadata recording (FR-D02/FR-D03)
            self._record_message_metadata(
                conversation_id,
                tokens_used=self._estimate_tokens(full_text),
            )
        
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
        self, user_message: str, provider_override: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process chat query (non-streaming).
        
        Raises:
            ArchivedConversationError: If the conversation is archived
        """
        self._validate_conversation_active(conversation_id)
        self._ensure_conversation_exists(conversation_id)
        
        # Load session context for this conversation (FR-012a)
        self._load_conversation_context(conversation_id)
        
        raw_response = self._agent.process_query(
            user_message, provider=provider_override, conversation_id=conversation_id
        )
        
        model_info = self._agent.get_current_model_info(provider=provider_override)
        provider, model, fallback = self.extract_meta(raw_response)
        
        if model_info:
            provider = provider or model_info.get("provider")
            model = model or model_info.get("model")
        
        cleaned_response = self.strip_fallback_prefix(raw_response)
        
        # Non-blocking metadata recording (FR-D02/FR-D03)
        self._record_message_metadata(
            conversation_id,
            tokens_used=self._estimate_tokens(raw_response),
        )
        
        return {
            "response": cleaned_response,
            "provider": provider,
            "model": model,
            "fallback": fallback,
            "timestamp": self.get_timestamp(),
        }
    
    def process_chat_query_structured(
        self, user_message: str, provider_override: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> AgentResponse:
        """Process chat query and return structured AgentResponse."""
        try:
            response = self._agent.process_query_structured(
                user_message, provider=provider_override, conversation_id=conversation_id
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
        self, user_message: str, provider_override: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Stream chat response with structured completion metadata (SSE)."""
        try:
            self.logger.info(f"Starting structured streaming: {user_message[:50]}...")
            
            model_info = self._agent.get_current_model_info(provider=provider_override)
            meta = {
                "event": "meta",
                "provider": model_info["provider"],
                "model": model_info["model"],
            }
            yield f"data: {json.dumps(meta)}\n\n"
            
            chunk_count = 0
            for chunk in self._agent.process_query_streaming(
                user_message, provider=provider_override, conversation_id=conversation_id
            ):
                if chunk:
                    chunk_count += 1
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            response = self._agent.process_query_structured(
                user_message, provider=provider_override, conversation_id=conversation_id
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
    

