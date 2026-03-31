"""Service layer helpers for workspace-centric workflows."""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional

from bson import ObjectId

from data.repositories.conversation_repository import ConversationRepository
from data.repositories.session_repository import SessionRepository
from data.repositories.watchlist_repository import WatchlistRepository
from data.repositories.workspace_repository import WorkspaceRepository
from services.base import BaseService, HealthReport
from services.exceptions import EntityNotFoundError, OwnershipViolationError, StaleEntityError
from utils.cache import CacheBackend
from utils.service_utils import batched, normalize_document, stringify_identifier


class WorkspaceService(BaseService):
    """High-level orchestration for workspace, session, and watchlist data."""

    WORKSPACE_CACHE_TTL = 120  # seconds
    DEFAULT_BATCH_SIZE = 5
    DEFAULT_LIST_LIMIT = 20

    def __init__(
        self,
        *,
        workspace_repository: WorkspaceRepository,
        session_repository: Optional[SessionRepository] = None,
        conversation_repository: Optional[ConversationRepository] = None,
        watchlist_repository: Optional[WatchlistRepository] = None,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._workspace_repository = workspace_repository
        self._session_repository = session_repository
        self._conversation_repository = conversation_repository
        self._watchlist_repository = watchlist_repository

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def list_workspaces(
        self,
        user_id: str,
        *,
        limit: int = DEFAULT_LIST_LIMIT,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """Return recent workspaces for a user, optionally cached.
        
        Args:
            user_id: User identifier (must be non-empty)
            limit: Maximum number of workspaces to return
            use_cache: Whether to use cached results
            
        Returns:
            List of workspace documents
            
        Raises:
            ValueError: If user_id is empty or invalid
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string")
        
        cache_key = self._workspace_cache_key(user_id, limit)

        if use_cache and self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached.get("items", [])

        records = self._fetch_workspaces(user_id, limit)
        payload = [normalize_document(doc, id_fields=("_id", "user_id")) for doc in records]

        if use_cache and self.cache:
            self.cache.set_json(cache_key, {"items": payload}, ttl_seconds=self.WORKSPACE_CACHE_TTL)

        return payload

    async def list_workspaces_async(
        self,
        user_id: str,
        *,
        limit: int = DEFAULT_LIST_LIMIT,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """Async wrapper around :meth:`list_workspaces` for asyncio callers."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: self.list_workspaces(user_id, limit=limit, use_cache=use_cache)
        )

    def stream_workspaces(
        self,
        user_id: str,
        *,
        chunk_size: int = DEFAULT_BATCH_SIZE,
        limit: Optional[int] = None,
    ) -> Iterator[List[Dict[str, Any]]]:
        """Yield workspaces in batches for SSE/WebSocket streaming APIs."""
        records = self._fetch_workspaces(user_id, limit)
        serialized = [normalize_document(doc, id_fields=("_id", "user_id")) for doc in records]
        yield from batched(serialized, chunk_size)

    def create_workspace(
        self,
        user_id: str,
        *,
        name: str,
        description: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        invalidate_cache: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Insert a new workspace record and return a normalized representation."""

        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Workspace name is required")

        workspace_id = str(uuid.uuid4())

        document: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "user_id": self._coerce_user_identifier(user_id),
            "name": normalized_name,
            "status": WorkspaceRepository.STATUS_ACTIVE,
        }

        if description is not None:
            document["description"] = description.strip()

        if data:
            for key, value in data.items():
                if key in {"_id", "user_id", "workspace_id", "status"}:
                    continue
                document[key] = value

        try:
            workspace_id = self._workspace_repository.create(document)
        except Exception:
            self.logger.exception("Workspace creation failed", extra={"user_id": user_id})
            return None

        if not workspace_id:
            return None

        try:
            created_record = self._workspace_repository.get_by_id(workspace_id)
        except Exception:
            self.logger.exception("Failed to reload workspace", extra={"workspace_id": workspace_id})
            created_record = None

        if not created_record:
            created_record = {"_id": workspace_id, **document}

        result = normalize_document(created_record, id_fields=("_id", "user_id"))

        if invalidate_cache:
            self.invalidate_user_cache(user_id)

        return result

    def summarize_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Return lightweight metrics for dashboards without extra round-trips."""
        summary = {"workspace_id": workspace_id, "session_count": 0, "watchlist_count": 0}

        if self._session_repository:
            try:
                sessions = self._session_repository.get_by_workspace_id(workspace_id)
                summary["session_count"] = len(sessions)
            except Exception:
                self.logger.exception("Failed to fetch sessions for workspace", extra={"workspace_id": workspace_id})

        if self._watchlist_repository:
            try:
                watchlists = self._watchlist_repository.get_by_workspace(workspace_id)
                summary["watchlist_count"] = len(watchlists)
            except Exception:
                self.logger.exception(
                    "Failed to fetch watchlists for workspace", extra={"workspace_id": workspace_id}
                )

        return summary

    def invalidate_user_cache(
        self,
        user_id: str,
        *,
        limit: Optional[int] = None,
        limits: Optional[Iterable[int]] = None,
    ) -> None:
        """Clear cached workspace lists for the provided user."""
        if not self.cache:
            return

        target_limits: List[Optional[int]]
        if limits is not None:
            target_limits = list(limits)
        else:
            target_limits = [limit if limit is not None else self.DEFAULT_LIST_LIMIT]

        for target in target_limits:
            try:
                self.cache.delete(self._workspace_cache_key(user_id, target))
            except Exception:
                self.logger.exception(
                    "Failed to invalidate workspace cache",
                    extra={"user_id": user_id, "limit": target},
                )

    def remove_workspace(
        self,
        workspace_id: str,
        *,
        user_id: Optional[str] = None,
        invalidate_cache: bool = True,
    ) -> bool:
        """Delete a workspace and invalidate cached listings when possible."""

        if not workspace_id:
            raise ValueError("workspace_id is required")

        owner_id = user_id or self._resolve_workspace_owner(workspace_id)

        try:
            deleted = self._workspace_repository.delete(workspace_id)
        except Exception:
            self.logger.exception("Workspace deletion failed", extra={"workspace_id": workspace_id})
            return False

        if deleted and invalidate_cache and owner_id:
            self.invalidate_user_cache(owner_id)

        return deleted

    # ------------------------------------------------------------------
    # Management API (Phase C)
    # ------------------------------------------------------------------

    def get_workspace_detail(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Fetch workspace with aggregate counts, verifying ownership.

        Returns:
            Workspace dict with ``session_count`` and ``active_conversation_count``.

        Raises:
            EntityNotFoundError: If workspace does not exist.
            OwnershipViolationError: If requesting user is not the owner.
        """
        workspace = self._workspace_repository.find_by_workspace_id(workspace_id)
        if workspace is None:
            raise EntityNotFoundError("workspace", workspace_id)

        self._verify_ownership(workspace, user_id)

        result = normalize_document(workspace)
        result["session_count"] = self._count_sessions(workspace_id)
        result["active_conversation_count"] = self._count_active_conversations(workspace_id)
        return result

    def list_workspaces_paginated(
        self,
        user_id: str,
        *,
        limit: int = 25,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return paginated workspace list with total count.

        Returns:
            Dict with ``items``, ``total``, ``limit``, ``offset``.
        """
        items = self._workspace_repository.find_by_user_with_pagination(
            user_id, limit=limit, offset=offset, status=status,
        )
        total = self._workspace_repository.count_by_user(user_id, status=status)
        return {
            "items": [normalize_document(doc) for doc in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def update_workspace(
        self,
        workspace_id: str,
        user_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Partial update of workspace name/description.

        Returns:
            Updated workspace dict.

        Raises:
            EntityNotFoundError: If workspace does not exist.
            OwnershipViolationError: If requesting user is not the owner.
        """
        workspace = self._workspace_repository.find_by_workspace_id(workspace_id)
        if workspace is None:
            raise EntityNotFoundError("workspace", workspace_id)

        self._verify_ownership(workspace, user_id)

        updates: Dict[str, Any] = {}
        if name is not None:
            updates["name"] = name.strip()
        if description is not None:
            updates["description"] = description.strip()

        if not updates:
            return normalize_document(workspace)

        updated = self._workspace_repository.update_fields(workspace_id, updates)
        if updated is None:
            raise EntityNotFoundError("workspace", workspace_id)

        result = normalize_document(updated)
        result["session_count"] = self._count_sessions(workspace_id)
        result["active_conversation_count"] = self._count_active_conversations(workspace_id)
        return result

    def archive_workspace(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Archive a workspace (idempotent).

        Per the management API contract, repeated archive requests are safe.

        Returns:
            Workspace detail dict after archive transition.

        Raises:
            EntityNotFoundError: If workspace does not exist.
            OwnershipViolationError: If requesting user is not the owner.
        """
        workspace = self._workspace_repository.find_by_workspace_id(workspace_id)
        if workspace is None:
            raise EntityNotFoundError("workspace", workspace_id)

        self._verify_ownership(workspace, user_id)

        if workspace.get("status") == WorkspaceRepository.STATUS_ARCHIVED:
            # Idempotent: return current state
            result = normalize_document(workspace)
            result["session_count"] = self._count_sessions(workspace_id)
            result["active_conversation_count"] = self._count_active_conversations(workspace_id)
            return result

        # Cascade: archive all sessions and their conversations
        self._cascade_archive_descendants(workspace_id)

        archived = self._workspace_repository.archive(workspace_id)
        if archived is None:
            raise EntityNotFoundError("workspace", workspace_id)

        result = normalize_document(archived)
        result["session_count"] = self._count_sessions(workspace_id)
        result["active_conversation_count"] = self._count_active_conversations(workspace_id)
        return result

    def _verify_ownership(self, workspace: Dict[str, Any], user_id: str) -> None:
        """Verify the requesting user owns the workspace."""
        actual_owner = stringify_identifier(workspace.get("user_id"))
        expected_owner = stringify_identifier(user_id)
        if actual_owner != expected_owner:
            raise OwnershipViolationError(
                "workspace",
                workspace.get("workspace_id", workspace.get("_id", "")),
                expected_owner,
                actual_owner,
            )

    def _cascade_archive_descendants(self, workspace_id: str) -> None:
        """Archive all sessions (and their conversations) in a workspace.

        Iterates sessions and archives each session's conversations first,
        then archives the session itself. Uses bulk repo operations where available.
        """
        if not self._session_repository:
            return

        sessions = self._session_repository.find_by_workspace(workspace_id)
        conv_total = 0

        for session in sessions:
            sid = session.get("session_id")
            if not sid or session.get("status") == "archived":
                continue
            # Archive child conversations for this session
            if self._conversation_repository:
                count = self._conversation_repository.archive_by_session_id(
                    sid, archive_reason="workspace_archived",
                )
                conv_total += count
            # Archive the session itself
            self._session_repository.archive(sid)

        self.logger.info(
            "Cascade archive for workspace %s: archived %d sessions, %d conversations",
            workspace_id, len(sessions), conv_total,
        )

    def _count_sessions(self, workspace_id: str) -> int:
        """Count sessions belonging to a workspace."""
        if self._session_repository is None:
            return 0
        try:
            collection = self._session_repository.collection
            return collection.count_documents({"workspace_id": workspace_id})
        except Exception:
            self.logger.exception("Failed to count sessions", extra={"workspace_id": workspace_id})
            return 0

    def _count_active_conversations(self, workspace_id: str) -> int:
        """Count active conversations in a workspace's sessions."""
        if self._session_repository is None:
            return 0
        try:
            db = self._session_repository.collection.database
            return db["conversations"].count_documents({
                "workspace_id": workspace_id,
                "status": {"$ne": "archived"},
            })
        except Exception:
            self.logger.exception(
                "Failed to count active conversations", extra={"workspace_id": workspace_id},
            )
            return 0

    # ------------------------------------------------------------------
    # Health + internals
    # ------------------------------------------------------------------
    def health_check(self) -> HealthReport:
        return self._dependencies_health_report(
            required={"workspace_repository": self._workspace_repository},
            optional={
                "session_repository": self._session_repository,
                "watchlist_repository": self._watchlist_repository,
            },
        )

    def _workspace_cache_key(self, user_id: str, limit: Optional[int]) -> str:
        return f"workspace:list:{user_id}:{limit}"

    def _fetch_workspaces(self, user_id: str, limit: Optional[int]) -> List[Dict[str, Any]]:
        repo = self._workspace_repository
        try:
            if limit is not None and hasattr(repo, "get_recent"):
                return repo.get_recent(user_id, limit=limit)
            records = repo.get_by_user_id(user_id)
            if limit is not None:
                return records[:limit]
            return records
        except Exception:
            self.logger.exception("Failed to fetch workspaces", extra={"user_id": user_id})
            return []

    def _coerce_user_identifier(self, user_id: str) -> Any:
        if not user_id:
            raise ValueError("user_id is required")

        try:
            return ObjectId(user_id)
        except Exception as exc:
            raise ValueError("user_id must be a valid ObjectId string") from exc

    def _resolve_workspace_owner(self, workspace_id: str) -> Optional[str]:
        try:
            record = self._workspace_repository.get_by_id(workspace_id)
        except Exception:
            self.logger.exception("Failed to resolve workspace owner", extra={"workspace_id": workspace_id})
            return None

        if not record:
            return None

        owner = record.get("user_id")
        return stringify_identifier(owner) if owner is not None else None
