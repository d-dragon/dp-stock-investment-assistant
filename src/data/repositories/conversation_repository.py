"""
Conversation repository for managing conversation documents.

Reference: specs/agent-session-with-stm-wiring/spec.md
FR-3.1: Short-Term Memory (STM)

Key Behaviors:
- conversation_id is the primary lookup key (unique per conversation)
- thread_id maps 1:1 with conversation_id for LangGraph checkpointing
- session_id is a non-unique FK (one session → many conversations)
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
    Uses conversation_id as the primary business key.
    thread_id is the LangGraph checkpoint key (1:1 with conversation_id).
    session_id links to the parent session (many conversations per session).
    
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
    
    def find_by_conversation_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Find conversation by its business identifier (conversation_id).
        
        This is the primary lookup method.
        """
        if not conversation_id:
            return None
        try:
            return self.collection.find_one({"conversation_id": conversation_id})
        except PyMongoError as e:
            self.logger.error(f"Error finding conversation {conversation_id}: {e}")
            return None
    
    def find_by_thread_id(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Find conversation by its LangGraph thread_id."""
        if not thread_id:
            return None
        try:
            return self.collection.find_one({"thread_id": thread_id})
        except PyMongoError as e:
            self.logger.error(f"Error finding conversation by thread_id {thread_id}: {e}")
            return None
    
    def find_by_session_id(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Find all conversations belonging to a session.
        
        One session can have many conversations (1:N).
        Returns list sorted by last_activity_at descending.
        """
        if not session_id:
            return []
        try:
            return self.get_all(
                filter_query={"session_id": session_id},
                sort=[("last_activity_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error finding conversations for session {session_id}: {e}")
            return []
    
    def exists_by_conversation_id(self, conversation_id: str) -> bool:
        """Check if conversation exists by conversation_id."""
        if not conversation_id:
            return False
        try:
            return self.collection.find_one(
                {"conversation_id": conversation_id},
                {"_id": 1}
            ) is not None
        except PyMongoError as e:
            self.logger.error(f"Error checking existence for conversation {conversation_id}: {e}")
            return False
    
    def exists_by_session_id(self, session_id: str) -> bool:
        """Check if any conversations exist for a session_id."""
        if not session_id:
            return False
        try:
            return self.collection.find_one(
                {"session_id": session_id},
                {"_id": 1}
            ) is not None
        except PyMongoError as e:
            self.logger.error(f"Error checking conversation existence for session {session_id}: {e}")
            return False
    
    # ─────────────────────────────────────────────────────────────────
    # Query Methods
    # ─────────────────────────────────────────────────────────────────
    
    def find_active_by_user(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find active conversations for a user, newest first."""
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
        """Find conversations in a workspace with optional status filter."""
        if not workspace_id:
            return []
        try:
            query: Dict[str, Any] = {"workspace_id": workspace_id}
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
        """Find conversations focused on specific symbols."""
        if not symbols:
            return []
        try:
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
        """Find conversations inactive for N days (for archive job)."""
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
    
    def find_by_session_id_list(
        self,
        session_ids: List[str],
        status: str = None,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """Batch-fetch conversations for multiple session_ids."""
        if not session_ids:
            return []
        try:
            query: Dict[str, Any] = {"session_id": {"$in": session_ids}}
            if status and status in self.VALID_STATUSES:
                query["status"] = status
            return self.get_all(
                filter_query=query,
                limit=limit,
                sort=[("last_activity_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error batch-fetching conversations: {e}")
            return []
    
    # ─────────────────────────────────────────────────────────────────
    # Create Methods
    # ─────────────────────────────────────────────────────────────────
    
    def create_conversation(
        self,
        conversation_id: str,
        thread_id: str,
        session_id: str,
        workspace_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new conversation document.
        
        Args:
            conversation_id: Unique business ID (UUID v4)
            thread_id: LangGraph checkpoint thread ID (UUID v4)
            session_id: Parent session FK
            workspace_id: Workspace FK
            user_id: Owner user ID
            
        Returns:
            Newly created document, or None on failure
        """
        if not all([conversation_id, thread_id, session_id, workspace_id, user_id]):
            self.logger.error("create_conversation requires all identifiers")
            return None
        try:
            now = datetime.now(timezone.utc)
            doc = {
                "conversation_id": conversation_id,
                "thread_id": thread_id,
                "session_id": session_id,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "status": self.STATUS_ACTIVE,
                "message_count": 0,
                "total_tokens": 0,
                "focused_symbols": [],
                "context_overrides": None,
                "conversation_intent": None,
                "summary": None,
                "summarized_at": None,
                "archived_at": None,
                "archive_reason": None,
                "created_at": now,
                "updated_at": now,
                "last_activity_at": now,
            }
            result = self.collection.insert_one(doc)
            if result.inserted_id:
                doc["_id"] = result.inserted_id
                return doc
            return None
        except PyMongoError as e:
            self.logger.error(f"Error creating conversation {conversation_id}: {e}")
            return None
    
    def get_or_create(
        self,
        conversation_id: str,
        thread_id: str,
        session_id: str,
        workspace_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing conversation or create a new one.
        
        Looks up by conversation_id first — if not found, creates a new document.
        """
        if not conversation_id:
            return None
        try:
            existing = self.find_by_conversation_id(conversation_id)
            if existing:
                return existing
            return self.create_conversation(
                conversation_id=conversation_id,
                thread_id=thread_id,
                session_id=session_id,
                workspace_id=workspace_id,
                user_id=user_id,
            )
        except PyMongoError as e:
            self.logger.error(f"Error in get_or_create for conversation {conversation_id}: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────────
    # Update Methods
    # ─────────────────────────────────────────────────────────────────
    
    def update_by_conversation_id(
        self, 
        conversation_id: str, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Update conversation by conversation_id.
        
        Fails silently if conversation is archived (immutable).
        """
        if not conversation_id:
            return False
        try:
            existing = self.collection.find_one(
                {"conversation_id": conversation_id},
                {"status": 1}
            )
            if not existing:
                self.logger.warning(f"Conversation not found: {conversation_id}")
                return False
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(f"Cannot update archived conversation: {conversation_id}")
                return False
            update_data = {**data, "updated_at": datetime.now(timezone.utc)}
            result = self.collection.update_one(
                {"conversation_id": conversation_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            self.logger.error(f"Error updating conversation {conversation_id}: {e}")
            return False
    
    def update_activity(
        self, 
        conversation_id: str, 
        message_count_delta: int = 1, 
        token_delta: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Update activity metrics after message exchange.
        
        Uses $inc for atomic counter updates.
        """
        if not conversation_id:
            return None
        try:
            existing = self.collection.find_one(
                {"conversation_id": conversation_id},
                {"status": 1}
            )
            if not existing:
                return None
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(f"Cannot update activity for archived conversation: {conversation_id}")
                return None
            now = datetime.now(timezone.utc)
            result = self.collection.find_one_and_update(
                {"conversation_id": conversation_id},
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
            self.logger.error(f"Error updating activity for {conversation_id}: {e}")
            return None
    
    def update_summary(
        self, 
        conversation_id: str, 
        summary: str
    ) -> Optional[Dict[str, Any]]:
        """Update summary and set status to 'summarized'."""
        if not conversation_id or not summary:
            return None
        try:
            existing = self.collection.find_one(
                {"conversation_id": conversation_id},
                {"status": 1}
            )
            if not existing:
                return None
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(f"Cannot update summary for archived conversation: {conversation_id}")
                return None
            now = datetime.now(timezone.utc)
            result = self.collection.find_one_and_update(
                {"conversation_id": conversation_id},
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
            self.logger.error(f"Error updating summary for {conversation_id}: {e}")
            return None
    
    def update_focused_symbols(
        self, 
        conversation_id: str, 
        symbols: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Update focused symbols for a conversation (normalized to uppercase)."""
        if not conversation_id:
            return None
        try:
            normalized = list(set(s.upper().strip() for s in symbols if s))
            existing = self.collection.find_one(
                {"conversation_id": conversation_id},
                {"status": 1}
            )
            if not existing:
                return None
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(f"Cannot update symbols for archived conversation: {conversation_id}")
                return None
            now = datetime.now(timezone.utc)
            result = self.collection.find_one_and_update(
                {"conversation_id": conversation_id},
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
            self.logger.error(f"Error updating symbols for {conversation_id}: {e}")
            return None
    
    def update_context_overrides(
        self,
        conversation_id: str,
        context_overrides: Optional[Dict[str, Any]]
    ) -> bool:
        """Set thread-local context overrides for a conversation."""
        return self.update_by_conversation_id(conversation_id, {
            "context_overrides": context_overrides
        })
    
    # ─────────────────────────────────────────────────────────────────
    # Status Transition Methods
    # ─────────────────────────────────────────────────────────────────
    
    def archive(
        self,
        conversation_id: str,
        archive_reason: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Archive conversation (terminal state).
        
        Once archived, conversation becomes immutable.
        
        Args:
            conversation_id: Conversation business ID
            archive_reason: Optional reason (user_requested, session_closed, stale, admin)
        """
        if not conversation_id:
            return None
        try:
            existing = self.collection.find_one(
                {"conversation_id": conversation_id},
                {"status": 1}
            )
            if not existing:
                return None
            if existing.get("status") == self.STATUS_ARCHIVED:
                return self.collection.find_one({"conversation_id": conversation_id})
            now = datetime.now(timezone.utc)
            update_fields: Dict[str, Any] = {
                "status": self.STATUS_ARCHIVED,
                "archived_at": now,
                "updated_at": now,
            }
            if archive_reason:
                update_fields["archive_reason"] = archive_reason
            result = self.collection.find_one_and_update(
                {"conversation_id": conversation_id},
                {"$set": update_fields},
                return_document=True
            )
            return result
        except PyMongoError as e:
            self.logger.error(f"Error archiving conversation {conversation_id}: {e}")
            return None
    
    def archive_by_session_id(
        self,
        session_id: str,
        archive_reason: str = "session_closed"
    ) -> int:
        """
        Archive all conversations for a session (cascade).
        
        Returns the number of conversations archived.
        """
        if not session_id:
            return 0
        try:
            now = datetime.now(timezone.utc)
            result = self.collection.update_many(
                {
                    "session_id": session_id,
                    "status": {"$ne": self.STATUS_ARCHIVED}
                },
                {
                    "$set": {
                        "status": self.STATUS_ARCHIVED,
                        "archived_at": now,
                        "updated_at": now,
                        "archive_reason": archive_reason,
                    }
                }
            )
            return result.modified_count
        except PyMongoError as e:
            self.logger.error(f"Error archiving conversations for session {session_id}: {e}")
            return 0
    
    # ─────────────────────────────────────────────────────────────────
    # Phase C Management Helpers
    # ─────────────────────────────────────────────────────────────────

    def find_by_session_with_pagination(
        self,
        session_id: str,
        *,
        limit: int = 25,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return paginated conversations for a session.

        Sorted by last_activity_at desc, tie-break updated_at desc.
        """
        if not session_id:
            return []
        try:
            query: Dict[str, Any] = {"session_id": session_id}
            if status is not None and status in self.VALID_STATUSES:
                query["status"] = status
            cursor = (
                self.collection.find(query)
                .sort([("last_activity_at", -1), ("updated_at", -1)])
                .skip(offset)
                .limit(limit)
            )
            return list(cursor)
        except PyMongoError as e:
            self.logger.error(
                f"Error listing conversations for session {session_id}: {e}"
            )
            return []

    def count_by_session(
        self, session_id: str, *, status: Optional[str] = None
    ) -> int:
        """Count conversations in a session, with optional status filter."""
        if not session_id:
            return 0
        try:
            query: Dict[str, Any] = {"session_id": session_id}
            if status is not None and status in self.VALID_STATUSES:
                query["status"] = status
            return self.collection.count_documents(query)
        except PyMongoError as e:
            self.logger.error(
                f"Error counting conversations for session {session_id}: {e}"
            )
            return 0

    def update_fields(
        self, conversation_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Partial update of conversation fields; sets updated_at automatically.

        Refuses to update archived conversations (immutable per ADR-001).
        Returns the updated document or ``None`` on failure / not-found.
        """
        if not conversation_id:
            return None
        try:
            existing = self.collection.find_one(
                {"conversation_id": conversation_id}, {"status": 1}
            )
            if not existing:
                return None
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(
                    f"Cannot update archived conversation: {conversation_id}"
                )
                return None
            now = self._get_current_timestamp()
            set_fields = {**updates, "updated_at": now}
            result = self.collection.find_one_and_update(
                {"conversation_id": conversation_id},
                {"$set": set_fields},
                return_document=True,
            )
            return result
        except PyMongoError as e:
            self.logger.error(f"Error updating conversation {conversation_id}: {e}")
            return None

    def get_conversation_metadata(
        self, conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return management-facing metadata for a conversation.

        Fields: message_count, total_tokens, last_activity_at, focused_symbols,
        summary, status.  All data lives in the conversation document itself.
        """
        if not conversation_id:
            return None
        try:
            doc = self.collection.find_one(
                {"conversation_id": conversation_id},
                {
                    "_id": 0,
                    "conversation_id": 1,
                    "thread_id": 1,
                    "session_id": 1,
                    "workspace_id": 1,
                    "status": 1,
                    "message_count": 1,
                    "total_tokens": 1,
                    "summary": 1,
                    "focused_symbols": 1,
                    "last_activity_at": 1,
                    "created_at": 1,
                    "updated_at": 1,
                },
            )
            return doc
        except PyMongoError as e:
            self.logger.error(
                f"Error reading metadata for conversation {conversation_id}: {e}"
            )
            return None

    # ─────────────────────────────────────────────────────────────────
    # Runtime Metadata Update (Phase E — US5)
    # ─────────────────────────────────────────────────────────────────

    def update_metadata(
        self,
        conversation_id: str,
        *,
        message_count_delta: int = 0,
        token_delta: int = 0,
        last_activity_at: Optional[datetime] = None,
        focused_symbols: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Atomic metadata update using $inc and $set.

        Increments counters atomically and sets timestamps/symbols.
        Refuses to update archived conversations (ADR-001 immutability).

        Returns:
            Updated document, or None on failure / not-found / archived.
        """
        if not conversation_id:
            return None
        try:
            existing = self.collection.find_one(
                {"conversation_id": conversation_id}, {"status": 1}
            )
            if not existing:
                return None
            if existing.get("status") == self.STATUS_ARCHIVED:
                self.logger.warning(
                    f"Cannot update metadata for archived conversation: {conversation_id}"
                )
                return None

            update: Dict[str, Any] = {}
            inc_ops: Dict[str, int] = {}
            set_ops: Dict[str, Any] = {"updated_at": self._get_current_timestamp()}

            if message_count_delta:
                inc_ops["message_count"] = message_count_delta
            if token_delta:
                inc_ops["total_tokens"] = token_delta
            if last_activity_at is not None:
                set_ops["last_activity_at"] = last_activity_at
            if focused_symbols is not None:
                set_ops["metadata.focused_symbols"] = focused_symbols

            if inc_ops:
                update["$inc"] = inc_ops
            if set_ops:
                update["$set"] = set_ops

            if not update:
                return self.collection.find_one({"conversation_id": conversation_id})

            return self.collection.find_one_and_update(
                {"conversation_id": conversation_id},
                update,
                return_document=True,
            )
        except PyMongoError as e:
            self.logger.error(f"Error updating metadata for {conversation_id}: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────
    # Override: Disable Delete (ADR-001)
    # ─────────────────────────────────────────────────────────────────
    
    def delete(self, id: str) -> bool:
        """
        Delete is disabled for conversations (ADR-001: No-delete policy).
        
        Use archive() instead to mark conversations as read-only.
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
        """Check repository health."""
        try:
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
