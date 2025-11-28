"""Account repository for managing brokerage/custody accounts."""

from typing import List, Optional, Dict, Any
from bson import ObjectId

from .mongodb_repository import MongoGenericRepository


class AccountRepository(MongoGenericRepository):
    """Repository for accounts collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize account repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="accounts",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all accounts for a user."""
        try:
            return self.get_all({"user_id": ObjectId(user_id)}, sort=[("created_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting accounts by user_id {user_id}: {e}")
            return []
    
    def get_by_provider(self, provider: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all accounts for a specific provider."""
        try:
            return self.get_all({"provider": provider}, limit=limit)
        except Exception as e:
            self.logger.error(f"Error getting accounts by provider {provider}: {e}")
            return []
    
    def get_active_accounts(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get active accounts, optionally filtered by user."""
        try:
            query = {"status": "active"}
            if user_id:
                query["user_id"] = ObjectId(user_id)
            return self.get_all(query, sort=[("created_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting active accounts: {e}")
            return []
