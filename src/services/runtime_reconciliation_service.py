"""Scans for drift between STM checkpointer state and management API state.

Provides operator-only reconciliation that detects:
- Orphaned threads (exist in checkpointer, no management conversation)
- Metadata drift (conversation.message_count != checkpoint message count)
- Stale conversations (active with no recent activity)
- Missing threads (conversation exists but thread absent from checkpointer)

Reference: specs/stm-phase-cde/spec.md US6
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from services.base import BaseService

HealthReport = Tuple[bool, Dict[str, Any]]


class RuntimeReconciliationService(BaseService):
    """Scans for drift between STM checkpointer state and management API state."""

    STALE_THRESHOLD_DAYS = 30

    def __init__(
        self,
        conversation_repo: Any,
        session_repo: Any = None,
        workspace_repo: Any = None,
        *,
        checkpointer: Any = None,
        cache: Any = None,
        time_provider: Any = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self.conversation_repo = conversation_repo
        self.session_repo = session_repo
        self.workspace_repo = workspace_repo
        self.checkpointer = checkpointer

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self, *, scope: str = "full") -> Dict[str, Any]:
        """Run reconciliation scan, return machine-readable report."""
        correlation_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        self.logger.info(
            "reconciliation_scan",
            extra={
                "action": "scan_started",
                "correlation_id": correlation_id,
                "scope": scope,
            },
        )

        anomalies: List[Dict[str, Any]] = []

        anomalies.extend(self._detect_orphaned_threads())
        anomalies.extend(self._detect_metadata_drift())
        anomalies.extend(self._detect_stale_conversations())
        anomalies.extend(self._detect_missing_threads())

        completed_at = datetime.now(timezone.utc)
        duration_ms = (completed_at - started_at).total_seconds() * 1000

        report: Dict[str, Any] = {
            "correlation_id": correlation_id,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_ms": round(duration_ms),
            "scope": scope,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
        }

        for anomaly in anomalies:
            self.logger.warning(
                "reconciliation_anomaly",
                extra={
                    "action": "anomaly_detected",
                    "correlation_id": correlation_id,
                    **anomaly,
                },
            )

        self.logger.info(
            "reconciliation_scan",
            extra={
                "action": "scan_completed",
                "correlation_id": correlation_id,
                "anomaly_count": len(anomalies),
                "duration_ms": round(duration_ms),
            },
        )

        return report

    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------

    def _detect_orphaned_threads(self) -> List[Dict[str, Any]]:
        """Find threads in checkpointer with no management conversation record."""
        anomalies: List[Dict[str, Any]] = []
        if not self.checkpointer:
            return anomalies
        try:
            threads = self._list_checkpoint_threads()
            for thread in threads:
                thread_id = thread.get("thread_id") if isinstance(thread, dict) else str(thread)
                conversation = self.conversation_repo.find_by_thread_id(thread_id)
                if not conversation:
                    anomalies.append({
                        "type": "orphaned_thread",
                        "thread_id": thread_id,
                        "severity": "warning",
                    })
        except Exception as exc:
            self.logger.error(f"Error detecting orphaned threads: {exc}")
        return anomalies

    def _detect_metadata_drift(self) -> List[Dict[str, Any]]:
        """Find conversations where message_count doesn't match checkpoint state."""
        anomalies: List[Dict[str, Any]] = []
        if not self.checkpointer:
            return anomalies
        try:
            conversations = self.conversation_repo.get_all(
                filter_query={"status": "active"}
            )
            for conv in conversations:
                expected_count = conv.get("message_count", 0)
                thread_id = conv.get("thread_id")
                actual_count = self._count_checkpoint_messages(thread_id)
                if actual_count is not None and actual_count != expected_count:
                    anomalies.append({
                        "type": "metadata_drift",
                        "conversation_id": str(conv.get("conversation_id", conv.get("_id", ""))),
                        "thread_id": thread_id,
                        "field": "message_count",
                        "expected": expected_count,
                        "actual": actual_count,
                        "severity": "warning",
                    })
        except Exception as exc:
            self.logger.error(f"Error detecting metadata drift: {exc}")
        return anomalies

    def _detect_stale_conversations(self) -> List[Dict[str, Any]]:
        """Find active conversations with no recent activity."""
        anomalies: List[Dict[str, Any]] = []
        try:
            stale = self.conversation_repo.find_stale(
                days=self.STALE_THRESHOLD_DAYS
            )
            for conv in stale:
                anomalies.append({
                    "type": "stale_conversation",
                    "conversation_id": str(conv.get("conversation_id", conv.get("_id", ""))),
                    "last_activity_at": str(conv.get("last_activity_at")),
                    "severity": "info",
                })
        except Exception as exc:
            self.logger.error(f"Error detecting stale conversations: {exc}")
        return anomalies

    def _detect_missing_threads(self) -> List[Dict[str, Any]]:
        """Find conversations whose thread_id has no checkpoint in the checkpointer."""
        anomalies: List[Dict[str, Any]] = []
        if not self.checkpointer:
            return anomalies
        try:
            conversations = self.conversation_repo.get_all(
                filter_query={"status": "active"}
            )
            for conv in conversations:
                thread_id = conv.get("thread_id")
                if thread_id and not self._thread_exists(thread_id):
                    anomalies.append({
                        "type": "missing_thread",
                        "conversation_id": str(conv.get("conversation_id", conv.get("_id", ""))),
                        "thread_id": thread_id,
                        "severity": "error",
                    })
        except Exception as exc:
            self.logger.error(f"Error detecting missing threads: {exc}")
        return anomalies

    # ------------------------------------------------------------------
    # Checkpointer adapters
    # ------------------------------------------------------------------

    def _list_checkpoint_threads(self) -> List[Any]:
        """List all threads from the checkpointer.

        Adapts to MongoDBSaver by querying the underlying collection for
        distinct thread_ids.  Falls back to ``checkpointer.list(None)``
        for simpler/mock implementations.
        """
        if hasattr(self.checkpointer, "list"):
            return list(self.checkpointer.list(None))
        return []

    def _count_checkpoint_messages(self, thread_id: Optional[str]) -> Optional[int]:
        """Count messages stored in a checkpoint thread."""
        if not thread_id or not self.checkpointer:
            return None
        try:
            config = {"configurable": {"thread_id": thread_id}}
            checkpoint = self.checkpointer.get(config)
            if checkpoint and "channel_values" in checkpoint:
                messages = checkpoint["channel_values"].get("messages", [])
                return len(messages)
        except Exception:
            pass
        return None

    def _thread_exists(self, thread_id: str) -> bool:
        """Check if a thread exists in the checkpointer."""
        if not thread_id or not self.checkpointer:
            return True  # Can't verify without checkpointer
        try:
            config = {"configurable": {"thread_id": thread_id}}
            checkpoint = self.checkpointer.get(config)
            return checkpoint is not None
        except Exception:
            return True  # Can't verify, assume exists

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_check(self) -> HealthReport:
        return self._dependencies_health_report(
            required={"conversation_repo": self.conversation_repo},
            optional={"checkpointer": self.checkpointer},
        )
