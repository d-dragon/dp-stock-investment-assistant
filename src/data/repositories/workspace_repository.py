"""Workspace repository for managing user workspaces."""

from datetime import datetime
from typing import List, Optional, Dict, Any

from bson import ObjectId
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class WorkspaceRepository(MongoGenericRepository):
    """Repository for workspaces collection."""
    
    # Status constants
    STATUS_ACTIVE = "active"
    STATUS_ARCHIVED = "archived"
    
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
            return self.get_all(self._build_user_id_query(user_id), sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting workspaces by user_id {user_id}: {e}")
            return []
    
    def search_by_name(self, name_pattern: str, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search workspaces by name pattern, optionally filtered by user."""
        try:
            query = {"name": {"$regex": name_pattern, "$options": "i"}}
            if user_id:
                query.update(self._build_user_id_query(user_id))
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error searching workspaces by name: {e}")
            return []
    
    def get_recent(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently updated workspaces for a user."""
        try:
            query = self._build_user_id_query(user_id)
            return self.get_all(query, limit=limit, sort=[("updated_at", -1)])
        except Exception as e:
            self.logger.error(f"Error getting recent workspaces: {e}")
            return []

    # -----------------------------------------------------------------
    # Phase C management helpers
    # -----------------------------------------------------------------

    def find_by_workspace_id(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Find workspace by its business identifier (workspace_id field)."""
        if not workspace_id:
            return None
        try:
            return self.collection.find_one({"workspace_id": workspace_id})
        except PyMongoError as e:
            self.logger.error(f"Error finding workspace by workspace_id {workspace_id}: {e}")
            return None

    def find_by_user_with_pagination(
        self,
        user_id: str,
        *,
        limit: int = 25,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return paginated workspaces for a user, sorted by updated_at desc."""
        if not user_id:
            return []
        try:
            query: Dict[str, Any] = self._build_user_id_query(user_id)
            if status is not None:
                query["status"] = status
            cursor = (
                self.collection.find(query)
                .sort("updated_at", -1)
                .skip(offset)
                .limit(limit)
            )
            return list(cursor)
        except PyMongoError as e:
            self.logger.error(f"Error listing workspaces for user {user_id}: {e}")
            return []

    def count_by_user(self, user_id: str, *, status: Optional[str] = None) -> int:
        """Count workspaces owned by a user, with optional status filter."""
        if not user_id:
            return 0
        try:
            query: Dict[str, Any] = self._build_user_id_query(user_id)
            if status is not None:
                query["status"] = status
            return self.collection.count_documents(query)
        except PyMongoError as e:
            self.logger.error(f"Error counting workspaces for user {user_id}: {e}")
            return 0

    def _build_user_id_query(self, user_id: str) -> Dict[str, Any]:
        """Build a compatibility query for mixed string/ObjectId user_id records."""
        values: List[Any] = [user_id]
        try:
            values.append(ObjectId(user_id))
        except Exception:
            pass

        if len(values) == 1:
            return {"user_id": user_id}
        return {"user_id": {"$in": values}}

    def update_fields(self, workspace_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Partial update of workspace fields; sets updated_at automatically.

        Returns the updated document or ``None`` on failure / not-found.
        """
        if not workspace_id:
            return None
        try:
            now = self._get_current_timestamp()
            set_fields = {**updates, "updated_at": now}
            result = self.collection.find_one_and_update(
                {"workspace_id": workspace_id},
                {"$set": set_fields},
                return_document=True,
            )
            return result
        except PyMongoError as e:
            self.logger.error(f"Error updating workspace {workspace_id}: {e}")
            return None

    def archive(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Set status to 'archived', record archived_at and updated_at.

        Returns the updated document or ``None`` on failure / not-found.
        """
        if not workspace_id:
            return None
        try:
            now = self._get_current_timestamp()
            result = self.collection.find_one_and_update(
                {"workspace_id": workspace_id},
                {"$set": {
                    "status": self.STATUS_ARCHIVED,
                    "archived_at": now,
                    "updated_at": now,
                }},
                return_document=True,
            )
            return result
        except PyMongoError as e:
            self.logger.error(f"Error archiving workspace {workspace_id}: {e}")
            return None
