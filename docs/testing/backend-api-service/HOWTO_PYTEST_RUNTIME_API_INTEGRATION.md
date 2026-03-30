# How To Use pytest For Full Runtime API Integration In This Repository

Date: 2026-03-30

## 1. Purpose

This guide explains how to use `pytest` in this repository for full runtime REST API integration testing against live infrastructure.

The goal is not to replace the repository's existing fast mocked test layers. The goal is to add a clearly separated runtime layer that:

1. Runs against real MongoDB and Redis
2. Calls the real HTTP API instead of Flask `test_client()`
3. Uses the real `APIServer` startup path
4. Seeds and cleans test data predictably
5. Verifies both HTTP behavior and persisted state
6. Produces practical reports for local development and CI

> [!IMPORTANT]
> In this repository, `pytest` is the best fit when you need full integration testing of live REST API behavior with real MongoDB, Redis, and service wiring. `Schemathesis` and `Newman` remain complementary layers, not replacements for this role.

## 2. Where pytest Fits In The Testing Stack

Use each tool for a different job.

Use `pytest` for:

1. Full runtime integration against live MongoDB and Redis
2. Multi-step lifecycle and ownership flows
3. Persistence verification in storage
4. Restart-sensitive and checkpointer-sensitive behavior
5. Targeted runtime performance assertions

Use `Schemathesis` for:

1. OpenAPI conformance
2. Negative-case exploration
3. Broad contract coverage against a running API

Use `Newman` or Bruno for:

1. Collection-driven smoke checks
2. Curated black-box workflows
3. Team-friendly operator or Postman-style validation

