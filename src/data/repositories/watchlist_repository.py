"""Watchlist repository for managing user watchlists."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class WatchlistRepository(MongoGenericRepository):
    """Repository for watchlists collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize watchlist repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="watchlists",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get watchlists created by a specific user."""
        try:
            return self.get_all(
                {"user_id": user_id},
                limit=limit,
                sort=[("name", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting watchlists for user {user_id}: {e}")
            return []
    
    def get_by_workspace(self, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get watchlists in a specific workspace."""
        try:
            return self.get_all(
                {"workspace_id": workspace_id},
                limit=limit,
                sort=[("name", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting watchlists for workspace {workspace_id}: {e}")
            return []
    
    def get_by_name(self, user_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific watchlist by user and name."""
        try:
            return self.collection.find_one({"user_id": user_id, "name": name})
        except PyMongoError as e:
            self.logger.error(f"Error getting watchlist by name {name}: {e}")
            return None
    
    def get_watchlists_containing_symbol(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all watchlists containing a specific symbol."""
        try:
            return self.get_all(
                {"symbols": symbol},
                limit=limit,
                sort=[("name", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting watchlists containing symbol {symbol}: {e}")
            return []
    
    def add_symbol_to_watchlist(self, watchlist_id: str, symbol: str) -> bool:
        """Add a symbol to a watchlist."""
        try:
            result = self.collection.update_one(
                {"_id": self._validate_object_id(watchlist_id)},
                {
                    "$addToSet": {"symbols": symbol},
                    "$set": {"updated_at": self._get_current_timestamp()}
                }
            )
            return result.modified_count > 0
        except PyMongoError as e:
            self.logger.error(f"Error adding symbol {symbol} to watchlist {watchlist_id}: {e}")
            return False
    
    def remove_symbol_from_watchlist(self, watchlist_id: str, symbol: str) -> bool:
        """Remove a symbol from a watchlist."""
        try:
            result = self.collection.update_one(
                {"_id": self._validate_object_id(watchlist_id)},
                {
                    "$pull": {"symbols": symbol},
                    "$set": {"updated_at": self._get_current_timestamp()}
                }
            )
            return result.modified_count > 0
        except PyMongoError as e:
            self.logger.error(f"Error removing symbol {symbol} from watchlist {watchlist_id}: {e}")
            return False
    
    def get_public_watchlists(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get public/shared watchlists."""
        try:
            return self.get_all(
                {"is_public": True},
                limit=limit,
                sort=[("name", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting public watchlists: {e}")
            return []
