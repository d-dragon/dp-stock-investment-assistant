"""
Service Health Check Debugging Guide

Demonstrates how to diagnose and fix service health check failures
that result in 503 Service Unavailable responses.

Reference: backend-python.instructions.md § Pitfalls > Service Returning 503
"""

from typing import Any, Dict, Optional, Tuple
from unittest.mock import MagicMock


# ============================================================================
# STEP 1: Check Service Health Directly
# ============================================================================

def diagnose_service_health(service: Any) -> None:
    """
    Diagnostic script to identify unhealthy dependencies.
    
    Run this in Python REPL or debug script when routes return 503.
    """
    print("=" * 60)
    print("SERVICE HEALTH DIAGNOSTIC")
    print("=" * 60)
    
    # Call health_check method
    healthy, details = service.health_check()
    
    print(f"\n✅ Overall Health: {'HEALTHY' if healthy else '❌ UNHEALTHY'}")
    print(f"\nDetails:")
    print(f"  Status: {details.get('status', 'unknown')}")
    print(f"  Component: {details.get('component', 'unknown')}")
    
    # Inspect dependencies
    if 'dependencies' in details:
        print(f"\n📦 Dependencies:")
        for name, dep_info in details['dependencies'].items():
            status_icon = "✅" if dep_info.get('healthy', True) else "❌"
            status = dep_info.get('status', 'unknown')
            print(f"  {status_icon} {name:20} {status}")
            
            # Show error details
            if 'error' in dep_info:
                print(f"     └─ Error: {dep_info['error']}")
    
    # Optional status
    if 'optional_status' in details:
        print(f"\n⚠️  Optional Dependencies: {details['optional_status']}")
    
    return healthy, details


# ============================================================================
# STEP 2: Common Root Causes
# ============================================================================

def demonstrate_common_503_causes():
    """Show common reasons for 503 errors and how to fix them."""
    
    print("\n" + "=" * 60)
    print("COMMON 503 CAUSES")
    print("=" * 60)
    
    causes = [
        {
            "cause": "MongoDB Disconnected",
            "symptom": "user_repository health check returns False",
            "check": "Verify MONGODB_URI in config, check docker ps for mongodb container",
            "fix": "docker-compose up -d mongodb OR check network connectivity"
        },
        {
            "cause": "Redis Unavailable",
            "symptom": "cache health check returns False",
            "check": "Verify REDIS_HOST in config, check docker ps for redis container",
            "fix": "docker-compose up -d redis OR mark Redis as optional dependency"
        },
        {
            "cause": "Repository Missing health_check()",
            "symptom": "AttributeError: 'Repository' object has no attribute 'health_check'",
            "check": "All repositories must implement health_check() method",
            "fix": "Add health_check() method to repository extending MongoGenericRepository"
        },
        {
            "cause": "Optional Dependency Marked as Required",
            "symptom": "Service unhealthy when optional component fails",
            "check": "Verify _dependencies_health_report(required={}, optional={})",
            "fix": "Move optional dependencies to optional={} parameter"
        },
    ]
    
    for i, item in enumerate(causes, 1):
        print(f"\n{i}. {item['cause']}")
        print(f"   Symptom: {item['symptom']}")
        print(f"   Check: {item['check']}")
        print(f"   Fix: {item['fix']}")


# ============================================================================
# STEP 3: Fix Required vs Optional Dependencies
# ============================================================================

def demonstrate_required_vs_optional():
    """Show correct pattern for required vs optional dependencies."""
    
    print("\n" + "=" * 60)
    print("REQUIRED VS OPTIONAL DEPENDENCIES")
    print("=" * 60)
    
    print("\n❌ WRONG: Cache marked as required")
    print("""
    def health_check(self):
        return self._dependencies_health_report(
            required={
                "user_repo": self._user_repo,
                "cache": self._cache  # ❌ Cache is optional!
            }
        )
    """)
    print("Result: Service fails if Redis is down")
    
    print("\n✅ CORRECT: Cache marked as optional")
    print("""
    def health_check(self):
        return self._dependencies_health_report(
            required={
                "user_repo": self._user_repo  # Must be healthy
            },
            optional={
                "cache": self._cache  # Can fail without service failing
            }
        )
    """)
    print("Result: Service stays healthy even if Redis fails (degraded mode)")


