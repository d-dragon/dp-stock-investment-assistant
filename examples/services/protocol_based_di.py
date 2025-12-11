"""
Protocol-Based Dependency Injection Pattern
============================================

Demonstrates how to use protocols to avoid circular imports between services.

Problem: Concrete service dependencies create circular imports
Solution: Use structural typing (Protocol) for duck-typed dependencies

Reference: backend-python.instructions.md § Service Layer > Protocols for Decoupling
Related: backend-python.instructions.md § Pitfalls and Gotchas #2
"""

from typing import Protocol, runtime_checkable, List, Dict, Optional
from dataclasses import dataclass


# ============================================================================
# PROBLEM: Circular Import with Concrete Types
# ============================================================================

# ❌ BAD: This causes circular import
"""
# File: services/user_service.py
from services.workspace_service import WorkspaceService  # ← Import WorkspaceService

class UserService:
    def __init__(self, workspace_service: WorkspaceService):
        self._workspace_service = workspace_service
    
    def get_user_dashboard(self, user_id: str):
        workspaces = self._workspace_service.list_workspaces(user_id)
        return {"user_id": user_id, "workspaces": workspaces}


# File: services/workspace_service.py
from services.user_service import UserService  # ← Import UserService (circular!)

class WorkspaceService:
    def __init__(self, user_service: UserService):
        self._user_service = user_service
    
    def get_workspace_owner(self, workspace_id: str):
        owner_id = self._get_owner_id(workspace_id)
        return self._user_service.get_user(owner_id)

# Result: ImportError - circular dependency!
"""


# ============================================================================
# SOLUTION 1: Protocol-Based Dependencies
# ============================================================================

# Step 1: Define protocols in separate file (services/protocols.py)
# ---------------------------------------------------------------------

@runtime_checkable
class WorkspaceProvider(Protocol):
    """
    Protocol for services that provide workspace functionality.
    
    Any class implementing these methods satisfies this protocol,
    regardless of inheritance. This is structural subtyping (duck typing).
    """
    
    def list_workspaces(self, user_id: str, *, limit: int = 20, use_cache: bool = True) -> List[Dict]:
        """List workspaces for a user."""
        ...
    
    def get_workspace(self, workspace_id: str, *, use_cache: bool = True) -> Optional[Dict]:
        """Get workspace by ID."""
        ...


@runtime_checkable
class UserProvider(Protocol):
    """Protocol for services that provide user functionality."""
    
    def get_user(self, user_id: str, *, use_cache: bool = True) -> Optional[Dict]:
        """Get user by ID."""
        ...
    
    def get_user_profile(self, user_id: str, *, use_cache: bool = True) -> Optional[Dict]:
        """Get user profile."""
        ...


@runtime_checkable
class SymbolProvider(Protocol):
    """Protocol for services that provide symbol/market data."""
    
    def search_symbols(self, query: str, *, limit: int = 10) -> List[Dict]:
        """Search for stock symbols."""
        ...
    
    def get_symbol(self, symbol: str, *, use_cache: bool = True) -> Optional[Dict]:
        """Get symbol details."""
        ...


# Step 2: Use protocols in service dependencies (no circular imports!)
# ---------------------------------------------------------------------

# ✅ GOOD: UserService depends on WorkspaceProvider protocol
# File: services/user_service.py
"""
from services.protocols import WorkspaceProvider, SymbolProvider  # ← Only import protocols

class UserService:
    def __init__(
        self,
        user_repository,
        workspace_provider: WorkspaceProvider,  # ← Protocol, not concrete class
        symbol_provider: SymbolProvider,
        cache=None
    ):
        self._user_repository = user_repository
        self._workspace_provider = workspace_provider
        self._symbol_provider = symbol_provider
        self._cache = cache
    
    def get_user_dashboard(self, user_id: str) -> Dict:
        # WorkspaceProvider protocol guarantees list_workspaces() exists
        workspaces = self._workspace_provider.list_workspaces(user_id, limit=5)
        
        user = self._user_repository.find_one({"_id": user_id})
        
        return {
            "user_id": user_id,
            "email": user.get("email"),
            "workspaces": workspaces
        }
"""

