"""
Service Health Check Testing Patterns

Demonstrates comprehensive testing patterns for service health checks,
including required/optional dependency handling, degraded states, and
component-level health reporting.

Reference: backend-python.instructions.md § Testing > Health Check Testing
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


class MockExternalService:
    """Mock external service (API, database, etc.)."""
    
    def __init__(self, is_healthy: bool = True):
        self._is_healthy = is_healthy
    
    def ping(self) -> bool:
        return self._is_healthy


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
        optional_external: Optional[MockExternalService] = None
    ):
        self._required_repository = required_repository
        self._optional_cache = optional_cache
        self._optional_external = optional_external
    
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
            optional={
                "cache": self._optional_cache,
                "external_service": self._optional_external
            }
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


@pytest.fixture
def healthy_external():
    """External service that passes health check."""
    service = MockExternalService(is_healthy=True)
    # Mock health_check method
    service.health_check = lambda: (True, {"component": "external_api", "status": "available"})
    return service


@pytest.fixture
def unhealthy_external():
    """External service that fails health check."""
    service = MockExternalService(is_healthy=False)
    service.health_check = lambda: (False, {"component": "external_api", "status": "timeout", "error": "Request timeout"})
    return service


# ============================================================================
# HEALTH CHECK TESTS: ALL HEALTHY
# ============================================================================

def test_service_healthy_when_all_dependencies_healthy(
    healthy_repository,
    healthy_cache,
    healthy_external
):
    """Test service reports healthy when all dependencies healthy."""
    service = ExampleService(
        required_repository=healthy_repository,
        optional_cache=healthy_cache,
        optional_external=healthy_external
    )
    
    healthy, details = service.health_check()
    
    assert healthy is True
    assert details["status"] == "healthy"
    assert details["component"] == "example_service"
    
    # Check required dependency
    assert details["dependencies"]["repository"]["healthy"] is True
    assert details["dependencies"]["repository"]["status"] == "ready"
    
    # Check optional dependencies
    assert details["dependencies"]["cache"]["healthy"] is True
    assert details["dependencies"]["external_service"]["healthy"] is True
    
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


def test_service_healthy_when_optional_external_fails(
    healthy_repository,
    healthy_cache,
    unhealthy_external
):
    """Test service stays healthy when optional external service fails."""
    service = ExampleService(
        required_repository=healthy_repository,
        optional_cache=healthy_cache,
        optional_external=unhealthy_external
    )
    
    healthy, details = service.health_check()
    
    assert healthy is True
    assert details["status"] == "healthy"
    
    # Shows degraded status
    assert "optional_status" in details
    assert "external_service unavailable" in details["optional_status"]


def test_service_healthy_when_multiple_optional_dependencies_fail(
    healthy_repository,
    unhealthy_cache,
    unhealthy_external
):
    """Test service stays healthy even when multiple optional dependencies fail."""
    service = ExampleService(
        required_repository=healthy_repository,
        optional_cache=unhealthy_cache,
        optional_external=unhealthy_external
    )
    
    healthy, details = service.health_check()
    
    # Still healthy (all optional)
    assert healthy is True
    assert details["status"] == "healthy"
    
    # Multiple degraded services listed
    assert "optional_status" in details
    assert "cache" in details["optional_status"]
    assert "external_service" in details["optional_status"]


def test_service_healthy_when_optional_dependencies_not_configured(
    healthy_repository
):
    """Test service healthy when optional dependencies are None (not configured)."""
    service = ExampleService(
        required_repository=healthy_repository,
        optional_cache=None,
        optional_external=None
    )
    
    healthy, details = service.health_check()
    
    assert healthy is True
    assert details["status"] == "healthy"
    
    # Optional dependencies marked as not configured
    assert details["dependencies"]["cache"]["status"] == "not configured"
    assert details["dependencies"]["external_service"]["status"] == "not configured"
    
    # No degraded status (not configured != failed)
    assert "optional_status" not in details


# ============================================================================
# HEALTH CHECK TESTS: MOCK-BASED PATTERNS
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
        optional_cache=cache
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


# ============================================================================
# HEALTH CHECK TESTS: EDGE CASES
# ============================================================================

def test_health_check_with_mixed_dependency_states(
    unhealthy_repository,
    unhealthy_cache
):
    """Test service correctly reports when required fails and optional fails."""
    service = ExampleService(
        required_repository=unhealthy_repository,
        optional_cache=unhealthy_cache
    )
    
    healthy, details = service.health_check()
    
    # Service unhealthy (required dependency failed)
    assert healthy is False
    assert details["status"] == "unhealthy"
    
    # Both dependencies show as unhealthy
    assert details["dependencies"]["repository"]["healthy"] is False
    assert details["dependencies"]["cache"]["healthy"] is False
    
    # Optional status still shows degraded cache
    assert "optional_status" in details


# ============================================================================
# BEST PRACTICES DEMONSTRATION
# ============================================================================

def demonstrate_health_check_best_practices():
    """Show best practices for health check testing."""
    
    print("=" * 60)
    print("HEALTH CHECK TESTING BEST PRACTICES")
    print("=" * 60)
    
    practices = [
        {
            "practice": "Test All Healthy State",
            "test": "test_service_healthy_when_all_dependencies_healthy",
            "validates": "Service reports healthy when everything works"
        },
        {
            "practice": "Test Required Dependency Failures",
            "test": "test_service_unhealthy_when_required_dependency_fails",
            "validates": "Service unhealthy when critical component fails"
        },
        {
            "practice": "Test Optional Dependency Failures",
            "test": "test_service_healthy_when_optional_cache_fails",
            "validates": "Service stays healthy in degraded mode"
        },
        {
            "practice": "Test Uninitialized Dependencies",
            "test": "test_service_unhealthy_when_required_dependency_is_none",
            "validates": "Service detects missing required components"
        },
        {
            "practice": "Test Multiple Optional Failures",
            "test": "test_service_healthy_when_multiple_optional_dependencies_fail",
            "validates": "Service handles multiple degraded components"
        },
        {
            "practice": "Test Not Configured vs Failed",
            "test": "test_service_healthy_when_optional_dependencies_not_configured",
            "validates": "Distinguish between 'not configured' and 'failed'"
        },
        {
            "practice": "Test Component Details",
            "test": "test_health_check_aggregates_component_details",
            "validates": "Component-level health info preserved"
        },
    ]
    
    for i, item in enumerate(practices, 1):
        print(f"\n{i}. {item['practice']}")
        print(f"   Test: {item['test']}")
        print(f"   Validates: {item['validates']}")


if __name__ == "__main__":
    print("Service Health Check Testing Patterns")
    print("=" * 60)
    print("\nDemonstrates comprehensive testing patterns for service")
    print("health checks with required/optional dependency handling.\n")
    
    demonstrate_health_check_best_practices()
    
    print("\n" + "=" * 60)
    print("KEY PATTERNS")
    print("=" * 60)
    print("✅ Required dependencies: Must be healthy for service health")
    print("✅ Optional dependencies: Can fail without affecting service")
    print("✅ Degraded mode: Service healthy but with reduced functionality")
    print("✅ Component details: Preserve health info from each dependency")
    print("✅ Not configured: Distinguish from failed dependencies")
    
    print("\n📖 Reference: backend-python.instructions.md")
    print("   § Testing with pytest > Health Check Testing")
