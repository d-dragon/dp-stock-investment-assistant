"""Portfolio repository for managing investment portfolios."""

from typing import List, Optional, Dict, Any
from bson import ObjectId

from .mongodb_repository import MongoGenericRepository


class PortfolioRepository(MongoGenericRepository):
    """Repository for portfolios collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize portfolio repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="portfolios",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all portfolios for a user."""
        try:
            return self.get_all({"user_id": ObjectId(user_id)}, sort=[("created_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting portfolios by user_id {user_id}: {e}")
            return []
    
    def get_by_account_id(self, account_id: str) -> List[Dict[str, Any]]:
        """Get all portfolios linked to an account."""
        try:
            return self.get_all({"account_id": ObjectId(account_id)}, sort=[("created_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting portfolios by account_id {account_id}: {e}")
            return []
    
    def get_by_type(self, portfolio_type: str, user_id: str = None) -> List[Dict[str, Any]]:
        """Get portfolios by type (e.g., 'real', 'paper', 'model')."""
        try:
            query = {"type": portfolio_type}
            if user_id:
                query["user_id"] = ObjectId(user_id)
            return self.get_all(query, sort=[("created_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting portfolios by type {portfolio_type}: {e}")
            return []
    
    def search_by_name(self, name_pattern: str, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search portfolios by name pattern, optionally filtered by user."""
        try:
            query = {"name": {"$regex": name_pattern, "$options": "i"}}
            if user_id:
                query["user_id"] = ObjectId(user_id)
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error searching portfolios by name: {e}")
            return []
