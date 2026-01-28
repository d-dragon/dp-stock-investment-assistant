"""
Conversation repository for managing conversation documents.

Reference: specs/spec-driven-development-pilot/data-model.md
FR-3.1: Short-Term Memory (STM)

Key Behaviors:
- session_id is the primary lookup key (= thread_id, 1:1 mapping)
- Conversations are NEVER deleted (per ADR-001)
- Archived conversations are immutable
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple

from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class ConversationRepository(MongoGenericRepository):
    """
    Repository for conversations collection.
    
    Manages conversation metadata separate from LangGraph checkpoints.
    Uses session_id as primary key (1:1 with sessions.id and thread_id).
    
    Per ADR-001: Conversations are NEVER deleted - only archived.
    """
    
    # Status constants
    STATUS_ACTIVE = "active"
    STATUS_SUMMARIZED = "summarized"
    STATUS_ARCHIVED = "archived"
    
    VALID_STATUSES = frozenset([STATUS_ACTIVE, STATUS_SUMMARIZED, STATUS_ARCHIVED])
    
    def __init__(
        self,
        connection_string: str,
        database_name: str = "stock_assistant",
        username: str = None,
        password: str = None,
        auth_source: str = None
    ):
        """Initialize conversation repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="conversations",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Core Lookup Methods
    # ─────────────────────────────────────────────────────────────────
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Find conversation by session_id (primary lookup).
        
        Args:
            session_id: UUID string matching sessions.id
            
        Returns:
            Conversation document if found, None otherwise
        """
        if not session_id:
            return None
            
        try:
            return self.collection.find_one({"session_id": session_id})
        except PyMongoError as e:
            self.logger.error(f"Error finding conversation by session_id {session_id}: {e}")
            return None
    
    def exists_by_session_id(self, session_id: str) -> bool:
        """
        Check if conversation exists for session_id.
        
        Args:
            session_id: UUID string
            
        Returns:
            True if conversation exists
        """
        if not session_id:
            return False
            
        try:
            return self.collection.find_one(
                {"session_id": session_id}, 
                {"_id": 1}
            ) is not None
        except PyMongoError as e:
            self.logger.error(f"Error checking conversation existence for {session_id}: {e}")
            return False
    
    # ─────────────────────────────────────────────────────────────────
    # Query Methods
    # ─────────────────────────────────────────────────────────────────
    
    def find_active_by_user(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find active conversations for a user.
        
        Args:
            user_id: User ID string
            limit: Maximum results (default 20)
            
        Returns:
            List of active conversation documents, newest first
        """
        if not user_id:
            return []
            
        try:
            query = {
                "user_id": user_id,
                "status": self.STATUS_ACTIVE
            }
            return self.get_all(
                filter_query=query,
                limit=limit,
                sort=[("last_activity_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error finding active conversations for user {user_id}: {e}")
            return []
    
    def find_by_workspace(
        self, 
        workspace_id: str, 
        status: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find conversations in a workspace.
        
        Args:
            workspace_id: Workspace ID string
            status: Optional status filter
            limit: Maximum results (default 50)
            
        Returns:
            List of conversation documents
        """
        if not workspace_id:
            return []
            
        try:
            query = {"workspace_id": workspace_id}
            if status and status in self.VALID_STATUSES:
                query["status"] = status
                
            return self.get_all(
                filter_query=query,
                limit=limit,
                sort=[("last_activity_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error finding conversations in workspace {workspace_id}: {e}")
            return []
    
    def find_by_symbols(
        self, 
        symbols: List[str], 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find conversations focused on specific symbols.
        
        Args:
            symbols: List of stock symbols (e.g., ["AAPL", "MSFT"])
            limit: Maximum results
            
        Returns:
            List of conversation documents containing any of the symbols
        """
        if not symbols:
            return []
            
        try:
            # Normalize symbols to uppercase
            normalized = [s.upper().strip() for s in symbols if s]
            
            query = {"focused_symbols": {"$in": normalized}}
            return self.get_all(
                filter_query=query,
                limit=limit,
                sort=[("last_activity_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error finding conversations by symbols: {e}")
            return []
    
    def find_stale(
        self, 
        days: int = 30, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find conversations inactive for N days (for archive job).
        
        Args:
            days: Inactivity threshold in days (default 30)
            limit: Maximum results
            
        Returns:
            List of stale conversation documents
        """
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            
            query = {
                "status": {"$in": [self.STATUS_ACTIVE, self.STATUS_SUMMARIZED]},
                "last_activity_at": {"$lt": cutoff}
            }
            return self.get_all(
                filter_query=query,
                limit=limit,
                sort=[("last_activity_at", 1)]  # Oldest first
            )
        except PyMongoError as e:
            self.logger.error(f"Error finding stale conversations: {e}")
            return []
    
    # ─────────────────────────────────────────────────────────────────
    # Create/Upsert Methods
    # ─────────────────────────────────────────────────────────────────
    
    def get_or_create(
        self,
        session_id: str,
        workspace_id: str = None,
        user_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing conversation or create new one for session.
        
        This is the primary method for conversation initialization.
        Uses session_id as the unique key (1:1 with session).
        
        Args:
            session_id: UUID string (required)
            workspace_id: Workspace context (optional)
            user_id: Owner user ID (optional)
            
        Returns:
            Conversation document (existing or newly created)
            None if session_id is empty/invalid
        """
        if not session_id:
            return None
            
        try:
            # Check for existing conversation
            existing = self.find_by_session_id(session_id)
            if existing:
                return existing
            
            # Create new conversation document
            now = datetime.now(timezone.utc)
            new_conversation = {
                "session_id": session_id,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "status": self.STATUS_ACTIVE,
                "message_count": 0,
                "total_tokens": 0,
                "focused_symbols": [],
                "summary": None,
                "summarized_at": None,
                "archived_at": None,
                "created_at": now,
                "updated_at": now,
                "last_activity_at": now
            }
            
            result = self.collection.insert_one(new_conversation)
            
            if result.inserted_id:
                new_conversation["_id"] = result.inserted_id
                return new_conversation
            
            return None
            
        except PyMongoError as e:
            self.logger.error(f"Error in get_or_create for session {session_id}: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────────
    # Update Methods
    # ─────────────────────────────────────────────────────────────────
    
    def update_by_session_id(
        self, 
        session_id: str, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Update conversation by session_id.
        
        Args:
            session_id: UUID string
            data: Fields to update
            
        Returns:
            True if document was modified
            
        Note:
            Fails silently if conversation is archived (immutable).
        """
        if not session_id:
            return False
            
        try:
            # Check if archived (immutable)
            existing = self.collection.find_one(
                {"session_id": session_id},
                {"status": 1}
            )
            if not existing:
                self.logger.warning(f"Conversation not found for session_id: {session_id}")
                return False
                
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(f"Cannot update archived conversation: {session_id}")
                return False
            
            # Add updated_at timestamp
            update_data = {**data, "updated_at": datetime.now(timezone.utc)}
            
            result = self.collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
            
        except PyMongoError as e:
            self.logger.error(f"Error updating conversation {session_id}: {e}")
            return False
    
    def update_activity(
        self, 
        session_id: str, 
        message_count_delta: int = 1, 
        token_delta: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Update activity metrics after message exchange.
        
        Uses $inc for atomic updates to counters.
        
        Args:
            session_id: UUID string
            message_count_delta: Number of messages to add (default 1)
            token_delta: Number of tokens to add (default 0)
            
        Returns:
            Updated document if successful, None otherwise
        """
        if not session_id:
            return None
            
        try:
            # Check if archived first
            existing = self.collection.find_one(
                {"session_id": session_id},
                {"status": 1}
            )
            if not existing:
                return None
                
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(f"Cannot update activity for archived conversation: {session_id}")
                return None
            
            now = datetime.now(timezone.utc)
            
            result = self.collection.find_one_and_update(
                {"session_id": session_id},
                {
                    "$inc": {
                        "message_count": message_count_delta,
                        "total_tokens": token_delta
                    },
                    "$set": {
                        "last_activity_at": now,
                        "updated_at": now
                    }
                },
                return_document=True
            )
            return result
            
        except PyMongoError as e:
            self.logger.error(f"Error updating activity for {session_id}: {e}")
            return None
    
    def update_summary(
        self, 
        session_id: str, 
        summary: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update summary and set status to 'summarized'.
        
        Args:
            session_id: UUID string
            summary: Summary text
            
        Returns:
            Updated document if successful, None otherwise
        """
        if not session_id or not summary:
            return None
            
        try:
            # Validate not archived
            existing = self.collection.find_one(
                {"session_id": session_id},
                {"status": 1}
            )
            if not existing:
                return None
                
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(f"Cannot update summary for archived conversation: {session_id}")
                return None
            
            now = datetime.now(timezone.utc)
            
            result = self.collection.find_one_and_update(
                {"session_id": session_id},
                {
                    "$set": {
                        "summary": summary,
                        "status": self.STATUS_SUMMARIZED,
                        "updated_at": now
                    }
                },
                return_document=True
            )
            return result
            
        except PyMongoError as e:
            self.logger.error(f"Error updating summary for {session_id}: {e}")
            return None
    
    def update_focused_symbols(
        self, 
        session_id: str, 
        symbols: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Update focused symbols for a conversation.
        
        Args:
            session_id: UUID string
            symbols: List of stock symbols (will be normalized to uppercase)
            
        Returns:
            Updated document if successful, None otherwise
        """
        if not session_id:
            return None
            
        try:
            # Normalize and deduplicate
            normalized = list(set(s.upper().strip() for s in symbols if s))
            
            existing = self.collection.find_one(
                {"session_id": session_id},
                {"status": 1}
            )
            if not existing:
                return None
                
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(f"Cannot update symbols for archived conversation: {session_id}")
                return None
            
            now = datetime.now(timezone.utc)
            
            result = self.collection.find_one_and_update(
                {"session_id": session_id},
                {
                    "$set": {
                        "focused_symbols": normalized,
                        "updated_at": now
                    }
                },
                return_document=True
            )
            return result
            
        except PyMongoError as e:
            self.logger.error(f"Error updating symbols for {session_id}: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────────
    # Status Transition Methods
    # ─────────────────────────────────────────────────────────────────
    
    def archive(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Archive conversation (terminal state).
        
        Once archived, conversation becomes immutable.
        
        Args:
            session_id: UUID string
            
        Returns:
            Updated document if successful, None otherwise
        """
        if not session_id:
            return None
            
        try:
            # Check current status
            existing = self.collection.find_one(
                {"session_id": session_id},
                {"status": 1}
            )
            if not existing:
                return None
                
            if existing.get("status") == self.STATUS_ARCHIVED:
                # Already archived - return current document
                return self.collection.find_one({"session_id": session_id})
            
            now = datetime.now(timezone.utc)
            
            result = self.collection.find_one_and_update(
                {"session_id": session_id},
                {
                    "$set": {
                        "status": self.STATUS_ARCHIVED,
                        "archived_at": now,
                        "updated_at": now
                    }
                },
                return_document=True
            )
            return result
            
        except PyMongoError as e:
            self.logger.error(f"Error archiving conversation {session_id}: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────────
    # Override: Disable Delete (ADR-001)
    # ─────────────────────────────────────────────────────────────────
    
    def delete(self, id: str) -> bool:
        """
        Delete is disabled for conversations (ADR-001: No-delete policy).
        
        Use archive() instead to mark conversations as read-only.
        
        Args:
            id: Document ID
            
        Returns:
            Always False
        """
        self.logger.warning(
            f"Delete attempted on conversation {id}. "
            "Conversations cannot be deleted per ADR-001. Use archive() instead."
        )
        return False
    
    # ─────────────────────────────────────────────────────────────────
    # Health Check
    # ─────────────────────────────────────────────────────────────────
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check repository health.
        
        Returns:
            (healthy: bool, details: dict)
        """
        try:
            # Try to count documents (tests read permission)
            count = self.count()
            
            return True, {
                "component": "conversation_repository",
                "status": "ready",
                "collection": self.collection_name,
                "document_count": count
            }
            
        except Exception as e:
            return False, {
                "component": "conversation_repository",
                "status": "error",
                "error": str(e)
            }
