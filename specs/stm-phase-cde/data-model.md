# Data Model: STM Phase C-E

## Scope

This design extends the Phase A-B hierarchy already present in the repository:

```text
workspace -> session -> conversation -> thread
```

The canonical runtime identity remains:

```text
conversation_id -> thread_id
```

Phase C adds management-facing lifecycle and navigation contracts. Phase D adds consistency, anomaly-reporting, and migration-run entities. Phase E adds no new runtime entities but depends on the invariants below becoming testable.

## Core Entities

### Workspace

| Field | Type | Rules |
|-------|------|-------|
| workspace_id | string UUID v4 | Unique business identifier returned in all payloads. |
| user_id | string | Ownership boundary for all descendants. |
| name | string | Required on create; mutable while active. |
| description | string or null | Optional; mutable while active. |
| status | enum(`active`, `archived`) | `archived` is terminal. |
| created_at | datetime | Immutable. |
| updated_at | datetime | Updated on metadata or lifecycle change. |

Derived fields for GET/list payloads:

- `session_count`
- `active_conversation_count`

Lifecycle:

```text
active -> archived
```

Rules:

- Archiving a workspace archives all descendant sessions and conversations.
- Archived workspaces reject session creation and metadata mutation.

### Session

| Field | Type | Rules |
|-------|------|-------|
| session_id | string UUID v4 | Unique business identifier. |
| workspace_id | string UUID v4 | Must reference an owned workspace. |
| user_id | string | Must match workspace owner. |
| title | string | Required on create. |
| status | enum(`active`, `closed`, `archived`) | Forward-only lifecycle. |
| assumptions | string or null | Mutable only while active. |
| pinned_intent | string or null | Mutable only while active. |
| focused_symbols | array[string] | Mutable only while active; inherited by child conversations. |
| linked_symbol_ids | array[string] | Optional related symbol identifiers. |
| created_at | datetime | Immutable. |
| updated_at | datetime | Updated on context/lifecycle change. |

Derived fields for GET/list payloads:

- `conversation_count`

Lifecycle:

```text
active -> closed -> archived
```

Rules:

- `closed` blocks new conversation creation and session-context mutation.
- Existing non-archived conversations under a closed session remain chat-capable.
- `archived` archives all child conversations and rejects new messages anywhere in the subtree.
- Reverse transitions are invalid.

### Conversation

| Field | Type | Rules |
|-------|------|-------|
| conversation_id | string UUID v4 | Primary business identifier. |
| thread_id | string UUID v4 | Must equal `conversation_id`. |
| session_id | string UUID v4 | Must reference a valid session. |
| workspace_id | string UUID v4 | Must match parent session's workspace. |
| user_id | string | Must match hierarchy owner. |
| title | string or null | Optional create-time label. |
| status | enum(`active`, `summarized`, `archived`) | Only `archived` is immutable. |
| message_count | integer | Incremented for both user and assistant turns. |
| total_tokens | integer | Estimated and accumulated for assistant responses. |
| summary | string or null | Returned if available. |
| context_overrides | object or null | Thread-local refinement of inherited session context. |
| conversation_intent | string or null | Optional thread-local intent. |
| focused_symbols | array[string] | Session inheritance plus conversation/runtime accumulation. |
| archived_at | datetime or null | Set when archived. |
| archive_reason | string or null | Recorded on archive action. |
| last_activity_at | datetime | Updated on accepted turns. |
| created_at | datetime | Immutable. |
| updated_at | datetime | Updated on metadata/lifecycle change. |

Derived fields for GET/list payloads:

- `workspace_id`
- `session_id`
- `message_count`
- `total_tokens`
- `time_range` for summary responses

Lifecycle:

```text
active -> summarized -> archived
active -> archived
summarized -> archived
```

Rules:

- `summarized` conversations remain resumable and queryable.
- `archived` conversations reject further messages and archive requests remain safe no-ops.
- Nested route parent IDs must match stored parent IDs; mismatches are rejected.

## Operational Entities

### Reconciliation Report

