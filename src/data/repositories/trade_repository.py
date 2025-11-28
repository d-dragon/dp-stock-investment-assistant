"""Trade repository for managing trade transactions."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class TradeRepository(MongoGenericRepository):
    """Repository for trades collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize trade repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="trades",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_portfolio(self, portfolio_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades for a specific portfolio."""
        try:
            return self.get_all(
                {"portfolio_id": portfolio_id},
                limit=limit,
                sort=[("execution_time", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting trades for portfolio {portfolio_id}: {e}")
            return []
    
    def get_by_position(self, position_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades for a specific position."""
        try:
            return self.get_all(
                {"position_id": position_id},
                limit=limit,
                sort=[("execution_time", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting trades for position {position_id}: {e}")
            return []
    
    def get_by_symbol(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades for a specific symbol."""
        try:
            return self.get_all(
                {"symbol": symbol},
                limit=limit,
                sort=[("execution_time", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting trades for symbol {symbol}: {e}")
            return []
    
    def get_by_type(self, trade_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades by type (buy, sell, short, cover)."""
        try:
            return self.get_all(
                {"trade_type": trade_type},
                limit=limit,
                sort=[("execution_time", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting trades by type {trade_type}: {e}")
            return []
    
    def get_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades by status (pending, executed, cancelled, rejected)."""
        try:
            return self.get_all(
                {"status": status},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting trades by status {status}: {e}")
            return []
    
    def get_by_account(self, account_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades executed in a specific account."""
        try:
            return self.get_all(
                {"account_id": account_id},
                limit=limit,
                sort=[("execution_time", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting trades for account {account_id}: {e}")
            return []
    
    def get_recent_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get most recent executed trades."""
        try:
            return self.get_all(
                {"status": "executed"},
                limit=limit,
                sort=[("execution_time", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting recent trades: {e}")
            return []
