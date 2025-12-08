"""Factory responsible for wiring repositories into higher-level services."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from data.repositories.factory import RepositoryFactory
from services.symbols_service import SymbolsService
from services.user_service import UserService
from services.workspace_service import WorkspaceService
from utils.cache import CacheBackend

ServiceT = TypeVar("ServiceT")


class ServiceFactory:
    """Central place to build service instances with shared dependencies."""

    def __init__(
        self,
        config: Dict[str, Any],
        *,
        repository_factory: Optional[RepositoryFactory] = None,
        cache_backend: Optional[CacheBackend] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._config = config
        self._logger = logger or logging.getLogger(__name__)
        self._repository_factory = repository_factory or RepositoryFactory(config)
        self._cache = cache_backend or CacheBackend.from_config(config, logger=self._logger)
        self._services: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public builders
    # ------------------------------------------------------------------
    def get_workspace_service(self) -> WorkspaceService:
        return cast(WorkspaceService, self._get_or_create("workspace_service", self._build_workspace_service))

    def get_symbols_service(self) -> SymbolsService:
        return cast(SymbolsService, self._get_or_create("symbols_service", self._build_symbols_service))

    def get_user_service(self) -> UserService:
        return cast(UserService, self._get_or_create("user_service", self._build_user_service))

    # ------------------------------------------------------------------
    # Builders
    # ------------------------------------------------------------------
    def _build_workspace_service(self) -> WorkspaceService:
        workspace_repo = self._repository_factory.get_workspace_repository()
        if not workspace_repo:
            raise RuntimeError("WorkspaceRepository could not be initialized")

        session_repo = self._repository_factory.get_session_repository()
        watchlist_repo = self._repository_factory.get_watchlist_repository()

        return WorkspaceService(
            workspace_repository=workspace_repo,
            session_repository=session_repo,
            watchlist_repository=watchlist_repo,
            cache=self._cache,
            logger=self._logger.getChild("workspace"),
        )

    def _build_symbols_service(self) -> SymbolsService:
        symbol_repo = self._repository_factory.get_symbol_repository()
        if not symbol_repo:
            raise RuntimeError("SymbolRepository could not be initialized")

        watchlist_repo = self._repository_factory.get_watchlist_repository()

        return SymbolsService(
            symbol_repository=symbol_repo,
            watchlist_repository=watchlist_repo,
            cache=self._cache,
            logger=self._logger.getChild("symbols"),
        )

    def _build_user_service(self) -> UserService:
        user_repo = self._repository_factory.get_user_repository()
        if not user_repo:
            raise RuntimeError("UserRepository could not be initialized")

        workspace_service = self.get_workspace_service()
        symbols_service = self.get_symbols_service()
        watchlist_repo = self._repository_factory.get_watchlist_repository()

        return UserService(
            user_repository=user_repo,
            workspace_provider=workspace_service,  # Satisfies WorkspaceProvider protocol
            symbol_provider=symbols_service,       # Satisfies SymbolProvider protocol
            watchlist_repository=watchlist_repo,
            cache=self._cache,
            logger=self._logger.getChild("user"),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_or_create(self, key: str, builder: Callable[[], ServiceT]) -> ServiceT:
        if key not in self._services:
            self._services[key] = builder()
        return cast(ServiceT, self._services[key])
