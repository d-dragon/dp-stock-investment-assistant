"""Conversation tracking service.

Manages conversation lifecycle, statistics tracking, and context.
conversation_id is the primary identity (1:1 with thread_id).
session_id is the parent FK (one session → many conversations).

Specification Reference: FR-3.1 Short-Term Memory
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from data.repositories.conversation_repository import ConversationRepository
from services.base import BaseService
from services.exceptions import ArchivedConversationError, ConversationNotFoundError
from utils.cache import CacheBackend


class ConversationService(BaseService):
    """Orchestrates conversation tracking and statistics.
    
    Primary identity: conversation_id (unique per conversation).
    """
    
    # Cache TTLs (in seconds)
    CONVERSATION_CACHE_TTL = 300  # 5 minutes
    
    # Token estimation: ~4 characters per token
    CHARS_PER_TOKEN = 4
    
    def __init__(
        self,
        *,
        conversation_repository: ConversationRepository,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], datetime]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._repository = conversation_repository
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        return self._dependencies_health_report(
            required={"conversation_repository": self._repository},
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Create / Lookup
    # ─────────────────────────────────────────────────────────────────
    
    def create_conversation(
        self,
        conversation_id: str,
        thread_id: str,
        session_id: str,
        workspace_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Create a new conversation.
        
        Returns the created document, or None on failure.
        """
        if not all([conversation_id, thread_id, session_id, workspace_id, user_id]):
            self.logger.warning("create_conversation: missing required identifiers")
            return None
        doc = self._repository.create_conversation(
            conversation_id=conversation_id,
            thread_id=thread_id,
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        return doc
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by conversation_id (cache-aware)."""
        if not conversation_id:
            return None
        cache_key = self._conversation_cache_key(conversation_id)
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached
        conversation = self._repository.find_by_conversation_id(conversation_id)
        if conversation and self.cache:
            self.cache.set_json(cache_key, conversation, ttl_seconds=self.CONVERSATION_CACHE_TTL)
        return conversation
    
    def get_or_create_conversation(
        self,
        conversation_id: str,
        thread_id: str,
        session_id: str,
        workspace_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get existing or create new conversation."""
        return self._repository.get_or_create(
            conversation_id=conversation_id,
            thread_id=thread_id,
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Message Tracking
    # ─────────────────────────────────────────────────────────────────
    
    def track_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        *,
        thread_id: Optional[str] = None,
        session_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Track a message, updating statistics.
        
        If the conversation doesn't exist and all FK params are provided,
        creates it automatically (get_or_create).
        """
        if not conversation_id or not content:
            self.logger.warning("track_message: empty conversation_id or content")
            return None
        
        # Ensure conversation exists
        if thread_id and session_id and workspace_id and user_id:
            self._repository.get_or_create(
                conversation_id=conversation_id,
                thread_id=thread_id,
                session_id=session_id,
                workspace_id=workspace_id,
                user_id=user_id,
            )
        
        token_delta = self._estimate_tokens(content)
        updated = self._repository.update_activity(
            conversation_id=conversation_id,
            message_count_delta=1,
            token_delta=token_delta,
        )
        if updated:
            self._invalidate_conversation_cache(conversation_id)
            self.logger.debug(
                f"Tracked message in {conversation_id}: +1 message, +{token_delta} tokens"
            )
        return updated
    
    # ─────────────────────────────────────────────────────────────────
    # Query
    # ─────────────────────────────────────────────────────────────────
    
    def list_conversations(
        self,
        session_id: str,
    ) -> List[Dict[str, Any]]:
        """List all conversations for a session."""
        if not session_id:
            return []
        return self._repository.find_by_session_id(session_id)
    
    def list_active_conversations(
        self,
        user_id: str,
        *,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List active conversations for a user."""
        if not user_id:
            return []
        return self._repository.find_active_by_user(user_id, limit=limit)
    
    def get_conversation_stats(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        created_at = conversation.get("created_at")
        last_activity = conversation.get("last_activity_at", conversation.get("updated_at"))
        duration_seconds = None
        if created_at and last_activity:
            try:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
                duration_seconds = (last_activity - created_at).total_seconds()
            except (ValueError, TypeError):
                pass
        
        return {
            "conversation_id": conversation_id,
            "session_id": conversation.get("session_id"),
            "message_count": conversation.get("message_count", 0),
            "total_tokens": conversation.get("total_tokens", 0),
            "status": conversation.get("status", "active"),
            "duration_seconds": duration_seconds,
            "created_at": conversation.get("created_at"),
            "last_activity_at": last_activity,
        }
    
    # ─────────────────────────────────────────────────────────────────
    # Context overrides (T026)
    # ─────────────────────────────────────────────────────────────────
    
    def get_conversation_with_context(
        self,
        conversation_id: str,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Return conversation with merged context.
        
        Merges thread-local context_overrides on top of the session 
        context to produce the effective context for this conversation.
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        base_context = dict(session_context or {})
        overrides = conversation.get("context_overrides") or {}
        merged = {**base_context, **overrides}
        conversation["effective_context"] = merged
        return conversation
    
    def update_context_overrides(
        self,
        conversation_id: str,
        context_overrides: Optional[Dict[str, Any]],
    ) -> bool:
        """Set thread-local context overrides for a conversation."""
        if not conversation_id:
            return False
        ok = self._repository.update_context_overrides(conversation_id, context_overrides)
        if ok:
            self._invalidate_conversation_cache(conversation_id)
        return ok
    
    # ─────────────────────────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────────────────────────
    
    def archive_conversation(self, conversation_id: str, archive_reason: str = None) -> bool:
        """Archive a conversation (soft delete). Immutable per ADR-001."""
        if not conversation_id:
            return False
        result = self._repository.archive(conversation_id, archive_reason=archive_reason)
        if result:
            self._invalidate_conversation_cache(conversation_id)
            self.logger.info(f"Archived conversation: {conversation_id}")
            return True
        return False
    
    def archive_by_session(self, session_id: str, archive_reason: str = "session_closed") -> int:
        """Archive all conversations in a session (cascade)."""
        if not session_id:
            return 0
        count = self._repository.archive_by_session_id(session_id, archive_reason=archive_reason)
        if count:
            self.logger.info(f"Archived {count} conversations for session {session_id}")
        return count
    
    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    
    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // self.CHARS_PER_TOKEN)
    
    def _conversation_cache_key(self, conversation_id: str) -> str:
        return f"conversation:{conversation_id}"
    
    def _invalidate_conversation_cache(self, conversation_id: str) -> None:
        if self.cache:
            self.cache.delete(self._conversation_cache_key(conversation_id))
