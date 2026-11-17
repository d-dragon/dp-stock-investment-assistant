# Phase 0 Research: M-000 Frontend foundation core (delivery 1 of 2)

**Feature**: `specs/004-m000-b-frontend-foundation-core/`

**Branch**: `features/pitch-m000-B-frontend-foundation`

**Date**: 2026-11-17

**Spec**: `specs/004-m000-b-frontend-foundation-core/spec.md`

This file records design choices for the plan. Each choice cites a source. A library or name the sources leave open stays open as `[NEEDS CLARIFICATION]`. Nothing here selects a package the technical design still marks Proposed.

## R1 — This delivery is B0, B1, B2, and thin B4

- **Decision**: Plan B0 (instruction files), B1 (Vite shell and subtract, T0–T2), B2 (OpenAPI types, one API client, SSE-only transport, Socket.IO removal), and thin B4 (dark tokens, vi-VN format, i18n seam, self-hosted fonts, chart-import lint). B3 and B5 stay in a reserved feature.
- **Rationale**: The spec is delivery 1 of 2. Slice order is B0, then B1, then B2 alongside B4.
- **Alternatives considered**: Planning the full Pitch B stack in one feature (shell, router, Zustand, TanStack Query, Storybook, Playwright width matrix). Rejected for this directory because the spec places those in B3 and B5.
- **Source**: `specs/004-m000-b-frontend-foundation-core/spec.md` — "Out of Scope"; `specs/pitches/M-000-B-frontend-foundation.md` — "Slices" and "Delivery workflow (agentic)"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" (Pitch B slice ↔ step map).

## R2 — Node pin and proving commands

- **Decision**: Prerequisite is Node v26.13.1, installed by the Product Owner before the first B1 run. The laptop has Node 22.18 today. `frontend/.nvmrc` is `26`, `engines.node` is `">=26.13.0"`, `frontend/.npmrc` sets `engine-strict=true`, and the Frontend image uses `node:26-alpine`. With `engine-strict=true`, `npm ci` on Node 22.18 fails fast. B1 does not start until v26.13.1 is installed. Shared proving commands, all from `frontend/`, are `npm ci`, `npx tsc --noEmit`, `npx vitest run`, and `npm run build`.
- **Rationale**: The pin and the four commands are Product Owner constraints on every slice. Implementation is later, in a worktree, not in the main tree.
- **Alternatives considered**: Planning against the laptop's Node 22.18, or a happy-dom fallback. Rejected. The spec requires jsdom and the Node 26 pin.
- **Source**: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Node pin), "Risks", and "Delivery workflow (agentic)" (Agent constraints for every slice); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run"; `specs/004-m000-b-frontend-foundation-core/spec.md` — "Prerequisites" and FR-011.

## R3 — Vite, same-origin proxy, and `VITE_*` only

- **Decision**: Create React App is removed. Vite serves dev and production. `server.proxy` sends `/api` to port 5000 on the same origin. `VITE_API_BASE_URL` defaults to empty. The dev setup does not use credentialed CORS. Public build settings are `VITE_*` only. `REACT_APP_*` is removed, including the reads the spec names at `config.ts`, `modelsApi.ts`, and `WebSocketTest.tsx`, and the hard-coded `http://localhost:5000` in `App.tsx`.
- **Rationale**: Same-origin is required so a future `__Host-` session cookie can ride with `credentials: 'same-origin'`. This delivery does not implement login. It only keeps the proxy and the empty base URL.
- **Alternatives considered**: A credentialed cross-origin dev server. Rejected by ADR-SYS-001 and the B1 architecture block.
- **Source**: ADR-FRONTEND-002 — "Decision" and "Guardrails"; ADR-SYS-001 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run" and "6.1 Typed REST client"; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Architecture and Known traps).

## R4 — Test stack for this delivery

