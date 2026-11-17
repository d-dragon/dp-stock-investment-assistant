# Contract: chat stream

**Slice**: B2

**Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract" and "6.3 SSE client"; SR-5.1.2; SNR-8.1.2; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix"; `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints and Idle timeout); `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-018, FR-019, FR-020, FR-021.

## Entry

```ts
openChatStream(
  body: ChatRequest,
  opts?: { signal?: AbortSignal; idleTimeoutMs?: number },
): StreamHandle
```

`ChatRequest` is the generated type. The live call is `POST /api/chat` with `stream: true`, through the same `platform/api` fetch path, with `credentials: 'same-origin'`.

`EventSource` is forbidden. `fetch` for this reader lives in `platform/stream`.

The parser keeps WHATWG `id`, `event`, `retry`, and `data`. The parser package is not selected (`research.md` R8).

## Today's frames

The MSW fixture uses these frames from `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract":

```text
data: {"event":"meta","provider":"openai","model":"gpt-4"}
data: {"chunk":"AAPL "}
data: {"event":"done","fallback":false,"provider":"openai","model":"gpt-4"}
data: [DONE]
```

`legacyChatAdapter` maps them to `meta`, `token`, `final`, and end. An `{"error"}` object or a malformed frame becomes `error`. A line that starts with `:` is not a `StreamEvent`. Stream event names appear only in the `StreamEvent` union and the adapter. Lint enforces that.

## Idle timeout

| Mode | Value |
|---|---|
| Live | `VITE_STREAM_IDLE_TIMEOUT_MS`, default `60000`, not a source literal |
| MSW test | `15000`, fake timers |

Any received line, including a `:` comment, resets the timer. Timeout aborts the stream and moves it to `interrupted`. The user-facing retry label is the catalogue string "Tạo lại" via `t()`. The Z4 draft and any partial message stay as they are. `frontend/.env.example` documents the 60 s default as a stopgap.

## One stream

A second `openChatStream` in the same tab aborts the stream already open.

## Out of this contract

Backend response headers, `: ping` emission, HTTP/2, typed events, resume, and cancel. The client is proven against the MSW fixture only. SNR-8.1.2 for this delivery is "Frontend part verified" on that fixture.

## Removal

Absent after B2: `socket.io-client`, `@types/socket.io-client`, `webSocketService.ts`, `API_CONFIG.WEBSOCKET`. A `no-restricted-imports` rule stops the client returning. `rg socket.io dist` returns nothing.

Source for the removal set: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.4 Socket.IO removal".
