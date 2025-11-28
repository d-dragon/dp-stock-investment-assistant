"""Chat repository for managing chat sessions and messages."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class ChatRepository(MongoGenericRepository):
    """Repository for chats collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize chat repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="chats",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_session(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get chat messages for a specific session."""
        try:
            return self.get_all(
                {"session_id": session_id},
                limit=limit,
                sort=[("timestamp", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting chats for session {session_id}: {e}")
            return []
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get chat messages from a specific user."""
        try:
            return self.get_all(
                {"user_id": user_id},
                limit=limit,
                sort=[("timestamp", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting chats for user {user_id}: {e}")
            return []
    
    def get_by_workspace(self, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get chat messages in a specific workspace."""
        try:
            return self.get_all(
                {"workspace_id": workspace_id},
                limit=limit,
                sort=[("timestamp", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting chats for workspace {workspace_id}: {e}")
            return []
    
    def get_by_message_type(self, message_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages by type (user, assistant, system)."""
        try:
            return self.get_all(
                {"message_type": message_type},
                limit=limit,
                sort=[("timestamp", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting chats by type {message_type}: {e}")
            return []
    
    def search_content(self, search_text: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search chat messages by content (case-insensitive)."""
        try:
            query = {"content": {"$regex": search_text, "$options": "i"}}
            return self.get_all(query, limit=limit, sort=[("timestamp", -1)])
        except PyMongoError as e:
            self.logger.error(f"Error searching chat messages: {e}")
            return []
    
    def get_latest_by_session(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the most recent messages for a session."""
        try:
            return self.get_all(
                {"session_id": session_id},
                limit=limit,
                sort=[("timestamp", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting latest chats for session {session_id}: {e}")
            return []
