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
from data.repositories.session_repository import SessionRepository
from data.repositories.workspace_repository import WorkspaceRepository
from services.base import BaseService
from services.exceptions import (
    ArchivedConversationError,
    ConversationNotFoundError,
    EntityNotFoundError,
    OwnershipViolationError,
    ParentNotFoundError,
)
from utils.cache import CacheBackend
from utils.service_utils import normalize_document, stringify_identifier


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
        session_repository: Optional[SessionRepository] = None,
        workspace_repository: Optional[WorkspaceRepository] = None,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], datetime]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._repository = conversation_repository
        self._session_repo = session_repository
        self._workspace_repo = workspace_repository
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        optional = {}
        if self._session_repo:
            optional["session_repository"] = self._session_repo
        if self._workspace_repo:
            optional["workspace_repository"] = self._workspace_repo
        return self._dependencies_health_report(
            required={"conversation_repository": self._repository},
            optional=optional,
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
    
    def ensure_conversation_exists(self, conversation_id: str) -> None:
        """Ensure a conversation record exists, auto-creating if needed (FR-D01).
        
        Non-blocking: logs a warning on failure so the chat flow is never
        disrupted by a metadata-store error.
        
        Auto-created records use conversation_id as thread_id (1:1 mapping)
        and 'unlinked' placeholders for hierarchy FKs.  Reconciliation
        scans detect and surface these for manual or automated linkage.
        """
        if not conversation_id:
            return
        try:
            existing = self._repository.find_by_conversation_id(conversation_id)
            if existing is not None:
                return
            self._repository.get_or_create(
                conversation_id=conversation_id,
                thread_id=conversation_id,
                session_id="unlinked",
                workspace_id="unlinked",
                user_id="unlinked",
            )
            self.logger.info(f"Auto-created conversation record: {conversation_id}")
        except Exception as e:
            self.logger.warning(
                f"Failed to ensure conversation exists {conversation_id}: {e}"
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
        
        time_range = None
        if conversation.get("created_at") and last_activity:
            time_range = {
                "start": conversation.get("created_at"),
                "end": last_activity,
            }

        return {
            "conversation_id": conversation_id,
            "session_id": conversation.get("session_id"),
            "workspace_id": conversation.get("workspace_id"),
            "message_count": conversation.get("message_count", 0),
            "total_tokens": conversation.get("total_tokens", 0),
            "status": conversation.get("status", "active"),
            "summary": conversation.get("summary"),
            "focused_symbols": conversation.get("focused_symbols", []),
            "time_range": time_range,
            "duration_seconds": duration_seconds,
            "created_at": conversation.get("created_at"),
            "last_activity_at": last_activity,
        }
    
    # ─────────────────────────────────────────────────────────────────
    # Runtime Metadata Recording (Phase E — US5)
    # ─────────────────────────────────────────────────────────────────

    def record_message_metadata(
        self,
        conversation_id: str,
        *,
        tokens_used: int = 0,
        symbols: Optional[List[str]] = None,
    ) -> None:
        """Record metadata after a chat message is processed.

        Non-blocking: logs a warning instead of raising on failure so that
        the chat response is never disrupted by a metadata-write error.
        """
        try:
            self._repository.update_metadata(
                conversation_id,
                message_count_delta=1,
                token_delta=tokens_used,
                last_activity_at=datetime.now(timezone.utc),
                focused_symbols=symbols,
            )
        except Exception as e:
            self.logger.warning(
                f"Non-blocking metadata update failed for {conversation_id}: {e}"
            )

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
    # Management API (Phase C)
    # ------------------------------------------------------------------

    def get_conversation_detail(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """Fetch conversation with aggregate metadata, verifying ownership.

        Returns:
            Conversation dict with message_count, total_tokens, last_activity_at.

        Raises:
            EntityNotFoundError: If conversation does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
            ParentNotFoundError: If parent session or workspace does not exist.
        """
        conversation = self._repository.find_by_conversation_id(conversation_id)
        if conversation is None:
            raise EntityNotFoundError("conversation", conversation_id)

        self._verify_conversation_ownership(conversation, user_id)

        result = normalize_document(conversation)
        return result

    def get_conversation_summary(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """Return conversation statistics, verifying ownership.

        Returns:
            Stats dict with message_count, total_tokens, duration_seconds, etc.

        Raises:
            EntityNotFoundError: If conversation does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
            ParentNotFoundError: If parent session or workspace does not exist.
        """
        conversation = self._repository.find_by_conversation_id(conversation_id)
        if conversation is None:
            raise EntityNotFoundError("conversation", conversation_id)

        self._verify_conversation_ownership(conversation, user_id)

        stats = self.get_conversation_stats(conversation_id)
        if stats is None:
            raise EntityNotFoundError("conversation", conversation_id)
        return stats

    def list_conversations_paginated(
        self,
        session_id: str,
        user_id: str,
        *,
        limit: int = 25,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return paginated conversation list with total count, verifying ownership.

        Returns:
            Dict with ``items``, ``total``, ``limit``, ``offset``.

        Raises:
            ParentNotFoundError: If session does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
        """
        session = self._get_session(session_id)
        if session is None:
            raise ParentNotFoundError("session", session_id, "conversation")

        workspace = self._get_workspace(session.get("workspace_id"))
        if workspace is None:
            raise ParentNotFoundError("workspace", session.get("workspace_id", ""), "session")

        actual_owner = stringify_identifier(workspace.get("user_id"))
        expected_owner = stringify_identifier(user_id)
        if actual_owner != expected_owner:
            raise OwnershipViolationError(
                "session", session_id, expected_owner, actual_owner,
            )

        items = self._repository.find_by_session_with_pagination(
            session_id, limit=limit, offset=offset, status=status,
        )
        total = self._repository.count_by_session(session_id, status=status)
        return {
            "items": [normalize_document(doc) for doc in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def update_conversation_managed(
        self,
        conversation_id: str,
        user_id: str,
        *,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Partial update of conversation title with ownership verification.

        Returns:
            Updated conversation dict.

        Raises:
            EntityNotFoundError: If conversation does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
            ParentNotFoundError: If parent session or workspace does not exist.
        """
        conversation = self._repository.find_by_conversation_id(conversation_id)
        if conversation is None:
            raise EntityNotFoundError("conversation", conversation_id)

        self._verify_conversation_ownership(conversation, user_id)

        updates: Dict[str, Any] = {}
        if title is not None:
            updates["title"] = title.strip()

        if not updates:
            return normalize_document(conversation)

        updated = self._repository.update_fields(conversation_id, updates)
        if updated is None:
            raise EntityNotFoundError("conversation", conversation_id)

        self._invalidate_conversation_cache(conversation_id)
        return normalize_document(updated)

    def archive_conversation_managed(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Archive a conversation (idempotent), verifying ownership.

        Unlike the lifecycle ``archive_conversation`` method, this is
        idempotent and includes ownership verification for the management API.

        Returns:
            Conversation dict after archive.

        Raises:
            EntityNotFoundError: If conversation does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
            ParentNotFoundError: If parent session or workspace does not exist.
        """
        conversation = self._repository.find_by_conversation_id(conversation_id)
        if conversation is None:
            raise EntityNotFoundError("conversation", conversation_id)

        self._verify_conversation_ownership(conversation, user_id)

        if conversation.get("status") == "archived":
            return normalize_document(conversation)

        archived = self._repository.archive(conversation_id)
        if archived is None:
            raise EntityNotFoundError("conversation", conversation_id)

        self._invalidate_conversation_cache(conversation_id)
        return normalize_document(archived)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _verify_conversation_ownership(self, conversation: Dict[str, Any], user_id: str) -> None:
        """Verify user owns the workspace containing this conversation's session."""
        session = self._get_session(conversation.get("session_id"))
        if not session:
            raise ParentNotFoundError(
                "session", conversation.get("session_id", ""), "conversation",
            )
        workspace = self._get_workspace(session.get("workspace_id"))
        if not workspace:
            raise ParentNotFoundError(
                "workspace", session.get("workspace_id", ""), "session",
            )
        actual_owner = stringify_identifier(workspace.get("user_id"))
        expected_owner = stringify_identifier(user_id)
        if actual_owner != expected_owner:
            raise OwnershipViolationError(
                "conversation",
                conversation.get("conversation_id", conversation.get("_id", "")),
                expected_owner,
                actual_owner,
            )

    def _get_session(self, session_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Look up session via the session repository."""
        if not session_id or not self._session_repo:
            return None
        try:
            return self._session_repo.find_by_session_id(session_id)
        except Exception:
            self.logger.exception(
                "Failed to fetch session", extra={"session_id": session_id},
            )
            return None

    def _get_workspace(self, workspace_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Look up workspace via the workspace repository."""
        if not workspace_id or not self._workspace_repo:
            return None
        try:
            return self._workspace_repo.find_by_workspace_id(workspace_id)
        except Exception:
            self.logger.exception(
                "Failed to fetch workspace", extra={"workspace_id": workspace_id},
            )
            return None

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // self.CHARS_PER_TOKEN)
    
    def _conversation_cache_key(self, conversation_id: str) -> str:
        return f"conversation:{conversation_id}"
    
    def _invalidate_conversation_cache(self, conversation_id: str) -> None:
        if self.cache:
            self.cache.delete(self._conversation_cache_key(conversation_id))
