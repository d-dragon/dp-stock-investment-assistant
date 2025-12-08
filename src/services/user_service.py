"""Service orchestration for user-centric workflows."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Iterable, List, Optional
from typing import Set

from data.repositories.user_repository import UserRepository
from data.repositories.watchlist_repository import WatchlistRepository
from services.base import BaseService, HealthReport
from services.protocols import SymbolProvider, WorkspaceProvider
from utils.cache import CacheBackend
from utils.service_utils import normalize_document


class UserService(BaseService):
    """Aggregate user data together with workspace and symbol context."""

    USER_PROFILE_CACHE_TTL = 180  # seconds
    USER_CACHE_TTL = 300  # seconds (for email→user_id mapping)
    DEFAULT_WORKSPACE_LIST_LIMIT = 20  # Default workspace limit (from WorkspaceService)
    RESERVED_MUTATION_FIELDS = {"_id", "id"}
    DEFAULT_PROFILE_FIELDS = (
        "name",
        "email",
        "title",
        "location",
        "bio",
        "timezone",
        "preferences",
        "avatar_url",
        "status",
        "metadata",
    )

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        workspace_provider: WorkspaceProvider,
        symbol_provider: SymbolProvider,
        watchlist_repository: Optional[WatchlistRepository] = None,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._user_repository = user_repository
        self._workspace_provider = workspace_provider
        self._symbol_provider = symbol_provider
        self._watchlist_repository = watchlist_repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_user_profile(self, user_id: str, *, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Return a normalized user profile document, optionally cached."""
        if not user_id:
            raise ValueError("user_id is required")

        cache_key = self._user_profile_cache_key(user_id)
        if use_cache and self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached

        record = self._fetch_user(user_id)
        if not record:
            return None

        payload = normalize_document(record, id_fields=("_id", "group_id"))

        if use_cache and self.cache:
            self.cache.set_json(cache_key, payload, ttl_seconds=self.USER_PROFILE_CACHE_TTL)

        return payload

    def get_user_by_email(self, email: str, *, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Fetch a user document by email with email-based caching."""
        if not email:
            raise ValueError("email is required")

        # Check email cache first to avoid DB query stampede
        email_cache_key = self._user_email_cache_key(email)
        if use_cache and self.cache:
            cached_user_id = self.cache.get_json(email_cache_key)
            if cached_user_id and isinstance(cached_user_id, str):
                return self.get_user_profile(cached_user_id, use_cache=use_cache)

        # Cache miss or disabled - fetch from DB
        record = self._fetch_user_by_email(email)
        if not record:
            return None

        user_id = record.get("_id")
        if user_id:
            user_id_str = str(user_id)
            # Store email → user_id mapping in cache
            if use_cache and self.cache:
                self.cache.set_json(email_cache_key, user_id_str, ttl_seconds=self.USER_CACHE_TTL)
            return self.get_user_profile(user_id_str, use_cache=use_cache)

        return normalize_document(record, id_fields=("_id", "group_id"))

    def get_user_overview(
        self,
        user_id: str,
        *,
        include_workspaces: bool = True,
        workspace_limit: int = DEFAULT_WORKSPACE_LIST_LIMIT,
        include_watchlists: bool = True,
        watchlist_limit: int = 5,
        include_symbols: bool = True,
        symbol_limit: int = 15,
        use_cache: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Return a profile enriched with workspace, watchlist, and symbol context."""

        profile = self.get_user_profile(user_id, use_cache=use_cache)
        if not profile:
            return None

        overview: Dict[str, Any] = dict(profile)

        if include_workspaces:
            overview["workspaces"] = self.list_user_workspaces(
                user_id, limit=workspace_limit, use_cache=use_cache
            )

        watchlists: List[Dict[str, Any]] = []
        if include_watchlists:
            watchlists = self._get_user_watchlists(user_id, limit=watchlist_limit)
            overview["watchlists"] = watchlists

        if include_symbols:
            overview["symbols"] = self.favorite_symbols(
                user_id,
                limit=symbol_limit,
                watchlists=watchlists if include_watchlists else None,
            )

        return overview

    def create_or_update_user(
        self,
        payload: Dict[str, Any],
        *,
        user_id: Optional[str] = None,
        invalidate_cache: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Create a new user or update an existing user document."""

        if not payload:
            raise ValueError("payload is required")

        sanitized = self._sanitize_user_payload(payload)
        if not sanitized:
            raise ValueError("No mutable fields provided in payload")

        target_user_id = user_id

        try:
            if target_user_id:
                updated = self._user_repository.update(target_user_id, sanitized)
                if not updated:
                    return None
            else:
                created_id = self._user_repository.create(sanitized)
                if not created_id:
                    return None
                target_user_id = created_id
        except Exception:
            self.logger.exception("Failed to persist user", extra={"user_id": user_id})
            return None

        if invalidate_cache and target_user_id:
            self.invalidate_user_cache(target_user_id)

        return self.get_user_profile(target_user_id, use_cache=False) if target_user_id else None

    def update_user_profile(
        self,
        user_id: str,
        profile_updates: Dict[str, Any],
        *,
        allowed_fields: Optional[Iterable[str]] = None,
        invalidate_cache: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Update user profile-focused fields with validation and cache handling."""

        if not user_id:
            raise ValueError("user_id is required")
        if not profile_updates:
            raise ValueError("profile_updates cannot be empty")

        permitted_fields = tuple(allowed_fields) if allowed_fields is not None else self.DEFAULT_PROFILE_FIELDS
        sanitized = self._sanitize_user_payload(profile_updates, allowed_fields=permitted_fields)
        if not sanitized:
            raise ValueError("No allowed profile fields were provided")

        try:
            updated = self._user_repository.update(user_id, sanitized)
        except Exception:
            self.logger.exception("Failed to update user profile", extra={"user_id": user_id})
            return None

        if not updated:
            return None

        if invalidate_cache:
            self.invalidate_user_cache(user_id)

        return self.get_user_profile(user_id, use_cache=False)

    def list_user_workspaces(
        self,
        user_id: str,
        *,
        limit: int = DEFAULT_WORKSPACE_LIST_LIMIT,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """Delegate to WorkspaceProvider for workspace listings."""
        return self._workspace_provider.list_workspaces(user_id, limit=limit, use_cache=use_cache)

    def favorite_symbols(
        self,
        user_id: str,
        *,
        limit: int = 15,
        watchlists: Optional[Iterable[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Return detailed symbol metadata for a user's frequently tracked tickers.
        
        Note: Current implementation performs sequential symbol lookups (N+1 query pattern).
        Consider implementing batch fetch API in SymbolProvider when symbol count exceeds threshold.
        """
        tickers = self._collect_symbol_universe(user_id, limit=limit, watchlists=watchlists)
        ticker_count = len(tickers)
        
        # Monitor N+1 query pattern - log warning when fetching many symbols
        if ticker_count > 10:
            self.logger.warning(
                "Performing sequential symbol lookups (N+1 pattern)",
                extra={"user_id": user_id, "symbol_count": ticker_count, "limit": limit}
            )
        
        results: List[Dict[str, Any]] = []

        for ticker in tickers:
            details = self._symbol_provider.get_symbol(ticker)
            if not details:
                continue
            results.append(details)
            if len(results) >= limit:
                break

        return results

    def invalidate_user_cache(self, user_id: str, email: Optional[str] = None) -> None:
        """Drop cached fragments for a user profile and optionally email mapping.
        
        Args:
            user_id: User ID to invalidate
            email: Optional email to also invalidate email→user_id cache
        """
        if not self.cache:
            return
        try:
            # Clear profile cache
            self.cache.delete(self._user_profile_cache_key(user_id))
            
            # Clear email cache if provided
            if email:
                email_cache_key = self._user_email_cache_key(email)
                self.cache.delete(email_cache_key)
        except Exception:
            self.logger.exception("Failed to invalidate user profile cache", extra={"user_id": user_id, "email": email})

    # ------------------------------------------------------------------
    # Health + internals
    # ------------------------------------------------------------------
    def health_check(self) -> HealthReport:
        return self._dependencies_health_report(
            required={
                "user_repository": self._user_repository,
                "workspace_provider": self._workspace_provider,
                "symbol_provider": self._symbol_provider,
            },
            optional={"watchlist_repository": self._watchlist_repository},
        )

    def _fetch_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self._user_repository.get_by_id(user_id)
        except Exception:
            self.logger.exception("Failed to fetch user", extra={"user_id": user_id})
            return None

    def _fetch_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            return self._user_repository.get_by_email(email)
        except Exception:
            self.logger.exception("Failed to fetch user", extra={"email": email})
            return None

    def _user_profile_cache_key(self, user_id: str) -> str:
        return f"user:profile:{user_id}"

    def _user_email_cache_key(self, email: str) -> str:
        return f"user:email:{email}"

    def _get_user_watchlists(self, user_id: str, *, limit: int) -> List[Dict[str, Any]]:
        if not self._watchlist_repository:
            return []

        try:
            watchlists = self._watchlist_repository.get_by_user_id(user_id, limit=limit)
        except Exception:
            self.logger.exception("Failed to load user watchlists", extra={"user_id": user_id})
            return []

        return [normalize_document(doc, id_fields=("_id", "user_id", "workspace_id")) for doc in watchlists]

    def _collect_symbol_universe(
        self,
        user_id: str,
        *,
        limit: int,
        watchlists: Optional[Iterable[Dict[str, Any]]] = None,
    ) -> List[str]:
        source = watchlists if watchlists is not None else self._get_user_watchlists(user_id, limit=limit * 2)
        seen: Set[str] = set()
        ordered: List[str] = []

        for watchlist in source:
            symbols = watchlist.get("symbols")
            if not symbols:
                continue
            for raw_symbol in symbols:
                normalized = (raw_symbol or "").strip().upper()
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                ordered.append(normalized)
                if len(ordered) >= limit:
                    return ordered

        return ordered

    def _sanitize_user_payload(
        self,
        payload: Dict[str, Any],
        *,
        allowed_fields: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        allowed_set = set(allowed_fields) if allowed_fields is not None else None
        sanitized: Dict[str, Any] = {}

        for key, value in (payload or {}).items():
            if key in self.RESERVED_MUTATION_FIELDS:
                continue
            if allowed_set is not None and key not in allowed_set:
                continue
            sanitized[key] = value

        return sanitized