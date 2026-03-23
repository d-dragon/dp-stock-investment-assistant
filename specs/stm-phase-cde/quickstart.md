# Quickstart: Validate STM Phase C-E

## Goal

Use this guide after implementation work begins to verify that Phase C, D, and E behaviors match the plan and clarified spec without requiring frontend changes.

## 1. Start dependencies

```powershell
docker-compose up -d mongodb redis
python src\data\migration\db_setup.py
python src\main.py --mode web
```

## 2. Smoke-test management API

### Create a workspace

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/workspaces -ContentType application/json -Body '{"name":"Growth watchlist","description":"Phase C smoke test"}'
```

Expected:

- Response contains `workspace_id`, `status=active`, timestamps.

### Create a session

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/workspaces/{workspace_id}/sessions -ContentType application/json -Body '{"title":"Q2 review","focused_symbols":["MSFT","NVDA"]}'
```

Expected:

- Response contains `session_id`, `workspace_id`, `status=active`.

### Create a conversation

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/sessions/{session_id}/conversations -ContentType application/json -Body '{"title":"Scenario run","context_overrides":{"conversation_intent":"stress case"}}'
```

Expected:

- Response contains `conversation_id`, `thread_id`, `session_id`, `workspace_id`, `status=active`.

### Validate list pagination

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:5000/api/sessions/{session_id}/conversations?limit=25&offset=0"
```

Expected:

- Response contains `items`, `total`, `limit`, `offset`.

### Verify management API latency budgets

```powershell
python -m pytest tests/performance/test_management_api_latency.py -v
```

Expected:

- Single-resource GET requests stay below `200ms` P95.
- List requests stay below `500ms` P95.
- Create, update, and archive requests stay below `500ms` P95.
- Parent-triggered cascade archive completes below `2s` P95.

## 3. Validate lifecycle behavior

### Close the session

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/sessions/{session_id}/close
```

Expected:

- Existing non-archived conversations remain readable and chat-capable.
- Creating a new conversation under the closed session is rejected.
- Updating session context is rejected.

### Archive the session or workspace

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/sessions/{session_id}/archive
```

Expected:

- Child conversations are archived.
- Chat to archived conversation is rejected.

## 4. Validate runtime metadata consistency

### Send a chat request with conversation context

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/chat -ContentType application/json -Body '{"message":"Compare MSFT and NVDA cloud exposure","conversation_id":"{conversation_id}"}'
```

Within 5 seconds, verify:

```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:5000/api/conversations/{conversation_id}
```

Expected:

- `message_count` increased for accepted user and assistant turns.
- `total_tokens` increased.
- `last_activity_at` updated.
- `focused_symbols` retains previous symbols and adds new detected symbols.

## 5. Validate reconciliation tooling

### Run on-demand scan

```powershell
python scripts/reconcile_stm_runtime.py --mode on-demand --format json --output reports/reconciliation/latest.json
```

Expected:

- JSON report produced.
- Structured log entries include `correlation_id`, timestamps, and scan actions.
- No public `/api` route is required.

## 6. Validate migration tooling

### Dry-run

```powershell
python scripts/migrate_legacy_threads.py --dry-run
```

Expected:

- Planned create/skip counts returned.
- No writes performed.

### Resume-capable execution

```powershell
python scripts/migrate_legacy_threads.py --resume --output reports/migration/latest.json
```

Expected:

- Already-migrated items skipped.
- Remaining legacy items promoted.
- Post-migration reconciliation is clean before closing the migration window.

## 7. Run regression tests

```powershell
python -m pytest tests/test_workspace_service.py tests/test_session_service.py tests/test_conversation_service.py tests/test_chat_service.py -v
python -m pytest tests/integration/test_management_api_contracts.py tests/integration/test_stm_runtime_wiring.py tests/integration/test_memory_persistence.py -v
python -m pytest tests/security/test_operator_tooling_boundaries.py -v
```

Add performance and coverage checks when implemented:

```powershell
python -m pytest tests/performance/test_reconciliation_impact.py -v
python -m pytest tests/performance/test_management_api_latency.py -v
python -m pytest --cov=src --cov-report=term-missing
```

Expected:

- Hierarchy, lifecycle, STM isolation, consistency, migration, and operator-boundary tests all pass.
- Management API latency checks satisfy the SC-005 thresholds.
- Agent-core coverage baseline does not regress.