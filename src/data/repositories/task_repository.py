"""Task repository for managing user tasks and to-do items."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class TaskRepository(MongoGenericRepository):
    """Repository for tasks collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize task repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="tasks",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a specific user."""
        try:
            return self.get_all(
                {"assignee_id": user_id},
                limit=limit,
                sort=[("due_date", 1), ("priority", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting tasks for user {user_id}: {e}")
            return []
    
    def get_by_workspace(self, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tasks in a specific workspace."""
        try:
            return self.get_all(
                {"workspace_id": workspace_id},
                limit=limit,
                sort=[("due_date", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting tasks for workspace {workspace_id}: {e}")
            return []
    
    def get_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tasks by status (pending, in_progress, completed, etc.)."""
        try:
            return self.get_all(
                {"status": status},
                limit=limit,
                sort=[("due_date", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting tasks by status {status}: {e}")
            return []
    
    def get_overdue_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get overdue tasks."""
        try:
            from datetime import datetime
            return self.get_all(
                {
                    "due_date": {"$lt": datetime.utcnow()},
                    "status": {"$ne": "completed"}
                },
                limit=limit,
                sort=[("due_date", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting overdue tasks: {e}")
            return []
    
    def get_by_priority(self, priority: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tasks by priority level (low, medium, high, critical)."""
        try:
            return self.get_all(
                {"priority": priority},
                limit=limit,
                sort=[("due_date", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting tasks by priority {priority}: {e}")
            return []
    
    def get_by_symbol(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get tasks related to a specific symbol."""
        try:
            return self.get_all(
                {"related_entities.symbols": symbol},
                limit=limit,
                sort=[("due_date", 1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting tasks for symbol {symbol}: {e}")
            return []
