"""Conversation tracking service for session persistence.

This service manages conversation lifecycle and statistics tracking,
providing a clean interface between the chat layer and conversation storage.

Specification Reference: FR-3.1 Short-Term Memory (Conversation Context)
- FR-3.1.2: Session identifier binds memory state to conversation
- FR-3.1.3: Metrics are tracked per session (message count, tokens)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from data.repositories.conversation_repository import ConversationRepository
from services.base import BaseService
from utils.cache import CacheBackend


class ConversationService(BaseService):
    """Orchestrates conversation tracking and statistics.
    
    Responsibilities:
    - Track message activity (counts, tokens) per session
    - Manage conversation lifecycle (create, lookup, archive)
    - Provide conversation statistics for monitoring
    - Cache conversation metadata for performance
    
    This service encapsulates conversation-specific logic, separating
    storage concerns from chat orchestration.
    """
    
    # Cache TTLs (in seconds)
    CONVERSATION_CACHE_TTL = 300  # 5 minutes for conversation metadata
    
    # Token estimation: ~4 characters per token (rough approximation)
    CHARS_PER_TOKEN = 4
    
    def __init__(
        self,
        *,
        conversation_repository: ConversationRepository,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], datetime]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize ConversationService.
        
        Args:
            conversation_repository: Repository for conversation persistence
            cache: Optional cache backend for conversation metadata
            time_provider: Optional callable returning current UTC datetime (for testing)
            logger: Optional logger instance
        """
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._repository = conversation_repository
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """Check service health.
        
        Service is healthy if conversation repository is available.
        
        Returns:
            Tuple of (healthy: bool, details: dict)
        """
        return self._dependencies_health_report(
            required={"conversation_repository": self._repository},
        )
    
    def track_message(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Track a message in the conversation, updating statistics.
        
        This method ensures the conversation exists (creating if needed)
        and atomically updates the message count and token estimate.
        
        Args:
            session_id: Unique session/thread identifier
            role: Message role ("user", "assistant", "system")
            content: Message text content
            workspace_id: Optional workspace context for new conversations
            user_id: Optional user ID for new conversations
            
        Returns:
            Updated conversation document, or None if tracking failed
            
        Example:
            >>> service.track_message("sess-123", "user", "What is AAPL?")
            {"session_id": "sess-123", "message_count": 1, "total_tokens": 6, ...}
        """
        if not session_id or not content:
            self.logger.warning(
                "track_message called with empty session_id or content"
            )
            return None
        
        # Ensure conversation exists (creates if needed)
        conversation = self._repository.get_or_create(
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        
        if not conversation:
            self.logger.error(f"Failed to get_or_create conversation: {session_id}")
            return None
        
        # Calculate token estimate for this message
        token_delta = self._estimate_tokens(content)
        
        # Atomically update activity counters
        updated = self._repository.update_activity(
            session_id=session_id,
            message_count_delta=1,
            token_delta=token_delta,
        )
        
        if updated:
            # Invalidate cache since stats changed
            self._invalidate_conversation_cache(session_id)
            self.logger.debug(
                f"Tracked message in {session_id}: +1 message, +{token_delta} tokens"
            )
        
        return updated
    
    def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by session ID.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Conversation document or None if not found
        """
        if not session_id:
            return None
        
        # Try cache first
        cache_key = self._conversation_cache_key(session_id)
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached
        
        # Fetch from repository
        conversation = self._repository.find_by_session_id(session_id)
        
        # Cache for future lookups
        if conversation and self.cache:
            self.cache.set_json(cache_key, conversation, ttl_seconds=self.CONVERSATION_CACHE_TTL)
        
        return conversation
    
    def get_conversation_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a conversation.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Statistics dict with message_count, total_tokens, duration, etc.
            or None if conversation not found
        """
        conversation = self.get_conversation(session_id)
        if not conversation:
            return None
        
        # Calculate session duration
        created_at = conversation.get("created_at")
        last_activity = conversation.get("last_activity_at", conversation.get("updated_at"))
        
        duration_seconds = None
        if created_at and last_activity:
            try:
                # Handle both datetime objects and ISO strings
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
                duration_seconds = (last_activity - created_at).total_seconds()
            except (ValueError, TypeError):
                pass
        
        return {
            "session_id": session_id,
            "message_count": conversation.get("message_count", 0),
            "total_tokens": conversation.get("total_tokens", 0),
            "status": conversation.get("status", "active"),
            "duration_seconds": duration_seconds,
            "created_at": conversation.get("created_at"),
            "last_activity_at": last_activity,
        }
    
    def list_active_conversations(
        self,
        user_id: str,
        *,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List active conversations for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return
            
        Returns:
            List of active conversation documents
        """
        if not user_id:
            return []
        
        return self._repository.find_active_by_user(user_id, limit=limit)
    
    def archive_conversation(self, session_id: str) -> bool:
        """Archive a conversation (soft delete).
        
        Archived conversations become immutable per ADR-001.
        
        Args:
            session_id: Session to archive
            
        Returns:
            True if archived successfully, False otherwise
        """
        if not session_id:
            return False
        
        result = self._repository.archive(session_id)
        
        if result:
            self._invalidate_conversation_cache(session_id)
            self.logger.info(f"Archived conversation: {session_id}")
            return True
        
        return False
    
    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count from text.
        
        Uses a simple character-based approximation. For production,
        consider using tiktoken for accurate counts per model.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count (minimum 1)
        """
        if not text:
            return 0
        return max(1, len(text) // self.CHARS_PER_TOKEN)
    
    def _conversation_cache_key(self, session_id: str) -> str:
        """Generate cache key for conversation metadata."""
        return f"conversation:{session_id}"
    
    def _invalidate_conversation_cache(self, session_id: str) -> None:
        """Invalidate cached conversation data."""
        if self.cache:
            cache_key = self._conversation_cache_key(session_id)
            self.cache.delete(cache_key)
