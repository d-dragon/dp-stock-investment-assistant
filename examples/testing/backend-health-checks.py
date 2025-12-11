"""
Backend Health Check Testing Patterns

Demonstrates how to test service health checks with required and optional dependencies.

Reference: testing.instructions.md#health-check-testing
"""

import pytest
from typing import Dict, Tuple, Any, Optional
from unittest.mock import MagicMock


# ============================================================================
# MOCK COMPONENTS (for testing)
# ============================================================================

class MockRepository:
    """Mock repository with health check."""
    
    def __init__(self, is_healthy: bool = True, error_message: str = ""):
        self._is_healthy = is_healthy
        self._error_message = error_message
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        if self._is_healthy:
            return True, {
                "component": "mock_repository",
                "status": "ready"
            }
        else:
            return False, {
                "component": "mock_repository",
                "status": "unavailable",
                "error": self._error_message
            }


class MockCacheBackend:
    """Mock cache backend with health check."""
    
    def __init__(self, is_healthy: bool = True):
        self._is_healthy = is_healthy
    
    def is_healthy(self) -> bool:
        return self._is_healthy
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        if self._is_healthy:
            return True, {
                "component": "cache",
                "status": "connected",
                "backend": "redis"
            }
        else:
            return False, {
                "component": "cache",
                "status": "unreachable",
                "error": "Connection refused"
            }


# ============================================================================
# EXAMPLE SERVICE WITH HEALTH CHECK
# ============================================================================

class ExampleService:
    """
    Service demonstrating health check patterns.
    
    Shows:
    - Required vs optional dependency handling
    - Degraded state detection
    - Component-level health reporting
    """
    
    def __init__(
        self,
        required_repository: MockRepository,
        optional_cache: Optional[MockCacheBackend] = None,
    ):
        self._required_repository = required_repository
        self._optional_cache = optional_cache
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check health of service and dependencies.
        
        Returns:
            (healthy: bool, details: dict)
            
        Logic:
        - Service healthy = all required dependencies healthy
        - Optional dependencies can fail without affecting service health
        - Details include component-level health status
        """
        return self._dependencies_health_report(
            required={"repository": self._required_repository},
            optional={"cache": self._optional_cache}
        )
    
    def _dependencies_health_report(
        self,
        required: Dict[str, Any],
        optional: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Aggregate health of required and optional dependencies.
        
        Pattern from BaseService in backend-python.instructions.md
        """
        all_healthy = True
        dependencies_status = {}
        degraded_services = []
        
        # Check required dependencies
        for name, component in required.items():
            if component is None:
                all_healthy = False
                dependencies_status[name] = {
                    "healthy": False,
                    "error": "Component not initialized"
                }
            else:
                comp_healthy, comp_details = component.health_check()
                dependencies_status[name] = {
                    "healthy": comp_healthy,
                    **comp_details
                }
                if not comp_healthy:
                    all_healthy = False
        
        # Check optional dependencies (don't affect overall health)
        for name, component in optional.items():
            if component is None:
                dependencies_status[name] = {
                    "healthy": None,
                    "status": "not configured"
                }
            else:
                comp_healthy, comp_details = component.health_check()
                dependencies_status[name] = {
                    "healthy": comp_healthy,
                    **comp_details
                }
                if not comp_healthy:
                    degraded_services.append(name)
        
        # Build response
        details = {
            "status": "healthy" if all_healthy else "unhealthy",
            "component": "example_service",
            "dependencies": dependencies_status
        }
        
        if degraded_services:
            details["optional_status"] = f"{', '.join(degraded_services)} unavailable (degraded mode)"
        
        return all_healthy, details


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def healthy_repository():
    """Repository that passes health check."""
    return MockRepository(is_healthy=True)


@pytest.fixture
def unhealthy_repository():
    """Repository that fails health check."""
    return MockRepository(is_healthy=False, error_message="Database connection failed")


@pytest.fixture
def healthy_cache():
    """Cache that passes health check."""
    return MockCacheBackend(is_healthy=True)


@pytest.fixture
def unhealthy_cache():
    """Cache that fails health check."""
    return MockCacheBackend(is_healthy=False)


# ============================================================================
# HEALTH CHECK TESTS: ALL HEALTHY
# ============================================================================

def test_service_healthy_when_all_dependencies_healthy(
    healthy_repository,
    healthy_cache,
):
    """Test service reports healthy when all dependencies healthy."""
    service = ExampleService(
        required_repository=healthy_repository,
        optional_cache=healthy_cache,
    )
    
    healthy, details = service.health_check()
    
    assert healthy is True
    assert details["status"] == "healthy"
    assert details["component"] == "example_service"
    
    # Check required dependency
    assert details["dependencies"]["repository"]["healthy"] is True
    assert details["dependencies"]["repository"]["status"] == "ready"
    
    # Check optional dependency
    assert details["dependencies"]["cache"]["healthy"] is True
    
    # No degraded services
    assert "optional_status" not in details


