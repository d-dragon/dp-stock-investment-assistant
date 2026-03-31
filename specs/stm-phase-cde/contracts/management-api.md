# Contract: Management API

## Scope

This contract defines the public Phase C management endpoints under the existing `/api` namespace. It is additive to the current chat and health routes and must reuse the existing Flask blueprint and `APIRouteContext` patterns already registered in `src/web/api_server.py`.

Implementation note: the project-scoped OpenAPI document at `docs/openapi.yaml` must be updated alongside Phase C route delivery and any affected chat request/response contract changes so external API documentation stays aligned with the implemented REST surface.

The OpenAPI update is not limited to newly added management endpoints. It must also reconcile the existing documented public API surface with the currently registered routes, especially where legacy session-oriented chat documentation diverges from the conversation-aware runtime contract.

## Common Rules

- All list responses return:
  - `items`: array
  - `total`: integer
  - `limit`: integer
  - `offset`: integer
- Supported list query parameters:
  - `limit`: optional integer, default `25`, max `100`
  - `offset`: optional integer, default `0`
  - `status`: optional filter where the resource supports it
- Error shape matches the chat API envelope:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Conversation not found",
    "correlation_id": "3d7008a3-7b1e-43d7-a69f-e080eeea1234"
  }
}
```

- GET requests are safe and idempotent.
- Archive actions use `POST`, never `DELETE`.
- All resource payloads include the relevant hierarchy identifiers needed for client navigation.

## Workspace Endpoints

### `GET /api/workspaces`

- Returns owned workspaces only.
- Sort order: `updated_at desc`.
- Item fields:
  - `workspace_id`
  - `name`
  - `description`
  - `status`
  - `session_count`
  - `created_at`
  - `updated_at`

### `POST /api/workspaces`

Request:

```json
{
  "name": "Semiconductor swing trades",
  "description": "Tracking cyclical names and catalysts"
}
```

Response fields:

- `workspace_id`
- `name`
- `description`
- `status`
- `created_at`
- `updated_at`

### `GET /api/workspaces/{workspace_id}`

Response extends base payload with:

- `session_count`
- `active_conversation_count`

### `PUT /api/workspaces/{workspace_id}`

- Accepts partial updates for `name` and `description` only while the workspace is active.
- Response fields match the workspace detail payload:
  - `workspace_id`
  - `name`
  - `description`
  - `status`
  - `session_count`
  - `active_conversation_count`
  - `created_at`
  - `updated_at`

### `POST /api/workspaces/{workspace_id}/archive`

Request body is optional.

Behavior:

- Archives the workspace.
- Archives all descendant sessions and conversations atomically per parent operation.
- Repeated archive requests are safe and leave archived descendants unchanged.
- Response fields match the workspace detail payload after the archive transition:
  - `workspace_id`
  - `name`
  - `description`
  - `status`
  - `session_count`
  - `active_conversation_count`
  - `created_at`
  - `updated_at`

## Session Endpoints

### `GET /api/workspaces/{workspace_id}/sessions`

- Lists sessions for the specified workspace after parent-match validation.
- Sort order: `updated_at desc`.
- Optional query param: `status` in `active|closed|archived`.
- Collection response schema:
  - `items`: array of session list items
  - `total`: integer
  - `limit`: integer
  - `offset`: integer
- Session list item fields:
  - `session_id`
  - `workspace_id`
  - `title`
  - `status`
  - `conversation_count`
  - `focused_symbols`
  - `created_at`
  - `updated_at`

### `POST /api/workspaces/{workspace_id}/sessions`

Request:

```json
{
  "title": "NVDA earnings prep",
  "assumptions": "Demand remains supply constrained",
  "pinned_intent": "Assess post-earnings risk/reward",
  "focused_symbols": ["NVDA", "AMD"]
}
```

Reject if the workspace is archived.

Response fields:

- `session_id`
- `workspace_id`
- `title`
- `status`
- `assumptions`
- `pinned_intent`
- `focused_symbols`
- `conversation_count`
- `created_at`
- `updated_at`

### `GET /api/sessions/{session_id}`

Response fields:

- `session_id`
- `workspace_id`
- `title`
- `status`
- `assumptions`
- `pinned_intent`
- `focused_symbols`
- `conversation_count`
- `created_at`
- `updated_at`

### `PUT /api/sessions/{session_id}`

- Accepts partial updates for session context fields while `status=active`.
- Rejects updates for `closed` and `archived` sessions.
- Response fields match the session detail payload:
  - `session_id`
  - `workspace_id`
  - `title`
  - `status`
  - `assumptions`
  - `pinned_intent`
  - `focused_symbols`
  - `conversation_count`
  - `created_at`
  - `updated_at`

### `POST /api/sessions/{session_id}/close`

- Valid only from `active`.
- `closed` means no new conversations may be created; existing non-archived conversations remain message-capable.
- Response fields match the session detail payload after the lifecycle transition:
  - `session_id`
  - `workspace_id`
  - `title`
  - `status`
  - `assumptions`
  - `pinned_intent`
  - `focused_symbols`
  - `conversation_count`
  - `created_at`
  - `updated_at`

### `POST /api/sessions/{session_id}/archive`

- Valid from `active` or `closed`.
- Archives all child conversations.
- Response fields match the session detail payload after the lifecycle transition:
  - `session_id`
  - `workspace_id`
  - `title`
  - `status`
  - `assumptions`
  - `pinned_intent`
  - `focused_symbols`
  - `conversation_count`
  - `created_at`
  - `updated_at`

### Nested parent mismatch rule

- If `/api/workspaces/{workspace_id}/sessions/{session_id}` style access is implemented during execution, the route must reject when the session's stored `workspace_id` does not match the path `workspace_id`.
- The rejection uses the same secure not-found/error envelope as other out-of-hierarchy access cases.

## Conversation Endpoints

### `GET /api/sessions/{session_id}/conversations`

- Lists conversations for the specified session after parent-match validation.
- Sort order: `last_activity_at desc`, tie-break `updated_at desc`.
- Optional query param: `status` in `active|summarized|archived`.
- Collection response schema:
  - `items`: array of conversation list items
  - `total`: integer
  - `limit`: integer
  - `offset`: integer
- Conversation list item fields:
  - `conversation_id`
  - `thread_id`
  - `session_id`
  - `workspace_id`
  - `title`
  - `status`
  - `message_count`
  - `total_tokens`
  - `focused_symbols`
  - `last_activity_at`
  - `created_at`
  - `updated_at`

### `POST /api/sessions/{session_id}/conversations`

Request:

```json
{
  "title": "Scenario analysis",
  "context_overrides": {
    "focused_symbols": ["MSFT"],
    "conversation_intent": "Compare Azure growth cases"
  }
}
```

Response fields:

- `conversation_id`
- `thread_id`
- `session_id`
- `workspace_id`
- `status`
- `created_at`
- `updated_at`

Reject if parent session is `closed` or `archived`.

### `GET /api/conversations/{conversation_id}`

Response fields:

- `conversation_id`
- `thread_id`
- `session_id`
- `workspace_id`
- `status`
- `message_count`
- `total_tokens`
- `summary`
- `focused_symbols`
- `last_activity_at`
- `created_at`
- `updated_at`

### `PUT /api/conversations/{conversation_id}`

- Accepts partial updates for `title` while the conversation is active.
- Rejects updates for `archived` conversations.
- Response fields match the conversation detail payload:
  - `conversation_id`
  - `thread_id`
  - `session_id`
  - `workspace_id`
  - `status`
  - `message_count`
  - `total_tokens`
  - `focused_symbols`
  - `last_activity_at`
  - `created_at`
  - `updated_at`

### `POST /api/conversations/{conversation_id}/archive`

Request body may include:

```json
{
  "archive_reason": "user_completed"
}
```

Behavior:

- Allowed from `active` or `summarized`.
- Records `archive_reason` and `archived_at`.
- Rejects future chat requests once archived.

### `GET /api/conversations/{conversation_id}/summary`

Response fields:

- `conversation_id`
- `session_id`
- `workspace_id`
- `status`
- `summary`
- `message_count`
- `total_tokens`
- `focused_symbols`
- `time_range`

### Nested parent mismatch rule

- If a nested conversation route is invoked with a `session_id` that does not match the conversation's stored parent `session_id`, the request is rejected using the same secure not-found/error envelope as out-of-hierarchy access.

## Public Contract Notes for Phase D and E

- Chat requests with `conversation_id` must cause metadata updates to become visible through `GET /api/conversations/{conversation_id}` within 5 seconds.
- Archived conversations must produce a conflict-style error envelope when targeted by chat.
- No reconciliation or migration endpoint is added to the public management API.