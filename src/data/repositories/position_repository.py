"""Position repository for managing portfolio positions."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class PositionRepository(MongoGenericRepository):
    """Repository for positions collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize position repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="positions",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_portfolio(self, portfolio_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all positions in a portfolio."""
        try:
            return self.get_all(
                {"portfolio_id": portfolio_id},
                limit=limit,
                sort=[("symbol", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting positions for portfolio {portfolio_id}: {e}")
            return []
    
    def get_by_symbol(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get positions for a specific symbol across portfolios."""
        try:
            return self.get_all(
                {"symbol": symbol},
                limit=limit,
                sort=[("opened_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting positions for symbol {symbol}: {e}")
            return []
    
    def get_open_positions(self, portfolio_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all open positions, optionally filtered by portfolio."""
        try:
            query = {"status": "open"}
            if portfolio_id:
                query["portfolio_id"] = portfolio_id
            return self.get_all(query, limit=limit, sort=[("symbol", 1)])
        except PyMongoError as e:
            self.logger.error(f"Error getting open positions: {e}")
            return []
    
    def get_closed_positions(self, portfolio_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all closed positions, optionally filtered by portfolio."""
        try:
            query = {"status": "closed"}
            if portfolio_id:
                query["portfolio_id"] = portfolio_id
            return self.get_all(query, limit=limit, sort=[("closed_at", -1)])
        except PyMongoError as e:
            self.logger.error(f"Error getting closed positions: {e}")
            return []
    
    def get_by_account(self, account_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get positions in a specific account."""
        try:
            return self.get_all(
                {"account_id": account_id},
                limit=limit,
                sort=[("symbol", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting positions for account {account_id}: {e}")
            return []
    
    def get_profitable_positions(self, portfolio_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get positions with positive P&L."""
        try:
            query = {
                "portfolio_id": portfolio_id,
                "performance.total_return": {"$gt": 0}
            }
            return self.get_all(query, limit=limit, sort=[("performance.total_return", -1)])
        except PyMongoError as e:
            self.logger.error(f"Error getting profitable positions: {e}")
            return []