# ============================================================================
# HEALTH CHECK TESTS: REQUIRED DEPENDENCY FAILURES
# ============================================================================

def test_service_unhealthy_when_required_dependency_fails(
    unhealthy_repository,
    healthy_cache
):
    """Test service reports unhealthy when required dependency fails."""
    service = ExampleService(
        required_repository=unhealthy_repository,
        optional_cache=healthy_cache
    )
    
    healthy, details = service.health_check()
    
    assert healthy is False
    assert details["status"] == "unhealthy"
    
    # Check failed required dependency
    assert details["dependencies"]["repository"]["healthy"] is False
    assert "error" in details["dependencies"]["repository"]
    assert "Database connection failed" in details["dependencies"]["repository"]["error"]
    
    # Optional dependencies still checked
    assert details["dependencies"]["cache"]["healthy"] is True


def test_service_unhealthy_when_required_dependency_is_none(healthy_cache):
    """Test service reports unhealthy when required dependency is None."""
    service = ExampleService(
        required_repository=None,  # type: ignore
        optional_cache=healthy_cache
    )
    
    healthy, details = service.health_check()
    
    assert healthy is False
    assert details["status"] == "unhealthy"
    assert details["dependencies"]["repository"]["healthy"] is False
    assert "not initialized" in details["dependencies"]["repository"]["error"]


# ============================================================================
# HEALTH CHECK TESTS: OPTIONAL DEPENDENCY FAILURES
# ============================================================================

def test_service_healthy_when_optional_cache_fails(
    healthy_repository,
    unhealthy_cache
):
    """Test service stays healthy when optional cache fails."""
    service = ExampleService(
        required_repository=healthy_repository,
        optional_cache=unhealthy_cache
    )
    
    healthy, details = service.health_check()
    
    # Service still healthy (cache is optional)
    assert healthy is True
    assert details["status"] == "healthy"
    
    # But shows degraded status
    assert "optional_status" in details
    assert "cache unavailable" in details["optional_status"]
    
    # Cache marked as unhealthy
    assert details["dependencies"]["cache"]["healthy"] is False


def test_service_healthy_when_optional_dependencies_not_configured(
    healthy_repository
):
    """Test service healthy when optional dependencies are None (not configured)."""
    service = ExampleService(
        required_repository=healthy_repository,
        optional_cache=None,
    )
    
    healthy, details = service.health_check()
    
    assert healthy is True
    assert details["status"] == "healthy"
    
    # Optional dependency marked as not configured
    assert details["dependencies"]["cache"]["status"] == "not configured"
    
    # No degraded status (not configured != failed)
    assert "optional_status" not in details


# ============================================================================
# HEALTH CHECK TESTS: MAGIC MOCK PATTERNS
# ============================================================================

def test_health_check_with_magic_mock():
    """Test health check using MagicMock for all dependencies."""
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.health_check.return_value = (True, {"component": "repo", "status": "ready"})
    
    # Create mock cache
    mock_cache = MagicMock()
    mock_cache.health_check.return_value = (True, {"component": "cache", "status": "connected"})
    
    service = ExampleService(
        required_repository=mock_repo,
        optional_cache=mock_cache
    )
    
    healthy, details = service.health_check()
    
    assert healthy is True
    
    # Verify health_check was called on dependencies
    mock_repo.health_check.assert_called_once()
    mock_cache.health_check.assert_called_once()


def test_health_check_aggregates_component_details():
    """Test health check includes component-level details."""
    repo = MockRepository(is_healthy=True)
    cache = MockCacheBackend(is_healthy=True)
    
    service = ExampleService(
        required_repository=repo,
        optional_cache=cache,
    )
    
    healthy, details = service.health_check()
    
    # Component details preserved
    assert "dependencies" in details
    assert "repository" in details["dependencies"]
    assert "cache" in details["dependencies"]
    
    # Repository details
    repo_details = details["dependencies"]["repository"]
    assert repo_details["component"] == "mock_repository"
    assert repo_details["status"] == "ready"
    
    # Cache details
    cache_details = details["dependencies"]["cache"]
    assert cache_details["component"] == "cache"
    assert cache_details["backend"] == "redis"


if __name__ == "__main__":
    print("Backend Health Check Testing Patterns")
    print("=" * 60)
    print("\nRun tests with:")
    print("  pytest examples/testing/backend-health-checks.py -v")
    print("\n📖 Reference: testing.instructions.md#health-check-testing")
