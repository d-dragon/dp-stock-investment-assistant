# Tasks: M-000 Frontend foundation core (delivery 1 of 2)

**Input**: Design documents from `specs/004-m000-b-frontend-foundation-core/`

**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required for B1, B2, and B4 by `specs/004-m000-b-frontend-foundation-core/spec.md` — "Test-first rule" (FR-001). B0 is exempt. Test tasks say **confirm failing**. Implementation tasks in the same story must leave those test files unchanged.

**Organization**: Phases follow slice order B0, then B1, then B2 alongside B4. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Slices" and "Delivery workflow (agentic)"; `specs/004-m000-b-frontend-foundation-core/spec.md` — "User Scenarios & Testing". The Frontend package already exists, so this file has no separate bootstrap phase. Phase 1 is User Story 1 (B0). Phase 2 is User Story 2 (B1) and blocks B2 and B4.

**Branch for later implementation**: `features/pitch-m000-B-frontend-foundation`, in a named git worktree. Do not edit the Product Owner's main tree, `main`, or the `wt/m001-s3` worktree. Do not modify `backend/`, `docs/**` (including `docs/openapi.yaml`), the Accepted ADRs, or `specs/spec-traceability.yaml`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-002; `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "Where the Software Engineer works".

**Do not commit or push** from these tasks. The Product Owner approves any commit. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)".

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: [US1] B0, [US2] B1, [US3] B2, [US4] B4
- Each task names 2–5 file paths, the pitch slice item (pitch T-step, with the `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step when that step exists), and the technical-design section it implements

## Path Conventions

- Frontend package: `frontend/`
- Instruction files for B0 also include the repository root and `.github/instructions/frontend-react.instructions.md`
- Tests and lint fixtures live under `frontend/` and are written by test tasks only

## Pitch label map (do not swap these names)

| Pitch label in this file | Meaning | TECHNICAL_DESIGN "10.2 CRA → Vite migration" step to note |
|---|---|---|
| B0 (no T-step) | Instruction files only | None. Sections "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)" |
| B1-T0 | Delete the unused files | **T0 subtract** |
| B1-T1 | Vite build, config, and environment move | **T2 Vite**, the `react-scripts` → Vite, root `index.html`, and `REACT_APP_*` → `VITE_*` portion only |
| B1-T2 | Vitest, MSW base, G1 smoke | **T2 Vite**, the Vitest + RTL + MSW + first chat smoke portion only |
| B1 types alignment | `@types/react` and `@types/react-dom` with React 18, TypeScript 5.9+ | **T1 types fix**. This is not pitch T1 |
| B2 codegen | `openapi-typescript` into `src/platform/api/generated` | None. Section "6.1 Typed REST client" |
| B2-T3 | One client in `platform/api` and the reader in `platform/stream` | **T3 platform/api + stream** |
| B2-T8 | Remove Socket.IO and block its return | **T8 drop Socket.IO** |
| B4-T6 | Dark tokens, Tailwind preset, `fmt`, `t()`, the three patterns | **T6 tokens + Tailwind + Radix + format/i18n seam** |
| B4-T7 (chart part only) | `lightweight-charts` / `chart.js` import lint | **T7 boundary lint + a11y**, chart-library clause only |

Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-032 and "Source conflicts" ("B1 step labels", "Lint-rule timing"); `specs/pitches/M-000-B-frontend-foundation.md` — "Slices"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration".

Design rows `B4-F1`..`B4-F5`, `P1`..`P4`, and `B4-T1`..`B4-T4` are UX acceptance rows. They are not migration T-steps. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4: tokens, format, fonts".

---

## Phase 1: User Story 1 — Agent instructions on the target stack (B0) (Priority: P1)

**Goal**: Instruction files describe the target Frontend stack before the toolchain changes. Instruction files only.

**Independent Test**: From `frontend/`, `grok inspect` lists the new rules, and a search of the instruction files finds no recommendation of Create React App, Jest, `REACT_APP_*`, or Socket.IO. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Acceptance); `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "B0 proof".

**Exempt from the failing-test rule.** Do not add a test file. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-001 and FR-007.

**Target rules** (every file in this phase states the same list). Source: `specs/004-m000-b-frontend-foundation-core/contracts/instruction-set.md` — "Rules the files state"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)":

- Vite and Vitest.
- `VITE_*` environment variables only.
- No `socket.io-client`, WebSocket, or EventSource.
- `fetch` only inside `platform/api` and `platform/stream`.
- Module folders are `features/` and `platform/`. Do not tell a session to create `modules/`. ADR-FRONTEND-001 — "Implementation Direction" (`modules/`) is stale for this delivery.
- Lint rules 1–3 as B1 enables them: dependency direction `app` → `features` → `platform` / `design-system`; no sibling-feature or deep imports; only `platform` talks to the Backend.

A prohibition that names Create React App, Jest, `REACT_APP_*`, or Socket.IO in order to forbid them is required. The proof fails only when a file recommends those stacks.

### Implementation for User Story 1

- [ ] T001 [P] [US1] B0 (no T-step). Add `frontend/AGENTS.md` (under 10,000 characters) and rewrite the Frontend lines of root `AGENTS.md`, including the SPA clause in the opening summary, so both state the target rules above. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)". Files: `frontend/AGENTS.md`, `AGENTS.md`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-004.

- [ ] T002 [P] [US1] B0 (no T-step). Update `.github/instructions/frontend-react.instructions.md` to the same target rules. Where `CLAUDE.md`, `.claude/rules`, or `.cursor/rules` exist and recommend Create React App, Jest, `REACT_APP_*`, or Socket.IO, remove or rewrite that entry. Do not create those three paths when they are absent. Do not edit `docs/**` or application source. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)". Files: `.github/instructions/frontend-react.instructions.md`, `CLAUDE.md`, `.claude/rules`, `.cursor/rules`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-005; `specs/004-m000-b-frontend-foundation-core/contracts/instruction-set.md` — "Files".