- **Decision**: Vitest with jsdom, React Testing Library, and the MSW base the G1 and B2 tests need. The G1 smoke is one component test that sends a chat and renders streamed tokens from an MSW handler using today's chat frames. Storybook, the browser MSW worker, and `VITE_USE_MOCKS` as a browser acceptance stay with B5. The production bundle must not be planned as a Storybook or mock host.
- **Rationale**: ADR-FRONTEND-008 brings MSW and Storybook into M-000. The spec splits that decision: the test base is B1; the browser-handler acceptance and Storybook are the reserved feature. ADR-FRONTEND-008 replaces the "later phases" bullet in ADR-FRONTEND-002. This plan does not restate that replaced bullet as the scope of this delivery.
- **Alternatives considered**: happy-dom; building the Storybook theme matrix here. Rejected. jsdom is decided, and the theme matrix is reserved with B5 (dark-only set). The light half and visual snapshots move to M-001.
- **Source**: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" and "B5 — MSW, minimal Storybook, and Frontend CI"; ADR-FRONTEND-008 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G1) and "8.2 Pattern rules"; `specs/004-m000-b-frontend-foundation-core/spec.md` — "Out of Scope" and the Storybook clarification.

## R5 — OpenAPI codegen is selected; the HTTP client package is not

- **Decision**: `npm run gen:api` runs `openapi-typescript` on `docs/openapi.yaml` and writes `frontend/src/platform/api/generated/schema.d.ts`. The generated file is committed. CI fails when it drifts. The proving command is `npm run gen:api && git diff --exit-code src/platform/api/generated`, run from `frontend/` on a clean tree. The hand-written client behavior is specified in R6. The package that implements that client (`openapi-fetch` or another) is **not** selected.
- **Rationale**: ADR-FRONTEND-002 and the technical design name `openapi-typescript` and the output path. The same technical design marks `openapi-fetch` Proposed. The spec says this delivery does not select Proposed libraries. `docs/openapi.yaml` is an input. This delivery does not edit it.
- **Alternatives considered**: Hand-written request types; selecting `openapi-fetch` because the technical design names it. Rejected. Hand-written types fight the drift guard. Selecting `openapi-fetch` would promote a Proposed package.
- **Source**: ADR-FRONTEND-002 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client" and "12. Domain-specific constraints and open items"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-015 and "Assumptions".
- **Open**: `[NEEDS CLARIFICATION]` Which package, if any, wraps `fetch` for the typed client. Behavior in R6 is required either way. `openapi-fetch` stays Proposed (`docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items").

## R6 — One same-origin client and `NoAuthAdapter`

- **Decision**: One client in `platform/api` sends `credentials: 'same-origin'` on every request, including the stream. A request hook adds `AuthAdapter.csrfHeaders()` on POST, PUT, PATCH, and DELETE. HTTP 401 calls `onUnauthorized`. The client sends no `Authorization` header and no `X-User-ID` header. No token appears in JavaScript, storage, or fixtures. This delivery ships `NoAuthAdapter`: `getSession` returns null, `csrfHeaders` returns an empty set, and sign-in, sign-out, and `onUnauthorized` are no-ops. Tests use a fake adapter. `/api/auth/*` is not implemented. The client calls only health, config, `models/*`, and chat. Non-2xx responses map to `ApiError` (`status`, `code`, a safe `message`, `retriable` for network, 429, and 502–504).
- **Rationale**: Pitch A owns identity. Pitch B only reserves the adapter and the same-origin hooks. ADR-SYS-001 retires caller-set `X-User-ID`. The error shape is the technical design's one error model.
- **Alternatives considered**: Reading a bearer token in the client; calling workspace or user routes from this delivery. Rejected by the B2 agent constraints.
- **Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts" and "6.1 Typed REST client"; ADR-SYS-001 — "Decision" and "Follow-ups"; `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client, OpenAPI types, SSE-only transport, and Socket.IO removal" (Agent constraints); `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-016 and FR-017.

## R7 — `sessionRef` stays opaque; the chat wire field for the session id is open

- **Decision**: The platform type `sessionRef` is an opaque `{sessionId, conversationId}`. This delivery does not build the shell store that holds it. Chat requests use the generated `ChatRequest`. `conversation_id` is the conversation id. `ChatRequest.session_id` is a deprecated alias for `conversation_id`, so it is not the Backend session id and must not be filled with `sessionRef.sessionId`.
- **Rationale**: SR-1.4.2 defines `sessionRef` as the Backend session id plus the conversation id, in the hierarchy workspace > session > conversation. The current chat schema does not have a separate session field. This delivery must not edit `docs/openapi.yaml`.
- **Alternatives considered**: Sending `sessionRef.sessionId` as `ChatRequest.session_id`. Rejected. That property is documented as a deprecated alias for `conversation_id`.
- **Source**: `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — SR-1.4.2; `docs/openapi.yaml` — `ChatRequest`; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.1 Ownership (from ARCHITECTURE §6.1)"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-017 and "Key Entities".
- **Open**: `[NEEDS CLARIFICATION]` Where `sessionRef.sessionId` is carried on `POST /api/chat`, if it is carried at all in this delivery. The store that owns the pair is B3. B2 must not invent a header or a body field that is not in `docs/openapi.yaml`.

## R8 — SSE reader behavior; parser package not selected

- **Decision**: `openChatStream(body, { signal, idleTimeoutMs })` reads `POST /api/chat` with `stream: true` using `fetch`, `ReadableStream`, and `TextDecoderStream`. It parses WHATWG fields and keeps `id`, `event`, and `retry`. `:` comments are ignored as events and still reset the idle timer. `EventSource` is not used. `legacyChatAdapter` behind `StreamAdapter` maps today's frames: `{"event":"meta"}` to `meta`, `{"chunk"}` to `token`, `{"event":"done"}` to `final`, `[DONE]` to end, and `{"error"}` or a malformed frame to `error`. Stream event names appear only in the `StreamEvent` union and the adapter. A second `openChatStream` in the same tab aborts the one already open. The parser package is not selected: `eventsource-parser` and an in-house parser are both still Proposed.
- **Rationale**: The technical design allows either parser behind the same API. The spec requires the behavior and does not choose the library. The Backend stream is unchanged. Proof is an MSW fixture only.
- **Alternatives considered**: `EventSource`; a WebSocket client; selecting `eventsource-parser` in this plan. Rejected. `EventSource` cannot express the POST body the contract uses. Socket.IO is out. Selecting the parser would promote a Proposed choice.
- **Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract" and "6.3 SSE client"; SR-5.1.2; `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-018 and FR-021.
- **Open**: `[NEEDS CLARIFICATION]` In-house parser or `eventsource-parser`. Both remain acceptable until a later confirmation. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items".

## R9 — Idle timeout

- **Decision**: Live idle timeout is `VITE_STREAM_IDLE_TIMEOUT_MS`, default `60000`, never hard-coded. Any received line, including `:` comments, resets it. On timeout the stream aborts and moves to `interrupted`. The retry label is "Tạo lại" through `t()`. The Z4 draft and any partial message stay as they are. `frontend/.env.example` documents the 60 s default as a stopgap. MSW tests use `15000` ms with fake timers. This delivery does not add Backend heartbeats, `Cache-Control`, `X-Accel-Buffering`, or HTTP/2.
- **Rationale**: The Frontend must already tolerate comment lines and silence so a later Backend heartbeat pitch can land without a second Frontend change.
- **Alternatives considered**: A hard-coded 15 s live timeout; treating a future `: ping` as a chat event. Rejected by the Product Owner idle-timeout decision.
- **Source**: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Idle timeout) and "Risks"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract" and "6.3 SSE client"; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-019 and FR-021.

## R10 — Socket.IO removal

- **Decision**: Remove `socket.io-client`, `@types/socket.io-client`, `webSocketService.ts`, and `API_CONFIG.WEBSOCKET`. Add a lint rule that blocks their return. `rg socket.io dist` returns nothing. No WebSocket client and no `EventSource`. `fetch` exists only in `platform/api` and `platform/stream`. SR-5.2.1 and SR-5.2.2 stay Superseded. SNR-8.1.2 is recorded as "Frontend part verified" against the MSW fixture. End-to-end verification waits for the later Backend pitch.
- **Rationale**: The target transport is HTTPS plus SSE. The current Socket.IO client is unused once `WebSocketTest.tsx` is deleted in B1 T0.
- **Alternatives considered**: Leaving the dependency until B5. Rejected. T8 is in B2.
- **Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.4 Socket.IO removal" and "9.2 Tests mapped to gates" (G6); ADR-FRONTEND-002 — "Carve-outs"; `docs/domains/frontend/ARCHITECTURE.md` — "5.3 Carve-outs" and "8.2 Gates G1–G6 → M-001"; SNR-8.1.2; SR-5.2.1; SR-5.2.2; `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." and "Done means".

## R11 — Boundary lint outcomes; plugin not selected

- **Decision**: B1 enables rules 1–3 and `react/no-danger`. Rule 1 is dependency direction `app` → `features` → `platform` / `design-system`, never reverse. Rule 2 is no sibling-feature or deep imports. Rule 3 is that only `platform` talks to the Backend (`fetch`, `XMLHttpRequest`, `EventSource`, and `WebSocket` outside `platform/api` and `platform/stream` fail; `socket.io-client` and `axios` imports fail). B4 enables rule 4 (market and state colour reads) and the chart-library part of rule 5 (`lightweight-charts` only under `platform/chart`, `chart.js` only under `platform/stat-chart`). `eslint-plugin-boundaries` is not selected. The chart packages are not added to `package.json`. `ChartEngine` and `StatChart` are not built. The Frontend does not compute reference, ceiling, or floor prices.
- **Rationale**: The pitch moves rules 1–3 and `react/no-danger` into B1. The technical design's "T4 shell" placement of `react/no-danger` and its "T7" placement of rules 1–3 are stale on timing. The mechanisms in the rule table are Proposed. The outcomes are not.
- **Alternatives considered**: Enabling every §3.3 rule in B1, including chart imports and `jsx-no-literals`. Rejected for chart imports and rule 4 because the spec assigns those to B4. See R17 for `jsx-no-literals`.
- **Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" and "3.1 Module tree (Target M-000)"; `docs/domains/frontend/ARCHITECTURE.md` — "4.3 Building blocks (target)"; ADR-FRONTEND-004 — "Decision" and "Considered Options"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-003, FR-031, and FR-029; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" and "B4 — Dark tokens...".
- **Resolved**: Product Owner, 2026-11-17 (analysis G2). Rules 1 and 2 use core ESLint `no-restricted-imports` path patterns. `eslint-plugin-boundaries` stays Proposed and is not added.

## R12 — Instruction files name `features/` and `platform/`

- **Decision**: B0 instruction files state Vite, Vitest, `VITE_*` only, no `socket.io-client` / WebSocket / `EventSource`, `fetch` only in `platform/api` and `platform/stream`, and the module tree and lint rules above. They name `features/` and `platform/`. They do not name `modules/`. `frontend/AGENTS.md` is under 10,000 characters. Root Frontend lines match. Stale Create React App, Jest, `REACT_APP_*`, or Socket.IO recommendations in `CLAUDE.md`, `.claude/rules`, `.cursor/rules`, and `.github/instructions/frontend-react.instructions.md` are removed or rewritten. B0 changes instruction files only. Proof is `grok inspect` from `frontend/` plus that search. B0 adds no test file.
- **Rationale**: ADR-FRONTEND-001 — "Implementation Direction" still says `modules/`. The technical design tree and the pitch govern this delivery. The stale ADR wording is a follow-up doc fix, not an edit in this delivery.
- **Alternatives considered**: Using `modules/` because the ADR says so. Rejected by the Product Owner clarification of 2026-11-17.
- **Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)"; `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack"; ADR-FRONTEND-001 — "Implementation Direction" (stale `modules/` wording, not followed); `specs/004-m000-b-frontend-foundation-core/spec.md` — User Story 1 and FR-004 through FR-007.

## R13 — Dark colour tokens only; generator not selected

- **Decision**: A build step generates CSS variables for every dark hex in `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette" (sections 3.1, 3.3, and 3.6). The worked example is `--market-up` = `#2EBD6B`. This plan applies that same shape to the other single-segment ids (`market.down` → `--market-down`). `<html>` carries `data-theme="dark"`. Light values, theme switching, and the contrast script are not generated. They move to M-001. `track.a` and `track.b` have no hex and receive none. `surface.z1`–`surface.z4` and `surface.overlay` have no distinct hex and receive none. The Tailwind config exposes no `market` or `state` colour utilities. Style Dictionary is not selected.
- **Rationale**: The pitch and the technical design govern theme timing. DESIGN_SYSTEM — "1. Principles" and "10. Quality", and DESIGN_LOCK — "4.2 Token groups", are stale where they say light is built and contrast-checked from day one, and where they require both-theme Storybook stories in M-000. ADR-FRONTEND-007 replaces the colour bullet in ADR-FRONTEND-002 (emerald / rose / cyan). This plan does not restate that replaced bullet. The generator is Proposed. The required output is the dark column.
- **Alternatives considered**: Generating the light column because DESIGN_SYSTEM §1 still says so; inventing hex for `track.a` and `track.b`; selecting Style Dictionary. Rejected by the Product Owner clarification and by the open token rows.
- **Source**: `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette", "3.1 Surface and market / state (both themes)", "3.2 Track (`track.*`)", "3.3 Accent", "3.6 Provenance (`ai.*`)", and "2. Token architecture"; ADR-FRONTEND-007 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" and "12. Domain-specific constraints and open items"; `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T1 and "B4 — Dark tokens..."; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-025 and "Source conflicts".
- **Resolved**: Product Owner, 2026-11-17 (analysis G3). This delivery commits hand-written two-part variables (`--market-up` is `#2EBD6B`; `market.down` becomes `--market-down`). Style Dictionary stays Proposed and is not selected. Three-part `ai.*` custom property names are not invented. Full B4-T1 generation and the `npm run tokens` drift check stay out of this delivery.

## R14 — Custom board formatters; `Intl` for dates only

- **Decision**: `fmt.price`, `fmt.change`, `fmt.pct`, `fmt.vnd`, and `fmt.volume` are custom formatters. They do not use `Intl`. Dates and times use `Intl` with locale `vi-VN` and time zone `Asia/Ho_Chi_Minh`. Locale and time zone are settings with those launch defaults, not literals buried in each call site. Volume does not go through the price formatter. Exact outputs are the spec rows B4-F1..F5 and P1..P4, including U+2212 for negatives, unsigned zero, em dash for null / undefined / NaN, and volume `0` for a real zero. The dot only marks a decimal and the comma only groups thousands, proven over 1,000 random values.
- **Rationale**: The later price-board bullet in ADR-FRONTEND-005 and DESIGN_LOCK §8 govern. The earlier ADR-FRONTEND-005 sentence that every number goes through `Intl` is stale. The spec records that follow-up. This plan follows the price-board bullet and the pitch rows.
- **Alternatives considered**: `Intl.NumberFormat('vi-VN')` for prices and VND totals. Rejected. It would print `25,30` and `25.300.000 ₫`, which the design lock and the technical design forbid.
- **Source**: ADR-FRONTEND-005 — "Decision" (price-board bullet governs; the `Intl`-for-every-number sentence is stale); `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam"; `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — "SNR-7: Usability, Accessibility, and Responsive Behavior" (launch UI note); `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-F1..F5 and P1..P4.

## R15 — `t()` and one vi-VN catalogue; no i18n library

- **Decision**: Every user-facing string goes through `t()` and `messages` for `vi-VN`. English is not shipped. No i18n library is chosen. The catalogue includes the strings this delivery shows: "Tạo lại", "Không có dữ liệu", "AI gợi ý", and "Đã xác nhận". Tests select by `data-zone`, `data-state`, `data-origin`, and ARIA role, never by CSS class.
- **Rationale**: ADR-FRONTEND-005 keeps the library decision in the future. The seam exists now.
- **Alternatives considered**: Adding react-i18next or FormatJS; shipping an English catalogue. Rejected. Both are Future.
- **Source**: ADR-FRONTEND-005 — "Decision"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance (`ai.*`)" and "9. Content voice"; `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy"; `specs/pitches/M-000-B-frontend-foundation.md` — "Agent constraints for every slice" and "B4 — Dark tokens..." (Acceptance).
- **Open**: `[NEEDS CLARIFICATION]` The vi-VN accessible-name phrases for a positive, negative, and zero `Delta`. The spec requires the accessible name to include the direction and to come from `t()`. It does not give those phrases. This plan does not invent them.

## R16 — Patterns this delivery builds, and the ones it does not

- **Decision**: B4 builds `PriceCell`, `Delta`, and `StatusBadge` under `design-system/patterns/` because the colour-read lint and rows B4-T2 and B4-T3 name them. `Delta` shows a sign or an arrow as well as colour. Zero uses `market.ref` and no sign. Missing renders `—`. `PriceCell` does not compute bands. Fonts are self-hosted from `public/fonts`: UI text starts with `Be Vietnam Pro`; `fmt.*` text starts with `IBM Plex Mono`. No request goes to a third-party font host. B4-T4 is a Playwright check of computed style and the network log. That check stays in this delivery. It is not added to the B1 CI skeleton. `MessageBody`, zone shells, React Router, Zustand, TanStack Query, and Radix primitives beyond those three patterns are not this delivery. Storybook stories for the patterns are B5.
- **Rationale**: The design rows are acceptance for B4. The shell that hosts zones is B3. ADR-FRONTEND-002 decides Tailwind and Radix for the modernization program. The pitch moves primitives the shell needs into B3, and primitives beyond that to M-001. This delivery still needs a Tailwind config that refuses `market` and `state` utilities, because row B4-T2 says so.
- **Alternatives considered**: Building `MessageBody` here because `react/no-danger` turns on in B1. Rejected. The spec keeps `MessageBody` and the XSS tests in B3. The lint rule lands first.
- **Source**: `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-T2, B4-T3, and B4-T4, "B3 — Modular shell, state, and safe rendering", and "B4 — Dark tokens..."; `docs/domains/frontend/DESIGN_SYSTEM.md` — "4. Typography" and "8. Patterns"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules" and "10.2 CRA → Vite migration" (T6); ADR-FRONTEND-002 — "Decision"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-026, FR-027, FR-028, and "Out of Scope".

## R17 — Raw-string lint timing is open

- **Decision**: The behavior "every user-facing string goes through `t()`" applies to every slice in this delivery. Whether `react/jsx-no-literals` is enabled in B1, in B4, or in the reserved B5 feature is not decided by the spec. This plan does not assign that plugin to a slice.
- **Rationale**: The technical design lists the rule beside the other boundary rules and says it works before an i18n library is chosen. The Product Owner clarification assigns rules 1–3 and `react/no-danger` to B1, and rule 4 plus chart-library rule 5 to B4. It does not mention `react/jsx-no-literals`.
- **Alternatives considered**: Turning the rule on in B1 because B0 already states the `t()` rule. Rejected as a guess. Instruction text and an ESLint rule are different slices in the pitch.
- **Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" (i18n raw strings row); `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-031 and the lint-rule clarification.
- **Open**: `[NEEDS CLARIFICATION]` Which slice enables `react/jsx-no-literals`.

## R18 — CI skeleton shape; filename and drift-step position are open

- **Decision**: B1 adds a Frontend CI skeleton whose command order is lint, then `tsc --noEmit`, then Vitest, then build. It does not change the trigger of the existing Docker workflow `.github/workflows/build-push-dockerhub.yml` (`push` to `main`, plus `workflow_dispatch`). The Docker image build for `frontend/Dockerfile` must succeed and must package Vite `dist`, not `/app/build`. Playwright and Storybook are not jobs in this skeleton. The codegen drift check must fail CI when `src/platform/api/generated` is stale. SNR-7.2.1 stays P2. The axe baseline stays with B5.
- **Rationale**: The pitch splits the skeleton (B1) from the Storybook and Playwright extension (B5). The existing workflow file is the Docker workflow whose trigger must stay put. B4-T4 still has its own Playwright proof, run as that row's check, outside this skeleton.
- **Alternatives considered**: Putting Playwright into the B1 skeleton because B4-T4 uses it. Rejected. The spec says extending the skeleton with Playwright is the reserved feature, and B4-T4's own check stays in this delivery as acceptance.
- **Source**: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Acceptance) and "B5 — MSW, minimal Storybook, and Frontend CI"; `.github/workflows/build-push-dockerhub.yml` — `on`; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run"; SNR-7.2.1; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-014, FR-015, and FR-030.
- **Resolved**: Product Owner, 2026-11-17 (analysis G1). The file is `.github/workflows/frontend-ci.yml`. One job runs lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`. The Docker workflow trigger is unchanged.

## R19 — `data-density` is `compact` in B4

- **Decision**: This delivery requires `data-theme="dark"` and `data-density="compact"` on `<html>`. B4 sets both. No other density is used.
- **Rationale**: The technical design says compact is the default from M-000 and that comfortable arrives in M-006. The Product Owner assigned the attribute to this delivery's B4 (analysis X1, 2026-11-17).
- **Alternatives considered**: Leaving `data-density` to the reserved B3 shell. Not selected. The value in the sources is already `compact`, and this delivery owns the `<html>` hook.
- **Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "5. Density, space, radius"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-025.
- **Resolved**: Product Owner, 2026-11-17 (analysis X1). B4 sets `data-density="compact"`.

## R20 — Performance budgets stay unset

- **Decision**: No numeric performance budget is planned. The technical design leaves budgets TBD until after the Vite step.
- **Rationale**: Inventing a p95 or a bundle-size gate would not cite a source.
- **Alternatives considered**: A placeholder millisecond budget. Rejected.
- **Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items".
- **Open**: Performance budgets remain TBD. That is the source status, not a new question.

## R21 — What this plan does not change

- **Decision**: Planning writes only under `specs/004-m000-b-frontend-foundation-core/`. Implementation later runs in a named git worktree on `features/pitch-m000-B-frontend-foundation`. It does not modify `backend/`, `docs/**` (including `docs/openapi.yaml`), the Accepted ADRs, `main`, the Product Owner's main tree, or the `wt/m001-s3` worktree. Stale sentences listed in the spec's "Source conflicts" stay follow-up doc fixes.
- **Rationale**: The Product Owner forbade those edits for this delivery. Constitution traceability still applies later, after verification, in a change that is allowed to touch those files.
- **Alternatives considered**: Editing the stale DESIGN_SYSTEM and ADR sentences inside this plan so the citations match. Rejected. The spec says those files are not edited here.
- **Source**: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" (Agent constraints for every slice); `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-002 and "Source conflicts"; `.specify/memory/constitution.md` — "I. Spec-Driven, Traceable Delivery" and "Document Referencing in Spec-Kit Workflows".

## Resolved clarifications carried from the spec

The spec session of 2026-11-17 already closed these. Research does not reopen them:

| Topic | Governing text | Stale text, not followed |
|---|---|---|
| Light theme and contrast | Pitch and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" | `docs/domains/frontend/DESIGN_SYSTEM.md` — "1. Principles" and "10. Quality"; `docs/domains/frontend/DESIGN_LOCK.md` — "4.2 Token groups" |
| Number format | Custom board formatters; `Intl` for dates only | ADR-FRONTEND-005 — "Decision", the sentence that every number goes through `Intl` |
| Task labels for the Vite move | Pitch T1 and T2, with the technical design "10.2" step noted beside each | Using the technical design step names as the `tasks.md` labels |
| Lint timing | Rules 1–3 and `react/no-danger` in B1 | `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration", the T4 placement of `react/no-danger` and the T7 placement of rules 1–3 |
| Folder name | `features/` and `platform/` | ADR-FRONTEND-001 — "Implementation Direction" (`modules/`) |
| B0 tests | Instruction proof only | The pitch's blanket test-first sentence, which does not apply to B0 |
| Storybook matrix | Reserved with B5, dark-only minimal set, not built here | `docs/domains/frontend/DESIGN_SYSTEM.md` — "10. Quality" |

Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — "Clarifications" and "Source conflicts".
