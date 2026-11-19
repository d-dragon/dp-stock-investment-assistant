# Contract: workspace store and routes

**Slice**: B3 (T5)

**Source**: ADR-FRONTEND-003 — "Decision"; `docs/domains/frontend/ARCHITECTURE.md` — "4.2 Workspace context ownership" and "6.1 State ownership matrix"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store", "4.3 Query key taxonomy", and "5. Routing and navigation"; `docs/domains/frontend/DESIGN_LOCK.md` — "2. Workspace context seam"; `spec.md` — FR-011, FR-015, FR-016, FR-017, FR-018. Decisions: `research.md` R10, R13, R15.

## Routes

React Router data router (`createBrowserRouter`). Feature route elements are `React.lazy`. No performance budget is set (`research.md` R19).

| Path | Result |
|---|---|
| `/` | Redirect to `/sandbox` |
| `/:track` | `sandbox` or `portfolio`. Anything else renders the not-found frame inside the shell |
| `/:track/:symbol` | Uppercase ticker or index. Examples that must pass: `FPT`, `VNINDEX`, `VN30`. A lowercase segment renders not-found |
| `*` | Not-found frame inside the shell |
| `/:track/:symbol/:coreType/:coreId` | Not a route in this delivery |
| Search params | Not part of M-000 routes |

`parseTrack` and `parseSymbol` live in `platform/workspace/routeParams.ts` and have unit tests. `parseSymbol` does not add a character class beyond "non-empty and no lowercase letter". A Backend 404 or 403 for a ref the shell did request renders not-found. The Frontend does not decide access. This delivery does not add a screen that requests a Core object, so that branch is covered by a unit of the not-found frame, not by a new Backend call.

## Chart slot

`app` mounts an empty chart slot in Z3 only when `track === 'sandbox'`. On `/portfolio` the slot is absent. A route test asserts both. The slot has no chart content. Z3 empty shows an invitation through `t()` and does not start a Case. `lightweight-charts` and `chart.js` stay out of `package.json`. The delivery 1 import lint stays in force.

## Store write rule

`useUrlSync()` is mounted once in the shell. It is the only writer of `symbol`, `coreObjectRef`, and `activeTrack`. Features read the store through narrow selectors, one field or one slice each. React Context does not carry `symbol`, pane sizes, or the draft. A component that changes symbol, object, or track calls `navigate()`. A unit test asserts the store does not keep a direct write of those fields. A track switch navigates and restores `lastRouteByTrack`.

Loading `/sandbox/FPT` sets the mirrors to that symbol and the sandbox track.

## What the store persists

| Data | Where |
|---|---|
| URL mirrors | Not persisted. The URL is the source |
| `context` and pane sizes | `sessionStorage`, same tab |
| Z4 draft | `sessionStorage`, key namespaced by `sessionRef` |
| `ui.theme` | Always `dark`. Not switchable |
| Durable preferences and layout presets | Not built |

The draft value is text only. Send removes the key. Stop, idle timeout, and `interrupted` leave the key in place. The partial message stays visible.

## sessionRef

One opaque `{ sessionId, conversationId }` on the companion run. Chat requests go through the delivery 1 client, which sends `conversation_id` and omits `sessionId`. The workspace slices do not store a second copy. No `X-User-ID`, no `Authorization`, no token in JavaScript, storage, or fixtures. No `/api/auth/*` and no sign-in control.

## Queries

TanStack Query is the server cache. Keys used: `qk.health()`, `qk.config()`, `qk.models(provider)`. No prices key. No chosen `staleTime`, `retry`, or `refetchOnWindowFocus`. The hand-written `platform/api` client stays. `openapi-fetch` stays unselected.

## Companion stream

Z4 calls `platform/stream`. States: `idle`, `streaming`, `done`, `interrupted`, `error`. Stop and the idle timeout end in `interrupted` and keep the draft. "Tạo lại" sends the same user message as a new run and sends nothing until activated. No resume and no cancel endpoint. The thread is `aria-live="polite"` and announces at message end, not per token.
