"""Service layer helpers for workspace-centric workflows."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional

from bson import ObjectId

from data.repositories.session_repository import SessionRepository
from data.repositories.watchlist_repository import WatchlistRepository
from data.repositories.workspace_repository import WorkspaceRepository
from services.base import BaseService, HealthReport
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
        watchlist_repository: Optional[WatchlistRepository] = None,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._workspace_repository = workspace_repository
        self._session_repository = session_repository
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

        document: Dict[str, Any] = {
            "user_id": self._coerce_user_identifier(user_id),
            "name": normalized_name,
        }

        if description is not None:
            document["description"] = description.strip()

        if data:
            for key, value in data.items():
                if key in {"_id", "user_id"}:
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
