"""
Service Health Check Implementation Pattern
===========================================

Demonstrates BaseService health check contract and _dependencies_health_report helper.

Reference: backend-python.instructions.md § Service Layer > BaseService Abstract Class
Related: examples/troubleshooting/health_check_debugging.py
"""

from typing import Tuple, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging


# ============================================================================
# BASE SERVICE: Abstract Health Check Contract
# ============================================================================

@dataclass
class HealthReport:
    """Health check result structure."""
    healthy: bool
    details: Dict[str, Any]


class BaseService(ABC):
    """
    Abstract base class for all services.
    
    Provides:
    - Logging via LoggingMixin
    - Cache access via self.cache
    - Time provider via self._utc_now()
    - Health check contract (must implement)
    - Dependency health aggregation helper
    """
    
    def __init__(
        self,
        *,
        cache: Optional[Any] = None,
        time_provider: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.cache = cache
        self._time_provider = time_provider
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check service health.
        
        Returns:
            (healthy: bool, details: dict) tuple
            
        Implementation MUST call _dependencies_health_report() helper.
        """
        pass
    
    def _dependencies_health_report(
        self,
        *,
        required: Dict[str, Any] = None,
        optional: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Aggregate health of dependencies.
        
        Args:
            required: Dict of dependencies that MUST be healthy
            optional: Dict of dependencies that can fail without affecting service
        
        Returns:
            (healthy: bool, details: dict)
            
        Key Behavior:
        - Service is healthy if ALL required dependencies are healthy
        - Service stays healthy even if optional dependencies fail
        - Optional failures noted in "optional_status" field
        """
        required = required or {}
        optional = optional or {}
        
        checks = {}
        
        # Check required dependencies
        for name, dep in required.items():
            if dep is None:
                checks[name] = (False, {"error": "Dependency is None", "healthy": False})
            elif hasattr(dep, 'health_check'):
                healthy, payload = dep.health_check()
                checks[name] = (healthy, {**payload, "healthy": healthy})
            else:
                checks[name] = (True, {"component": name, "status": "available", "healthy": True})
        
        # Check optional dependencies (don't affect overall health)
        optional_failures = []
        for name, dep in optional.items():
            if dep is None:
                optional_failures.append(f"{name} unavailable")
            elif hasattr(dep, 'health_check'):
                healthy, _ = dep.health_check()
                if not healthy:
                    optional_failures.append(f"{name} unhealthy")
            # If optional dep exists and healthy, no action needed
        
        # Check cache if present
        if self.cache:
            try:
                cache_healthy = self.cache.is_healthy() if hasattr(self.cache, 'is_healthy') else True
                checks['cache'] = (cache_healthy, {
                    "component": "cache",
                    "status": "available" if cache_healthy else "unavailable",
                    "healthy": cache_healthy
                })
            except Exception as e:
                checks['cache'] = (False, {"component": "cache", "error": str(e), "healthy": False})
        
        # Aggregate: Service healthy if ALL required dependencies healthy
        ok = all(result[0] for result in checks.values())
        
        details = {
            "status": "healthy" if ok else "unhealthy",
            "component": self.__class__.__name__.lower().replace("service", "_service"),
            "dependencies": {name: payload for name, (_, payload) in checks.items()}
        }
        
        if optional_failures:
            details["optional_status"] = f"{', '.join(optional_failures)} (degraded mode)"
        
        return ok, details


# ============================================================================
# EXAMPLE 1: Simple Service (No Optional Dependencies)
# ============================================================================

class SymbolsService(BaseService):
    """
    Example service with only required dependencies.
    
    Health check is simple: repository must be healthy.
    """
    
    SYMBOL_CACHE_TTL = 300  # 5 minutes
    
    def __init__(
        self,
        *,
        symbols_repository,
        cache=None,
        logger=None
    ):
        super().__init__(cache=cache, logger=logger)
        self._symbols_repository = symbols_repository
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """Check service health - repository must be healthy."""
        return self._dependencies_health_report(
            required={"symbols_repo": self._symbols_repository}
        )
    
    def search_symbols(self, query: str, *, limit: int = 10):
        """Search for symbols (example method)."""
        cache_key = f"symbols_search:{query}:{limit}"
        
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached
        
        results = self._symbols_repository.search(query, limit=limit)
        
        if self.cache and results:
            self.cache.set_json(cache_key, results, ttl_seconds=self.SYMBOL_CACHE_TTL)
        
        return results


# ============================================================================
# EXAMPLE 2: Complex Service (Required + Optional Dependencies)
# ============================================================================

class UserService(BaseService):
    """
    Example service with both required and optional dependencies.
    
    Required:
    - user_repository: Must be healthy
    - workspace_provider: Must be healthy
    
    Optional:
    - watchlist_repository: Can be None or unhealthy
    - symbol_provider: Can be None or unhealthy
    """
    
    USER_CACHE_TTL = 300  # 5 minutes
    
    def __init__(
        self,
        *,
        user_repository,
        workspace_provider,
        watchlist_repository=None,
        symbol_provider=None,
        cache=None,
        logger=None
    ):
        super().__init__(cache=cache, logger=logger)
        self._user_repository = user_repository
        self._workspace_provider = workspace_provider
        self._watchlist_repository = watchlist_repository
        self._symbol_provider = symbol_provider
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check service health.
        
        Service is healthy if:
        - user_repository is healthy
        - workspace_provider is healthy
        - (watchlist_repository and symbol_provider failures are OK)
        """
        return self._dependencies_health_report(
            required={
                "user_repo": self._user_repository,
                "workspace_provider": self._workspace_provider
            },
            optional={
                "watchlist_repo": self._watchlist_repository,
                "symbol_provider": self._symbol_provider
            }
        )


# ============================================================================
# EXAMPLE 3: Service with Custom Health Logic
# ============================================================================

class WorkspaceService(BaseService):
    """
    Example service with custom health checks.
    
    Demonstrates checking non-standard dependencies.
    """
    
    WORKSPACE_CACHE_TTL = 300
    
    def __init__(
        self,
        *,
        workspace_repository,
        user_provider,
        data_manager=None,  # Custom dependency (not a repository)
        cache=None,
        logger=None
    ):
        super().__init__(cache=cache, logger=logger)
        self._workspace_repository = workspace_repository
        self._user_provider = user_provider
        self._data_manager = data_manager
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check service health with custom data_manager check.
        """
        # Start with standard dependency checks
        healthy, details = self._dependencies_health_report(
            required={
                "workspace_repo": self._workspace_repository,
                "user_provider": self._user_provider
            }
        )
        
        # Add custom check for data_manager (if present)
        if self._data_manager:
            try:
                # Assume data_manager has custom is_available() method
                dm_healthy = self._data_manager.is_available()
                details["dependencies"]["data_manager"] = {
                    "component": "data_manager",
                    "status": "available" if dm_healthy else "unavailable",
                    "healthy": dm_healthy
                }
                # Optional: Don't fail service if data_manager unavailable
                if not dm_healthy:
                    opt_status = details.get("optional_status", "")
                    details["optional_status"] = f"{opt_status}, data_manager unavailable" if opt_status else "data_manager unavailable"
            except Exception as e:
                self.logger.warning(f"Data manager health check failed: {e}")
                details["dependencies"]["data_manager"] = {
                    "component": "data_manager",
                    "error": str(e),
                    "healthy": False
                }
        
        return healthy, details


# ============================================================================
# TESTING: Mock Dependencies
# ============================================================================

def demonstrate_health_check_testing():
    """Show how to test health checks with mocks."""
    from unittest.mock import MagicMock
    
    print("=" * 80)
    print("HEALTH CHECK TESTING")
    print("=" * 80)
    
    # Test 1: All dependencies healthy
    print("\n1. All dependencies healthy:")
    print("-" * 80)
    
    mock_repo = MagicMock()
    mock_repo.health_check.return_value = (True, {"component": "symbols_repository", "status": "ready"})
    
    service = SymbolsService(symbols_repository=mock_repo)
    healthy, details = service.health_check()
    
    print(f"   Healthy: {healthy}")
    print(f"   Status: {details['status']}")
    print(f"   Dependencies: {list(details['dependencies'].keys())}")
    
    # Test 2: Required dependency unhealthy
    print("\n2. Required dependency unhealthy:")
    print("-" * 80)
    
    mock_repo_fail = MagicMock()
    mock_repo_fail.health_check.return_value = (False, {"component": "symbols_repository", "error": "Connection failed"})
    
    service_fail = SymbolsService(symbols_repository=mock_repo_fail)
    healthy, details = service_fail.health_check()
    
    print(f"   Healthy: {healthy}")
    print(f"   Status: {details['status']}")
    print(f"   Error: {details['dependencies']['symbols_repo'].get('error')}")
    
    # Test 3: Optional dependency unhealthy (service stays healthy)
    print("\n3. Optional dependency unhealthy (service stays healthy):")
    print("-" * 80)
    
    mock_user_repo = MagicMock()
    mock_user_repo.health_check.return_value = (True, {"status": "ready"})
    
    mock_workspace = MagicMock()
    mock_workspace.health_check.return_value = (True, {"status": "ready"})
    
    mock_watchlist_fail = MagicMock()
    mock_watchlist_fail.health_check.return_value = (False, {"error": "Database error"})
    
    user_service = UserService(
        user_repository=mock_user_repo,
        workspace_provider=mock_workspace,
        watchlist_repository=mock_watchlist_fail  # Optional - can fail
    )
    
    healthy, details = user_service.health_check()
    
    print(f"   Healthy: {healthy}")  # Still True!
    print(f"   Status: {details['status']}")
    print(f"   Optional Status: {details.get('optional_status', 'N/A')}")


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    print("=" * 80)
    print("SERVICE HEALTH CHECK IMPLEMENTATION PATTERNS")
    print("=" * 80)
    
    demonstrate_health_check_testing()
    
    print("\n" + "=" * 80)
    print("KEY PATTERNS")
    print("=" * 80)
    print("✅ All services extend BaseService and implement health_check()")
    print("✅ Use _dependencies_health_report(required={...}, optional={...})")
    print("✅ Required dependencies MUST be healthy for service to be healthy")
    print("✅ Optional dependencies can fail without affecting service health")
    print("✅ Cache is automatically checked if present")
    print("✅ Test with MagicMock returning (bool, dict) tuples")
    print("=" * 80)