This split is consistent with [docs/testing/HOWTO_SCHEMATHESIS_NEWMAN_ADOPTION.md](docs/testing/HOWTO_SCHEMATHESIS_NEWMAN_ADOPTION.md#L31-L53).

## 3. What Counts As "Runtime Integration" Here

In this repository, "runtime integration" means:

1. Start real infrastructure with Docker
2. Start the real API process through [src/main.py](src/main.py#L1-L88)
3. Send HTTP requests to `http://localhost:5000`
4. Inspect MongoDB and Redis directly where needed
5. Assert lifecycle, ownership, persistence, and caching behavior

This is different from several existing tests under `tests/integration/`, which are still valuable but often build a Flask app in-process and inject mocks. For example:

1. [tests/integration/test_management_api_contracts.py](tests/integration/test_management_api_contracts.py#L60-L107)
2. [tests/integration/test_stm_runtime_wiring.py](tests/integration/test_stm_runtime_wiring.py#L220-L360)

Those tests are authored integration tests. They are not the same as full live-stack runtime API integration.

## 4. Existing Project Evidence

This repository already has the pieces needed for a runtime `pytest` layer:

1. `pytest` is the main Python test runner in [pytest.ini](pytest.ini#L1-L6)
2. Shared test fixtures exist in [tests/conftest.py](tests/conftest.py#L1-L28)
3. The local backend startup flow is already documented in [QUICK_START.md](QUICK_START.md#L24-L50) and [specs/stm-phase-cde/quickstart.md](specs/stm-phase-cde/quickstart.md#L7-L12)
4. MongoDB schema bootstrap exists in [src/data/migration/db_setup.py](src/data/migration/db_setup.py#L1-L105)
5. App config can be driven by environment variables via [src/utils/config_loader.py](src/utils/config_loader.py#L95-L178)
6. Redis cache key patterns are explicit in [src/data/repositories/redis_cache_repository.py](src/data/repositories/redis_cache_repository.py#L42-L209)
7. The real API server startup path is in [src/web/api_server.py](src/web/api_server.py#L57-L161)

## 5. Recommended Repository Layout

Keep the runtime suite clearly separate from mocked integration tests.

Recommended structure:

1. `tests/runtime_api/`
2. `tests/runtime_api/conftest.py`
3. `tests/runtime_api/test_health_runtime.py`
4. `tests/runtime_api/test_management_lifecycle_runtime.py`
5. `tests/runtime_api/test_chat_runtime.py`
6. `tests/runtime_api/test_persistence_runtime.py`
7. `tests/runtime_api/test_cache_runtime.py`
8. `reports/pytest/`

Design rule:

1. `tests/integration/` stays for fast authored integration tests with in-process app construction or mocks
2. `tests/runtime_api/` is reserved for live HTTP tests against a running stack

## 6. Local Runtime Test Environment

### 6.1 Install Dependencies

Use the project virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The repository already includes `httpx` in [requirements.txt](requirements.txt#L1-L41), which is suitable for runtime HTTP tests.

### 6.2 Start MongoDB And Redis

Use Docker Compose:

```powershell
docker-compose up -d mongodb redis
```

The local Docker services are defined in [docker-compose.yml](docker-compose.yml#L1-L54).

### 6.3 Use Test-Specific Database Targets

Do not point runtime tests at your normal development database or shared Redis data.

Recommended isolation:

1. A dedicated Mongo database name such as `stock_assistant_test`
2. A dedicated Redis logical DB such as `15`
3. Optional unique per-run names for CI or parallel execution

Example PowerShell environment setup:

```powershell
$env:MONGODB_URI = "mongodb://stockadmin:stockpassword@localhost:27017"
$env:MONGODB_DB_NAME = "stock_assistant_test"
$env:REDIS_ENABLED = "true"
$env:REDIS_HOST = "localhost"
$env:REDIS_PORT = "6379"
$env:REDIS_DB = "15"
$env:REDIS_PASSWORD = "redispassword"
```

These values are consumed by the config overlay behavior in [src/utils/config_loader.py](src/utils/config_loader.py#L95-L178).

### 6.4 Initialize Schema

Run schema setup against the test database before runtime tests:

```powershell
python src\data\migration\db_setup.py --db stock_assistant_test
```

If you need to reset STM collections only:

```powershell
python src\data\migration\db_setup.py --db stock_assistant_test --clean-slate
```

The clean-slate behavior is implemented in [src/data/migration/db_setup.py](src/data/migration/db_setup.py#L14-L76).

### 6.5 Start The Real API

Start the real web server:

```powershell
python src\main.py --mode web --host 0.0.0.0 --port 5000
```

That path creates the real `APIServer`, loads config, initializes repositories and services, and wires the agent and checkpointer through [src/main.py](src/main.py#L34-L88) and [src/web/api_server.py](src/web/api_server.py#L57-L161).

### 6.6 Verify Health

Before the test run:

```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:5000/api/health
```

## 7. Data Management Strategy During The Full Test Cycle

Runtime integration fails quickly if test data is unmanaged. Use `pytest` fixtures to control the full data lifecycle.

Recommended lifecycle:

1. Initialize isolated MongoDB and Redis targets
2. Apply schema bootstrap once per test session
3. Seed minimum baseline data per test or per module
4. Execute API flows through real HTTP
5. Assert storage state directly when needed
6. Clean Mongo collections and Redis data after each test
7. Drop the test database at the end of the test session if appropriate

### 7.1 What To Seed Through HTTP vs Direct Storage

Seed through HTTP when:

1. The setup itself is part of the business contract
2. You want the route, service, and persistence layers all exercised
3. The setup flow is short and stable

Seed directly in MongoDB or Redis when:

1. You need a special state that is awkward to create through public APIs
2. You need archived, stale, or edge-case fixtures quickly
3. You are preparing cache state or checkpoint state

Recommended default:

1. Seed workspaces, sessions, and conversations through HTTP
2. Seed internal cache or abnormal state directly in storage only when justified

### 7.2 MongoDB Data Ownership

Use MongoDB for:

1. Durable seeded entities
2. Post-request verification of persisted documents
3. Cleanup of test-created business data

Typical collections involved here include:

1. `workspaces`
2. `sessions`
3. `conversations`
4. `agent_checkpoints`

The STM setup script already treats `sessions`, `conversations`, and `agent_checkpoints` as resettable migration collections in [src/data/migration/db_setup.py](src/data/migration/db_setup.py#L24-L38).

### 7.3 Redis Data Ownership

Use Redis for:

1. Cache warmup scenarios
2. Cache verification after API calls
3. Cleanup of ephemeral state between tests

Existing key patterns in this codebase include:

1. `stock:price:{symbol}`
2. `stock:history:{symbol}:{period}`
3. `analysis:fundamental:{symbol}`
4. `report:{symbol}:{report_type}`
5. `model:supported:{provider}`
6. `model:active:{provider}`

These patterns are implemented in [src/data/repositories/redis_cache_repository.py](src/data/repositories/redis_cache_repository.py#L57-L209).

## 8. Recommended Runtime Fixtures

Use fixtures for infrastructure handles, seeded data, and cleanup.

Recommended fixtures:

1. `base_url`
2. `management_headers`
3. `live_http_client`
4. `mongo_client`
5. `mongo_db`
6. `redis_client`
7. `wait_for_api`
8. `reset_live_state`
9. `seeded_workspace`
10. `seeded_session`
11. `seeded_conversation`

Recommended scopes:

1. Session scope for infrastructure clients and base config
2. Function scope for mutable seeded entities
3. Function scope for cleanup unless you deliberately optimize for slower end-to-end suites

## 9. Example `conftest.py` For Runtime Tests

The example below is intentionally practical rather than abstract.

```python
import os
import time
import uuid

import httpx
import pytest
import redis
from pymongo import MongoClient


TEST_DB_NAME = os.getenv("TEST_MONGODB_DB_NAME", f"stock_assistant_test_{uuid.uuid4().hex[:8]}")
TEST_REDIS_DB = int(os.getenv("TEST_REDIS_DB", "15"))


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("TEST_BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def management_headers():
    return {"X-User-ID": "693688b61af03340512889ea"}


@pytest.fixture(scope="session")
def mongo_client():
    uri = os.getenv("TEST_MONGODB_URI", "mongodb://stockadmin:stockpassword@localhost:27017")
    client = MongoClient(uri)
    yield client
    client.close()


@pytest.fixture(scope="session")
def mongo_db(mongo_client):
    db = mongo_client[TEST_DB_NAME]
    yield db
    mongo_client.drop_database(TEST_DB_NAME)


@pytest.fixture(scope="session")
def redis_client():
    client = redis.Redis(
        host=os.getenv("TEST_REDIS_HOST", "localhost"),
        port=int(os.getenv("TEST_REDIS_PORT", "6379")),
        db=TEST_REDIS_DB,
        password=os.getenv("TEST_REDIS_PASSWORD", "redispassword"),
        decode_responses=True,
    )
    client.flushdb()
    yield client
    client.flushdb()
    client.close()


@pytest.fixture(scope="session", autouse=True)
def wait_for_api(base_url):
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            response = httpx.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("Live API did not become healthy in time")


@pytest.fixture(autouse=True)
def reset_live_state(mongo_db, redis_client):
    for collection_name in ("workspaces", "sessions", "conversations", "agent_checkpoints"):
        mongo_db[collection_name].delete_many({})
    redis_client.flushdb()
    yield
```

This fixture model does four important things:

1. Uses dedicated test storage
2. Waits for the real HTTP API instead of assuming startup
3. Resets mutable state before each test
4. Drops the whole test MongoDB database at the end

## 10. Example: Seed Through The Real API

This is the preferred default for business entities.

```python
import httpx


def test_workspace_session_conversation_lifecycle_runtime(base_url, management_headers):
    with httpx.Client(base_url=base_url, headers=management_headers, timeout=10) as client:
        workspace = client.post(
            "/api/workspaces",
            json={"name": "Runtime workspace", "description": "pytest runtime"},
        )
        assert workspace.status_code in (200, 201)
        workspace_id = workspace.json()["workspace_id"]

        session = client.post(
            f"/api/workspaces/{workspace_id}/sessions",
            json={"title": "Runtime session"},
        )
        assert session.status_code in (200, 201)
        session_id = session.json()["session_id"]

        conversation = client.post(f"/api/sessions/{session_id}/conversations", json={})
        assert conversation.status_code in (200, 201)
        conversation_id = conversation.json()["conversation_id"]

        detail = client.get(f"/api/conversations/{conversation_id}")
        assert detail.status_code == 200
        assert detail.json()["conversation_id"] == conversation_id
```

## 11. Example: Verify Persistence Directly In MongoDB

Runtime integration should verify storage directly when storage state matters.

```python
def test_workspace_is_persisted_in_mongodb(base_url, management_headers, mongo_db):
    import httpx

    with httpx.Client(base_url=base_url, headers=management_headers, timeout=10) as client:
        response = client.post(
            "/api/workspaces",
            json={"name": "Persisted Workspace", "description": "storage assertion"},
        )
        assert response.status_code in (200, 201)
        workspace_id = response.json()["workspace_id"]

    stored = mongo_db["workspaces"].find_one({"workspace_id": workspace_id})
    assert stored is not None
    assert stored["name"] == "Persisted Workspace"
    assert stored["user_id"] == management_headers["X-User-ID"]
```

## 12. Example: Verify Cache Behavior In Redis

Use direct Redis verification only where the cache itself is part of the runtime contract.

```python
def test_active_model_cache_is_written(redis_client):
    redis_client.set(
        "model:active:openai",
        '{"model":"gpt-4","updated_at":"2026-03-30T10:00:00Z"}'
    )

    payload = redis_client.get("model:active:openai")
    assert payload is not None
    assert '"model":"gpt-4"' in payload
```

For repo-specific cache scenarios, prefer using the actual API route or service behavior that writes the key, then verify the resulting key.

## 13. Ownership And Lifecycle Assertions

Runtime `pytest` is the right place to validate:

1. `X-User-ID` ownership rules
2. Parent-child hierarchy constraints across workspace, session, and conversation
3. Session close and archive behavior
4. Conversation archive behavior
5. Idempotent archive semantics where applicable

The management flow and expected headers are already documented in [specs/stm-phase-cde/quickstart.md](specs/stm-phase-cde/quickstart.md#L13-L132).

Recommended pattern:

1. Create entities as user A
2. Access them as user B
3. Assert the expected `403`, `404`, or error envelope
4. Read storage if you need to prove no mutation occurred

## 14. Chat And Checkpointer Scenarios

Use runtime `pytest` when you need to validate:

1. `/api/chat` against the live API process
2. `conversation_id` reuse across multiple turns
3. Metadata persistence after chat
4. Checkpointer-sensitive state in MongoDB

Be selective here. Provider-sensitive tests may be slower or less deterministic than management API tests.

Recommended split:

1. Keep a minimal runtime chat suite in normal development
2. Keep provider-heavy scenarios in explicitly selected suites or CI jobs

## 15. Marker Strategy

Add explicit markers for runtime suites so they do not get mixed with fast local feedback loops.

Recommended markers:

1. `runtime_api`
2. `live_infra`
3. `seeded_state`

Example `pytest.ini` extension:

```ini
[pytest]
markers =
    performance: marks tests as performance benchmarks (deselect with '-m "not performance"')
    runtime_api: marks tests that call the real running HTTP API
    live_infra: marks tests that require live MongoDB and Redis
    seeded_state: marks tests that seed or inspect persistent storage
```

## 16. Commands For Local Development

Recommended local setup:

```powershell
.\.venv\Scripts\Activate.ps1
docker-compose up -d mongodb redis
$env:MONGODB_URI = "mongodb://stockadmin:stockpassword@localhost:27017"
$env:MONGODB_DB_NAME = "stock_assistant_test"
$env:REDIS_ENABLED = "true"
$env:REDIS_HOST = "localhost"
$env:REDIS_PORT = "6379"
$env:REDIS_DB = "15"
$env:REDIS_PASSWORD = "redispassword"
python src\data\migration\db_setup.py --db stock_assistant_test
python src\main.py --mode web --host 0.0.0.0 --port 5000
```

Run the runtime suite:

```powershell
python -m pytest tests/runtime_api -v -m "runtime_api and live_infra"
```

Run a single test:

```powershell
python -m pytest tests/runtime_api/test_management_lifecycle_runtime.py::test_workspace_session_conversation_lifecycle_runtime -v -s
```

Run runtime tests but exclude performance:

```powershell
python -m pytest tests/runtime_api -v -m "runtime_api and not performance"
```

## 17. Test Reports During Development

Use light reports during day-to-day work and richer artifacts only when needed.

Recommended local reporting:

1. Terminal output for ordinary iteration
2. JUnit XML when you want a CI-style result file
3. Coverage terminal and HTML reports for deeper checks

Recommended report location:

1. `reports/pytest/junit.xml`
2. `reports/pytest/coverage.xml`
3. `reports/pytest/htmlcov/`

Example commands:

```powershell
python -m pytest tests/runtime_api -q --tb=short

python -m pytest tests/runtime_api `
  --junitxml=reports/pytest/junit.xml `
  --cov=src `
  --cov-report=term-missing `
  --cov-report=xml:reports/pytest/coverage.xml `
  --cov-report=html:reports/pytest/htmlcov
```

Recommended management rule:

1. Commit the report configuration, not the generated report artifacts
2. Overwrite reports on each run instead of accumulating timestamped clutter by default
3. Keep runtime reports separate from Newman or other tool outputs

## 18. CI Pattern

Recommended CI sequence:

1. Install Python dependencies
2. Start MongoDB and Redis
3. Set test-specific env vars
4. Run schema bootstrap against the test DB
5. Start the API server
6. Wait for `/api/health`
7. Run runtime `pytest` suite
8. Publish JUnit and coverage artifacts

Example GitHub Actions shape:

```yaml
name: Runtime API Integration Tests

on:
  pull_request:
  push:
    branches: [main, stm-phase-cde]

jobs:
  runtime-api-tests:
    runs-on: ubuntu-latest

    services:
      mongodb:
        image: mongo:5
        ports:
          - 27017:27017
      redis:
        image: redis:6.2
        ports:
          - 6379:6379

    env:
      MONGODB_URI: mongodb://localhost:27017
      MONGODB_DB_NAME: stock_assistant_test_ci
      REDIS_ENABLED: "true"
      REDIS_HOST: localhost
      REDIS_PORT: "6379"
      REDIS_DB: "15"

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Prepare schema
        run: python src/data/migration/db_setup.py --db stock_assistant_test_ci

      - name: Start API
        run: |
          nohup python src/main.py --mode web --host 0.0.0.0 --port 5000 > api.log 2>&1 &
          sleep 10

      - name: Wait for health
        run: |
          for i in {1..30}; do
            curl -fsS http://localhost:5000/api/health && exit 0
            sleep 2
          done
          cat api.log
          exit 1

      - name: Run runtime API suite
        run: |
          python -m pytest tests/runtime_api \
            --junitxml=reports/pytest/junit.xml \
            --cov=src \
            --cov-report=xml:reports/pytest/coverage.xml \
            -m "runtime_api and live_infra" -v
```

## 19. Common Mistakes

Avoid these mistakes:

1. Using the normal development MongoDB database for runtime tests
2. Sharing Redis DB `0` with normal local development traffic
3. Calling Flask `test_client()` and treating that as full runtime integration
4. Seeding business entities manually outside the test suite
5. Leaving cleanup to human discipline after failed runs
6. Running provider-sensitive chat tests in every fast local loop
7. Mixing runtime reports with unrelated tool artifacts

## 20. Recommended First Scope

Start with a narrow but valuable runtime suite:

1. `GET /api/health`
2. Create workspace
3. Create session
4. Create conversation
5. Get conversation detail
6. Archive conversation
7. Verify persisted state in MongoDB
8. Verify no stale Redis state leaks across tests

After that, add:

1. Cross-user ownership denial cases
2. Session close and archive lifecycle checks
3. Chat with `conversation_id` reuse
4. Selected runtime performance checks

## 21. Decision Summary

For this repository:

1. Use `pytest` as the primary tool for full live-stack REST API integration
2. Keep `Schemathesis` as the contract and negative-case layer
3. Keep `Newman` or Bruno as smoke and workflow layers
4. Separate `tests/runtime_api/` clearly from mocked or in-process test suites
5. Use fixtures to manage MongoDB and Redis initialization, seeding, cleanup, and report generation

That gives you a practical testing model instead of forcing one tool to cover incompatible responsibilities.
