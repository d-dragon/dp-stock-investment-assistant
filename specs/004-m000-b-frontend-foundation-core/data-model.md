# Data Model: M-000 Frontend foundation core (delivery 1 of 2)

**Date**: 2026-11-17

**Spec**: `specs/004-m000-b-frontend-foundation-core/spec.md` — "Key Entities"

Entities below are the Frontend types and files this delivery introduces. They are not Backend collections. The shell store, zone host, and workspace URL state are B3 and are not modeled here.

Sources for the shapes: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts", "6.1 Typed REST client", "6.3 SSE client", and "8.3 i18n and locale seam"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette".

## Instruction set

The rules a coding session loads.

| Field | Rule |
|---|---|
| `frontend/AGENTS.md` | Exists, under 10,000 characters, states the target rules |
| Root `AGENTS.md` Frontend lines | Same target rules |
| `.github/instructions/frontend-react.instructions.md` | Same target rules, no drift |
| `CLAUDE.md`, `.claude/rules`, `.cursor/rules` | No recommendation of Create React App, Jest, `REACT_APP_*`, or Socket.IO |

Target rules: Vite and Vitest; `VITE_*` only; no `socket.io-client`, WebSocket, or `EventSource`; `fetch` only in `platform/api` and `platform/stream`; module folders `features/` and `platform/`; lint rules 1–3 as enabled in B1.

Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)".

Validation: `grok inspect` from `frontend/` lists the rules. A search of instruction files finds none of the retired recommendations. B0 has no test file.

## Generated API schema

| Field | Rule |
|---|---|
| Path | `frontend/src/platform/api/generated/schema.d.ts` |
| Producer | `openapi-typescript` reading `docs/openapi.yaml` |
| Hand edits | Not the source of truth |
| Drift | CI fails when the committed file differs from a fresh run |

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client"; ADR-FRONTEND-002 — "Decision".

This delivery's hand-written client may call only these operations. The generated file may still describe the rest of the contract.

| Operation | Path | In this delivery |
|---|---|---|
| `getHealth` | `GET /api/health` | Called |
| `getConfig` | `GET /api/config` | Called |
| `listOpenAIModels` | `GET /api/models/openai` | Called |
| `refreshOpenAIModels` | `POST /api/models/openai/refresh` | Called |
| `getSelectedModel` | `GET /api/models/openai/selected` | Called |
| `selectModel` | `POST /api/models/openai/select` | Called |
| `setDefaultModel` | `PUT /api/models/openai/default` | Called |
| `postChat` | `POST /api/chat` | Called, including `stream: true` |
| `/api/auth/*` | — | Not implemented |
| `GET /api/market/prices/{symbol}` | — | Not called and not mocked |

Source: `docs/openapi.yaml` — the paths above; `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints).

## Auth adapter

```ts
interface SessionInfo {
  userId: string
  displayName?: string
  expiresAt: string
}

