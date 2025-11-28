"""Notification repository for managing user notifications."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class NotificationRepository(MongoGenericRepository):
    """Repository for notifications collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize notification repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="notifications",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notifications for a specific user."""
        try:
            return self.get_all(
                {"user_id": user_id},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting notifications for user {user_id}: {e}")
            return []
    
    def get_unread(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get unread notifications for a user."""
        try:
            return self.get_all(
                {"user_id": user_id, "is_read": False},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting unread notifications for user {user_id}: {e}")
            return []
    
    def get_by_type(self, notification_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notifications by type (alert, info, warning, error)."""
        try:
            return self.get_all(
                {"type": notification_type},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting notifications by type {notification_type}: {e}")
            return []
    
    def get_by_priority(self, priority: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notifications by priority (low, medium, high, urgent)."""
        try:
            return self.get_all(
                {"priority": priority},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting notifications by priority {priority}: {e}")
            return []
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        try:
            from datetime import datetime
            return self.update(notification_id, {
                "is_read": True,
                "read_at": datetime.utcnow()
            })
        except PyMongoError as e:
            self.logger.error(f"Error marking notification {notification_id} as read: {e}")
            return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user. Returns count of modified documents."""
        try:
            from datetime import datetime
            result = self.collection.update_many(
                {"user_id": user_id, "is_read": False},
                {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
            )
            return result.modified_count
        except PyMongoError as e:
            self.logger.error(f"Error marking all notifications as read for user {user_id}: {e}")
            return 0
