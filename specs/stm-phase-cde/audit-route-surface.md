# T002 – Route Surface Audit: Code vs OpenAPI Spec

**Date**: 2026-03-23
**Source Code**: `src/web/api_server.py` + route files
**Contract**: `docs/openapi.yaml` (v1.3.0)

---

## 1. Registered Routes (Code)

All blueprints are registered with `url_prefix="/api"` in `api_server.py:152`.

| # | Method | Path | Blueprint | Route File |
|---|--------|------|-----------|------------|
| 1 | GET | `/api/health` | health | `service_health_routes.py` |
| 2 | POST | `/api/chat` | chat | `ai_chat_routes.py` |
| 3 | GET | `/api/config` | chat | `ai_chat_routes.py` |
| 4 | GET | `/api/models/openai` | models | `models_routes.py` |
| 5 | POST | `/api/models/openai/refresh` | models | `models_routes.py` |
| 6 | GET | `/api/models/openai/selected` | models | `models_routes.py` |
| 7 | POST | `/api/models/openai/select` | models | `models_routes.py` |
| 8 | PUT | `/api/models/openai/default` | models | `models_routes.py` |
| 9 | GET | `/api/users` | users | `user_routes.py` |
| 10 | POST | `/api/users` | users | `user_routes.py` |
| 11 | PATCH | `/api/users/<user_id>/profile` | users | `user_routes.py` |

**Total registered: 11 routes**

---

## 2. Documented Routes (OpenAPI)

| # | Method | Path | Tags |
|---|--------|------|------|
| 1 | GET | `/api/health` | Health |
| 2 | POST | `/api/chat` | Chat |
| 3 | GET | `/api/sessions/{session_id}/conversation` | Sessions |
| 4 | GET | `/api/config` | Config |
| 5 | GET | `/api/users` | Users |
| 6 | POST | `/api/users` | Users |
| 7 | PATCH | `/api/users/{userId}/profile` | Users |
| 8 | GET | `/api/models/openai` | Models |
| 9 | POST | `/api/models/openai/refresh` | Models |
| 10 | GET | `/api/models/openai/selected` | Models |
| 11 | POST | `/api/models/openai/select` | Models |
| 12 | PUT | `/api/models/openai/default` | Models |

**Total documented: 12 paths**

---

## 3. Drift Summary

### 3.1 Ghost Route – documented but NOT implemented

| Path | Status |
|------|--------|
| `GET /api/sessions/{session_id}/conversation` | **GHOST** – fully documented with schemas (`ConversationHistory`, `ConversationStatus`), examples, 200/400/404/500 responses, and a dedicated `Sessions` tag, but **no route handler exists anywhere in the codebase**. No blueprint registers this path. |

This route was added to the spec in v1.3.0 changelog as part of FR-3.1 session-aware short-term memory, but the implementation was never completed.

### 3.2 Naming Drift – `session_id` (spec) vs `conversation_id` (code)

The OpenAPI spec and the actual code use **different field names** for the same concept:

| Aspect | OpenAPI Spec | Code (`ai_chat_routes.py`) |
|--------|-------------|---------------------------|
| Chat request field | `session_id` | `conversation_id` |
| 400 error message | `"Invalid session_id format. Must be a valid UUID v4."` | `"conversation_id must be a valid UUID v4"` |
| Chat response echo field | `session_id` | `conversation_id` |

### 3.3 Error Response Shape Drift – 409 Archived Session

| Field | OpenAPI Spec | Code |
|-------|-------------|------|
| `error` | `"SESSION_ARCHIVED"` | `"Conversation is archived and cannot accept new messages"` |
| Status code key | _(not present)_ | `code: "CONVERSATION_ARCHIVED"` |
| ID field | `session_id` | `conversation_id` |
| Archived timestamp | `archived_at: "2025-09-16T12:30:00Z"` | _(not present)_ |

### 3.4 Matched Routes (no drift)

The remaining 10 routes (excluding the ghost) are present in both code and spec with matching methods and paths:

- `GET /api/health` ✓
- `POST /api/chat` ✓ (field naming drift noted above)
- `GET /api/config` ✓
- `GET /api/models/openai` ✓
- `POST /api/models/openai/refresh` ✓
- `GET /api/models/openai/selected` ✓
- `POST /api/models/openai/select` ✓
- `PUT /api/models/openai/default` ✓
- `GET /api/users` ✓
- `POST /api/users` ✓
- `PATCH /api/users/{userId}/profile` ✓

---

## 4. Action Items (for T008)

1. **Remove or implement** `GET /api/sessions/{session_id}/conversation`
   - If Phase C-E will implement this endpoint → keep in spec, implement route
   - If deferred → remove from spec to avoid ghost documentation
2. **Reconcile naming**: Choose `session_id` or `conversation_id` and align both spec and code
3. **Fix 409 error shape**: Align the `ArchivedConversationError` response between spec and code
4. **Remove orphaned schemas** if ghost route is removed: `ConversationHistory`, `ConversationStatus`, `SessionArchivedError`
