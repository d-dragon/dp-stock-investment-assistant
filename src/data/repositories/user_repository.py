"""User repository for managing user documents."""

from typing import List, Optional, Dict, Any
from bson import ObjectId

from .mongodb_repository import MongoGenericRepository


class UserRepository(MongoGenericRepository):
    """Repository for users collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize user repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="users",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        try:
            return self.collection.find_one({"email": email})
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_by_group_id(self, group_id: str) -> List[Dict[str, Any]]:
        """Get all users in a group."""
        try:
            return self.get_all({"group_id": ObjectId(group_id)})
        except Exception as e:
            self.logger.error(f"Error getting users by group_id {group_id}: {e}")
            return []
    
    def search_by_name(self, name_pattern: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search users by name pattern (case-insensitive)."""
        try:
            query = {"name": {"$regex": name_pattern, "$options": "i"}}
            return self.get_all(query, limit=limit)
        except Exception as e:
            self.logger.error(f"Error searching users by name: {e}")
            return []
    
    def get_active_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all active users."""
        try:
            query = {"status": "active"}
            return self.get_all(query, limit=limit, sort=[("created_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting active users: {e}")
            return []
