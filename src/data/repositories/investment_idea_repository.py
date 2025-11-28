"""Investment idea repository for managing investment ideas and opportunities."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class InvestmentIdeaRepository(MongoGenericRepository):
    """Repository for investment_ideas collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize investment idea repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="investment_ideas",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get investment ideas created by a specific user."""
        try:
            return self.get_all(
                {"creator_id": user_id},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting investment ideas for user {user_id}: {e}")
            return []
    
    def get_by_workspace(self, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get investment ideas in a specific workspace."""
        try:
            return self.get_all(
                {"workspace_id": workspace_id},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting investment ideas for workspace {workspace_id}: {e}")
            return []
    
    def get_by_symbol(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get investment ideas related to a specific symbol."""
        try:
            return self.get_all(
                {"symbols": symbol},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting investment ideas for symbol {symbol}: {e}")
            return []
    
    def get_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get investment ideas by status (draft, active, completed, abandoned)."""
        try:
            return self.get_all(
                {"status": status},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting investment ideas by status {status}: {e}")
            return []
    
    def get_by_strategy(self, strategy: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get investment ideas by strategy type (value, growth, momentum, etc.)."""
        try:
            return self.get_all(
                {"strategy": strategy},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting investment ideas by strategy {strategy}: {e}")
            return []
    
    def get_by_risk_level(self, risk_level: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get investment ideas by risk level (low, medium, high)."""
        try:
            return self.get_all(
                {"risk_assessment.risk_level": risk_level},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting investment ideas by risk level {risk_level}: {e}")
            return []
    
    def search_by_title(self, search_text: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search investment ideas by title (case-insensitive)."""
        try:
            query = {"title": {"$regex": search_text, "$options": "i"}}
            return self.get_all(query, limit=limit, sort=[("created_at", -1)])
        except PyMongoError as e:
            self.logger.error(f"Error searching investment ideas: {e}")
            return []