# ✅ GOOD: WorkspaceService depends on UserProvider protocol
# File: services/workspace_service.py
"""
from services.protocols import UserProvider  # ← Only import protocol

class WorkspaceService:
    def __init__(
        self,
        workspace_repository,
        user_provider: UserProvider,  # ← Protocol, not concrete class
        cache=None
    ):
        self._workspace_repository = workspace_repository
        self._user_provider = user_provider
        self._cache = cache
    
    def get_workspace_with_owner(self, workspace_id: str) -> Dict:
        workspace = self._workspace_repository.find_one({"_id": workspace_id})
        
        if workspace and "owner_id" in workspace:
            # UserProvider protocol guarantees get_user() exists
            owner = self._user_provider.get_user(workspace["owner_id"])
            workspace["owner"] = owner
        
        return workspace
"""


# ============================================================================
# SOLUTION 2: ServiceFactory Wiring
# ============================================================================

# File: services/factory.py
"""
from services.user_service import UserService
from services.workspace_service import WorkspaceService
from services.symbols_service import SymbolsService

class ServiceFactory:
    def __init__(self, config, repository_factory, cache_backend):
        self.config = config
        self.repository_factory = repository_factory
        self.cache_backend = cache_backend
        self._services = {}  # Singleton cache
    
    def get_user_service(self) -> UserService:
        if "user" not in self._services:
            # Wire UserService with protocol dependencies
            self._services["user"] = UserService(
                user_repository=self.repository_factory.get_user_repository(),
                workspace_provider=self.get_workspace_service(),  # ← Satisfies WorkspaceProvider protocol
                symbol_provider=self.get_symbols_service(),       # ← Satisfies SymbolProvider protocol
                cache=self.cache_backend
            )
        return self._services["user"]
    
    def get_workspace_service(self) -> WorkspaceService:
        if "workspace" not in self._services:
            # Wire WorkspaceService with protocol dependencies
            self._services["workspace"] = WorkspaceService(
                workspace_repository=self.repository_factory.get_workspace_repository(),
                user_provider=self.get_user_service(),  # ← Satisfies UserProvider protocol
                cache=self.cache_backend
            )
        return self._services["workspace"]
    
    def get_symbols_service(self) -> SymbolsService:
        if "symbols" not in self._services:
            self._services["symbols"] = SymbolsService(
                symbols_repository=self.repository_factory.get_symbols_repository(),
                cache=self.cache_backend
            )
        return self._services["symbols"]
"""


# ============================================================================
# TESTING: Protocol Mocking
# ============================================================================

def demonstrate_protocol_mocking():
    """
    Protocols make testing easier - any mock with required methods works.
    
    Used in: tests/test_user_service.py
    """
    from unittest.mock import MagicMock
    
    # Create mock that satisfies WorkspaceProvider protocol
    mock_workspace_provider = MagicMock()
    mock_workspace_provider.list_workspaces.return_value = [
        {"id": "ws1", "name": "Trading Workspace"},
        {"id": "ws2", "name": "Research Workspace"}
    ]
    
    # Create mock that satisfies SymbolProvider protocol
    mock_symbol_provider = MagicMock()
    mock_symbol_provider.search_symbols.return_value = [
        {"symbol": "AAPL", "name": "Apple Inc."}
    ]
    
    # Mock repository
    mock_user_repo = MagicMock()
    mock_user_repo.find_one.return_value = {"_id": "user123", "email": "test@example.com"}
    
    print("✅ Mocks created - they satisfy protocols through duck typing")
    print(f"   WorkspaceProvider.list_workspaces: {callable(mock_workspace_provider.list_workspaces)}")
    print(f"   SymbolProvider.search_symbols: {callable(mock_symbol_provider.search_symbols)}")
    
    # These mocks can now be used in UserService tests
    # No need to import actual WorkspaceService or SymbolsService!
    return mock_workspace_provider, mock_symbol_provider, mock_user_repo


# ============================================================================
# PROTOCOL VALIDATION: runtime_checkable
# ============================================================================

