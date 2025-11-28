"""Data repositories package."""

from .base_repository import (
    BaseRepository,
    StockDataRepository,
    AnalysisRepository,
    ReportRepository
)
from .mongodb_repository import (
    MongoDBRepository,
    MongoGenericRepository,
    MongoDBStockDataRepository
)
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

__all__ = [
    'BaseRepository',
    'StockDataRepository',
    'AnalysisRepository',
    'ReportRepository',
    'MongoDBRepository',
    'MongoGenericRepository',
    'MongoDBStockDataRepository',
    'UserRepository',
    'AccountRepository',
    'WorkspaceRepository',
    'PortfolioRepository',
    'SymbolRepository',
    'SessionRepository',
    'NoteRepository',
    'TaskRepository',
    'AnalysisRepository',
    'ChatRepository',
    'NotificationRepository',
    'PositionRepository',
    'TradeRepository',
    'TechnicalIndicatorRepository',
    'MarketSnapshotRepository',
    'InvestmentIdeaRepository',
    'WatchlistRepository',
]
