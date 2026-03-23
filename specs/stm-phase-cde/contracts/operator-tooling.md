# Contract: Operator Tooling

## Scope

This contract defines the operator-only Phase D tooling for reconciliation and migration. These operations are intentionally not exposed through public `/api` management routes.

Execution follows the repository's operational tooling pattern:

- Script entrypoints under `scripts/`
- Reusable logic under `src/services/` or `src/data/migration/`
- Structured logs and machine-readable outputs written to `reports/` or stdout

## Authorization Boundary

- Reconciliation and migration require elevated/operator execution paths.
- Public REST routes and Socket.IO events must not invoke these workflows.
- Tests must verify absence from registered public route maps and rejection of non-operator invocation paths.

## Reconciliation Contract

### Planned entrypoint

```powershell
python scripts/reconcile_stm_runtime.py --mode on-demand --format json --output reports/reconciliation/latest.json
```

### Supported arguments

- `--mode on-demand|scheduled|pre-migration|post-migration`
- `--workspace-id <uuid>` optional scope filter
- `--session-id <uuid>` optional scope filter
- `--format json`
- `--output <path>` optional file output
- `--chunk-size <n>` optional scan batch size override

### Output contract

```json
{
  "report_id": "2c32ad2f-163e-4111-a847-35d98e6720f4",
  "generated_at": "2026-03-23T10:15:30Z",
  "correlation_id": "760f0b2d-7731-4b93-97a0-a15d9b48d9b9",
  "mode": "on-demand",
  "scan_duration_ms": 1480,
  "total_scanned": {
    "workspaces": 12,
    "sessions": 44,
    "conversations": 117,
    "checkpoint_threads": 119
  },
  "anomalies": [
    {
      "type": "conversation_without_checkpoint",
      "affected_ids": {
        "conversation_id": "7d2d5858-68cb-412a-9399-f1e854ed8fe3",
        "session_id": "2d4890bf-4a90-47f9-a5ed-7ac83c52eaa7"
      },
      "severity": "critical",
      "suggested_remediation": "Inspect chat metadata write path and re-run scan after repair"
    }
  ]
}
```

### Logging contract

- Every scan emits structured log entries with:
  - `correlation_id`
  - `action` in `scan_started|anomaly_detected|scan_completed`
  - `timestamp`
  - scan context or anomaly counts

### Operational policy

- Scheduled production cadence: hourly.
- Mandatory scans: before any migration execution and after migration completion.
- Alert thresholds:
  - critical: any orphan or checkpoint/conversation mismatch outside active migration window
  - warning: repeated anomalies across 2 consecutive scans during migration window
  - critical: latency impact at or above 5 percent

## Migration Contract

### Planned entrypoint

```powershell
python scripts/migrate_legacy_threads.py --dry-run
python scripts/migrate_legacy_threads.py --resume --output reports/migration/latest.json
```

### Supported arguments

- `--dry-run`
- `--resume`
- `--run-id <uuid>` optional resume target
- `--batch-size <n>` optional batch size override
- `--output <path>` optional output path
- `--fail-fast` optional execution behavior for operator troubleshooting

### Dry-run output contract

```json
{
  "run_id": "bc0b46d3-c092-4555-a772-03c7d1b36d15",
  "mode": "dry-run",
  "correlation_id": "ecfd99f7-e6ff-468b-a508-07d324b42da1",
  "to_create": 38,
  "to_skip": 12,
  "to_update": 0,
  "remaining_legacy_records": 38,
  "writes_performed": 0
}
```

### Execution guarantees

- Migration is additive and resumable.
- Existing checkpoints are not deleted or overwritten during the migration window.
- Resume logic skips already-migrated records and continues from the last successful source identifier.
- Mixed traffic remains supported throughout the migration window.

### Audit log contract

Each action emits:

- `timestamp`
- `correlation_id`
- `action_type`
- `source_id`
- `target_id`
- `outcome`
- optional `details`

### Window and rollback policy

- The migration window closes only after a dry-run returns zero remaining legacy records and 2 consecutive reconciliation scans are clean.
- Rollback means stop future migration execution, retain additive conversation metadata already created, keep legacy stateless handling active, and postpone cleanup of compatibility logic until a later controlled phase.

## Test Obligations

- Security tests must verify no public route or socket event exposes reconciliation or migration.
- Contract tests must verify dry-run performs zero writes.
- Resume tests must verify interrupted and uninterrupted runs converge to the same final state.
- Mixed-traffic tests must verify both legacy stateless and conversation-aware requests work during the migration window.