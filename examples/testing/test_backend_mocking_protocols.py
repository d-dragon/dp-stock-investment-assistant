"""
Backend Testing: Protocol-Based Mocking for Services

Demonstrates how to use protocols to avoid circular imports between services
and create clean, testable service dependencies.

Reference: backend-python.instructions.md § Testing > Protocol-Based Mocking
Related: examples/services/protocol_based_di.py
"""

import pytest
from unittest.mock import MagicMock
from typing import List, Dict, Optional


# ============================================================================
# PROTOCOL DEFINITIONS (Mock These in Tests)
# ============================================================================

class WorkspaceProvider:
    """Protocol: Any service providing workspace functionality."""
    
    def list_workspaces(self, user_id: str, *, limit: int = 20) -> List[Dict]:
        """List workspaces for a user."""
        ...
    
    def get_workspace(self, workspace_id: str) -> Optional[Dict]:
        """Get workspace by ID."""
        ...


class SymbolProvider:
    """Protocol: Any service providing symbol/market data."""
    
    def search_symbols(self, query: str, *, limit: int = 10) -> List[Dict]:
        """Search for stock symbols."""
        ...


# ============================================================================
# TEST FIXTURES: Protocol Mocks
# ============================================================================

@pytest.fixture
def mock_workspace_provider():
    """
    Mock implementing WorkspaceProvider protocol.
    
    Benefits:
    - No need to import actual WorkspaceService (avoids circular imports)
    - Duck typing: any object with these methods satisfies protocol
    - Easy to control behavior for testing different scenarios
    """
    provider = MagicMock()
    
    provider.list_workspaces.return_value = [
        {"id": "ws1", "name": "Trading Workspace", "owner_id": "user123"},
        {"id": "ws2", "name": "Research Workspace", "owner_id": "user123"}
    ]
    
    provider.get_workspace.return_value = {
        "id": "ws1",
        "name": "Trading Workspace",
        "owner_id": "user123"
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
    
    return provider


@pytest.fixture
def mock_user_repository():
    """
    Mock repository with health_check method.
    
    All repositories must implement:
    - Standard CRUD methods (find_one, insert_one, update_one, delete_one)
    - health_check() -> (bool, dict) for health status
    """
    repo = MagicMock()
    
    # Health check
    repo.health_check.return_value = (True, {
        "component": "user_repository",
        "status": "ready"
    })
    
    # CRUD operations
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


# ============================================================================
# SERVICE BUILDER HELPER: Consistent Construction
# ============================================================================

def build_user_service(
    user_repo,
    workspace_provider,
    symbol_provider,
    cache=None
):
    """
    Build UserService with dependencies.
    
    Pattern: Centralize service construction to:
    - Reduce boilerplate across tests
    - Ensure consistent wiring
    - Make dependency changes easy to propagate
    
    Usage:
        service = build_user_service(mock_user_repo, mock_workspace_provider, mock_symbol_provider)
    """
    # Import here to avoid circular dependencies in test file
    # In real tests, import at top of file
    
    class UserService:
        """Mock service for demonstration."""
        def __init__(self, user_repository, workspace_provider, symbol_provider, cache=None):
            self._user_repository = user_repository
            self._workspace_provider = workspace_provider
            self._symbol_provider = symbol_provider
            self._cache = cache
        
        def get_user(self, user_id: str) -> Dict:
            """Get user by ID."""
            return self._user_repository.find_one({"_id": user_id})
        
        def get_user_dashboard(self, user_id: str) -> Dict:
            """Aggregate data from multiple providers."""
            user = self._user_repository.find_one({"_id": user_id})
            workspaces = self._workspace_provider.list_workspaces(user_id, limit=5)
            
            return {
                "user_id": user_id,
                "email": user.get("email"),
                "workspaces": workspaces
            }
    
    return UserService(user_repo, workspace_provider, symbol_provider, cache)


# ============================================================================
# TEST SUITE: Service with Protocol Dependencies
# ============================================================================

class TestUserServiceWithProtocols:
    """Test service that depends on protocols."""
    
    def test_get_user_returns_user_data(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test get_user retrieves data from repository."""
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        user = service.get_user("user123")
        
        assert user["_id"] == "user123"
        assert user["email"] == "test@example.com"
        mock_user_repository.find_one.assert_called_once_with({"_id": "user123"})
    
    def test_get_user_dashboard_aggregates_from_providers(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """
        Test dashboard aggregates data from multiple protocol providers.
        
        Key benefit: Don't import actual WorkspaceService or SymbolService
        """
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        dashboard = service.get_user_dashboard("user123")
        
        # Verify aggregation
        assert dashboard["user_id"] == "user123"
        assert dashboard["email"] == "test@example.com"
        assert "workspaces" in dashboard
        assert len(dashboard["workspaces"]) == 2
        
        # Verify protocol methods called
        mock_user_repository.find_one.assert_called_once()
        mock_workspace_provider.list_workspaces.assert_called_once_with("user123", limit=5)
    
    def test_service_handles_provider_exceptions(
        self,
        mock_user_repository,
        mock_workspace_provider,
        mock_symbol_provider
    ):
        """Test service handles exceptions from protocol providers."""
        mock_workspace_provider.list_workspaces.side_effect = Exception("Service unavailable")
        
        service = build_user_service(
            mock_user_repository,
            mock_workspace_provider,
            mock_symbol_provider
        )
        
        with pytest.raises(Exception, match="Service unavailable"):
            service.get_user_dashboard("user123")


# ============================================================================
# PROTOCOL MOCKING BENEFITS
# ============================================================================

def demonstrate_protocol_benefits():
    """Show why protocol-based mocking is better than concrete mocking."""
    
    print("=" * 60)
    print("PROTOCOL-BASED MOCKING BENEFITS")
    print("=" * 60)
    
    print("\n❌ WITHOUT Protocols (Concrete Mocking):")
    print("-" * 60)
    print("""
    from services.workspace_service import WorkspaceService  # Import real service
    from services.symbol_service import SymbolService        # Import real service
    
    mock_workspace = MagicMock(spec=WorkspaceService)  # Must import actual class
    mock_symbol = MagicMock(spec=SymbolService)        # Must import actual class
    
    Problems:
    - Circular imports if UserService imports WorkspaceService
    - Test tightly coupled to implementation
    - Adding new services requires import changes
    """)
    
    print("\n✅ WITH Protocols (Structural Typing):")
    print("-" * 60)
    print("""
    from protocols import WorkspaceProvider  # Only import protocol (interface)
    from protocols import SymbolProvider      # Only import protocol (interface)
    
    mock_workspace = MagicMock()  # Any object with methods satisfies protocol
    mock_symbol = MagicMock()      # No need to import real implementation
    
    Benefits:
    - No circular imports
    - Duck typing: any implementation works
    - Decoupled from concrete implementations
    - Easy to add new service implementations
    """)


if __name__ == "__main__":
    print("Backend Testing: Protocol-Based Mocking for Services")
    print("=" * 60)
    print("\nRun with pytest:")
    print("  pytest examples/testing/test_backend_mocking_protocols.py -v\n")
    
    demonstrate_protocol_benefits()
    
    print("\n" + "=" * 60)
    print("KEY PATTERNS")
    print("=" * 60)
    print("✅ Define protocols as interfaces (no implementation)")
    print("✅ Mock protocols in tests (no need for actual implementations)")
    print("✅ Use builder helpers for consistent service construction")
    print("✅ Test protocol methods called with correct arguments")
    print("✅ Avoid circular imports by depending on protocols")