| Field | Type | Rules |
|-------|------|-------|
| report_id | string UUID v4 | Unique identifier for a scan result. |
| generated_at | datetime | Completion timestamp. |
| correlation_id | string | Shared across scan logs and report output. |
| anomalies | array[Anomaly] | Machine-readable findings. |
| total_scanned | object | Counts by resource type. |
| scan_duration_ms | integer | For performance tracking. |
| mode | enum(`on-demand`, `scheduled`, `pre-migration`, `post-migration`) | Execution context. |

Anomaly structure:

| Field | Type | Rules |
|-------|------|-------|
| type | enum | `orphan_session`, `orphan_conversation`, `checkpoint_without_conversation`, `conversation_without_checkpoint`, `thread_id_mismatch`, `ambiguous_parent` |
| affected_ids | object | Includes relevant workspace/session/conversation/thread IDs. |
| suggested_remediation | string | Detection-only guidance; no auto-heal in this feature. |
| severity | enum(`warning`, `critical`) | Threshold-driven operational severity. |

### Reconciliation Scan Log Entry

| Field | Type | Rules |
|-------|------|-------|
| correlation_id | string | Shared with report. |
| action | enum(`scan_started`, `anomaly_detected`, `scan_completed`) | Required by FR-D08a. |
| timestamp | datetime | Required for auditability. |
| details | object | Counts, anomaly references, or timing context. |

### Migration Audit Entry

| Field | Type | Rules |
|-------|------|-------|
| timestamp | datetime | Required. |
| correlation_id | string | Required. |
| action_type | enum(`preview`, `create`, `skip`, `error`, `complete`) | Required. |
| source_id | string | Legacy thread/session identifier. |
| target_id | string or null | New conversation identifier if applicable. |
| outcome | string | Machine-readable result string. |
| details | object | Optional diagnostic context. |

### Migration Run State

| Field | Type | Rules |
|-------|------|-------|
| run_id | string UUID v4 | Unique run identifier. |
| correlation_id | string | Shared across audit entries. |
| mode | enum(`dry-run`, `execute`) | Required. |
| status | enum(`pending`, `running`, `completed`, `failed`, `cancelled`) | Resumable lifecycle. |
| last_processed_source_id | string or null | Resume cursor. |
| processed_count | integer | Count of completed items. |
| skipped_count | integer | Count of already-migrated items. |
| error_count | integer | Count of failed items. |
| started_at | datetime | Required. |
| completed_at | datetime or null | Optional until completion. |

## Invariants

### Hierarchy and Ownership

- Every session must belong to exactly one workspace.
- Every conversation must belong to exactly one session and one workspace.
- `conversation.workspace_id` must equal the parent session's `workspace_id`.
- `session.user_id`, `workspace.user_id`, and `conversation.user_id` must match for owned resources.
- Direct routes must validate ownership through stored hierarchy; nested routes must validate both ownership and path-parent match.

### Lifecycle

- No hard deletion exists for workspace, session, or conversation records.
- Reverse lifecycle transitions are not permitted.
- Parent archive cascades to all descendants.
- `closed` session is a non-terminal, read-only-for-context state.
- `summarized` conversation is non-terminal and chat-capable.

### Runtime Consistency

- A conversation metadata record must exist before agent processing when `conversation_id` is supplied.
- For accepted user turns, `message_count += 1` and `last_activity_at` updates.
- For assistant turns, `message_count += 1` and `total_tokens` updates.
- `focused_symbols` updates are additive.
- Chat responses may still succeed when metadata writes fail, but such drift must become visible through logs and reconciliation.

### Migration and Reconciliation

- Migration is additive and must never orphan or delete original checkpoint data during the migration window.
- Reconciliation is detection-only for this feature.
- `thread_id != conversation_id` is always an integrity anomaly.
- Ambiguous-parent findings require manual remediation and cannot be auto-linked.

## Query and Contract Considerations

- List endpoints use `limit` and `offset`.
- Workspace/session lists sort by `updated_at desc`.
- Conversation lists sort by `last_activity_at desc`, then `updated_at desc`.
- Zero-result list responses still return valid pagination metadata.
- Summary retrieval is a read model over the conversation plus aggregated message metadata, not a separate mutable resource.