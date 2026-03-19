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
from services.exceptions import InvalidLifecycleTransitionError
from utils.cache import CacheBackend


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
        """Create a new session document."""
        if not all([session_id, workspace_id, user_id]):
            self.logger.warning("create_session: missing required identifiers")
            return None
        if self._workspace_repo:
            workspace = self._workspace_repo.get_by_id(workspace_id)
            if not workspace:
                self.logger.warning(f"create_session: workspace not found: {workspace_id}")
                return None
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
    # Private helpers
    # ------------------------------------------------------------------
    
    def _session_cache_key(self, session_id: str) -> str:
        return f"session:{session_id}"
    
    def _invalidate_session_cache(self, session_id: str) -> None:
        if self.cache:
            self.cache.delete(self._session_cache_key(session_id))