**Checkpoint**: From `frontend/`, run `grok inspect` and confirm it lists the target rules. From the repository root, search `frontend/AGENTS.md`, `AGENTS.md`, `.github/instructions/frontend-react.instructions.md`, `CLAUDE.md`, `.claude/rules`, and `.cursor/rules` and confirm none recommend Create React App, Jest, `REACT_APP_*`, or Socket.IO. `frontend/AGENTS.md` is under 10,000 characters. Proving command: `grok inspect` (cwd `frontend/`) plus that instruction search. Source: `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "B0 proof"; `specs/004-m000-b-frontend-foundation-core/spec.md` — SC-001.

- [ ] T003 [US1] B0 (no T-step). Run the checkpoint proof and change no files. Confirm `grok inspect` (cwd `frontend/`) lists the rules from T001, and confirm the instruction search finds no recommendation of Create React App, Jest, `REACT_APP_*`, or Socket.IO. If `.grok/rules` or `AGENT.md` recommends those stacks, stop and record [NEEDS CLARIFICATION]; the contract file list does not include them. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)". Files read only: `frontend/AGENTS.md`, `AGENTS.md`, `.github/instructions/frontend-react.instructions.md`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-006 and FR-007.

---

## Phase 2: User Story 2 — Vite shell and subtract (B1) (Priority: P2)

**Goal**: Replace Create React App with Vite, delete the unused files named for T0, align React 18 types, and leave Vitest (jsdom), the MSW test base, the G1 smoke, lint rules 1–3, `react/no-danger`, a CI skeleton, and a `node:26-alpine` image that packages `dist`.

**Independent Test**: From `frontend/` on Node v26.13.1: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`, and `npm run dev` succeed; `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` returns nothing; the image built from `frontend/Dockerfile` succeeds. Source: `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "Shared proof" and "B1 proof, in addition".

**Blocks**: B2 and B4. Their proving commands run from `frontend/` after this toolchain exists.

**Prerequisite**: The Product Owner installs Node v26.13.1 before the first B1 command. The laptop that prompted the plan has Node 22.18. With `engine-strict=true`, `npm ci` on 22.18 fails fast. That failure is the guard. Do not lower `engines.node`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Node pin) and "Risks"; `research.md` R2 (plan open item O11).

### Tests for User Story 2

> Write these tests first. **Confirm failing** before T008. Later implementation tasks must not edit these files.

- [ ] T004 [P] [US2] B1-T0. Write `frontend/src/test/b1-t0-subtract.test.ts` so it fails while `MessageFormatter`, `dangerouslySetInnerHTML`, or `REACT_APP_` remain under `frontend/src`. **Confirm failing**: from `frontend/`, `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` still matches, and `npx vitest run src/test/b1-t0-subtract.test.ts` fails because Vitest is not wired yet. Do not delete source files in this task. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T0 subtract** and "6.5 Safe rendering of Agent output". Files: `frontend/src/test/b1-t0-subtract.test.ts`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Proving commands); `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-001 and FR-009.

- [ ] T005 [P] [US2] B1-T2 (pitch T2; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T2 Vite**, Vitest + RTL + MSW + first chat smoke portion). Write a self-contained G1 component test and the MSW SSE fixture that uses the frames in "6.2 Today's stream contract" (`meta`, `chunk`, `done`, `[DONE]`). The test component lives in the test file and renders the streamed token text. jsdom only. **Confirm failing**: `npx vitest run src/test/g1-chat-smoke.test.tsx` fails before Vitest is installed. Implements "9.2 Tests mapped to gates" (G1) and "6.2 Today's stream contract". Files: `frontend/src/test/g1-chat-smoke.test.tsx`, `frontend/src/test/msw/chat-frames.ts`, `frontend/src/test/msw/handlers.ts`, `frontend/src/test/setup.ts`. Source: SNR-6.1.4 (path only); `specs/004-m000-b-frontend-foundation-core/contracts/toolchain-and-ci.md` — "Tests in B1"; ADR-FRONTEND-008 — "Decision" (MSW in Vitest; browser worker stays with B5).

- [ ] T006 [P] [US2] B1 lint rules 1–3 and `react/no-danger` (pitch B1; these are not pitch T4 or T7). Write planted fixtures that will fail lint once the rules exist: a reverse dependency import, a deep feature import, a `fetch` outside `platform/api` and `platform/stream`, and a `dangerouslySetInnerHTML` use. **Confirm failing**: `npm run lint` does not enforce these rules yet. Do not add `eslint-plugin-boundaries`. Rules 1 and 2 use core ESLint `no-restricted-imports` (Product Owner, 2026-11-17, analysis G2). Do not enable `react/jsx-no-literals` ([NEEDS CLARIFICATION] `research.md` R17 / plan O7). Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" rules 1–3 and the Agent-output row. The "10.2" placement of `react/no-danger` on T4 and of rules 1–3 on T7 is stale for this delivery. Files: `frontend/eslint-fixtures/b1-rule1-reverse-import.ts`, `frontend/eslint-fixtures/b1-rule2-deep-import.ts`, `frontend/eslint-fixtures/b1-rule3-fetch.ts`, `frontend/eslint-fixtures/b1-no-danger.tsx`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-031 and "Source conflicts" ("Lint-rule timing").

### Implementation for User Story 2

> Do not edit `frontend/src/test/**` or `frontend/eslint-fixtures/**`.

- [ ] T007 [US2] B1 Node pin. Stop the phase when `node -v` is anything other than v26.13.1. Do not change `frontend/package.json` so that Node 22.18 satisfies `engines`. When the version is v26.13.1, continue. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run". Files: `frontend/package.json` (read; do not loosen `engines`). Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Risks"; `research.md` R2.

- [ ] T008 [P] [US2] B1-T0. Delete the four unused component files. Do not patch `MessageFormatter.js`. Do not edit T004. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T0 subtract** and "6.5 Safe rendering of Agent output". Files: `frontend/src/components/OptimizedApp.js`, `frontend/src/components/PerformanceProfiler.js`, `frontend/src/components/WebSocketTest.tsx`, `frontend/src/components/MessageFormatter.js`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-009.

- [ ] T009 [P] [US2] B1-T0. Delete `frontend/src/services/apiService.ts`. Delete `frontend/src/utils/performance.js` only when an import scan shows it is still unreferenced; if a live import remains, stop and leave the file. Do not edit T004. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T0 subtract**. Files: `frontend/src/services/apiService.ts`, `frontend/src/utils/performance.js`. Source: `specs/004-m000-b-frontend-foundation-core/contracts/toolchain-and-ci.md` — "T0 deletions".