interface AuthAdapter {
  getSession(): Promise<SessionInfo | null>
  csrfHeaders(): Record<string, string>
  signIn(ctx: { returnTo: string }): void
  signOut(): Promise<void>
  onUnauthorized(ctx: { returnTo: string }): Promise<void>
}
```

`NoAuthAdapter` in this delivery:

| Method | Result |
|---|---|
| `getSession` | `null` |
| `csrfHeaders` | empty |
| `signIn`, `signOut`, `onUnauthorized` | no-op |

Tests pass a fake adapter. No token is stored on `SessionInfo` in this delivery, and `NoAuthAdapter` never returns a session. Pitch A replaces the implementation behind the same interface.

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts" and "6.1 Typed REST client".

## ApiError

| Field | Rule |
|---|---|
| `status` | HTTP status, or `0` for a network failure |
| `code` | Backend error code when present, otherwise `http_<status>` or `network` |
| `message` | Safe to show. Never raw HTML |
| `retriable` | `true` for network, 429, and 502–504 |

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client".

Relationship: the client throws `ApiError` for every non-2xx response. Status 401 also calls `AuthAdapter.onUnauthorized` before or as part of that failure. `NoAuthAdapter.onUnauthorized` is a no-op, so the error still surfaces to the caller.

## sessionRef

| Field | Rule |
|---|---|
| `sessionId` | Opaque Backend session id |
| `conversationId` | Opaque Backend conversation id |

This delivery does not build the store that holds the pair. `ChatRequest.conversation_id` is the conversation id. `ChatRequest.session_id` is a deprecated alias for `conversation_id` and is not a place to put `sessionId`.

Source: SR-1.4.2; `docs/openapi.yaml` — `ChatRequest`; `specs/004-m000-b-frontend-foundation-core/spec.md` — "Key Entities".

Open: `[NEEDS CLARIFICATION]` in `research.md` R7 for how `sessionId` is sent on chat, if it is sent at all before the contract grows.

## Chat stream

### SseFrame

| Field | Rule |
|---|---|
| `id` | Optional. Kept. Today's contract does not send it |
| `event` | Optional. Kept |
| `retry` | Optional number. Kept |
| `data` | Dispatch payload. A line that is only a `:` comment does not dispatch |

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client".

### StreamEvent

| `type` | Payload | Today's frame |
|---|---|---|
| `meta` | `provider`, `model` | `data: {"event":"meta",...}` |
| `token` | `text` | `data: {"chunk":"..."}` |
| `final` | `provider`, `model`, `fallback` | `data: {"event":"done",...}` |
| `error` | `ApiError` | `data: {"error":...}` or a malformed frame |
| end of iterable | — | `data: [DONE]` |

`tool` and `citation` are not in this delivery.

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract" and "6.3 SSE client".

### StreamHandle

| Field | Rule |
|---|---|
| `events` | `AsyncIterable<StreamEvent>` |
| `abort()` | Aborts the reader |

`openChatStream(body, { signal?, idleTimeoutMs? })` returns that handle. `body` is the generated chat request type. `idleTimeoutMs` defaults from `VITE_STREAM_IDLE_TIMEOUT_MS` (`60000` in live mode).

### States used here

The companion reducer lives in B3. This delivery's stream client still uses these outcomes:

| State | Entry |
|---|---|
| `streaming` | Frames are arriving and being adapted |
| `interrupted` | Idle window elapsed with no further line. The draft and any partial message stay |
| `error` | Malformed frame or an `{"error"}` frame |
| ended | `[DONE]` or a normal completion (`final` then end) |

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client"; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix"; `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Idle timeout).

### Transitions

```text
openChatStream
  -> streaming
streaming + any received line, including ":" comments -> streaming (timer reset)
streaming + idle window with no line -> abort -> interrupted
streaming + [DONE] -> ended
streaming + {"error"} or malformed frame -> error
streaming + abort() or a second openChatStream in the tab -> previous reader aborted
```

Only one chat stream is open per tab.

Validation: MSW tests use `idleTimeoutMs` of `15000` with fake timers. A comment line is accepted and is not dispatched as `token` or `meta`. Silence past the window yields `interrupted`.

## Format result

Inputs may be `number`, or, for the missing-value rule, `null`, `undefined`, or `NaN`. The technical design signatures take `number`. The pitch edge cases widen the inputs. This model follows the edge cases.

| Function | Input example | Output | Mechanism |
|---|---|---|---|
| `fmt.price` | `25300` | `25.30` | Custom. Integer VND shown as thousands with a dot and two decimals |
| `fmt.change` | `1750` / `-450` / `0` | `+1.75` / `−0.45` / `0.00` | Custom. Minus is U+2212. Zero has no sign |
| `fmt.pct` | `0.0698` / `-0.0698` / `0` | `+6.98%` / `−6.98%` / `0.00%` | Custom. Same minus rule |
| `fmt.volume` | `1234500` / `0` | `1,234,500` / `0` | Custom. Whole shares. Not the price formatter |
| `fmt.vnd` | `25300000` | `25,300,000 ₫` | Custom. Whole VND, comma grouping, ` ₫` suffix |
| `fmt.dateTime` | `Date` or string | standard `vi-VN` `Intl` | `timeZone` default `Asia/Ho_Chi_Minh` |
| any `fmt.*` number | `null`, `undefined`, `NaN` | `—` | Accessible name key "Không có dữ liệu". Never `0`, never blank. Volume zero is not this row |

