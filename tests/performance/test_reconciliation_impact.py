"""Performance tests: Reconciliation scan latency-impact verification.

Validates that RuntimeReconciliationService.scan() completes within
acceptable P95 latency budgets using mock repositories returning
controlled data sets.

Reference: specs/stm-phase-cde/tasks.md - T037 (US6)
Run with: pytest tests/performance/ -m performance -v
"""

import statistics
import time
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from services.runtime_reconciliation_service import RuntimeReconciliationService


# ---------------------------------------------------------------------------
# Latency budgets (P95, milliseconds)
# ---------------------------------------------------------------------------
BUDGET_SMALL_SCOPE_MS = 1000   # 10 conversations
BUDGET_MEDIUM_SCOPE_MS = 5000  # 100 conversations

ITERATIONS = 30


# ---------------------------------------------------------------------------
# Data generators
# ---------------------------------------------------------------------------

def _make_conversations(count: int) -> list:
    """Generate *count* active conversation documents."""
    now = datetime.now(timezone.utc)
    return [
        {
            "conversation_id": str(uuid.uuid4()),
            "thread_id": str(uuid.uuid4()),
            "status": "active",
            "message_count": 5,
            "last_activity_at": now - timedelta(hours=i),
        }
        for i in range(count)
    ]


def _make_checkpoint(message_count: int = 5) -> dict:
    """Create a checkpoint stub with *message_count* messages."""
    return {
        "channel_values": {
            "messages": [f"msg-{i}" for i in range(message_count)],
        }
    }


def _build_service(conversations: list, *, inject_anomalies: bool = False):
    """Return a RuntimeReconciliationService wired with mock repos."""
    repo = MagicMock()
    repo.health_check.return_value = (True, {})
    repo.get_all.return_value = conversations
    repo.find_stale.return_value = []
    repo.find_by_thread_id.side_effect = lambda tid: next(
        (c for c in conversations if c["thread_id"] == tid), None
    )

    cp = MagicMock()
    # Checkpointer lists the same threads as repo conversations
    cp.list.return_value = [{"thread_id": c["thread_id"]} for c in conversations]

    if inject_anomalies:
        # Drift: checkpoint reports 7 messages vs repo's 5
        cp.get.return_value = _make_checkpoint(message_count=7)
    else:
        cp.get.return_value = _make_checkpoint(message_count=5)

    return RuntimeReconciliationService(
        conversation_repo=repo,
        checkpointer=cp,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _measure_p95(svc: RuntimeReconciliationService, iterations: int) -> float:
    """Run scan() *iterations* times and return P95 latency in ms."""
    latencies: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        svc.scan()
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)
    latencies.sort()
    idx = int(len(latencies) * 0.95) - 1
    return latencies[max(idx, 0)]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.performance
class TestReconciliationScanLatency:
    """Reconciliation scan must stay within P95 latency budgets."""

    def test_small_scope_latency(self):
        """10 conversations: scan() < 1000ms P95."""
        convs = _make_conversations(10)
        svc = _build_service(convs)

        p95 = _measure_p95(svc, ITERATIONS)

        assert p95 < BUDGET_SMALL_SCOPE_MS, (
            f"Small-scope P95 {p95:.1f}ms exceeds budget {BUDGET_SMALL_SCOPE_MS}ms"
        )

    def test_medium_scope_latency(self):
        """100 conversations: scan() < 5000ms P95."""
        convs = _make_conversations(100)
        svc = _build_service(convs)

        p95 = _measure_p95(svc, ITERATIONS)

        assert p95 < BUDGET_MEDIUM_SCOPE_MS, (
            f"Medium-scope P95 {p95:.1f}ms exceeds budget {BUDGET_MEDIUM_SCOPE_MS}ms"
        )

    def test_small_scope_with_anomalies(self):
        """10 conversations with drift anomalies: scan() < 1000ms P95."""
        convs = _make_conversations(10)
        svc = _build_service(convs, inject_anomalies=True)

        p95 = _measure_p95(svc, ITERATIONS)

        assert p95 < BUDGET_SMALL_SCOPE_MS, (
            f"Small-scope (anomalies) P95 {p95:.1f}ms exceeds budget {BUDGET_SMALL_SCOPE_MS}ms"
        )

    def test_medium_scope_with_anomalies(self):
        """100 conversations with drift anomalies: scan() < 5000ms P95."""
        convs = _make_conversations(100)
        svc = _build_service(convs, inject_anomalies=True)

        p95 = _measure_p95(svc, ITERATIONS)

        assert p95 < BUDGET_MEDIUM_SCOPE_MS, (
            f"Medium-scope (anomalies) P95 {p95:.1f}ms exceeds budget {BUDGET_MEDIUM_SCOPE_MS}ms"
        )