- [ ] T010 [US2] B1 types alignment. This is **not** pitch T1. Declare TypeScript 5.9 or newer as a direct dependency and align `@types/react` and `@types/react-dom` with React 18 (they are currently `^19`). Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T1 types fix**. Files: `frontend/package.json`, `frontend/package-lock.json`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-010 and FR-032; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Known traps).

- [ ] T011 [US2] B1 Node pin, after T010. Set `engines.node` to `">=26.13.0"` in `frontend/package.json`. Add `frontend/.nvmrc` containing `26` and `frontend/.npmrc` containing `engine-strict=true`. Point `frontend/Dockerfile` at `node:26-alpine` and at the Vite `dist` output (the image copies `/app/build` today). Do not edit T004. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run". Files: `frontend/package.json`, `frontend/.nvmrc`, `frontend/.npmrc`, `frontend/Dockerfile`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-011; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Node pin and Known traps).

- [ ] T012 [US2] B1-T1 (pitch T1; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T2 Vite**, the `react-scripts` → Vite portion). After T011, switch `dev` and `build` to Vite, add `frontend/vite.config.ts` with `server.proxy` sending `/api` to port 5000 on the same origin, move `frontend/public/index.html` to `frontend/index.html`, and set `frontend/tsconfig.json` so `tsc --noEmit` is not left on `target es5` and `moduleResolution node`. Exclude `frontend/eslint-fixtures` from the TypeScript program. `VITE_API_BASE_URL` defaults to empty. No credentialed CORS. Delete the dead CRA configs in the same task. Implements "10.1 Build and run" and "10.2" step **T2 Vite**. Files: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/index.html`, `frontend/tsconfig.json`, `frontend/config-overrides.js`, `frontend/webpack.config.dev.js`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-008, FR-012, and FR-032; ADR-FRONTEND-002 — "Decision" and "Guardrails"; ADR-SYS-001 — "Decision".

- [ ] T013 [US2] B1-T1 (pitch T1; same **T2 Vite** row, the `REACT_APP_*` → `VITE_*` portion). Replace `process.env.REACT_APP_*` reads and remove the hard-coded `http://localhost:5000` so calls use the empty `VITE_API_BASE_URL` and the dev proxy. `WebSocketTest.tsx` is already gone in T008. Leave `API_CONFIG.WEBSOCKET` for B2-T8. Do not edit T004 or T005. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run" and "10.2" step **T2 Vite**. Files: `frontend/src/config.ts`, `frontend/src/services/modelsApi.ts`, `frontend/src/App.tsx`, `frontend/src/index.tsx`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Known traps); `research.md` R3.

- [ ] T014 [US2] B1-T2 (pitch T2; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T2 Vite**, Vitest + RTL + MSW portion). After T012, add `frontend/vitest.config.ts` with the jsdom environment (no happy-dom fallback), wire `frontend/src/test/setup.ts`, and add the Vitest, React Testing Library, jsdom, and MSW test dependencies plus the `test` script. Make T004 and T005 pass. Do not edit those test files. Implements "9.2 Tests mapped to gates" (G1) and "9.1 Pyramid". Files: `frontend/vitest.config.ts`, `frontend/package.json`, `frontend/package-lock.json`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-013 and FR-032; SNR-6.1.4 (path).

- [ ] T015 [US2] B1 lint implementation, after T006 and after T014 (`frontend/package.json`). Add `frontend/eslint.config.js` and an `lint` script. Enable rule 3 with `no-restricted-globals` / `no-restricted-syntax` / `no-restricted-imports` as "3.3 Boundary enforcement (Target G2)" describes for `fetch`, `XMLHttpRequest`, `EventSource`, `WebSocket`, `socket.io-client`, and `axios`. Enable `react/no-danger` as an error. For rules 1 and 2, enforce the outcomes on `frontend/eslint-fixtures` with core ESLint `no-restricted-imports` path patterns. Do not add `eslint-plugin-boundaries` (Product Owner, 2026-11-17, analysis G2). Do not enable `react/jsx-no-literals` (`research.md` R17 / plan O7). Do not edit the fixtures. Exclude the fixtures from `tsc`. Implements "3.3 Boundary enforcement (Target G2)". Files: `frontend/eslint.config.js`, `frontend/package.json`, `frontend/tsconfig.json`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-031.

- [ ] T016 [US2] B1 CI skeleton. Add `.github/workflows/frontend-ci.yml`. One job runs lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated` (Product Owner, 2026-11-17, analysis G1). Do not change the `on` trigger of `.github/workflows/build-push-dockerhub.yml`. Do not add Playwright or Storybook. The `gen:api` script is added in T021; this task still writes the fifth step that calls it. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run" (CI row). The extended CI workflow in "10.2" (Storybook and Playwright) stays with B5. Files: `.github/workflows/frontend-ci.yml`, `.github/workflows/build-push-dockerhub.yml` (read; leave the trigger unchanged). Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-014; `specs/004-m000-b-frontend-foundation-core/contracts/toolchain-and-ci.md` — "CI skeleton".

**Checkpoint**: On Node v26.13.1, from `frontend/`: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`, `npm run dev`. Also `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` returns nothing, and the Docker image build from `frontend/Dockerfile` succeeds on `node:26-alpine` packaging `dist`. The G1 smoke renders streamed tokens. T004 and T005 were confirmed failing before T008 and are unchanged. Source: `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "Shared proof" and "B1 proof, in addition"; `specs/004-m000-b-frontend-foundation-core/spec.md` — SC-002, SC-003, SC-004, and SC-011.

---

## Phase 3: User Story 3 — API client, OpenAPI types, and SSE-only transport (B2) (Priority: P3)

**Goal**: Generate types from `docs/openapi.yaml`, ship one same-origin client and `NoAuthAdapter`, read the chat stream with `fetch`, and remove Socket.IO. The Backend stream is unchanged. The client is proven against an MSW fixture only.

**Independent Test**: From `frontend/`: `npm run gen:api && git diff --exit-code src/platform/api/generated` passes; `rg socket.io dist` returns nothing; a fake-timer test at 15000 ms accepts `:` comments and moves a silent stream to `interrupted`. Source: `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "B2 proof, in addition".