Property: across 1,000 random numeric outputs, the dot only marks a decimal and the comma only groups thousands.

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam"; `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-F1..F5 and P1..P4; `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy".

## Message catalogue

| Key meaning | vi-VN string | Shown through |
|---|---|---|
| Retry | Tạo lại | `t()` |
| Missing value | Không có dữ liệu | `t()`, as the accessible name of `—` |
| AI suggested | AI gợi ý | `t()` |
| Investor confirmed | Đã xác nhận | `t()` |

English catalogue: absent. Library: not chosen. Additional keys for `Delta` direction are `[NEEDS CLARIFICATION]` (`research.md` R15).

Source: ADR-FRONTEND-005 — "Decision"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance (`ai.*`)"; `specs/pitches/M-000-B-frontend-foundation.md` — "Agent constraints for every slice".

## Design tokens (dark column)

Generated CSS variables. Light column is not generated. `<html data-theme="dark">` is the theme hook.

Dark hex values copied from `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette". The variable-name shape for a two-part id follows the spec example `--market-up`. Three-part names are open (`research.md` R13).

| Token | Dark |
|---|---|
| `surface.bg` | `#0D1014` |
| `surface.card` | `#15191E` |
| `surface.text` | `#E6E8EB` |
| `surface.text2` | `#9AA3AE` |
| `surface.line` | `#2A313B` |
| `market.up` | `#2EBD6B` |
| `market.down` | `#F0524A` |
| `market.ref` | `#E8B931` |
| `market.ceiling` | `#C062F0` |
| `market.floor` | `#22B8D9` |
| `state.info` | `#8FB3E0` |
| `state.success` | `#6ACAA1` |
| `state.warn` | `#DFA045` |
| `state.danger` | `#F38275` |
| `state.streaming` | `#B8C2CF` |
| `accent` | `#D8CDBB` |
| `ai.suggested.edge` | `#9AA3AE` |
| `ai.suggested.label` | `#9AA3AE` |
| `ai.confirmed.edge` | `#E6E8EB` |
| `ai.confirmed.label` | `#E6E8EB` |

Not generated: light hexes; `track.a`; `track.b`; distinct values for `surface.z1`–`surface.z4` and `surface.overlay`.

Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.1 Surface and market / state (both themes)", "3.2 Track (`track.*`)", "3.3 Accent", and "3.6 Provenance (`ai.*`)"; ADR-FRONTEND-007 — "Decision".

### Who may read market and state colours

| Pattern | Reads | Does not |
|---|---|---|
| `PriceCell` | `market.up` `market.down` `market.ref` `market.ceiling` `market.floor` | Compute reference, ceiling, or floor |
| `Delta` | `market.up` `market.down` `market.ref` (zero) | Use colour without a sign or an arrow |
| `StatusBadge` | `state.*` | Omit the icon or the label |

`Delta` accessible name includes the direction. Zero change is `0.00` / `0.00%` with no sign and colour `market.ref`.

Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "8. Patterns"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules"; `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-T2, B4-T3, and P2.

## Relationships

```text
docs/openapi.yaml
  -> generated schema.d.ts
    -> platform/api client
      -> AuthAdapter (NoAuthAdapter in this delivery)
      -> ApiError

ChatRequest + sessionRef.conversationId
  -> openChatStream
    -> SseFrame
      -> legacyChatAdapter
        -> StreamEvent

VITE_STREAM_IDLE_TIMEOUT_MS
  -> idle timer on the open stream
    -> interrupted

DESIGN_SYSTEM §3 dark column
  -> generated CSS variables
    -> PriceCell / Delta / StatusBadge only, for market.* and state.*

vi-VN catalogue
  -> t()
    -> every user-facing string, including retry and missing-value

fmt.*
  -> IBM Plex Mono on screen
t() strings
  -> Be Vietnam Pro on screen
```

No entity in this delivery is a Backend document, a checkpointer payload, or a market-evidence record.
