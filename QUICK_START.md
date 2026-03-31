# Quick Start: Local Setup and API Verification

## Goal

Use this guide to start the backend locally, verify configuration loading, and smoke-test the current API surface with copy-paste-ready PowerShell commands.

## 1. Prepare the environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
Copy-Item config\config_example.yaml config\config.yaml
```

Update `.env` and `config\config.yaml` with real local values before running the application.

Current configuration sources load in this order:

1. `config/config.yaml`
2. `config/config.{APP_ENV}.yaml`
3. Environment variables and `.env`

Minimum local values to review in `.env`:

```dotenv
OPENAI_API_KEY=your-openai-api-key-here
GROK_API_KEY=your-grok-api-key-here
MONGODB_URI=mongodb://username:password@hostname:port/stock_assistant?retryWrites=true&w=majority
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
APP_ENV=local
MODEL_PROVIDER=openai
```

## 2. Start local dependencies

```powershell
docker-compose up -d mongodb redis
python src\data\migration\db_setup.py
```

If Docker is not already running, start it before the commands above.

## 3. Verify configuration and core wiring

### Configuration sanity check

```powershell
python examples\config_usage.py
```

Expected:

- Configuration loads without throwing.
- Sensitive values are masked in output.
- Model and logging settings are shown from the merged config.

### System health check

```powershell
python scripts\health_check.py
```

Expected:

- The script completes with `ALL CHECKS PASSED`.
- API server instantiation succeeds or reports a non-fatal warning with context.

### Tool wiring test

```powershell
python -m pytest tests/test_tools.py -v
```

Expected:

- Tool registry and tool implementations load through the test suite.

### Optional agent script

```powershell
python test_agent.py
```

Use this only after model credentials and dependencies are configured. It exercises a direct agent query path rather than the HTTP API.

## 4. Start the API server

```powershell
python src\main.py --mode web --host 0.0.0.0 --port 5000
```

Server startup is complete when the console prints the API and WebSocket endpoints.

## 5. Smoke-test public API routes

### Set base URL

```powershell
$baseUrl = "http://localhost:5000"
```

### Health check

```powershell
Invoke-RestMethod -Method Get -Uri "$baseUrl/api/health"
```

Expected:

- Response contains `status: healthy`.
- Response also includes a human-readable `message`.

### Non-streaming chat

```powershell
Invoke-RestMethod -Method Post -Uri "$baseUrl/api/chat" -ContentType application/json -Body '{"message":"What is the current price of AAPL?"}'
```

Expected:

- HTTP 200 response.
- JSON payload with the assistant reply.

### Streaming chat

The current implementation uses the same `/api/chat` route for streaming. Set `stream` to `true` and use `curl.exe` to keep the SSE response open.

```powershell
curl.exe -N -X POST "$baseUrl/api/chat" -H "Content-Type: application/json" -d '{"message":"Summarize recent news about AAPL","stream":true}'
```

Expected:

- Server responds as `text/event-stream`.
- Chunks arrive incrementally until completion.

## 6. Smoke-test management API routes

Management workspace, session, and conversation routes require `X-User-ID`. Workspace creation currently validates this header as a Mongo ObjectId-style string.

### Set required auth header

```powershell
$headers = @{
    "X-User-ID" = "693688b61af03340512889ea"
}
```

### Create a workspace and capture `workspace_id`

```powershell
$workspace = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/workspaces" -Headers $headers -ContentType application/json -Body '{"name":"Growth watchlist","description":"Quick start smoke test"}'
$workspaceId = $workspace.workspace_id
$workspace
```

Expected:

- Response contains `workspace_id`, `status`, and timestamps.

### List workspaces

```powershell
Invoke-RestMethod -Method Get -Uri "$baseUrl/api/workspaces?limit=25&offset=0" -Headers $headers
```

Expected:

- Response contains `items`, `total`, `limit`, and `offset`.

### Create a session and capture `session_id`

```powershell
$session = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/workspaces/$workspaceId/sessions" -Headers $headers -ContentType application/json -Body '{"title":"Q2 review"}'
$sessionId = $session.session_id
$session
```

### Create a conversation and capture `conversation_id`

```powershell
$conversation = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/sessions/$sessionId/conversations" -Headers $headers -ContentType application/json -Body '{}'
$conversationId = $conversation.conversation_id
$conversation
```

### Retrieve conversation summary

```powershell
Invoke-RestMethod -Method Get -Uri "$baseUrl/api/conversations/$conversationId/summary" -Headers $headers
```

Expected:

- Response contains `message_count`, `total_tokens`, `duration_seconds`, `status`, `created_at`, and `last_activity_at`.

## 7. Run focused automated checks

### Core management and chat tests

```powershell
python -m pytest tests/test_workspace_service.py tests/test_session_service.py tests/test_conversation_service.py tests/test_chat_service.py -v
python -m pytest tests/integration/test_management_api_contracts.py -v
```

### Performance-marked tests

```powershell
python -m pytest tests/performance/test_management_api_latency.py tests/performance/test_reconciliation_impact.py -m performance -q
```

### Coverage snapshot

```powershell
python -m pytest tests/ --cov=src --cov-fail-under=56 -q
```

## 8. Common corrections from older docs

- Use `python scripts\health_check.py`, not `python health_check.py`.
- Use `python -m pytest tests/test_tools.py -v`, not `python test_tools.py`.
- There is no separate `/api/chat/stream` route. Streaming uses `POST /api/chat` with `"stream": true`.
- Do not paste live API keys or partial secrets into documentation or logs.

## 9. Next steps

1. Start the frontend from [frontend/README.md](/g:/00_Work/Projects/dp-stock-investment-assistant/frontend/README.md) after the backend is healthy.
2. Use the STM validation runbook in [specs/stm-phase-cde/quickstart.md](/g:/00_Work/Projects/dp-stock-investment-assistant/specs/stm-phase-cde/quickstart.md) for deeper lifecycle, reconciliation, and migration checks.
3. Review the API surface in [docs/openapi.yaml](/g:/00_Work/Projects/dp-stock-investment-assistant/docs/openapi.yaml) if you need request and response details.