**Runs alongside Phase 4** after Phase 2. Shared files `frontend/package.json` and `frontend/eslint.config.js` stay ordered: B1, then this phase, then the B4 edits in Phase 4.

### Tests for User Story 3

> Write these tests first. **Confirm failing** before T023. Implementation must not edit them.

- [ ] T017 [P] [US3] B2-T3. Write client tests that fail until the client exists: `credentials: 'same-origin'` on every call including the stream; `AuthAdapter.csrfHeaders()` on POST, PUT, PATCH, and DELETE; `onUnauthorized` on 401; no `Authorization` header; no `X-User-ID`; non-2xx becomes `ApiError` (`status`, `code`, safe `message`, `retriable` for network, 429, and 502–504); calls limited to health, config, `models/*`, and chat. **Confirm failing**: `npx vitest run src/platform/api/client.test.ts` fails. Do not call `GET /api/market/prices/{symbol}`. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client" and "10.2" step **T3 platform/api + stream**. Files: `frontend/src/platform/api/client.test.ts`, `frontend/src/platform/api/client.scope.test.ts`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-016 and FR-017; ADR-SYS-001 — "Decision" and "Follow-ups"; SR-1.4.2 (`sessionRef` shape only).

- [ ] T018 [P] [US3] B2-T3. Write `NoAuthAdapter` tests: `getSession` returns null, `csrfHeaders` returns an empty set, and `signIn`, `signOut`, and `onUnauthorized` are no-ops. Tests supply a fake adapter. No token in the test, in storage, or in a fixture. **Confirm failing**: `npx vitest run src/platform/auth/NoAuthAdapter.test.ts` fails. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts" and "6.1 Typed REST client". Files: `frontend/src/platform/auth/NoAuthAdapter.test.ts`, `frontend/src/platform/auth/fakeAuthAdapter.ts`. Source: `specs/004-m000-b-frontend-foundation-core/contracts/platform-api.md` — "Client behavior". `/api/auth/*` stays in Pitch A.

- [ ] T019 [P] [US3] B2-T3. Write stream tests for `openChatStream(body, { signal, idleTimeoutMs })`: WHATWG `id`, `event`, and `retry` are kept; `legacyChatAdapter` maps today's frames to `meta`, `token`, `final`, and end; `{"error"}` or a malformed frame becomes `error`; a `:` line resets the idle timer and is not a `StreamEvent`; a second open in the tab aborts the first; fake timers at 15000 ms move silence to `interrupted`; the retry label is "Tạo lại" through `t()` (stub `t()` inside the test file so this story stays testable before Phase 4); the Z4 draft and any partial message stay. **Confirm failing**: `npx vitest run src/platform/stream` fails. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client", "6.2 Today's stream contract", and "10.2" step **T3 platform/api + stream**. Files: `frontend/src/platform/stream/legacyChatAdapter.test.ts`, `frontend/src/platform/stream/openChatStream.test.ts`, `frontend/src/platform/stream/idle-timeout.test.ts`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-018 and FR-019; SR-5.1.2; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix".

- [ ] T020 [P] [US3] B2-T8. Write lint fixtures for a `socket.io-client` import and for a stream event name outside the `StreamEvent` union and the adapter. **Confirm failing**: lint does not yet reject them. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.4 Socket.IO removal" and "10.2" step **T8 drop Socket.IO**. Files: `frontend/eslint-fixtures/b2-socket-io-import.ts`, `frontend/eslint-fixtures/b2-stream-event-outside-union.ts`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-020; SNR-8.1.2; SR-5.2.1 and SR-5.2.2 (both stay Superseded).

### Implementation for User Story 3

> Do not edit the test files from T017–T020 or `frontend/eslint-fixtures/**`.

- [ ] T021 [US3] B2 codegen (not a pitch T-number). Add `npm run gen:api` running `openapi-typescript` on `docs/openapi.yaml` (read only; do not edit that file) and commit the output at `frontend/src/platform/api/generated/schema.d.ts`. Do not add `openapi-fetch`. The HTTP client package is [NEEDS CLARIFICATION] (`research.md` R5 / plan O1); the hand-written client uses `fetch`. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client". Files: `frontend/package.json`, `frontend/package-lock.json`, `frontend/src/platform/api/generated/schema.d.ts`. Source: ADR-FRONTEND-002 — "Decision"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-015.

- [ ] T022 [P] [US3] B2-T3. Add `NoAuthAdapter` and the `AuthAdapter` / `SessionInfo` types from "3.4 Platform contracts". Do not edit T018. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts" and "10.2" step **T3 platform/api + stream**. Files: `frontend/src/platform/auth/types.ts`, `frontend/src/platform/auth/NoAuthAdapter.ts`, `frontend/src/platform/auth/index.ts`. Source: ADR-SYS-001 — "Follow-ups".

- [ ] T023 [US3] B2-T3. After T021 and T022, add one client that uses `fetch` and `import.meta.env.VITE_API_BASE_URL` (empty means same origin). Apply the behavior T017 locks. `sessionRef` is `{sessionId, conversationId}`. Send `conversationId` as `ChatRequest.conversation_id`. Do not write `sessionRef.sessionId` into `ChatRequest.session_id` (deprecated alias for `conversation_id`). Where `sessionId` is carried on `POST /api/chat` is [NEEDS CLARIFICATION] (`research.md` R7 / plan O2): omit it. Do not edit T017. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client" and "10.2" step **T3 platform/api + stream**. Files: `frontend/src/platform/api/client.ts`, `frontend/src/platform/api/errors.ts`, `frontend/src/platform/api/sessionRef.ts`, `frontend/src/platform/api/index.ts`. Source: `docs/openapi.yaml` — `ChatRequest`; `specs/004-m000-b-frontend-foundation-core/contracts/platform-api.md` — "sessionRef on the wire".

