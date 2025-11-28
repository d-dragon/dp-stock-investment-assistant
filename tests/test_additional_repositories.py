"""Tests for additional repositories (notes, tasks, analyses, chats, notifications, positions, trades, technical_indicators, market_snapshots, investment_ideas, watchlists)."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from data.repositories.note_repository import NoteRepository
from data.repositories.task_repository import TaskRepository
from data.repositories.analysis_repository import AnalysisRepository
from data.repositories.chat_repository import ChatRepository
from data.repositories.notification_repository import NotificationRepository
from data.repositories.position_repository import PositionRepository
from data.repositories.trade_repository import TradeRepository
from data.repositories.technical_indicator_repository import TechnicalIndicatorRepository
from data.repositories.market_snapshot_repository import MarketSnapshotRepository
from data.repositories.investment_idea_repository import InvestmentIdeaRepository
from data.repositories.watchlist_repository import WatchlistRepository


class TestNoteRepository:
    """Test cases for NoteRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_by_user_id(self, mock_client):
        """Test retrieving notes by user ID."""
        repo = NoteRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "user_id": "user123", "title": "Note 1"},
            {"_id": "2", "user_id": "user123", "title": "Note 2"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        notes = repo.get_by_user_id("user123")
        
        assert len(notes) == 2
        assert notes[0]["user_id"] == "user123"
        repo.collection.find.assert_called_once_with({"user_id": "user123"})
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_search_content(self, mock_client):
        """Test searching notes by content."""
        repo = NoteRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "title": "Market Analysis", "content": "Stock is bullish"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        notes = repo.search_content("bullish")
        
        assert len(notes) == 1
        assert "bullish" in notes[0]["content"].lower()


class TestTaskRepository:
    """Test cases for TaskRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_by_status(self, mock_client):
        """Test retrieving tasks by status."""
        repo = TaskRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "status": "pending", "title": "Task 1"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        tasks = repo.get_by_status("pending")
        
        assert len(tasks) == 1
        assert tasks[0]["status"] == "pending"
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_overdue_tasks(self, mock_client):
        """Test retrieving overdue tasks."""
        repo = TaskRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "status": "pending", "due_date": datetime(2024, 1, 1)}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        tasks = repo.get_overdue_tasks()
        
        assert len(tasks) == 1


class TestAnalysisRepository:
    """Test cases for AnalysisRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_by_symbol(self, mock_client):
        """Test retrieving analyses by symbol."""
        repo = AnalysisRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "symbol": "AAPL", "analysis_type": "fundamental"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        analyses = repo.get_by_symbol("AAPL")
        
        assert len(analyses) == 1
        assert analyses[0]["symbol"] == "AAPL"
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_latest_by_symbol(self, mock_client):
        """Test retrieving latest analysis for a symbol."""
        repo = AnalysisRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "symbol": "AAPL", "created_at": datetime(2024, 12, 1)}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        analysis = repo.get_latest_by_symbol("AAPL")
        
        assert analysis is not None
        assert analysis["symbol"] == "AAPL"


class TestChatRepository:
    """Test cases for ChatRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_by_session(self, mock_client):
        """Test retrieving chats by session."""
        repo = ChatRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "session_id": "session123", "content": "Hello"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        chats = repo.get_by_session("session123")
        
        assert len(chats) == 1
        assert chats[0]["session_id"] == "session123"


class TestNotificationRepository:
    """Test cases for NotificationRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_unread(self, mock_client):
        """Test retrieving unread notifications."""
        repo = NotificationRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "user_id": "user123", "is_read": False}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        notifications = repo.get_unread("user123")
        
        assert len(notifications) == 1
        assert notifications[0]["is_read"] is False
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_mark_all_as_read(self, mock_client):
        """Test marking all notifications as read."""
        repo = NotificationRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_result = MagicMock()
        mock_result.modified_count = 5
        repo.collection.update_many = MagicMock(return_value=mock_result)
        
        count = repo.mark_all_as_read("user123")
        
        assert count == 5


class TestPositionRepository:
    """Test cases for PositionRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_open_positions(self, mock_client):
        """Test retrieving open positions."""
        repo = PositionRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "status": "open", "symbol": "AAPL"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        positions = repo.get_open_positions()
        
        assert len(positions) == 1
        assert positions[0]["status"] == "open"


class TestTradeRepository:
    """Test cases for TradeRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_by_symbol(self, mock_client):
        """Test retrieving trades by symbol."""
        repo = TradeRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "symbol": "AAPL", "trade_type": "buy"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        trades = repo.get_by_symbol("AAPL")
        
        assert len(trades) == 1
        assert trades[0]["symbol"] == "AAPL"
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_recent_trades(self, mock_client):
        """Test retrieving recent executed trades."""
        repo = TradeRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "status": "executed", "symbol": "AAPL"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        trades = repo.get_recent_trades()
        
        assert len(trades) == 1
        assert trades[0]["status"] == "executed"


class TestTechnicalIndicatorRepository:
    """Test cases for TechnicalIndicatorRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_by_symbol_and_type(self, mock_client):
        """Test retrieving indicators by symbol and type."""
        repo = TechnicalIndicatorRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "symbol": "AAPL", "indicator_type": "rsi"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        indicators = repo.get_by_symbol_and_type("AAPL", "rsi")
        
        assert len(indicators) == 1
        assert indicators[0]["indicator_type"] == "rsi"


class TestMarketSnapshotRepository:
    """Test cases for MarketSnapshotRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_latest(self, mock_client):
        """Test retrieving latest market snapshot."""
        repo = MarketSnapshotRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "market": "US", "snapshot_time": datetime.utcnow()}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        snapshot = repo.get_latest("US")
        
        assert snapshot is not None
        assert snapshot["market"] == "US"


class TestInvestmentIdeaRepository:
    """Test cases for InvestmentIdeaRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_by_status(self, mock_client):
        """Test retrieving investment ideas by status."""
        repo = InvestmentIdeaRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "status": "active", "title": "Idea 1"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        ideas = repo.get_by_status("active")
        
        assert len(ideas) == 1
        assert ideas[0]["status"] == "active"


class TestWatchlistRepository:
    """Test cases for WatchlistRepository."""
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_add_symbol_to_watchlist(self, mock_client):
        """Test adding a symbol to watchlist."""
        repo = WatchlistRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_result = MagicMock()
        mock_result.modified_count = 1
        repo.collection.update_one = MagicMock(return_value=mock_result)
        
        # Mock ObjectId validation
        with patch.object(repo, '_validate_object_id', return_value="507f1f77bcf86cd799439011"):
            success = repo.add_symbol_to_watchlist("507f1f77bcf86cd799439011", "AAPL")
        
        assert success is True
    
    @patch('data.repositories.mongodb_repository.MongoClient')
    def test_get_public_watchlists(self, mock_client):
        """Test retrieving public watchlists."""
        repo = WatchlistRepository("mongodb://localhost:27017", "test_db")
        repo.initialize()
        
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value.limit.return_value = [
            {"_id": "1", "is_public": True, "name": "Tech Stocks"}
        ]
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        watchlists = repo.get_public_watchlists()
        
        assert len(watchlists) == 1
        assert watchlists[0]["is_public"] is True
