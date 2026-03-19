"""Session repository for managing workspace collaboration sessions.

Sessions are business grouping containers with lifecycle states
(active → closed → archived) and reusable context.

Reference: specs/agent-session-with-stm-wiring/spec.md (FR-004, FR-007–FR-009)
"""

from typing import List, Optional, Dict, Any, Tuple

from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class SessionRepository(MongoGenericRepository):
    """Repository for sessions collection."""
    
    # Status constants
    STATUS_ACTIVE = "active"
    STATUS_CLOSED = "closed"
    STATUS_ARCHIVED = "archived"
    
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
    
    # ─────────────────────────────────────────────────────────────────
    # Core Lookup Methods
    # ─────────────────────────────────────────────────────────────────
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find session by its business identifier (session_id)."""
        if not session_id:
            return None
        try:
            return self.collection.find_one({"session_id": session_id})
        except PyMongoError as e:
            self.logger.error(f"Error finding session by session_id {session_id}: {e}")
            return None
    
    def get_by_workspace_id(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a workspace."""
        try:
            return self.get_all({"workspace_id": workspace_id}, sort=[("created_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting sessions by workspace_id {workspace_id}: {e}")
            return []
    
    def find_by_workspace(self, workspace_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find sessions by workspace with optional status filter."""
        if not workspace_id:
            return []
        try:
            query: Dict[str, Any] = {"workspace_id": workspace_id}
            if status:
                query["status"] = status
            return self.get_all(query, sort=[("updated_at", -1)])
        except PyMongoError as e:
            self.logger.error(f"Error finding sessions for workspace {workspace_id}: {e}")
            return []
    
    def get_by_status(self, status: str, workspace_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sessions by status, optionally filtered by workspace."""
        try:
            query: Dict[str, Any] = {"status": status}
            if workspace_id:
                query["workspace_id"] = workspace_id
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting sessions by status {status}: {e}")
            return []
    
    def get_active_sessions(self, workspace_id: str = None) -> List[Dict[str, Any]]:
        """Get all active sessions, optionally filtered by workspace."""
        return self.get_by_status(self.STATUS_ACTIVE, workspace_id)
    
    # ─────────────────────────────────────────────────────────────────
    # Update Methods
    # ─────────────────────────────────────────────────────────────────
    
    def update_status(self, session_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update session status by session_id.
        
        Returns the updated document or None on failure.
        """
        if not session_id or not status:
            return None
        try:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            result = self.collection.find_one_and_update(
                {"session_id": session_id},
                {"$set": {"status": status, "updated_at": now}},
                return_document=True,
            )
            return result
        except PyMongoError as e:
            self.logger.error(f"Error updating status for session {session_id}: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────────
    # Query Methods
    # ─────────────────────────────────────────────────────────────────
    
    def get_by_symbol(self, symbol: str, workspace_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sessions that reference a specific symbol."""
        try:
            query: Dict[str, Any] = {"linked_symbol_ids": symbol}
            if workspace_id:
                query["workspace_id"] = workspace_id
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting sessions by symbol {symbol}: {e}")
            return []
    
    def search_by_title(self, title_pattern: str, workspace_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search sessions by title pattern, optionally filtered by workspace."""
        try:
            query: Dict[str, Any] = {"title": {"$regex": title_pattern, "$options": "i"}}
            if workspace_id:
                query["workspace_id"] = workspace_id
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error searching sessions by title: {e}")
            return []