def demonstrate_protocol_validation():
    """
    @runtime_checkable allows isinstance() checks at runtime.
    
    Useful for validation and debugging.
    """
    from unittest.mock import MagicMock
    
    # Create mock with protocol methods
    mock_provider = MagicMock()
    mock_provider.list_workspaces = lambda user_id, limit=20, use_cache=True: []
    mock_provider.get_workspace = lambda workspace_id, use_cache=True: None
    
    # Check if mock satisfies protocol
    is_valid = isinstance(mock_provider, WorkspaceProvider)
    
    print("\n✅ Protocol Validation (runtime_checkable)")
    print(f"   isinstance(mock_provider, WorkspaceProvider): {is_valid}")
    print("   Mock has required methods: list_workspaces, get_workspace")
    
    # Create incomplete mock (missing methods)
    incomplete_mock = MagicMock()
    incomplete_mock.list_workspaces = lambda: []  # Only one method
    
    is_invalid = isinstance(incomplete_mock, WorkspaceProvider)
    print(f"\n❌ Incomplete Mock Validation")
    print(f"   isinstance(incomplete_mock, WorkspaceProvider): {is_invalid}")
    print("   Mock missing: get_workspace method")


# ============================================================================
# BENEFITS: Why Protocols?
# ============================================================================

def show_protocol_benefits():
    """Display key benefits of protocol-based dependency injection."""
    
    benefits = [
        ("No Circular Imports", "Services depend on protocols, not concrete classes"),
        ("Duck Typing", "Any object with required methods satisfies protocol"),
        ("Easy Testing", "Mock any protocol without importing concrete service"),
        ("Loose Coupling", "Services don't know about each other's implementation"),
        ("Type Safety", "Type checkers (mypy) verify protocol conformance"),
        ("Runtime Validation", "@runtime_checkable enables isinstance() checks"),
        ("Flexible Wiring", "ServiceFactory wires concrete implementations"),
    ]
    
    print("\n" + "=" * 80)
    print("BENEFITS OF PROTOCOL-BASED DEPENDENCY INJECTION")
    print("=" * 80)
    
    for i, (benefit, description) in enumerate(benefits, 1):
        print(f"\n{i}. {benefit}")
        print(f"   {description}")


# ============================================================================
# COMPARISON: Before vs After
# ============================================================================

def show_comparison():
    """Show before/after comparison."""
    
    print("\n" + "=" * 80)
    print("BEFORE VS AFTER COMPARISON")
    print("=" * 80)
    
    print("\n❌ BEFORE (Circular Imports):")
    print("-" * 80)
    print("""
# services/user_service.py
from services.workspace_service import WorkspaceService  # ← Concrete import

class UserService:
    def __init__(self, workspace_service: WorkspaceService):
        self._workspace_service = workspace_service

# services/workspace_service.py
from services.user_service import UserService  # ← Circular!

class WorkspaceService:
    def __init__(self, user_service: UserService):
        self._user_service = user_service

# Result: ImportError!
    """)
    
    print("\n✅ AFTER (Protocol-Based):")
    print("-" * 80)
    print("""
# services/protocols.py
from typing import Protocol

class WorkspaceProvider(Protocol):
    def list_workspaces(self, user_id: str) -> List[Dict]: ...

class UserProvider(Protocol):
    def get_user(self, user_id: str) -> Optional[Dict]: ...

# services/user_service.py
from services.protocols import WorkspaceProvider  # ← Only protocol

class UserService:
    def __init__(self, workspace_provider: WorkspaceProvider):
        self._workspace_provider = workspace_provider

# services/workspace_service.py
from services.protocols import UserProvider  # ← Only protocol

class WorkspaceService:
    def __init__(self, user_provider: UserProvider):
        self._user_provider = user_provider

# Result: No circular imports! ServiceFactory wires concrete implementations.
    """)


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("PROTOCOL-BASED DEPENDENCY INJECTION")
    print("=" * 80)
    
    show_comparison()
    show_protocol_benefits()
    
    print("\n" + "=" * 80)
    print("TESTING DEMONSTRATION")
    print("=" * 80)
    demonstrate_protocol_mocking()
    demonstrate_protocol_validation()
    
    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("✅ Use Protocol for cross-service dependencies (avoid circular imports)")
    print("✅ Define all protocols in services/protocols.py")
    print("✅ ServiceFactory wires concrete implementations")
    print("✅ Tests mock protocols with MagicMock (no real service imports)")
    print("✅ Type checkers verify protocol conformance at compile time")
    print("✅ @runtime_checkable enables isinstance() validation")
    print("=" * 80)
