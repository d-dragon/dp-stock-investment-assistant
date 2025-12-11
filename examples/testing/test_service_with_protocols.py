"""
Testing Services with Protocol Mocking
=======================================

Demonstrates pytest patterns for testing services that depend on protocols.

Reference: backend-python.instructions.md § Testing with pytest > Protocol-Based Mocking
Related: examples/services/protocol_based_di.py
"""

import pytest
from unittest.mock import MagicMock
from typing import List, Dict, Optional


# ============================================================================
# FIXTURES: Protocol Mocks
# ============================================================================

@pytest.fixture
def mock_workspace_provider():
    """
    Mock implementing WorkspaceProvider protocol.
    
    Any mock with required methods satisfies the protocol.
    No need to import actual WorkspaceService!
    """
    provider = MagicMock()
    
    # Mock list_workspaces method
    provider.list_workspaces.return_value = [
        {"id": "ws1", "name": "Trading Workspace", "owner_id": "user123"},
        {"id": "ws2", "name": "Research Workspace", "owner_id": "user123"}
    ]
    
    # Mock get_workspace method
    provider.get_workspace.return_value = {
        "id": "ws1",
        "name": "Trading Workspace",
        "owner_id": "user123",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    return provider


@pytest.fixture
def mock_symbol_provider():
    """Mock implementing SymbolProvider protocol."""
    provider = MagicMock()
    
    provider.search_symbols.return_value = [
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"}
    ]
    
    provider.get_symbol.return_value = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "sector": "Technology"
    }
    
    return provider


@pytest.fixture
def mock_user_provider():
    """Mock implementing UserProvider protocol."""
    provider = MagicMock()
    
    provider.get_user.return_value = {
        "_id": "user123",
        "email": "test@example.com",
        "name": "Test User"
    }
    
    provider.get_user_profile.return_value = {
        "user_id": "user123",
        "bio": "Stock trader",
        "joined_date": "2023-01-01"
    }
    
    return provider


@pytest.fixture
def mock_user_repository():
    """
    Mock repository with health_check method.
    
    All repositories must implement health_check() returning (bool, dict).
    """
    repo = MagicMock()
    
    # Mock health check
    repo.health_check.return_value = (True, {
        "component": "user_repository",
        "status": "ready"
    })
    
    # Mock CRUD operations
    repo.find_one.return_value = {
        "_id": "user123",
        "email": "test@example.com",
        "name": "Test User"
    }
    
    repo.find_many.return_value = [
        {"_id": "user123", "email": "test@example.com"},
        {"_id": "user456", "email": "user2@example.com"}
    ]
    
    repo.insert_one.return_value = "user789"
    repo.update_one.return_value = {"_id": "user123", "email": "updated@example.com"}
    repo.delete_one.return_value = True
    
    return repo


@pytest.fixture
def mock_cache():
    """Mock cache backend."""
    cache = MagicMock()
    
    cache.is_healthy.return_value = True
    cache.get_json.return_value = None  # Default: cache miss
    cache.set_json.return_value = True
    
    return cache


# ============================================================================
# SERVICE BUILDER: Helper for Consistent Construction
# ============================================================================

def build_user_service(
    user_repo,
    workspace_provider,
    symbol_provider,
    watchlist_repo=None,
    cache=None
):
    """
    Build UserService with dependencies.
    
    Pattern: Centralize service construction to avoid duplication in tests.
    """
    from services.user_service import UserService
    
    return UserService(
        user_repository=user_repo,
        workspace_provider=workspace_provider,
        symbol_provider=symbol_provider,
        watchlist_repository=watchlist_repo,
        cache=cache
    )


# ============================================================================
# TEST SUITE: UserService
# ============================================================================

