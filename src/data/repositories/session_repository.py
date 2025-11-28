"""Session repository for managing workspace collaboration sessions."""

from typing import List, Optional, Dict, Any
from bson import ObjectId

from .mongodb_repository import MongoGenericRepository


class SessionRepository(MongoGenericRepository):
    """Repository for sessions collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize session repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="sessions",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_workspace_id(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a workspace."""
        try:
            return self.get_all({"workspace_id": ObjectId(workspace_id)}, sort=[("created_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting sessions by workspace_id {workspace_id}: {e}")
            return []
    
    def get_by_status(self, status: str, workspace_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sessions by status (open, closed, archived), optionally filtered by workspace."""
        try:
            query = {"status": status}
            if workspace_id:
                query["workspace_id"] = ObjectId(workspace_id)
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting sessions by status {status}: {e}")
            return []
    
    def get_active_sessions(self, workspace_id: str = None) -> List[Dict[str, Any]]:
        """Get all open/active sessions, optionally filtered by workspace."""
        return self.get_by_status("open", workspace_id)
    
    def get_by_symbol(self, symbol: str, workspace_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sessions that reference a specific symbol."""
        try:
            query = {"linked_symbol_ids": symbol}
            if workspace_id:
                query["workspace_id"] = ObjectId(workspace_id)
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting sessions by symbol {symbol}: {e}")
            return []
    
    def search_by_title(self, title_pattern: str, workspace_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search sessions by title pattern, optionally filtered by workspace."""
        try:
            query = {"title": {"$regex": title_pattern, "$options": "i"}}
            if workspace_id:
                query["workspace_id"] = ObjectId(workspace_id)
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error searching sessions by title: {e}")
            return []