# ============================================================================
# STEP 4: Test Health Check Behavior
# ============================================================================

def test_health_check_with_mocks():
    """Demonstrate testing health check with mocks."""
    
    print("\n" + "=" * 60)
    print("TESTING HEALTH CHECK BEHAVIOR")
    print("=" * 60)
    
    # Create mock repository (healthy)
    mock_repo = MagicMock()
    mock_repo.health_check.return_value = (True, {"component": "user_repository", "status": "ready"})
    
    # Create mock cache (unhealthy)
    mock_cache = MagicMock()
    mock_cache.is_available.return_value = False
    mock_cache.ping.return_value = False
    
    print("\nScenario: Repository healthy, Cache failed")
    print(f"  Repository health: {mock_repo.health_check()}")
    print(f"  Cache available: {mock_cache.is_available()}")
    
    # Simulate service health check
    print("\n✅ Expected: Service still healthy (cache is optional)")
    print("   Details should show:")
    print("   - status: 'healthy'")
    print("   - dependencies.user_repo: healthy=True")
    print("   - dependencies.cache: healthy=False, status='unreachable'")
    print("   - optional_status: 'cache unavailable (degraded mode)'")


# ============================================================================
# STEP 5: Debugging Pattern for 503 Errors
# ============================================================================

def debugging_503_pattern():
    """Step-by-step debugging workflow."""
    
    print("\n" + "=" * 60)
    print("DEBUGGING 503 ERRORS - STEP-BY-STEP")
    print("=" * 60)
    
    steps = [
        "1. Verify service exists: if context.user_service is None",
        "2. Check service health: healthy, details = service.health_check()",
        "3. Inspect dependencies: Look at details['dependencies']",
        "4. Check logs: Look for 'health check failed' messages",
        "5. Verify infrastructure: docker ps (MongoDB, Redis running?)",
        "6. Test connections: mongo mongodb://localhost:27017",
        "7. Review health_check() implementation: required vs optional",
        "8. Add defensive logging: logger.error(f'Service unhealthy: {details}')",
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print("\n✅ Quick Health Check Command:")
    print("""
    python -c "
    from services.factory import ServiceFactory
    from data.repositories.factory import RepositoryFactory
    from utils.config_loader import ConfigLoader
    from utils.cache import CacheBackend
    from pymongo import MongoClient
    
    config = ConfigLoader.load_config()
    client = MongoClient(config['mongodb']['uri'])
    db = client[config['mongodb']['database']]
    
    repo_factory = RepositoryFactory(db, config)
    cache = CacheBackend.from_config(config)
    service_factory = ServiceFactory(config, repository_factory=repo_factory, cache_backend=cache)
    
    user_service = service_factory.get_user_service()
    healthy, details = user_service.health_check()
    
    print(f'Healthy: {healthy}')
    print(f'Details: {details}')
    "
    """)


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SERVICE HEALTH CHECK DEBUGGING")
    print("=" * 60)
    print("\nThis guide helps diagnose 503 Service Unavailable errors")
    print("caused by unhealthy service dependencies.\n")
    
    # Show example with mock service
    mock_service = MagicMock()
    mock_service.health_check.return_value = (
        False,
        {
            "status": "unhealthy",
            "component": "user_service",
            "dependencies": {
                "user_repo": {"healthy": True, "component": "user_repository", "status": "ready"},
                "workspace_provider": {"healthy": True, "component": "workspace_service", "status": "ready"},
                "cache": {"healthy": False, "component": "cache", "status": "unreachable", "error": "Connection refused"}
            }
        }
    )
    
    diagnose_service_health(mock_service)
    demonstrate_common_503_causes()
    demonstrate_required_vs_optional()
    test_health_check_with_mocks()
    debugging_503_pattern()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ Always check service.health_check() when debugging 503")
    print("✅ Inspect details['dependencies'] for failed components")
    print("✅ Mark optional dependencies as optional={}")
    print("✅ Ensure repositories implement health_check() method")
    print("✅ Test with mock dependencies in unit tests")
