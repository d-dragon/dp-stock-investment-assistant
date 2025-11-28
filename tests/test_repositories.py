"""Unit tests for repository implementations using direct mocking."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from bson import ObjectId

# Import repositories
from data.repositories.mongodb_repository import MongoGenericRepository
from data.repositories.user_repository import UserRepository
from data.repositories.account_repository import AccountRepository
from data.repositories.workspace_repository import WorkspaceRepository
from data.repositories.portfolio_repository import PortfolioRepository
from data.repositories.symbol_repository import SymbolRepository
from data.repositories.session_repository import SessionRepository


class TestMongoGenericRepository:
    """Tests for the generic MongoDB repository base class."""
    
    def test_create_adds_timestamps(self):
        """Test that create method adds created_at and updated_at timestamps."""
        repo = MongoGenericRepository("mongodb://localhost:27017", "test_db", "test_collection")
        
        # Mock the collection directly
        mock_collection = MagicMock()
        mock_collection.insert_one.return_value = Mock(inserted_id=ObjectId())
        repo._collection = mock_collection
        
        test_data = {"name": "Test"}
        result_id = repo.create(test_data)
        
        # Assert timestamps were added
        assert result_id is not None
        call_args = mock_collection.insert_one.call_args[0][0]
        assert "created_at" in call_args
        assert "updated_at" in call_args
    
    def test_update_sets_updated_at(self):
        """Test that update method sets updated_at timestamp."""
        repo = MongoGenericRepository("mongodb://localhost:27017", "test_db", "test_collection")
        
        # Mock the collection directly
        mock_collection = MagicMock()
        mock_collection.update_one.return_value = Mock(modified_count=1)
        repo._collection = mock_collection
        
        test_id = str(ObjectId())
        test_data = {"name": "Updated"}
        result = repo.update(test_id, test_data)
        
        # Assert updated_at was added
        assert result is True
        call_args = mock_collection.update_one.call_args
        assert "updated_at" in call_args[0][1]["$set"]
    
    def test_get_by_id(self):
        """Test getting document by ID."""
        repo = MongoGenericRepository("mongodb://localhost:27017", "test_db", "test_collection")
        
        expected_doc = {"_id": ObjectId(), "name": "Test"}
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = expected_doc
        repo._collection = mock_collection
        
        result = repo.get_by_id(str(expected_doc["_id"]))
        
        assert result == expected_doc
    
    def test_count(self):
        """Test counting documents."""
        repo = MongoGenericRepository("mongodb://localhost:27017", "test_db", "test_collection")
        
        mock_collection = MagicMock()
        mock_collection.count_documents.return_value = 5
        repo._collection = mock_collection
        
        result = repo.count({"status": "active"})
        
        assert result == 5


class TestUserRepository:
    """Tests for UserRepository."""
    
    def test_get_by_email(self):
        """Test getting user by email."""
        repo = UserRepository("mongodb://localhost:27017", "test_db")
        
        expected_user = {"_id": ObjectId(), "email": "test@example.com"}
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = expected_user
        repo._collection = mock_collection
        
        result = repo.get_by_email("test@example.com")
        
        assert result == expected_user
        mock_collection.find_one.assert_called_once_with({"email": "test@example.com"})
    
    def test_search_by_name(self):
        """Test searching users by name."""
        repo = UserRepository("mongodb://localhost:27017", "test_db")
        
        expected_users = [{"_id": ObjectId(), "name": "John Doe"}]
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter(expected_users)
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        repo._collection = mock_collection
        
        result = repo.search_by_name("John")
        
        assert result == expected_users
        # Verify regex query
        call_args = mock_collection.find.call_args[0][0]
        assert "$regex" in call_args["name"]


class TestWorkspaceRepository:
    """Tests for WorkspaceRepository."""
    
    def test_get_by_user_id(self):
        """Test getting workspaces by user ID."""
        repo = WorkspaceRepository("mongodb://localhost:27017", "test_db")
        
        user_id = str(ObjectId())
        expected_workspaces = [{"_id": ObjectId(), "user_id": ObjectId(user_id)}]
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter(expected_workspaces)
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        repo._collection = mock_collection
        
        result = repo.get_by_user_id(user_id)
        
        assert result == expected_workspaces
        call_args = mock_collection.find.call_args[0][0]
        assert call_args["user_id"] == ObjectId(user_id)


class TestSymbolRepository:
    """Tests for SymbolRepository."""
    
    def test_get_by_symbol(self):
        """Test getting symbol by ticker."""
        repo = SymbolRepository("mongodb://localhost:27017", "test_db")
        
        expected_symbol = {"_id": ObjectId(), "symbol": "AAPL"}
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = expected_symbol
        repo._collection = mock_collection
        
        result = repo.get_by_symbol("AAPL")
        
        assert result == expected_symbol
        mock_collection.find_one.assert_called_once_with({"symbol": "AAPL"})
    
    def test_get_tracked_symbols(self):
        """Test getting tracked symbols."""
        repo = SymbolRepository("mongodb://localhost:27017", "test_db")
        
        expected_symbols = [{"_id": ObjectId(), "coverage": {"is_tracked": True}}]
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter(expected_symbols)
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        repo._collection = mock_collection
        
        result = repo.get_tracked_symbols()
        
        assert result == expected_symbols
        call_args = mock_collection.find.call_args[0][0]
        assert call_args["coverage.is_tracked"] is True


class TestSessionRepository:
    """Tests for SessionRepository."""
    
    def test_get_active_sessions(self):
        """Test getting active sessions."""
        repo = SessionRepository("mongodb://localhost:27017", "test_db")
        
        workspace_id = str(ObjectId())
        expected_sessions = [{"_id": ObjectId(), "status": "open"}]
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter(expected_sessions)
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        repo._collection = mock_collection
        
        result = repo.get_active_sessions(workspace_id)
        
        assert result == expected_sessions
        call_args = mock_collection.find.call_args[0][0]
        assert call_args["status"] == "open"


class TestPortfolioRepository:
    """Tests for PortfolioRepository."""
    
    def test_get_by_type(self):
        """Test getting portfolios by type."""
        repo = PortfolioRepository("mongodb://localhost:27017", "test_db")
        
        expected_portfolios = [{"_id": ObjectId(), "type": "real"}]
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter(expected_portfolios)
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        repo._collection = mock_collection
        
        result = repo.get_by_type("real")
        
        assert result == expected_portfolios
        call_args = mock_collection.find.call_args[0][0]
        assert call_args["type"] == "real"


class TestAccountRepository:
    """Tests for AccountRepository."""
    
    def test_get_active_accounts(self):
        """Test getting active accounts."""
        repo = AccountRepository("mongodb://localhost:27017", "test_db")
        
        expected_accounts = [{"_id": ObjectId(), "status": "active"}]
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter(expected_accounts)
        
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor
        repo._collection = mock_collection
        
        result = repo.get_active_accounts()
        
        assert result == expected_accounts
        call_args = mock_collection.find.call_args[0][0]
        assert call_args["status"] == "active"
