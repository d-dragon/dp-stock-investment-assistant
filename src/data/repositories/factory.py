# src/data/repositories/factory.py
from typing import Optional, Dict, Any
import os
from urllib.parse import urlparse

from .mongodb_repository import MongoDBStockDataRepository
from .redis_cache_repository import RedisCacheRepository
from .user_repository import UserRepository
from .account_repository import AccountRepository
from .workspace_repository import WorkspaceRepository
from .portfolio_repository import PortfolioRepository
from .symbol_repository import SymbolRepository
from .session_repository import SessionRepository
from .note_repository import NoteRepository
from .task_repository import TaskRepository
from .analysis_repository import AnalysisRepository
from .chat_repository import ChatRepository
from .notification_repository import NotificationRepository
from .position_repository import PositionRepository
from .trade_repository import TradeRepository
from .technical_indicator_repository import TechnicalIndicatorRepository
from .market_snapshot_repository import MarketSnapshotRepository
from .investment_idea_repository import InvestmentIdeaRepository
from .watchlist_repository import WatchlistRepository
from ..services.stock_data_service import StockDataService
import logging

class RepositoryFactory:
    """
    Factory for creating repository instances.
    
    Centralizes repository instantiation and configuration parsing.
    Supports both legacy MongoDBStockDataRepository and new generic repositories.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize factory with configuration.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._connection_string = None
        self._database_name = None
        self._username = None
        self._password = None
        self._auth_source = None
        self._parse_mongo_config()
    
    def _parse_mongo_config(self):
        """Parse MongoDB configuration from config dict."""
        db_root = self.config.get('database', {}) if isinstance(self.config, dict) else {}
        mongo_config = db_root.get('mongodb', {}) or self.config.get('mongodb', {})

        self._connection_string = mongo_config.get('connection_string')
        if not self._connection_string:
            self.logger.warning("MongoDB connection string not configured")
            return

        parsed = urlparse(self._connection_string)
        if parsed.scheme not in ('mongodb', 'mongodb+srv'):
            self.logger.error("Invalid MongoDB URI scheme")
            return

        self._database_name = mongo_config.get('database_name', 'stock_assistant')
        
        # Check if connection string has embedded credentials
        has_embedded_creds = parsed.username is not None and parsed.password is not None

        if not has_embedded_creds:
            # Use separate credentials if provided
            self._username = mongo_config.get('username')
            self._password = mongo_config.get('password')
            self._auth_source = mongo_config.get('auth_source', self._database_name if self._username else None)
        else:
            # Embedded credentials - don't set separate auth params
            self._username = None
            self._password = None
            self._auth_source = None
        
        self.logger.debug(f"MongoDB config parsed - Database: {self._database_name}")
    
    # --- New Generic Repositories ---
    
    def get_user_repository(self) -> Optional[UserRepository]:
        """Create UserRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = UserRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create UserRepository: {e}")
        return None
    
    def get_account_repository(self) -> Optional[AccountRepository]:
        """Create AccountRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = AccountRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create AccountRepository: {e}")
        return None
    
    def get_workspace_repository(self) -> Optional[WorkspaceRepository]:
        """Create WorkspaceRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = WorkspaceRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create WorkspaceRepository: {e}")
        return None
    
    def get_portfolio_repository(self) -> Optional[PortfolioRepository]:
        """Create PortfolioRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = PortfolioRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create PortfolioRepository: {e}")
        return None
    
    def get_symbol_repository(self) -> Optional[SymbolRepository]:
        """Create SymbolRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = SymbolRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create SymbolRepository: {e}")
        return None
    
    def get_session_repository(self) -> Optional[SessionRepository]:
        """Create SessionRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = SessionRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create SessionRepository: {e}")
        return None
    
    def get_note_repository(self) -> Optional[NoteRepository]:
        """Create NoteRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = NoteRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create NoteRepository: {e}")
        return None
    
    def get_task_repository(self) -> Optional[TaskRepository]:
        """Create TaskRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = TaskRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create TaskRepository: {e}")
        return None
    
    def get_analysis_repository(self) -> Optional[AnalysisRepository]:
        """Create AnalysisRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = AnalysisRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create AnalysisRepository: {e}")
        return None
    
    def get_chat_repository(self) -> Optional[ChatRepository]:
        """Create ChatRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = ChatRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create ChatRepository: {e}")
        return None
    
    def get_notification_repository(self) -> Optional[NotificationRepository]:
        """Create NotificationRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = NotificationRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create NotificationRepository: {e}")
        return None
    
    def get_position_repository(self) -> Optional[PositionRepository]:
        """Create PositionRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = PositionRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create PositionRepository: {e}")
        return None
    
    def get_trade_repository(self) -> Optional[TradeRepository]:
        """Create TradeRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = TradeRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create TradeRepository: {e}")
        return None
    
    def get_technical_indicator_repository(self) -> Optional[TechnicalIndicatorRepository]:
        """Create TechnicalIndicatorRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = TechnicalIndicatorRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create TechnicalIndicatorRepository: {e}")
        return None
    
    def get_market_snapshot_repository(self) -> Optional[MarketSnapshotRepository]:
        """Create MarketSnapshotRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = MarketSnapshotRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create MarketSnapshotRepository: {e}")
        return None
    
    def get_investment_idea_repository(self) -> Optional[InvestmentIdeaRepository]:
        """Create InvestmentIdeaRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = InvestmentIdeaRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create InvestmentIdeaRepository: {e}")
        return None
    
    def get_watchlist_repository(self) -> Optional[WatchlistRepository]:
        """Create WatchlistRepository instance."""
        if not self._connection_string:
            return None
        
        try:
            repo = WatchlistRepository(
                self._connection_string,
                self._database_name,
                self._username,
                self._password,
                self._auth_source
            )
            if repo.initialize():
                return repo
        except Exception as e:
            self.logger.error(f"Failed to create WatchlistRepository: {e}")
        return None
    
    # --- Legacy Static Methods (Backward Compatibility) ---
    
    @staticmethod
    def create_mongo_repository(
        config: Dict[str, Any]
    ) -> Optional[MongoDBStockDataRepository]:
        """
        Create a MongoDB repository from configuration (legacy method).

        Looks under `database.mongodb` (primary) and falls back to legacy
        top-level `mongodb` keys if present.
        
        Note: For new code, prefer using instance methods:
            factory = RepositoryFactory(config)
            repo = factory.get_user_repository()
        """
        logger = logging.getLogger(__name__)
        db_root = config.get('database', {}) if isinstance(config, dict) else {}
        mongo_config = db_root.get('mongodb', {}) or config.get('mongodb', {})

        connection_string = mongo_config.get('connection_string')
        if not connection_string:
            raise RuntimeError("MongoDB connection string not configured")

        # Add debugging logs
        logger.debug(f"MongoDB connection string: {connection_string}")

        parsed = urlparse(connection_string)
        if parsed.scheme not in ('mongodb', 'mongodb+srv'):
            raise ValueError("Invalid MongoDB URI scheme")

        database_name = mongo_config.get('database_name', 'stock_assistant')
        logger.debug(f"Database name: {database_name}")
        
        # Check if connection string has embedded credentials
        has_embedded_creds = parsed.username is not None and parsed.password is not None

        if has_embedded_creds:
            # Use connection string as-is
            repository = MongoDBStockDataRepository(connection_string, database_name)
        else:
            # Use separate credentials if provided
            username = mongo_config.get('username')
            password = mongo_config.get('password')
            auth_source = mongo_config.get('auth_source', database_name)
            repository = MongoDBStockDataRepository(
                connection_string,
                database_name,
                username,
                password,
                auth_source,
            )

        if repository.initialize():
            return repository
        return None
    
    def get_cache_repository(self) -> Optional[RedisCacheRepository]:
        """Create Redis cache repository instance."""
        db_root = self.config.get('database', {}) if isinstance(self.config, dict) else {}
        cache_config = db_root.get('redis', {}) or self.config.get('redis', {})

        if not cache_config.get('enabled', False):
            return None

        try:
            repository = RedisCacheRepository(
                host=cache_config.get('host', 'localhost'),
                port=cache_config.get('port', 6379),
                db=cache_config.get('db', 0),
                password=cache_config.get('password'),
                ssl=cache_config.get('ssl', False),
            )

            if repository.initialize():
                return repository
        except Exception as e:
            self.logger.error(f"Failed to create RedisCacheRepository: {e}")
        return None
    
    @staticmethod
    def create_cache_repository(
        config: Dict[str, Any]
    ) -> Optional[RedisCacheRepository]:
        """
        Create a Redis cache repository from configuration (legacy method).

        Looks under `database.redis` (primary) and falls back to legacy
        top-level `redis` keys if present.
        
        Note: For new code, prefer using instance methods:
            factory = RepositoryFactory(config)
            repo = factory.get_cache_repository()
        """
        db_root = config.get('database', {}) if isinstance(config, dict) else {}
        cache_config = db_root.get('redis', {}) or config.get('redis', {})

        if not cache_config.get('enabled', False):
            return None

        repository = RedisCacheRepository(
            host=cache_config.get('host', 'localhost'),
            port=cache_config.get('port', 6379),
            db=cache_config.get('db', 0),
            password=cache_config.get('password'),
            ssl=cache_config.get('ssl', False),
        )

        if repository.initialize():
            return repository
        return None
    
    @staticmethod
    def create_stock_data_service(
        config: Dict[str, Any]
    ) -> Optional[StockDataService]:
        """Create the stock data service with appropriate repositories"""
        mongo_repo = RepositoryFactory.create_mongo_repository(config)
        if not mongo_repo:
            return None
            
        cache_repo = RepositoryFactory.create_cache_repository(config)
        
        return StockDataService(mongo_repo, cache_repo)