- [ ] T024 [US3] B2-T3. Implement `openChatStream` with `fetch`, `ReadableStream`, and `TextDecoderStream` on `POST /api/chat` with `stream: true`, plus `legacyChatAdapter` behind `StreamAdapter`. Put WHATWG field splitting in `parseSse.ts`. Do not add `eventsource-parser`. Do not use `EventSource`. The parser package remains [NEEDS CLARIFICATION] (`research.md` R8 / plan O3). Do not add `eventsource-parser`. Keep the WHATWG split in `parseSse.ts` with no new dependency, and leave O3 open so a later confirmation can replace that file. Live idle timeout is read from `VITE_STREAM_IDLE_TIMEOUT_MS` (documented default 60000 in `frontend/.env.example`, described there as a stopgap). MSW tests pass 15000. Only one chat stream is open per tab. Stream event names appear only in the union and the adapter. Do not edit T019. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client", "6.2 Today's stream contract", and "10.2" step **T3 platform/api + stream**. Files: `frontend/src/platform/stream/openChatStream.ts`, `frontend/src/platform/stream/legacyChatAdapter.ts`, `frontend/src/platform/stream/parseSse.ts`, `frontend/src/platform/stream/types.ts`, `frontend/.env.example`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-018, FR-019, and FR-021.

- [ ] T025 [US3] B2-T3. Fold `frontend/src/services/restApiClient.js` and `frontend/src/services/modelsApi.ts` into the `platform/api` client and point current callers at that client so the G1 smoke stays green. Convert those call sites to TypeScript as this step requires. Do not split `App.tsx` into `app/` and `features/` (that is B3 / T4). Do not edit T005 or T017. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T3 platform/api + stream**. Files: `frontend/src/services/restApiClient.js`, `frontend/src/services/modelsApi.ts`, `frontend/src/App.tsx`, `frontend/src/components/models/ModelSelector.tsx`, `frontend/src/platform/api/client.ts`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — "Out of Scope" (B3).

- [ ] T026 [US3] B2-T8. Remove `socket.io-client` and `@types/socket.io-client`, delete `frontend/src/services/webSocketService.ts`, and delete `API_CONFIG.WEBSOCKET` from `frontend/src/config.ts`. Extend `frontend/eslint.config.js` with `no-restricted-imports` so the client cannot return, and so stream event names stay in the union and the adapter. Do not edit T020. `rg socket.io dist` returns nothing after `npm run build`. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.4 Socket.IO removal" and "10.2" step **T8 drop Socket.IO**. Files: `frontend/package.json`, `frontend/package-lock.json`, `frontend/src/services/webSocketService.ts`, `frontend/src/config.ts`, `frontend/eslint.config.js`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-020; ADR-FRONTEND-002 — "Carve-outs"; SNR-8.1.2.

- [ ] T027 [US3] B2-T8 evidence. After T026 and the idle-timeout test pass, write `specs/004-m000-b-frontend-foundation-core/evidence/snr-8.1.2.md` recording SNR-8.1.2 as "Frontend part verified" against the MSW stream fixture. Do not edit `specs/spec-traceability.yaml` or `docs/**`. End-to-end verification waits for the later Backend pitch. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G6). Files: `specs/004-m000-b-frontend-foundation-core/evidence/snr-8.1.2.md`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Done means"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-020 and FR-002.

**Checkpoint**: From `frontend/`: `npm run gen:api && git diff --exit-code src/platform/api/generated`; `rg socket.io dist` returns nothing; `npx vitest run src/platform/stream/idle-timeout.test.ts` passes. Then the shared proof: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`. T017–T020 were confirmed failing before T021 and are unchanged. The CI drift step is the fifth step of `.github/workflows/frontend-ci.yml`, after build (Product Owner, 2026-11-17, analysis G1). Source: `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "B2 proof, in addition"; `specs/004-m000-b-frontend-foundation-core/spec.md` — SC-005, SC-006, SC-007, and SC-011.

---

## Phase 4: User Story 4 — Dark tokens, vi-VN format, i18n seam, fonts, and chart-import lint (B4) (Priority: P3)

**Goal**: Dark CSS variables and the `data-theme="dark"` hook, custom board formatters, one vi-VN catalogue behind `t()`, self-hosted fonts, `PriceCell` / `Delta` / `StatusBadge`, and the chart-library import lint.

**Independent Test**: Vitest exact outputs match rows B4-F1..F5 and P1..P4, including the 1,000-value property test; a planted `lightweight-charts` or `chart.js` import fails lint; generated dark variables match the dark column copied in `data-model.md` — "Design tokens (dark column)", including `--market-up` = `#2EBD6B`. Source: `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "B4 proof, in addition".

**Runs alongside Phase 3** after Phase 2. Edit `frontend/eslint.config.js` and `frontend/package.json` only after the B2 tasks that touch those files, or rebase onto them.

### Tests for User Story 4

> Write these tests first. **Confirm failing** before T035. Implementation must not edit them.

- [ ] T028 [P] [US4] B4-T6 format tests (pitch T6; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2" step **T6 tokens + Tailwind + Radix + format/i18n seam**, and section "8.3 i18n and locale seam"). Lock the exact strings: `fmt.price(25300)` → `25.30`; `fmt.pct(0.0698)` → `+6.98%`; `fmt.volume(1234500)` → `1,234,500`; `fmt.vnd(25300000)` → `25,300,000 ₫`; `fmt.change(1750)` → `+1.75`; `fmt.change(-450)` → `−0.45` (U+2212); `fmt.pct(-0.0698)` → `−6.98%`; zero change → `0.00` and `0.00%` with no sign; `null` / `undefined` / `NaN` → `—` with accessible name key "Không có dữ liệu"; `fmt.volume(0)` → `0`. Property test: 1,000 random values, dot only as decimal, comma only as thousands grouping. Numeric formatters do not use `Intl`. **Confirm failing**: `npx vitest run src/platform/format` fails. Files: `frontend/src/platform/format/format.test.ts`, `frontend/src/platform/format/format.property.test.ts`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-F1..F5 and P1..P4; `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy"; ADR-FRONTEND-005 — "Decision" (price-board bullet).

- [ ] T029 [P] [US4] B4-T6 catalogue tests (pitch T6; section "8.3 i18n and locale seam"). `t()` returns the vi-VN strings "Tạo lại", "Không có dữ liệu", "AI gợi ý", and "Đã xác nhận". No English catalogue and no i18n library. `fmt.dateTime` uses `Intl` with locale `vi-VN` and time zone `Asia/Ho_Chi_Minh`. **Confirm failing**: `npx vitest run src/platform/i18n/catalogue.test.ts` fails. Files: `frontend/src/platform/i18n/catalogue.test.ts`, `frontend/src/platform/format/dateTime.test.ts`. Source: ADR-FRONTEND-005 — "Decision"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance" and "9. Content voice".

