# Contract: platform API client

**Slice**: B2, after the B1 toolchain exists

**Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client" and "3.4 Platform contracts"; ADR-FRONTEND-002 — "Decision"; ADR-SYS-001 — "Decision" and "Follow-ups"; `docs/openapi.yaml`; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-015, FR-016, FR-017.

## Codegen

| Item | Contract |
|---|---|
| Script | `npm run gen:api` from `frontend/` |
| Tool | `openapi-typescript` |
| Input | `docs/openapi.yaml` (read only; this delivery does not edit it) |
| Output | `src/platform/api/generated/schema.d.ts` |
| Commit | The generated file is committed |
| Drift | `npm run gen:api && git diff --exit-code src/platform/api/generated` passes on a clean tree. CI fails when it does not |

The HTTP client package that sits on top of the generated types is not selected. `openapi-fetch` remains Proposed. See `research.md` R5.

## Client behavior

One client module in `platform/api`.

| Rule | Detail |
|---|---|
| Base URL | `import.meta.env.VITE_API_BASE_URL`. Empty means same origin |
| Credentials | `credentials: 'same-origin'` on every request, including the chat stream |
| CSRF | `AuthAdapter.csrfHeaders()` on POST, PUT, PATCH, and DELETE |
| 401 | Call `onUnauthorized` |
| Forbidden headers | No `Authorization`. No `X-User-ID` |
| Secrets | No token in JavaScript, storage, or fixtures |
| Errors | Non-2xx becomes `ApiError` (`data-model.md`) |
| Scope | Health, config, `models/*`, and chat only |

`NoAuthAdapter` ships with this delivery. Tests construct a fake adapter. `/api/auth/*` is out of scope.

## MSW

Handlers in this delivery cover only paths already in `docs/openapi.yaml`, and only the health, config, `models/*`, and chat paths the client calls. `GET /api/market/prices/{symbol}` is not added.

## sessionRef on the wire

The TypeScript pair is `{sessionId, conversationId}`.

| Field | Wire |
|---|---|
| `conversationId` | `ChatRequest.conversation_id` when a conversation is in scope |
| `sessionId` | `[NEEDS CLARIFICATION]` (`research.md` R7). Do not write it to `ChatRequest.session_id`. That property is a deprecated alias for `conversation_id` (`docs/openapi.yaml` — `ChatRequest`) |

The shell store that retains the pair is B3 and is not part of this contract.
