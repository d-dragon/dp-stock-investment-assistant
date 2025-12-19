"""Shared base class for domain services."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Tuple

from utils.cache import CacheBackend
from utils.logging import LoggingMixin

HealthReport = Tuple[bool, Dict[str, Any]]


class BaseService(LoggingMixin, ABC):
    """Common utilities for service-layer implementations."""

    def __init__(
        self,
        *,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(logger=logger)
        self._time_provider = time_provider or self._default_time_provider
        self.cache = cache

    @abstractmethod
    def health_check(self) -> HealthReport:
        """Return a tuple indicating readiness and supporting diagnostics."""

    def _utc_now(self) -> str:
        return self._time_provider()

    def _default_time_provider(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    def _health_response(self, ok: bool, details: Optional[Dict[str, Any]] = None) -> HealthReport:
        payload: Dict[str, Any] = {"checked_at": self._utc_now()}
        if details:
            payload.update(details)
        return ok, payload

    def _dependency_health(self, name: str, dependency: Any) -> HealthReport:
        if dependency is None:
            self.logger.warning("Dependency missing", extra={"component": name})
            return self._health_response(False, {"component": name, "status": "missing"})

        check = getattr(dependency, "health_check", None)
        if callable(check):
            try:
                healthy, info = check()
                info = info or {}
                info.setdefault("component", name)
                return self._health_response(healthy, info)
            except Exception as exc:  # defensive
                self.logger.exception("Dependency health check failed", extra={"component": name})
                return self._health_response(False, {"component": name, "status": "error", "detail": str(exc)})

        return self._health_response(True, {"component": name, "status": "assumed_healthy"})

    def _cache_health(self) -> HealthReport:
        if not self.cache:
            return self._health_response(False, {"component": "cache", "status": "disabled"})

        try:
            available = self.cache.is_available()
            healthy = self.cache.ping()
        except Exception as exc:  # defensive
            self.logger.exception("Cache health check failed")
            return self._health_response(False, {"component": "cache", "status": "error", "detail": str(exc)})

        status = "ready" if healthy else "unreachable"
        return self._health_response(healthy, {"component": "cache", "status": status, "available": available})

    def _optional_dependency_health(self, name: str, dependency: Any) -> HealthReport:
        """Return a neutral status when an optional dependency is not configured."""
        if dependency is None:
            return self._health_response(True, {"component": name, "status": "not_configured"})
        return self._dependency_health(name, dependency)

    def _dependencies_health_report(
        self,
        *,
        required: Dict[str, Any],
        optional: Optional[Dict[str, Any]] = None,
        include_cache: bool = True,
    ) -> HealthReport:
        """Aggregate dependency health data into a normalized response."""

        checks: Dict[str, HealthReport] = {}

        for name, dependency in required.items():
            checks[name] = self._dependency_health(name, dependency)

        if optional:
            for name, dependency in optional.items():
                checks[name] = self._optional_dependency_health(name, dependency)

        if include_cache:
            if self.cache:
                checks["cache"] = self._cache_health()
            else:
                checks["cache"] = self._health_response(True, {"component": "cache", "status": "disabled"})

        ok = all(result[0] for result in checks.values())
        details = {name: payload for name, (_, payload) in checks.items()}
        return self._health_response(ok, {"dependencies": details})