- [ ] T030 [P] [US4] Design row B4-T1 (this row is not migration T1). Copy the dark hex table from `specs/004-m000-b-frontend-foundation-core/data-model.md` — "Design tokens (dark column)" into a fixture and assert generated CSS. `--market-up` is `#2EBD6B`. Two-part ids use that same shape (`market.down` → `--market-down`). Assert no light values. Omit `track.a`, `track.b`, and `surface.z1`–`surface.z4` / `surface.overlay`. Assert two-part variables only. Do not invent three-part custom property names for `ai.*` ids. Full generation of every dark palette value is out of this delivery (Product Owner, 2026-11-17, analysis G3). **Confirm failing**: `npx vitest run src/design-system/tokens/dark-tokens.test.ts` fails. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline". Files: `frontend/src/design-system/tokens/dark-palette.fixture.ts`, `frontend/src/design-system/tokens/dark-tokens.test.ts`. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette", "3.2 Track", "3.3 Accent", and "3.6 Provenance"; ADR-FRONTEND-007 — "Decision"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-025.

- [ ] T031 [P] [US4] Design row B4-T2. Write a Tailwind config test that fails if `market` or `state` colour utilities exist, plus lint fixtures for `var(--market-*)` outside `PriceCell` / `Delta`, `var(--state-*)` outside `StatusBadge`, and an arbitrary Tailwind colour (`text-[#…]`, `bg-[var(--market-up)]`) outside `design-system/patterns/`. **Confirm failing**: the config test and `npm run lint` do not enforce this yet. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" rule 4 and "8.1 Token pipeline". Files: `frontend/src/design-system/tailwind-market-state.test.ts`, `frontend/eslint-fixtures/b4-market-var-outside.tsx`, `frontend/eslint-fixtures/b4-state-var-outside.tsx`, `frontend/eslint-fixtures/b4-arbitrary-color.tsx`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T2; `docs/domains/frontend/DESIGN_SYSTEM.md` — "2. Token architecture"; ADR-FRONTEND-007 — "Decision".

- [ ] T032 [P] [US4] Design rows B4-T3 and P2. Write RTL tests: a positive or negative `Delta` shows a sign or an arrow as well as colour; zero shows `0.00` with no sign and colour `market.ref` (the zero clause inside verbatim B4-T3 is superseded by row P2); missing shows `—`. The accessible name includes the direction and comes from `t()`. The vi-VN phrases for the three directions are [NEEDS CLARIFICATION] (`research.md` R15 / plan O6): assert that the three names differ, are non-empty, and equal `t(key)`, and do not lock invented wording. `PriceCell` tests give reference, ceiling, and floor as inputs and fail if the component computes them. `StatusBadge` tests require an icon and a label. Select by `data-zone`, `data-state`, `data-origin`, and ARIA role, never by CSS class. **Confirm failing**: `npx vitest run src/design-system/patterns` fails. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Files: `frontend/src/design-system/patterns/Delta/Delta.test.tsx`, `frontend/src/design-system/patterns/PriceCell/PriceCell.test.tsx`, `frontend/src/design-system/patterns/StatusBadge/StatusBadge.test.tsx`. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "8. Patterns"; ADR-FRONTEND-005 — "Decision".

- [ ] T033 [P] [US4] Design row B4-T4. Write a Playwright test that checks computed style and the network log: `fmt.*` text `font-family` starts with `IBM Plex Mono`; UI text starts with `Be Vietnam Pro`; no request goes to a third-party font host. **Confirm failing**: the Playwright run fails before the fonts and the test dependency exist. Do not add this test to the B1 CI skeleton. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline". Files: `frontend/e2e/b4-t4-fonts.spec.ts`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T4; `docs/domains/frontend/DESIGN_SYSTEM.md` — "4. Typography"; `research.md` R16 and R18.

