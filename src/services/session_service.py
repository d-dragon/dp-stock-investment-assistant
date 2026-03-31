"""Session lifecycle service.

Manages session creation, status transitions, and reusable context.
Sessions are business grouping containers for conversations.

Specification Reference:
- FR-004: Session Lifecycle (active → closed → archived)
- FR-007–FR-009: Session context (assumptions, pinned_intent, focused_symbols)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from data.repositories.session_repository import SessionRepository
from data.repositories.conversation_repository import ConversationRepository
from data.repositories.workspace_repository import WorkspaceRepository
from services.base import BaseService
from services.exceptions import (
    EntityNotFoundError,
    InvalidLifecycleTransitionError,
    OwnershipViolationError,
    ParentNotFoundError,
)
from utils.cache import CacheBackend
from utils.service_utils import normalize_document, stringify_identifier


# Valid lifecycle transitions (sequential: active → closed → archived)
_VALID_TRANSITIONS = {
    "active": {"closed"},
    "closed": {"archived"},
    # archived is terminal — no transitions out
}


class SessionService(BaseService):
    """Manages session lifecycle and reusable context.
    
    Sessions group related conversations. Closing or archiving
    a session cascades to its child conversations.
    """
    
    SESSION_CACHE_TTL = 300  # 5 minutes
    
    def __init__(
        self,
        *,
        session_repository: SessionRepository,
        conversation_repository: Optional[ConversationRepository] = None,
        workspace_repository: Optional[WorkspaceRepository] = None,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], datetime]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._session_repo = session_repository
        self._conversation_repo = conversation_repository
        self._workspace_repo = workspace_repository
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        optional = {}
        if self._conversation_repo:
            optional["conversation_repository"] = self._conversation_repo
        if self._workspace_repo:
            optional["workspace_repository"] = self._workspace_repo
        return self._dependencies_health_report(
            required={"session_repository": self._session_repo},
            optional=optional,
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Create / Lookup
    # ─────────────────────────────────────────────────────────────────
    
    def create_session(
        self,
        session_id: str,
        workspace_id: str,
        user_id: str,
        *,
        title: str = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new session document.

        Raises:
            ParentNotFoundError: If workspace does not exist.
            OwnershipViolationError: If user does not own the workspace.
        """
        if not all([session_id, workspace_id, user_id]):
            self.logger.warning("create_session: missing required identifiers")
            return None
        if self._workspace_repo:
            workspace = self._workspace_repo.find_by_workspace_id(workspace_id)
            if not workspace:
                raise ParentNotFoundError("workspace", workspace_id, "session")
            actual_owner = stringify_identifier(workspace.get("user_id"))
            expected_owner = stringify_identifier(user_id)
            if actual_owner != expected_owner:
                raise OwnershipViolationError(
                    "workspace", workspace_id, expected_owner, actual_owner,
                )
        now = datetime.now(timezone.utc)
        doc = {
            "session_id": session_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "title": title or "",
            "status": "active",
            "assumptions": None,
            "pinned_intent": None,
            "focused_symbols": [],
            "linked_symbol_ids": [],
            "created_at": now,
            "updated_at": now,
        }
        result = self._session_repo.create(doc)
        if result:
            doc["_id"] = result
            return doc
        return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by session_id (cache-aware)."""
        if not session_id:
            return None
        cache_key = self._session_cache_key(session_id)
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached
        session = self._session_repo.find_by_session_id(session_id)
        if session and self.cache:
            self.cache.set_json(cache_key, session, ttl_seconds=self.SESSION_CACHE_TTL)
        return session
    
    def list_sessions(
        self,
        workspace_id: str,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List sessions for a workspace with optional status filter."""
        if not workspace_id:
            return []
        return self._session_repo.find_by_workspace(workspace_id, status=status)
    
    # ─────────────────────────────────────────────────────────────────
    # Lifecycle Transitions
    # ─────────────────────────────────────────────────────────────────
    
    def close_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Transition session to 'closed'. Active conversations remain operational."""
        return self._transition(session_id, "closed")
    
    def archive_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Transition session to 'archived'. Cascades archive to child conversations."""
        return self._transition(session_id, "archived")
    
    def _transition(self, session_id: str, target_status: str) -> Optional[Dict[str, Any]]:
        """Apply a lifecycle transition with validation and optional cascade."""
        if not session_id:
            return None
        session = self._session_repo.find_by_session_id(session_id)
        if not session:
            return None
        current = session.get("status", "active")
        allowed = _VALID_TRANSITIONS.get(current, set())
        if target_status not in allowed:
            raise InvalidLifecycleTransitionError("session", session_id, current, target_status)
        
        updated = self._session_repo.update_status(session_id, target_status)
        if updated:
            self._invalidate_session_cache(session_id)
            # Cascade: archive child conversations only when archiving the session
            if self._conversation_repo and target_status == "archived":
                count = self._conversation_repo.archive_by_session_id(
                    session_id, archive_reason="session_archived"
                )
                self.logger.info(
                    f"Session {session_id} → archived: archived {count} child conversations"
                )
        return updated
    
    # ─────────────────────────────────────────────────────────────────
    # Context
    # ─────────────────────────────────────────────────────────────────
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Return the reusable context fields for a session."""
        session = self.get_session(session_id)
        if not session:
            return None
        return {
            "assumptions": session.get("assumptions"),
            "pinned_intent": session.get("pinned_intent"),
            "focused_symbols": session.get("focused_symbols", []),
        }
    
    def update_session_context(
        self,
        session_id: str,
        *,
        assumptions: Optional[str] = ...,
        pinned_intent: Optional[str] = ...,
        focused_symbols: Optional[List[str]] = ...,
    ) -> bool:
        """Update reusable context fields. Pass sentinel (...) to leave a field unchanged."""
        if not session_id:
            return False
        updates: Dict[str, Any] = {}
        if assumptions is not ...:
            updates["assumptions"] = assumptions
        if pinned_intent is not ...:
            updates["pinned_intent"] = pinned_intent
        if focused_symbols is not ...:
            updates["focused_symbols"] = focused_symbols or []
        if not updates:
            return True  # nothing to do
        
        session = self._session_repo.find_by_session_id(session_id)
        if not session:
            return False
        if session.get("status") == "archived":
            self.logger.warning(f"Cannot update context for archived session: {session_id}")
            return False
        
        from datetime import datetime, timezone
        updates["updated_at"] = datetime.now(timezone.utc)
        try:
            result = self._session_repo.collection.update_one(
                {"session_id": session_id},
                {"$set": updates},
            )
            if result.modified_count > 0:
                self._invalidate_session_cache(session_id)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating session context for {session_id}: {e}")
            return False
    
    # ------------------------------------------------------------------
    # Management API (Phase C)
    # ------------------------------------------------------------------

    def get_session_detail(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Fetch session with aggregate counts, verifying ownership.

        Returns:
            Session dict with ``conversation_count``.

        Raises:
            EntityNotFoundError: If session does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
            ParentNotFoundError: If the parent workspace does not exist.
        """
        session = self._session_repo.find_by_session_id(session_id)
        if session is None:
            raise EntityNotFoundError("session", session_id)

        self._verify_session_ownership(session, user_id)

        result = normalize_document(session)
        result["conversation_count"] = self._count_conversations(session_id)
        return result

    def list_sessions_paginated(
        self,
        workspace_id: str,
        user_id: str,
        *,
        limit: int = 25,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return paginated session list with total count, verifying workspace ownership.

        Returns:
            Dict with ``items``, ``total``, ``limit``, ``offset``.

        Raises:
            ParentNotFoundError: If workspace does not exist.
            OwnershipViolationError: If requesting user does not own the workspace.
        """
        workspace = self._get_workspace(workspace_id)
        if workspace is None:
            raise ParentNotFoundError("workspace", workspace_id, "session")

        actual_owner = stringify_identifier(workspace.get("user_id"))
        expected_owner = stringify_identifier(user_id)
        if actual_owner != expected_owner:
            raise OwnershipViolationError(
                "workspace", workspace_id, expected_owner, actual_owner,
            )

        items = self._session_repo.find_by_workspace_with_pagination(
            workspace_id, limit=limit, offset=offset, status=status,
        )
        total = self._session_repo.count_by_workspace(workspace_id, status=status)
        return {
            "items": [normalize_document(doc) for doc in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def update_session(
        self,
        session_id: str,
        user_id: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Partial update of session title/description.

        Returns:
            Updated session dict with ``conversation_count``.

        Raises:
            EntityNotFoundError: If session does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
            ParentNotFoundError: If the parent workspace does not exist.
        """
        session = self._session_repo.find_by_session_id(session_id)
        if session is None:
            raise EntityNotFoundError("session", session_id)

        self._verify_session_ownership(session, user_id)

        updates: Dict[str, Any] = {}
        if title is not None:
            updates["title"] = title.strip()
        if description is not None:
            updates["description"] = description.strip()

        if not updates:
            result = normalize_document(session)
            result["conversation_count"] = self._count_conversations(session_id)
            return result

        updated = self._session_repo.update_fields(session_id, updates)
        if updated is None:
            raise EntityNotFoundError("session", session_id)

        result = normalize_document(updated)
        result["conversation_count"] = self._count_conversations(session_id)
        return result

    def close_session_managed(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Close a session, verifying ownership.

        Blocks new conversation creation but leaves existing conversations
        operational. Idempotent if already closed.

        Returns:
            Session detail dict after close.

        Raises:
            EntityNotFoundError: If session does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
            ParentNotFoundError: If the parent workspace does not exist.
            InvalidLifecycleTransitionError: If transition is not allowed.
        """
        session = self._session_repo.find_by_session_id(session_id)
        if session is None:
            raise EntityNotFoundError("session", session_id)

        self._verify_session_ownership(session, user_id)

        if session.get("status") == "closed":
            result = normalize_document(session)
            result["conversation_count"] = self._count_conversations(session_id)
            return result

        closed = self.close_session(session_id)
        if closed is None:
            raise EntityNotFoundError("session", session_id)

        result = normalize_document(closed)
        result["conversation_count"] = self._count_conversations(session_id)
        return result

    def archive_session_managed(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Archive a session (idempotent), verifying ownership.

        Unlike the lifecycle ``archive_session`` method, this is idempotent
        and includes ownership verification for the management API.

        Returns:
            Session detail dict after archive.

        Raises:
            EntityNotFoundError: If session does not exist.
            OwnershipViolationError: If requesting user does not own the parent workspace.
            ParentNotFoundError: If the parent workspace does not exist.
        """
        session = self._session_repo.find_by_session_id(session_id)
        if session is None:
            raise EntityNotFoundError("session", session_id)

        self._verify_session_ownership(session, user_id)

        if session.get("status") == "archived":
            result = normalize_document(session)
            result["conversation_count"] = self._count_conversations(session_id)
            return result

        # Cascade: archive all child conversations first
        if self._conversation_repo:
            count = self._conversation_repo.archive_by_session_id(
                session_id, archive_reason="session_archived",
            )
            self.logger.info(
                "archive_session_managed: archived %d child conversations for session %s",
                count, session_id,
            )

        archived = self._session_repo.archive(session_id)
        if archived is None:
            raise EntityNotFoundError("session", session_id)

        self._invalidate_session_cache(session_id)

        result = normalize_document(archived)
        result["conversation_count"] = self._count_conversations(session_id)
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _verify_session_ownership(self, session: Dict[str, Any], user_id: str) -> None:
        """Verify user owns the workspace containing this session."""
        workspace = self._get_workspace(session.get("workspace_id"))
        if not workspace:
            raise ParentNotFoundError(
                "workspace", session.get("workspace_id", ""), "session",
            )
        actual_owner = stringify_identifier(workspace.get("user_id"))
        expected_owner = stringify_identifier(user_id)
        if actual_owner != expected_owner:
            raise OwnershipViolationError(
                "session",
                session.get("session_id", session.get("_id", "")),
                expected_owner,
                actual_owner,
            )

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

    def _count_conversations(self, session_id: str) -> int:
        """Count conversations belonging to this session."""
        try:
            return self._session_repo.count_conversations(session_id)
        except Exception:
            self.logger.exception(
                "Failed to count conversations", extra={"session_id": session_id},
            )
            return 0

    def _session_cache_key(self, session_id: str) -> str:
        return f"session:{session_id}"
    
    def _invalidate_session_cache(self, session_id: str) -> None:
        if self.cache:
            self.cache.delete(self._session_cache_key(session_id))
