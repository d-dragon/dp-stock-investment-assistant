"""Additive, resumable migration for promoting legacy session-keyed checkpoint
threads into the conversation-scoped data model.

Zero data loss — original checkpoints are never deleted or overwritten.
Operator-only; not exposed through Flask routes.

Reference: specs/stm-phase-cde/data-model.md
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ACTION_PREVIEW = "preview"
_ACTION_CREATE = "create"
_ACTION_SKIP = "skip"
_ACTION_ERROR = "error"
_ACTION_COMPLETE = "complete"

_MODE_DRY_RUN = "dry-run"
_MODE_EXECUTE = "execute"

_STATUS_PENDING = "pending"
_STATUS_RUNNING = "running"
_STATUS_COMPLETED = "completed"
_STATUS_FAILED = "failed"


class LegacyCheckpointMigration:
    """Promote legacy session-keyed checkpoint threads into the conversation model.

    Design invariants:
    - **Additive only**: creates new conversation records; never deletes or
      overwrites existing checkpoints.
    - **Resumable**: accepts ``resume_run_id`` to continue from the last
      successfully processed source id.
    - **Idempotent**: skips threads that already have a conversation record.
    - **Auditable**: every action is recorded in an audit log attached to the
      migration run report.
    """

    # Sentinel workspace / user for legacy records that lack this metadata.
    _LEGACY_WORKSPACE = "legacy"
    _LEGACY_USER = "legacy"

    def __init__(
        self,
        conversation_repo: Any,
        session_repo: Any = None,
        checkpointer: Any = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.conversation_repo = conversation_repo
        self.session_repo = session_repo
        self.checkpointer = checkpointer
        self.logger = logger or logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dry_run(self, batch_size: int = 100) -> Dict[str, Any]:
        """Preview migration without performing any writes.

        Returns a report conforming to the dry-run output contract.
        """
        correlation_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        self.logger.info(
            "legacy_migration_dry_run_started",
            extra={"run_id": run_id, "correlation_id": correlation_id},
        )

        audit_log: List[Dict[str, Any]] = []
        to_create = 0
        to_skip = 0
        error_count = 0

        try:
            threads = self._list_legacy_threads()
        except Exception as exc:
            self.logger.error("Failed to list legacy threads: %s", exc)
            return self._build_run_state(
                run_id=run_id,
                correlation_id=correlation_id,
                mode=_MODE_DRY_RUN,
                status=_STATUS_FAILED,
                started_at=started_at,
                audit_log=[self._audit_entry(
                    correlation_id, _ACTION_ERROR, source_id="",
                    outcome=f"Failed to list threads: {exc}",
                )],
            )

        for thread in threads:
            thread_id = self._extract_thread_id(thread)
            if not thread_id:
                error_count += 1
                audit_log.append(self._audit_entry(
                    correlation_id, _ACTION_ERROR,
                    source_id=str(thread),
                    outcome="Could not extract thread_id",
                ))
                continue

            try:
                if self._is_already_migrated(thread_id):
                    to_skip += 1
                    audit_log.append(self._audit_entry(
                        correlation_id, _ACTION_SKIP,
                        source_id=thread_id,
                        outcome="Already has conversation record",
                    ))
                else:
                    to_create += 1
                    audit_log.append(self._audit_entry(
                        correlation_id, _ACTION_PREVIEW,
                        source_id=thread_id,
                        target_id=thread_id,
                        outcome="Would create conversation record",
                    ))
            except Exception as exc:
                error_count += 1
                audit_log.append(self._audit_entry(
                    correlation_id, _ACTION_ERROR,
                    source_id=thread_id,
                    outcome=f"Error checking migration status: {exc}",
                ))

        completed_at = datetime.now(timezone.utc)
        audit_log.append(self._audit_entry(
            correlation_id, _ACTION_COMPLETE,
            source_id="",
            outcome=f"Dry-run finished: create={to_create}, skip={to_skip}, errors={error_count}",
        ))

        report = self._build_run_state(
            run_id=run_id,
            correlation_id=correlation_id,
            mode=_MODE_DRY_RUN,
            status=_STATUS_COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            processed_count=to_create + to_skip,
            skipped_count=to_skip,
            error_count=error_count,
            audit_log=audit_log,
        )
        # Add dry-run contract fields.
        report["to_create"] = to_create
        report["to_skip"] = to_skip
        report["to_update"] = 0
        report["remaining_legacy_records"] = to_create
        report["writes_performed"] = 0

        self.logger.info(
            "legacy_migration_dry_run_completed",
            extra={
                "run_id": run_id,
                "to_create": to_create,
                "to_skip": to_skip,
                "error_count": error_count,
            },
        )
        return report

    def execute(
        self,
        batch_size: int = 100,
        resume_run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run additive migration, creating conversation records for legacy threads.

        Args:
            batch_size: Number of threads to process per batch (for logging).
            resume_run_id: If provided, the ``last_processed_source_id`` from a
                previous run is used to skip already-processed threads.

        Returns:
            Migration report with embedded audit log.
        """
        correlation_id = str(uuid.uuid4())
        run_id = resume_run_id or str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        self.logger.info(
            "legacy_migration_execute_started",
            extra={
                "run_id": run_id,
                "correlation_id": correlation_id,
                "resume": resume_run_id is not None,
            },
        )

        audit_log: List[Dict[str, Any]] = []
        processed_count = 0
        skipped_count = 0
        created_count = 0
        error_count = 0
        last_processed_source_id: Optional[str] = None

        try:
            threads = self._list_legacy_threads()
        except Exception as exc:
            self.logger.error("Failed to list legacy threads: %s", exc)
            return self._build_run_state(
                run_id=run_id,
                correlation_id=correlation_id,
                mode=_MODE_EXECUTE,
                status=_STATUS_FAILED,
                started_at=started_at,
                audit_log=[self._audit_entry(
                    correlation_id, _ACTION_ERROR, source_id="",
                    outcome=f"Failed to list threads: {exc}",
                )],
            )

        # Sort thread IDs for deterministic resume ordering.
        thread_ids = []
        for thread in threads:
            tid = self._extract_thread_id(thread)
            if tid:
                thread_ids.append(tid)
            else:
                error_count += 1
                audit_log.append(self._audit_entry(
                    correlation_id, _ACTION_ERROR,
                    source_id=str(thread),
                    outcome="Could not extract thread_id",
                ))
        thread_ids.sort()

        # Resume support: skip threads already processed in previous run.
        resume_cursor = self._resolve_resume_cursor(resume_run_id)
        if resume_cursor:
            original_len = len(thread_ids)
            thread_ids = [t for t in thread_ids if t > resume_cursor]
            skipped_by_resume = original_len - len(thread_ids)
            self.logger.info(
                "legacy_migration_resuming",
                extra={
                    "run_id": run_id,
                    "resume_cursor": resume_cursor,
                    "skipped_by_resume": skipped_by_resume,
                },
            )

        for idx, thread_id in enumerate(thread_ids, 1):
            try:
                if self._is_already_migrated(thread_id):
                    skipped_count += 1
                    audit_log.append(self._audit_entry(
                        correlation_id, _ACTION_SKIP,
                        source_id=thread_id,
                        outcome="Already has conversation record",
                    ))
                else:
                    result = self._create_conversation_for_thread(
                        thread_id=thread_id,
                        session_id=self._resolve_session_id(thread_id),
                    )
                    if result:
                        created_count += 1
                        audit_log.append(self._audit_entry(
                            correlation_id, _ACTION_CREATE,
                            source_id=thread_id,
                            target_id=result.get("conversation_id", thread_id),
                            outcome="Conversation record created",
                        ))
                    else:
                        error_count += 1
                        audit_log.append(self._audit_entry(
                            correlation_id, _ACTION_ERROR,
                            source_id=thread_id,
                            outcome="create_conversation returned None",
                        ))
            except Exception as exc:
                error_count += 1
                audit_log.append(self._audit_entry(
                    correlation_id, _ACTION_ERROR,
                    source_id=thread_id,
                    outcome=f"Unexpected error: {exc}",
                ))
                self.logger.error(
                    "legacy_migration_thread_error",
                    extra={"thread_id": thread_id, "error": str(exc)},
                )

            processed_count += 1
            last_processed_source_id = thread_id

            if idx % batch_size == 0:
                self.logger.info(
                    "legacy_migration_batch_progress",
                    extra={
                        "run_id": run_id,
                        "processed": processed_count,
                        "created": created_count,
                        "skipped": skipped_count,
                        "errors": error_count,
                    },
                )

        completed_at = datetime.now(timezone.utc)
        status = _STATUS_COMPLETED if error_count == 0 else _STATUS_FAILED

        audit_log.append(self._audit_entry(
            correlation_id, _ACTION_COMPLETE,
            source_id="",
            outcome=(
                f"Migration {status}: processed={processed_count}, "
                f"created={created_count}, skipped={skipped_count}, errors={error_count}"
            ),
        ))

        self.logger.info(
            "legacy_migration_execute_completed",
            extra={
                "run_id": run_id,
                "status": status,
                "processed_count": processed_count,
                "created_count": created_count,
                "skipped_count": skipped_count,
                "error_count": error_count,
            },
        )

        return self._build_run_state(
            run_id=run_id,
            correlation_id=correlation_id,
            mode=_MODE_EXECUTE,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            processed_count=processed_count,
            skipped_count=skipped_count,
            error_count=error_count,
            last_processed_source_id=last_processed_source_id,
            audit_log=audit_log,
            extra={"created_count": created_count},
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _list_legacy_threads(self) -> List[Any]:
        """Get all threads from checkpointer."""
        if not self.checkpointer:
            self.logger.warning("No checkpointer configured; returning empty thread list")
            return []
        if hasattr(self.checkpointer, "list"):
            return list(self.checkpointer.list(None))
        return []

    def _extract_thread_id(self, thread: Any) -> Optional[str]:
        """Extract thread_id from a checkpoint list entry.

        The shape depends on the checkpointer implementation:
        - Dict with ``configurable.thread_id``
        - Dict with ``thread_id``
        - A ``CheckpointTuple`` with ``config["configurable"]["thread_id"]``
        - Plain string
        """
        if isinstance(thread, str):
            return thread

        # CheckpointTuple / namedtuple with .config
        config = getattr(thread, "config", None)
        if config and isinstance(config, dict):
            configurable = config.get("configurable", {})
            tid = configurable.get("thread_id")
            if tid:
                return str(tid)

        # Raw dict shapes
        if isinstance(thread, dict):
            configurable = thread.get("configurable", {})
            tid = configurable.get("thread_id") or thread.get("thread_id")
            if tid:
                return str(tid)

        return None

    def _is_already_migrated(self, thread_id: str) -> bool:
        """Check if thread already has a conversation record.

        The canonical mapping is ``conversation_id == thread_id``, but we also
        check ``thread_id`` as a foreign key for completeness.
        """
        if self.conversation_repo.find_by_conversation_id(thread_id):
            return True
        if self.conversation_repo.find_by_thread_id(thread_id):
            return True
        return False

    def _create_conversation_for_thread(
        self,
        thread_id: str,
        session_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a conversation metadata record for a legacy thread.

        The canonical mapping sets ``conversation_id == thread_id`` so the
        thread can be looked up by either key.
        """
        conversation_id = thread_id  # canonical 1:1 mapping

        return self.conversation_repo.create_conversation(
            conversation_id=conversation_id,
            thread_id=thread_id,
            session_id=session_id or self._LEGACY_WORKSPACE,
            workspace_id=workspace_id or self._LEGACY_WORKSPACE,
            user_id=user_id or self._LEGACY_USER,
        )

    def _resolve_session_id(self, thread_id: str) -> str:
        """Attempt to find a session that owns this thread.

        Falls back to the legacy sentinel when no session repository is
        available or no session is found.
        """
        if not self.session_repo:
            return self._LEGACY_WORKSPACE

        try:
            # Some legacy setups use thread_id == session_id.
            session = self.session_repo.find_by_session_id(thread_id)
            if session:
                return str(session.get("session_id", thread_id))
        except Exception as exc:
            self.logger.debug(
                "Could not resolve session for thread %s: %s", thread_id, exc,
            )

        return self._LEGACY_WORKSPACE

    def _resolve_resume_cursor(self, resume_run_id: Optional[str]) -> Optional[str]:
        """Resolve the last_processed_source_id for a previous run.

        When full run-state persistence is added this will query the
        migration_runs collection.  For now, ``resume_run_id`` is treated
        as the literal cursor value (last_processed_source_id) to keep the
        implementation simple and stateless.
        """
        # Future: look up run by ID in a migration_runs collection.
        return resume_run_id

    # ------------------------------------------------------------------
    # Report builders
    # ------------------------------------------------------------------

    @staticmethod
    def _audit_entry(
        correlation_id: str,
        action_type: str,
        source_id: str,
        outcome: str,
        target_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "action_type": action_type,
            "source_id": source_id,
            "target_id": target_id,
            "outcome": outcome,
        }
        if details:
            entry["details"] = details
        return entry

    @staticmethod
    def _build_run_state(
        *,
        run_id: str,
        correlation_id: str,
        mode: str,
        status: str,
        started_at: datetime,
        completed_at: Optional[datetime] = None,
        processed_count: int = 0,
        skipped_count: int = 0,
        error_count: int = 0,
        last_processed_source_id: Optional[str] = None,
        audit_log: Optional[List[Dict[str, Any]]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            "run_id": run_id,
            "correlation_id": correlation_id,
            "mode": mode,
            "status": status,
            "last_processed_source_id": last_processed_source_id,
            "processed_count": processed_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat() if completed_at else None,
            "audit_log": audit_log or [],
        }
        if extra:
            report.update(extra)
        return report
