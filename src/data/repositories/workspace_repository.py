"""Workspace repository for managing user workspaces."""

from typing import List, Optional, Dict, Any
from bson import ObjectId

from .mongodb_repository import MongoGenericRepository


class WorkspaceRepository(MongoGenericRepository):
    """Repository for workspaces collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize workspace repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="workspaces",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all workspaces for a user."""
        try:
            return self.get_all({"user_id": ObjectId(user_id)}, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting workspaces by user_id {user_id}: {e}")
            return []
    
    def search_by_name(self, name_pattern: str, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search workspaces by name pattern, optionally filtered by user."""
        try:
            query = {"name": {"$regex": name_pattern, "$options": "i"}}
            if user_id:
                query["user_id"] = ObjectId(user_id)
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error searching workspaces by name: {e}")
            return []
    
    def get_recent(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently updated workspaces for a user."""
        try:
            query = {"user_id": ObjectId(user_id)}
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting recent workspaces: {e}")
            return []