class TestUserService:
    """Test suite for UserService with protocol mocking."""
    
    def test_get_user_returns_user_data(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test get_user returns data from repository."""
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        user = service.get_user("user123")
        
        assert user["_id"] == "user123"
        assert user["email"] == "test@example.com"
        mock_user_repository.find_one.assert_called_once_with({"_id": "user123"})
    
    def test_get_user_dashboard_aggregates_data(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test dashboard aggregates data from multiple providers."""
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        dashboard = service.get_user_dashboard("user123")
        
        # Verify aggregation
        assert dashboard["user_id"] == "user123"
        assert "workspaces" in dashboard
        assert len(dashboard["workspaces"]) == 2
        
        # Verify protocol methods called
        mock_user_repository.find_one.assert_called_once()
        mock_workspace_provider.list_workspaces.assert_called_once_with("user123", limit=5)
    
    def test_service_uses_cache_when_available(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider,
        mock_cache
    ):
        """Test service uses cache to avoid repository calls."""
        # Setup cache hit
        mock_cache.get_json.return_value = {
            "_id": "user123",
            "email": "cached@example.com"
        }
        
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider,
            cache=mock_cache
        )
        
        user = service.get_user("user123")
        
        # Should return cached data
        assert user["email"] == "cached@example.com"
        
        # Repository should NOT be called (cache hit)
        mock_user_repository.find_one.assert_not_called()
        mock_cache.get_json.assert_called_once()


# ============================================================================
# TEST SUITE: Health Checks
# ============================================================================

class TestServiceHealthChecks:
    """Test health check behavior with protocol dependencies."""
    
    def test_service_healthy_when_all_dependencies_healthy(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test service reports healthy when all required deps healthy."""
        # Setup healthy workspace provider
        mock_workspace_provider.health_check.return_value = (True, {
            "component": "workspace_service",
            "status": "ready"
        })
        
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        healthy, details = service.health_check()
        
        assert healthy is True
        assert details["status"] == "healthy"
        assert "user_repo" in details["dependencies"]
        assert "workspace_provider" in details["dependencies"]
    
    def test_service_unhealthy_when_required_dependency_fails(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test service reports unhealthy when required dependency fails."""
        # Make user repository unhealthy
        mock_user_repository.health_check.return_value = (False, {
            "component": "user_repository",
            "error": "Database connection failed"
        })
        
        mock_workspace_provider.health_check.return_value = (True, {"status": "ready"})
        
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        healthy, details = service.health_check()
        
        assert healthy is False
        assert details["status"] == "unhealthy"
        assert "error" in details["dependencies"]["user_repo"]
    
    def test_service_stays_healthy_when_optional_dependency_fails(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test service stays healthy when optional dependency fails."""
        # Setup healthy required dependencies
        mock_workspace_provider.health_check.return_value = (True, {"status": "ready"})
        
        # Setup unhealthy optional dependency
        mock_watchlist_repo = MagicMock()
        mock_watchlist_repo.health_check.return_value = (False, {
            "error": "Connection timeout"
        })
        
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider,
            watchlist_repo=mock_watchlist_repo  # Optional
        )
        
        healthy, details = service.health_check()
        
        # Service should still be healthy
        assert healthy is True
        assert details["status"] == "healthy"
        
        # Optional failure noted in optional_status
        assert "optional_status" in details
        assert "watchlist_repo" in details["optional_status"]


# ============================================================================
# TEST SUITE: Error Handling
# ============================================================================

class TestServiceErrorHandling:
    """Test error handling patterns."""
    
    def test_service_handles_repository_exceptions(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test service handles repository exceptions gracefully."""
        # Make repository raise exception
        mock_user_repository.find_one.side_effect = Exception("Database error")
        
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        with pytest.raises(Exception, match="Database error"):
            service.get_user("user123")
    
    def test_service_handles_provider_exceptions(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test service handles provider exceptions."""
        # Make workspace provider raise exception
        mock_workspace_provider.list_workspaces.side_effect = Exception("Service unavailable")
        
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        with pytest.raises(Exception, match="Service unavailable"):
            service.get_user_dashboard("user123")


# ============================================================================
# DEMONSTRATION: Running Tests
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING SERVICES WITH PROTOCOL MOCKING")
    print("=" * 80)
    print("\nRun these tests with pytest:")
    print("  pytest examples/testing/test_service_with_protocols.py -v")
    print("\nKey Patterns:")
    print("✅ Use fixtures for protocol mocks (mock_workspace_provider, etc.)")
    print("✅ Builder helper for consistent service construction")
    print("✅ Test health checks: required vs optional dependencies")
    print("✅ Test caching behavior separately")
    print("✅ Test error handling with side_effect")
    print("=" * 80)
