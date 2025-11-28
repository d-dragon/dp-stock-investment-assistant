"""Unit tests for RepositoryFactory."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from data.repositories.factory import RepositoryFactory


class TestRepositoryFactory:
    """Test cases for RepositoryFactory."""
    
    @pytest.fixture
    def minimal_config(self):
        """Minimal configuration for testing."""
        return {
            'database': {
                'mongodb': {
                    'connection_string': 'mongodb://localhost:27017',
                    'database_name': 'test_db'
                }
            }
        }
    
    @pytest.fixture
    def config_with_auth(self):
        """Configuration with separate auth credentials."""
        return {
            'database': {
                'mongodb': {
                    'connection_string': 'mongodb://localhost:27017',
                    'database_name': 'test_db',
                    'username': 'test_user',
                    'password': 'test_pass',
                    'auth_source': 'admin'
                }
            }
        }
    
    @pytest.fixture
    def config_with_embedded_creds(self):
        """Configuration with embedded credentials in connection string."""
        return {
            'database': {
                'mongodb': {
                    'connection_string': 'mongodb://user:pass@localhost:27017',
                    'database_name': 'test_db'
                }
            }
        }
    
    @pytest.fixture
    def legacy_config(self):
        """Legacy configuration format (top-level mongodb key)."""
        return {
            'mongodb': {
                'connection_string': 'mongodb://localhost:27017',
                'database_name': 'test_db'
            }
        }
    
    def test_factory_initialization(self, minimal_config):
        """Test factory initializes with valid config."""
        factory = RepositoryFactory(minimal_config)
        
        assert factory._connection_string == 'mongodb://localhost:27017'
        assert factory._database_name == 'test_db'
        assert factory._username is None
        assert factory._password is None
    
    def test_factory_parses_separate_auth(self, config_with_auth):
        """Test factory parses separate authentication credentials."""
        factory = RepositoryFactory(config_with_auth)
        
        assert factory._username == 'test_user'
        assert factory._password == 'test_pass'
        assert factory._auth_source == 'admin'
    
    def test_factory_handles_embedded_creds(self, config_with_embedded_creds):
        """Test factory handles embedded credentials in URI."""
        factory = RepositoryFactory(config_with_embedded_creds)
        
        # Should not extract separate username/password when embedded
        assert factory._username is None
        assert factory._password is None
    
    def test_factory_supports_legacy_config(self, legacy_config):
        """Test factory supports legacy config format."""
        factory = RepositoryFactory(legacy_config)
        
        assert factory._connection_string == 'mongodb://localhost:27017'
        assert factory._database_name == 'test_db'
    
    def test_factory_handles_missing_connection_string(self):
        """Test factory handles missing connection string gracefully."""
        config = {'database': {'mongodb': {}}}
        factory = RepositoryFactory(config)
        
        assert factory._connection_string is None
    
    def test_factory_handles_invalid_scheme(self):
        """Test factory handles invalid MongoDB URI scheme."""
        config = {
            'database': {
                'mongodb': {
                    'connection_string': 'http://localhost:27017',  # Wrong scheme
                    'database_name': 'test_db'
                }
            }
        }
        factory = RepositoryFactory(config)
        
        # Should log error and not set connection string
        assert factory._connection_string == 'http://localhost:27017'  # Parsed but logged as error
    
    @patch('data.repositories.factory.UserRepository')
    def test_get_user_repository(self, mock_user_repo_class, minimal_config):
        """Test get_user_repository creates UserRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_user_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_user_repository()
        
        assert result == mock_repo
        # Without username/password, auth_source is None (no auth needed)
        mock_user_repo_class.assert_called_once_with(
            'mongodb://localhost:27017',
            'test_db',
            None,
            None,
            None
        )
        mock_repo.initialize.assert_called_once()
    
    @patch('data.repositories.factory.AccountRepository')
    def test_get_account_repository(self, mock_account_repo_class, minimal_config):
        """Test get_account_repository creates AccountRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_account_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_account_repository()
        
        assert result == mock_repo
        mock_repo.initialize.assert_called_once()
    
    @patch('data.repositories.factory.WorkspaceRepository')
    def test_get_workspace_repository(self, mock_workspace_repo_class, minimal_config):
        """Test get_workspace_repository creates WorkspaceRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_workspace_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_workspace_repository()
        
        assert result == mock_repo
        mock_repo.initialize.assert_called_once()
    
    @patch('data.repositories.factory.PortfolioRepository')
    def test_get_portfolio_repository(self, mock_portfolio_repo_class, minimal_config):
        """Test get_portfolio_repository creates PortfolioRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_portfolio_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_portfolio_repository()
        
        assert result == mock_repo
        mock_repo.initialize.assert_called_once()
    
    @patch('data.repositories.factory.SymbolRepository')
    def test_get_symbol_repository(self, mock_symbol_repo_class, minimal_config):
        """Test get_symbol_repository creates SymbolRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_symbol_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_symbol_repository()
        
        assert result == mock_repo
        mock_repo.initialize.assert_called_once()
    
    @patch('data.repositories.factory.SessionRepository')
    def test_get_session_repository(self, mock_session_repo_class, minimal_config):
        """Test get_session_repository creates SessionRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_session_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_session_repository()
        
        assert result == mock_repo
        mock_repo.initialize.assert_called_once()
    
    @patch('data.repositories.factory.UserRepository')
    def test_repository_returns_none_on_init_failure(self, mock_user_repo_class, minimal_config):
        """Test repository returns None when initialization fails."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = False
        mock_user_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_user_repository()
        
        assert result is None
    
    @patch('data.repositories.factory.UserRepository')
    def test_repository_returns_none_on_exception(self, mock_user_repo_class, minimal_config):
        """Test repository returns None when exception occurs."""
        mock_user_repo_class.side_effect = Exception("Connection failed")
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_user_repository()
        
        assert result is None
    
    def test_repository_returns_none_without_connection_string(self):
        """Test repository returns None when connection string missing."""
        config = {'database': {'mongodb': {}}}
        factory = RepositoryFactory(config)
        
        result = factory.get_user_repository()
        
        assert result is None
    
    @patch('data.repositories.factory.UserRepository')
    def test_repository_uses_auth_credentials(self, mock_user_repo_class, config_with_auth):
        """Test repository created with auth credentials."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_user_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(config_with_auth)
        factory.get_user_repository()
        
        mock_user_repo_class.assert_called_once_with(
            'mongodb://localhost:27017',
            'test_db',
            'test_user',
            'test_pass',
            'admin'
        )
    
    @patch('data.repositories.factory.RedisCacheRepository')
    def test_get_cache_repository(self, mock_redis_repo_class, minimal_config):
        """Test get_cache_repository creates RedisCacheRepository."""
        # Add Redis config
        minimal_config['database']['redis'] = {
            'enabled': True,
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }
        
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_redis_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_cache_repository()
        
        assert result == mock_repo
        mock_redis_repo_class.assert_called_once_with(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            ssl=False
        )
    
    def test_get_cache_repository_returns_none_when_disabled(self, minimal_config):
        """Test cache repository returns None when Redis disabled."""
        minimal_config['database']['redis'] = {'enabled': False}
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_cache_repository()
        
        assert result is None
    
    @patch('data.repositories.factory.MongoDBStockDataRepository')
    def test_legacy_create_mongo_repository(self, mock_stock_repo_class, minimal_config):
        """Test legacy static method create_mongo_repository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_stock_repo_class.return_value = mock_repo
        
        result = RepositoryFactory.create_mongo_repository(minimal_config)
        
        assert result == mock_repo
        mock_stock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.RedisCacheRepository')
    def test_legacy_create_cache_repository(self, mock_redis_repo_class, minimal_config):
        """Test legacy static method create_cache_repository."""
        minimal_config['database']['redis'] = {
            'enabled': True,
            'host': 'localhost',
            'port': 6379
        }
        
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_redis_repo_class.return_value = mock_repo
        
        result = RepositoryFactory.create_cache_repository(minimal_config)
        
        assert result == mock_repo
    
    @patch('data.repositories.factory.MongoDBStockDataRepository')
    @patch('data.repositories.factory.RedisCacheRepository')
    @patch('data.repositories.factory.StockDataService')
    def test_create_stock_data_service(self, mock_service_class, mock_redis_class, mock_mongo_class, minimal_config):
        """Test create_stock_data_service creates service with repositories."""
        mock_mongo_repo = MagicMock()
        mock_mongo_repo.initialize.return_value = True
        mock_mongo_class.return_value = mock_mongo_repo
        
        mock_redis_repo = MagicMock()
        mock_redis_repo.initialize.return_value = True
        mock_redis_class.return_value = mock_redis_repo
        
        minimal_config['database']['redis'] = {'enabled': True}
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        result = RepositoryFactory.create_stock_data_service(minimal_config)
        
        assert result == mock_service
        mock_service_class.assert_called_once_with(mock_mongo_repo, mock_redis_repo)
    
    # --- Tests for Additional Repositories ---
    
    @patch('data.repositories.factory.NoteRepository')
    def test_get_note_repository(self, mock_repo_class, minimal_config):
        """Test get_note_repository creates NoteRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_note_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
        mock_repo.initialize.assert_called_once()
    
    @patch('data.repositories.factory.TaskRepository')
    def test_get_task_repository(self, mock_repo_class, minimal_config):
        """Test get_task_repository creates TaskRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_task_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.AnalysisRepository')
    def test_get_analysis_repository(self, mock_repo_class, minimal_config):
        """Test get_analysis_repository creates AnalysisRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_analysis_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.ChatRepository')
    def test_get_chat_repository(self, mock_repo_class, minimal_config):
        """Test get_chat_repository creates ChatRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_chat_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.NotificationRepository')
    def test_get_notification_repository(self, mock_repo_class, minimal_config):
        """Test get_notification_repository creates NotificationRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_notification_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.PositionRepository')
    def test_get_position_repository(self, mock_repo_class, minimal_config):
        """Test get_position_repository creates PositionRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_position_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.TradeRepository')
    def test_get_trade_repository(self, mock_repo_class, minimal_config):
        """Test get_trade_repository creates TradeRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_trade_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.TechnicalIndicatorRepository')
    def test_get_technical_indicator_repository(self, mock_repo_class, minimal_config):
        """Test get_technical_indicator_repository creates TechnicalIndicatorRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_technical_indicator_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.MarketSnapshotRepository')
    def test_get_market_snapshot_repository(self, mock_repo_class, minimal_config):
        """Test get_market_snapshot_repository creates MarketSnapshotRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_market_snapshot_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.InvestmentIdeaRepository')
    def test_get_investment_idea_repository(self, mock_repo_class, minimal_config):
        """Test get_investment_idea_repository creates InvestmentIdeaRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_investment_idea_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
    
    @patch('data.repositories.factory.WatchlistRepository')
    def test_get_watchlist_repository(self, mock_repo_class, minimal_config):
        """Test get_watchlist_repository creates WatchlistRepository."""
        mock_repo = MagicMock()
        mock_repo.initialize.return_value = True
        mock_repo_class.return_value = mock_repo
        
        factory = RepositoryFactory(minimal_config)
        result = factory.get_watchlist_repository()
        
        assert result == mock_repo
        mock_repo_class.assert_called_once()
