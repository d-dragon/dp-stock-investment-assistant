"""Notes repository for managing user notes about symbols and analyses."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class NoteRepository(MongoGenericRepository):
    """Repository for notes collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize note repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="notes",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all notes created by a specific user."""
        try:
            return self.get_all(
                {"user_id": user_id},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting notes for user {user_id}: {e}")
            return []
    
    def get_by_workspace(self, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notes in a specific workspace."""
        try:
            return self.get_all(
                {"workspace_id": workspace_id},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting notes for workspace {workspace_id}: {e}")
            return []
    
    def get_by_symbol(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notes related to a specific symbol."""
        try:
            return self.get_all(
                {"related_entities.symbols": symbol},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting notes for symbol {symbol}: {e}")
            return []
    
    def get_by_tags(self, tags: List[str], limit: int = 100) -> List[Dict[str, Any]]:
        """Get notes with specific tags."""
        try:
            return self.get_all(
                {"tags": {"$in": tags}},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting notes by tags: {e}")
            return []
    
    def search_content(self, search_text: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search notes by content (case-insensitive)."""
        try:
            query = {
                "$or": [
                    {"title": {"$regex": search_text, "$options": "i"}},
                    {"content": {"$regex": search_text, "$options": "i"}}
                ]
            }
            return self.get_all(query, limit=limit, sort=[("created_at", -1)])
        except PyMongoError as e:
            self.logger.error(f"Error searching notes: {e}")
            return []
    
    def get_pinned_notes(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get pinned notes for a user."""
        try:
            return self.get_all(
                {"user_id": user_id, "is_pinned": True},
                limit=limit,
                sort=[("pinned_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting pinned notes: {e}")
            return []
