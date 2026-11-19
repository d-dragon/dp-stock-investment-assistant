# SNR-8.1.2 — Frontend part verified

**Status**: Frontend part verified

**Date**: 2026-11-17

**Scope**: Frontend only. End-to-end verification waits for the later Backend pitch. This delivery does not change Backend stream headers, heartbeat emission, or HTTP/2.

## What was checked

The chat client is proven against the MSW stream fixture, not a live Backend.

- `frontend/src/platform/stream/openChatStream.test.ts` posts `POST /api/chat` with `stream: true` and `credentials: 'same-origin'`, and `legacyChatAdapter` maps today's frames to `meta`, `token`, `final`, and end.
- `frontend/src/platform/stream/idle-timeout.test.ts` uses fake timers at 15000 ms. Silence moves the stream to `interrupted`. A `:` comment resets that window and is not a `StreamEvent`. The retry label is "Tạo lại" through `t()`. The Z4 draft and the partial message stay.
- `frontend/src/platform/stream/legacyChatAdapter.test.ts` keeps WHATWG `id`, `event`, and `retry`.

## Removal

`socket.io-client`, `@types/socket.io-client`, `frontend/src/services/webSocketService.ts`, and `API_CONFIG.WEBSOCKET` are gone. Lint rejects a `socket.io-client` import and a stream event name outside the `StreamEvent` union and `legacyChatAdapter`.

SR-5.2.1 and SR-5.2.2 stay Superseded. `specs/spec-traceability.yaml` is unchanged in this delivery.