- [ ] T034 [P] [US4] B4-T7 chart part only (pitch part of T7; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2" step **T7 boundary lint + a11y**, chart-library clause). Write fixtures that import `lightweight-charts` outside `platform/chart` and `chart.js` outside `platform/stat-chart`. **Confirm failing**: lint does not yet reject them. Do not add either package to `package.json`. Implements "3.3 Boundary enforcement (Target G2)" rule 5. Files: `frontend/eslint-fixtures/b4-lightweight-charts-outside.ts`, `frontend/eslint-fixtures/b4-chartjs-outside.ts`. Source: ADR-FRONTEND-004 — "Decision" and "Considered Options"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-029.

### Implementation for User Story 4

> Do not edit the test files from T028–T034 or `frontend/eslint-fixtures/**`. Do not build `MessageBody`, zone shells, Storybook, `ChartEngine`, or `StatChart`.

- [ ] T035 [P] [US4] B4-T6. Implement `fmt.price`, `fmt.change`, `fmt.pct`, `fmt.vnd`, `fmt.volume` as custom formatters, and `fmt.dateTime` with `Intl` only. Locale `vi-VN` and time zone `Asia/Ho_Chi_Minh` are launch settings in a small module, not literals inside each call. Do not create the Zustand `UiSlice` (the shell store is B3). Volume does not call the price formatter. Do not edit T028 or T029. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam" and "10.2" step **T6**. Files: `frontend/src/platform/format/format.ts`, `frontend/src/platform/format/localeSettings.ts`, `frontend/src/platform/format/index.ts`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-022 and FR-023; `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — "SNR-7: Usability, Accessibility, and Responsive Behavior" (launch UI note).

- [ ] T036 [P] [US4] B4-T6. Implement `t()` and the vi-VN catalogue for "Tạo lại", "Không có dữ liệu", "AI gợi ý", and "Đã xác nhận". Do not add an i18n library. Do not ship an English catalogue. Do not enable `react/jsx-no-literals` ([NEEDS CLARIFICATION] `research.md` R17 / plan O7). Direction phrases for `Delta` stay [NEEDS CLARIFICATION] (`research.md` R15 / plan O6): add keys whose vi-VN values are marked `[NEEDS CLARIFICATION]` in `messages/vi-VN.ts` rather than invented copy. Do not edit T029 or T032. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam" and "10.2" step **T6**. Files: `frontend/src/platform/i18n/t.ts`, `frontend/src/platform/i18n/messages/vi-VN.ts`, `frontend/src/platform/i18n/index.ts`. Source: ADR-FRONTEND-005 — "Decision"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-024.

- [ ] T037 [US4] B4-T6. Generate dark CSS variables that satisfy T030. `<html>` carries `data-theme="dark"` in `frontend/index.html`. Do not generate light values, a theme switch, or the contrast script (rows B4-T5 and B4-T6 move to M-001). Set `data-density="compact"` on `<html>` beside `data-theme="dark"` (Product Owner, 2026-11-17, analysis X1). Do not add Style Dictionary or any other generator package. Do not invent three-part `ai.*` custom properties. Commit two-part variables in `tokens.css` so T030 passes. Do not add `npm run tokens` or a token drift check; those stay out of this delivery (analysis G3). Do not edit T030. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" and "10.2" step **T6**. Files: `frontend/src/design-system/tokens/source/color.json`, `frontend/src/design-system/tokens/generated/tokens.css`, `frontend/index.html`. Source: ADR-FRONTEND-007 — "Decision"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-025.

- [ ] T038 [P] [US4] B4-T6. Add `frontend/tailwind.config.ts` that exposes no `market` or `state` colour utilities. Do not edit T031. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" and "10.2" step **T6**. Files: `frontend/tailwind.config.ts`, `frontend/src/design-system/tokens/generated/tokens.css`. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "2. Token architecture"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-026.

- [ ] T039 [US4] B4-T6. Implement `PriceCell`, `Delta`, and `StatusBadge` so T032 passes. `Delta` shows a sign or an arrow as well as colour for a non-zero value; zero uses `market.ref` and no sign (verbatim B4-T3's zero clause is superseded by row P2). `PriceCell` does not compute reference, ceiling, or floor. `StatusBadge` always shows an icon and a label. Do not add a Radix package for these three patterns. Do not edit T032. Leave `Delta` direction copy as the [NEEDS CLARIFICATION] keys from T036. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules" and "10.2" step **T6**. Files: `frontend/src/design-system/patterns/PriceCell/PriceCell.tsx`, `frontend/src/design-system/patterns/Delta/Delta.tsx`, `frontend/src/design-system/patterns/StatusBadge/StatusBadge.tsx`. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "8. Patterns"; `research.md` R16; ADR-FRONTEND-004 — "Decision".

- [ ] T040 [P] [US4] B4-T6 fonts. Self-host Be Vietnam Pro and IBM Plex Mono under `frontend/public/fonts` and declare `@font-face` so T033 can pass. No request to a third-party font host. Add the Playwright test dependency without putting `frontend/e2e/b4-t4-fonts.spec.ts` into the B1 CI workflow. Do not edit T033. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline". Files: `frontend/public/fonts/`, `frontend/src/design-system/tokens/generated/fonts.css`, `frontend/package.json`. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "4. Typography"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-028.

- [ ] T041 [US4] B4-T7 chart part, after T026 so `eslint.config.js` has the B2 rules. Add empty seam modules that do not export `ChartEngine` or `StatChart`. Lint fails on `lightweight-charts` outside `platform/chart` and on `chart.js` outside `platform/stat-chart`. Also enable rule 4 from T031 (market and state colour reads, arbitrary Tailwind colours). Do not add `lightweight-charts` or `chart.js` to `package.json`. Do not edit the fixtures. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" rules 4 and 5, "3.4 Platform contracts", and "10.2" step **T7** (chart-library clause). Files: `frontend/src/platform/chart/index.ts`, `frontend/src/platform/stat-chart/index.ts`, `frontend/eslint.config.js`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-026 and FR-029; ADR-FRONTEND-004 — "Considered Options".

- [ ] T042 [US4] B4-T6 legacy stylesheet removal, after T037. Delete `frontend/src/App.css` and `frontend/src/index.css`, remove `UI_CONFIG.THEME`, and import the generated token stylesheet as the global stylesheet. New modules do not import `frontend/src/components/**`. Do not perform the B3 shell rebuild. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step **T6**. Files: `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/config.ts`, `frontend/src/index.tsx`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" (T6 row). B3-D9's rendered shell stays out of scope (`specs/004-m000-b-frontend-foundation-core/spec.md` — "Out of Scope").

**Checkpoint**: From `frontend/`: `npx vitest run src/platform/format src/platform/i18n src/design-system`; `npm run lint` fails on `frontend/eslint-fixtures/b4-lightweight-charts-outside.ts` and `frontend/eslint-fixtures/b4-chartjs-outside.ts`; the dark-token fixture matches, including `--market-up` = `#2EBD6B`. Run `frontend/e2e/b4-t4-fonts.spec.ts` with Playwright. Then the shared proof: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`. T028–T034 were confirmed failing before T035 and are unchanged. Playwright is not a job in the B1 CI skeleton. Source: `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "B4 proof, in addition"; `specs/004-m000-b-frontend-foundation-core/spec.md` — SC-008, SC-009, SC-010, and SC-011.

---

## Phase 5: Polish and cross-cutting proof

**Purpose**: Re-run the quickstart after B2 and B4. This phase does not add product behavior and does not edit long-lived docs.

- [ ] T043 Re-run the shared proof from `frontend/` on Node v26.13.1: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`. Confirm B0's `grok inspect` result still lists the target rules. Files read: `specs/004-m000-b-frontend-foundation-core/quickstart.md`, `frontend/package.json`. Source: `specs/004-m000-b-frontend-foundation-core/quickstart.md` — "Shared proof"; `specs/004-m000-b-frontend-foundation-core/spec.md` — SC-002.

- [ ] T044 [P] Confirm `.github/workflows/frontend-ci.yml` orders lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`, and does not run Playwright or Storybook. Confirm `frontend/e2e/b4-t4-fonts.spec.ts` is outside that skeleton. Do not change `.github/workflows/build-push-dockerhub.yml`. Leave SNR-7.2.1 at P2. Files: `.github/workflows/frontend-ci.yml`, `.github/workflows/build-push-dockerhub.yml`, `frontend/e2e/b4-t4-fonts.spec.ts`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-014 and FR-030; SNR-7.2.1.

---

## Dependencies and execution order

### Phase dependencies

- **Phase 1 (B0 / US1)**: No dependency. Instruction files only.
- **Phase 2 (B1 / US2)**: After Phase 1. Blocks Phase 3 and Phase 4. Also waits on Node v26.13.1 (T007).
- **Phase 3 (B2 / US3) and Phase 4 (B4 / US4)**: Both after Phase 2. They run alongside each other. `frontend/package.json` and `frontend/eslint.config.js` are edited by B1, then B2 (T021, T026), then B4 (T040, T041).
- **Phase 5**: After the desired stories. B0+B1 is a coherent toolchain increment. B2 and B4 complete delivery 1.

### User story dependencies

- **US1 (B0)**: Independent. No test file.
- **US2 (B1)**: Independent of B2 and B4 once B0 is in place. Pitch T1 and pitch T2 both cite technical-design step **T2 Vite**, for different portions (FR-032).
- **US3 (B2)**: Needs the B1 toolchain. Does not need tokens or fonts. The idle-timeout test stubs `t()` inside the test file.
- **US4 (B4)**: Needs the B1 toolchain. Does not need the Socket.IO removal. Catalogue strings that B2 shows ("Tạo lại") live here; B2's production reader calls `t()`.

### Within each story

- Tests (B1, B2, B4) are written and **confirmed failing** before that story's implementation tasks.
- Implementation tasks must not edit those tests.
- B0 has no test task.
- Codegen (T021) before the hand-written client (T023). Auth types (T022) before the client. Stream reader (T024) after the client exists. T8 (T026) after the stream tests exist.
- Formatters and catalogue (T035, T036) before patterns (T039). Token CSS (T037) before the legacy stylesheet deletion (T042).

### Parallel opportunities

- T001 and T002 (B0 files).
- T004, T005, and T006 (B1 tests).
- T008 and T009 (T0 deletions).
- After Phase 2, Phase 3 and Phase 4 in parallel, except `frontend/package.json` and `frontend/eslint.config.js`.
- T017, T018, T019, and T020 (B2 tests).
- T028 through T034 (B4 tests).
- T035 and T036 (format and catalogue). T038 and T040 with those, on different files.

---

## Parallel example: B2 and B4 after B1

```text
# After T016 checkpoint, two Software Engineers:
# Engineer A (US3): T017, T018, T019, T020, then T021 → T026
# Engineer B (US4): T028 … T034, then T035, T036, T037, T038, T039, T040
# Shared files last, in order: T026 (eslint + package.json), then T040 (package.json), then T041 (eslint)
```

---

## Implementation strategy

### MVP first

1. Complete Phase 1 (B0). Stop at the `grok inspect` checkpoint.
2. Complete Phase 2 (B1). Stop at the Vite / Vitest / Docker checkpoint.
3. US1 is the smallest independent slice. US1+US2 is the smallest toolchain a later slice can run on.

### Incremental delivery

1. B0 → instruction proof.
2. B1 → `npm ci`, `tsc --noEmit`, `vitest run`, `build`, `dev`, Docker.
3. B2 and B4 together → codegen drift, Socket.IO absence, idle-timeout test, `fmt` exact outputs, dark tokens, chart-import lint, Playwright font check.
4. Do not start B3 or B5 from this file.

### What this delivery leaves undone

React Router, Zustand, TanStack Query, zone shells, `MessageBody`, Storybook, the browser MSW worker, `VITE_USE_MOCKS` as a browser acceptance, the Playwright width matrix, the axe baseline, light tokens, theme switching, the contrast script, chart interfaces, and `GET /api/market/prices/{symbol}`. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — "Out of Scope"; `docs/domains/frontend/ARCHITECTURE.md` — "8.2 Gates G1–G6" (G1 and the Frontend half of G6 are in this delivery; G2, G3, and the full G5 baseline are not).

---

## Open items (do not guess)

These stay open. A task above names each one next to the file it blocks. Source: `specs/004-m000-b-frontend-foundation-core/plan.md` — "Open items"; `research.md` R5, R7, R8, R11, R13, R15, R17, R18, R19, R20, R2.

| ID | Item | Task that stops rather than guessing |
|---|---|---|
| O1 | HTTP client package on top of `openapi-typescript`. `openapi-fetch` stays Proposed | T021 uses `fetch` and does not add the package |
| O2 | Wire field for `sessionRef.sessionId` on `POST /api/chat` | T023 omits it and does not use `ChatRequest.session_id` |
| O3 | SSE parser: in-house or `eventsource-parser` | T024 does not add `eventsource-parser`; O3 stays open |
| O4 | Resolved. Core ESLint `no-restricted-imports` for rules 1 and 2. `eslint-plugin-boundaries` stays unselected | T015 |
| O5 | Resolved for this delivery. Two-part hand-written variables. No generator. No invented `ai.*` names. Full B4-T1 and `npm run tokens` stay out | T030 and T037 |
| O6 | vi-VN accessible-name phrases for `Delta` direction | T032 and T036 |
| O7 | Which slice enables `react/jsx-no-literals` | T006, T015, and T036 do not enable it |
| O8 | Resolved. `.github/workflows/frontend-ci.yml`. Drift is the fifth step, after build | T016 and the B2 checkpoint |
| O9 | Resolved. B4 sets `data-density="compact"` beside `data-theme="dark"` | T037 |
| O10 | Performance budgets. Technical design status is TBD | No task sets a number |
| O11 | Node v26.13.1 is not on the laptop (22.18). B1 waits for the Product Owner | T007 |

`track.a` and `track.b` have no hex. The fixture omits them. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.2 Track".

If `.grok/rules` or `AGENT.md` recommends Create React App, Jest, `REACT_APP_*`, or Socket.IO, T003 records [NEEDS CLARIFICATION]. Those paths are outside `contracts/instruction-set.md` — "Files".

---

## Notes

- Test-first proof for SC-011 is the failing run recorded before the matching implementation task, plus unchanged test files. B0's proof is `grok inspect` and the instruction search.
- Role names in this file: Product Owner, UX Designer, Software Architect, Software Engineer.
- Do not commit, push, or open a pull request from a task. The Product Owner approves that separately.
