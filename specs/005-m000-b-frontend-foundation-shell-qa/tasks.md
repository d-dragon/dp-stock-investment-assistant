# Tasks: M-000 Frontend foundation shell and QA (delivery 2 of 2)

**Input**: Design documents from `specs/005-m000-b-frontend-foundation-shell-qa/`

**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required. The user asked for the tests that hold the quality bar, and `spec.md` — FR-001 requires test-first for B3 and for B5. Write the test task, **confirm failing**, then implement. Implementation tasks in the same story must not edit those test files or the eslint fixtures the test task planted.

**Organization**: Phase 1 and Phase 2 do not build the shell. Phase 3 is User Story 1 (B3, P1). Phase 4 is User Story 2 (B5, P2) and starts after the B3 checkpoint. Phase 5 re-runs the proofs and does not add behavior.

**Branch for later implementation**: `features/pitch-m000-B-frontend-foundation`, in a named git worktree. Do not edit the Product Owner's main tree, `main`, or the `wt/m001-s3` worktree. Do not modify `backend/`, `docs/**` (including `docs/openapi.yaml`), the Accepted ADRs, or `specs/spec-traceability.yaml`. Source: `spec.md` — FR-002; `.specify/memory/constitution.md` — "Recorded deferral when the delivery forbids the sync edit".

**Do not commit or push** from these tasks. The Product Owner approves any commit.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: [US1] B3, [US2] B5. Setup, foundational, and polish tasks have no story label
- Each task names the files it may edit, the pitch row or gate it proves, and the technical-design section it implements

## Path Conventions

- Frontend package: `frontend/`
- Commands run from `frontend/` unless the path says otherwise
- Vitest tests are colocated or under `frontend/src/test/`
- Playwright tests stay under `frontend/e2e/` (`frontend/playwright.config.ts` already sets `testDir: './e2e'`)
- Lint fixtures stay under `frontend/eslint-fixtures/` so a planted violation is not left inside `src/`

## Pitch label map (do not swap these names)

| Pitch label in this file | Meaning | TECHNICAL_DESIGN "10.2 CRA → Vite migration" step to note |
|---|---|---|
| B3-T4 | Shell split, `MessageBody`, features | **T4 shell**. The clause that turns on `react/no-danger` is stale. Delivery 1 already did that |
| B3-T5 | Router, `platform/workspace`, `useUrlSync`, zone wiring | **T5 router + store** |
| B5-T7 | Playwright + axe at four widths, one keyboard test at 1920 px | **T7 boundary lint + a11y**, the Playwright remainder only. Chart-import lint stays as delivery 1 left it |
| B5 Storybook | Dark compact catalogue, 11 to 15 stories | None. Section "8.2 Pattern rules" |
| B5 CI | Extend `.github/workflows/frontend-ci.yml` after the existing five steps | Section "10.1 Build and run" |

Design rows `B3-D1`..`B3-D9` and `B5-S1`..`B5-S3` are the quality bar. `B5-S4` is not a task.

## Quality bar (every row has a test task)

| Row or gate | Proof | Test task | Must fail before |
|---|---|---|---|
| G2, B3-D1 | Four landmarks, `/` → `/sandbox`, Z2 not resizable | T004 | T022 |
| B3-D4, SC-006 | Seven `ZoneFrame` states, `aria-busy` on loading and streaming, interrupted sends nothing for 5 s | T005 | T020 |
| G2, B3-D5, SC-002 | One zone errors, the other three stay up, `reportError` gets the zone | T006 | T019 |
| B3-D7, SC-003, §6.5 | XSS fixtures inert; dashed "AI gợi ý"; solid "Đã xác nhận" | T007 | T021 |
| G3, SC-004 | `FPT`, `VNINDEX`, `VN30` accepted; lowercase rejected; no invented character class | T008 | T016 |
| G3, ADR-FRONTEND-003 | `/sandbox/FPT` sets mirrors; a direct store write does not stick | T009 | T017 |
| FR-020 | Empty chart slot on `/sandbox`, absent on `/portfolio` | T010 | T022 |
| B3-D6, SC-005 | Draft restored from `sessionStorage`; send removes the key; stop does not | T011 | T023 |
| FR-019 | Run states, idle timeout, polite live region, "Tạo lại" sends only when activated | T012 | T023 |
| B3-D8, B3-D9, SC-007 | Lint fails a planted feature colour, a JSX literal, and a `src/components/**` import. Legacy CSS stays absent | T013 | T024 |
| B5 handlers, FR-021 | Health, config, `models/*`, chat. No price path | T026 | T031 |
| B5-S1, SC-009 | 11 to 15 dark stories, axe on every rendered case | T027 | T033 |
| B3-D2, B3-D3, B3-D6, B5-S2, SC-008 | Playwright at 1920, 1440, 1024, 768, plus keyboard order and the draft reload | T028 | T034 |
| FR-025, SC-011 | CI order, then Storybook, then Playwright. Docker trigger unchanged | T029 | T035 |
| B5-S3, SC-010 | Production `dist/` has no `msw` and no Storybook | T030 | T032 |

Source: `spec.md` — FR-001 and Success Criteria; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates"; `quickstart.md`.

---

## Phase 1: Setup

**Purpose**: Confirm the delivery 1 baseline and the worktree rule. Create no shell code.

- [x] T001 Confirm `node -v` is v26.13.1 or newer and at least `>=26.13.0`. Do not lower `frontend/package.json` `engines.node`. Do not edit `frontend/.nvmrc`. Record the worktree path the later tasks will use. Do not start those edits in the Product Owner's main tree. Files read: `frontend/package.json`, `frontend/.nvmrc`, `specs/005-m000-b-frontend-foundation-shell-qa/quickstart.md`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run"; `spec.md` — FR-002.

- [x] T002 [P] Read the delivery 1 surfaces this delivery reuses and do not recreate them: `frontend/src/platform/api/client.ts`, `frontend/src/platform/stream/openChatStream.ts`, `frontend/src/platform/i18n/t.ts`, `frontend/src/design-system/patterns/PriceCell/PriceCell.tsx`, `frontend/src/design-system/patterns/Delta/Delta.tsx`, `frontend/src/design-system/patterns/StatusBadge/StatusBadge.tsx`, `frontend/eslint.config.js` (`react/no-danger` already an error). Stop if any of those files is missing. Files read only. Source: `spec.md` — Dependencies; `research.md` R20.

---

## Phase 2: Foundational (blocks both stories)

**Purpose**: Record the pre-shell tree so later tests have a real failing baseline. No user story code yet.

**Checkpoint**: `frontend/src/app/` does not exist yet. `frontend/src/App.tsx` is still the shell.

- [x] T003 Confirm `frontend/src/test/msw/handlers.ts` handles only `POST /api/chat`, `frontend/src/App.tsx` is still the mounted shell, and `frontend/src/app/` is absent. Do not add a route, a store, or a handler in this task. Files read: `frontend/src/test/msw/handlers.ts`, `frontend/src/App.tsx`, `frontend/index.html`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree" (Current); `research.md` R6.

---

## Phase 3: User Story 1 — Modular shell, state, and safe rendering (B3) (Priority: P1) MVP

**Goal**: Z1–Z4 shell, URL-owned workspace store, `ZoneFrame`, and `MessageBody`. Gates G2 and G3. XSS fixtures inert.

**Independent Test**: From `frontend/`, `npm run lint` passes with `react/no-danger` still an error, and the Vitest files from T004 through T013 pass. Playwright is not this story's checkpoint. Source: `spec.md` — User Story 1 Independent Test; `quickstart.md` — "B3 proof".

### Tests for User Story 1

> Write these tests first. **Confirm failing** before T014. Implementation must not edit these files.

- [x] T004 [P] [US1] B3-T4, row B3-D1, gate G2. Write `frontend/src/app/layout/WorkspaceShell.test.tsx`. Render the shell at a 1920 px width. Assert `/` ends on `/sandbox`. Assert four landmarks: Z2 `banner` `data-zone="z2"`, Z1 `navigation` `data-zone="z1"`, Z3 `main` `data-zone="z3"`, Z4 `complementary` `data-zone="z4"`. Assert each accessible name equals `t('shell.zone.z1'|'shell.zone.z2'|'shell.zone.z3'|'shell.zone.z4')`, not a JSX literal. Assert Z2 has no resize handle. Assert the model selector is inside Z4, not Z2. Assert Z1 shows both tracks and an empty lifecycle frame whose accessible name is `t('shell.z1.lifecycle')` and that contains no stage rows. Select by role and `data-zone`, never by CSS class. **Confirm failing**: `npx vitest run src/app/layout/WorkspaceShell.test.tsx` fails because `WorkspaceShell` does not exist. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" and "9.2 Tests mapped to gates" (G2). Files: `frontend/src/app/layout/WorkspaceShell.test.tsx`. Source: `contracts/shell-zones.md`; `spec.md` — FR-006 and SC-001.

- [x] T005 [P] [US1] B3-T4, row B3-D4, SC-006. Write `frontend/src/design-system/patterns/ZoneFrame/ZoneFrame.test.tsx`. For each state `empty`, `loading`, `ready`, `stale`, `error`, `interrupted`, `streaming`, assert `data-state` equals that state. Assert `aria-busy="true"` for `loading` and for `streaming`. Assert `error` renders a retry control. Assert `interrupted` renders `t('stream.retry')` ("Tạo lại") and that an MSW request count stays 0 for 5 seconds until the control is activated. Assert `streaming` renders a stop control. Z2 `empty` shows `t('shell.z2.emptySymbol')`. **Confirm failing**: the pattern module does not exist. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" and `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix". Files: `frontend/src/design-system/patterns/ZoneFrame/ZoneFrame.test.tsx`. Source: `contracts/zone-frame-and-message-body.md`; `spec.md` — FR-009.

- [x] T006 [P] [US1] B3-T4, row B3-D5, gate G2, SC-002. Write `frontend/src/app/layout/ZoneHost.test.tsx`. A child that throws inside one zone leaves the other three zones showing their content. The thrown zone has `data-state="error"`. `reportError` is called with that zone id. Do not expect a vendor reporter. **Confirm failing**: `ZoneHost` does not exist. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts" and "3.5 Shell and zone component contracts". Files: `frontend/src/app/layout/ZoneHost.test.tsx`. Source: `contracts/shell-zones.md`; `spec.md` — FR-010.

- [x] T007 [P] [US1] B3-T4, row B3-D7, SC-003. Write `frontend/src/design-system/patterns/MessageBody/MessageBody.test.tsx`. Render the four XSS fixtures from `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output": `<img src=x onerror=alert(1)>`, `<script>alert(1)</script>`, `[x](javascript:alert(1))`, and an `<a onclick>`. Assert no event-handler attribute, no `script` element, and no `javascript:` href. Assert a markdown table, a list, and bold still render. Assert `data-origin="ai"` shows a dashed edge and `t('ai.suggested')`. Assert `data-origin="investor"` shows a solid edge and `t('ai.confirmed')`. Do not assert hue alone. Do not require `lucide-react`. **Confirm failing**: `MessageBody` does not exist. Implements "6.5 Safe rendering of Agent output" and `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance". Files: `frontend/src/design-system/patterns/MessageBody/MessageBody.test.tsx`. Source: `contracts/zone-frame-and-message-body.md`; `spec.md` — FR-012.

- [x] T008 [P] [US1] B3-T5, gate G3. Write `frontend/src/platform/workspace/routeParams.test.ts`. `parseTrack` accepts only `sandbox` and `portfolio`. `parseSymbol` accepts `FPT`, `VNINDEX`, and `VN30`. A segment that contains a lowercase letter is rejected. Do not add a length limit, a digit ban, or an exchange suffix. Those would invent the character class the spec refused. **Confirm failing**: `routeParams.ts` does not exist. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation". Files: `frontend/src/platform/workspace/routeParams.test.ts`. Source: `contracts/workspace-and-routes.md`; `research.md` R10; `spec.md` — FR-015.

- [x] T009 [P] [US1] B3-T5, gate G3, SC-004. Write `frontend/src/platform/workspace/useUrlSync.test.tsx`. Loading `/sandbox/FPT` sets `symbol` to `FPT` and `activeTrack` to `sandbox`. A direct store write of `symbol`, `coreObjectRef`, or `activeTrack` does not stick. A track switch restores `lastRouteByTrack`. `ui.theme` stays `dark`. Assert there is no setter that stores `light`. Assert the module exports narrow selectors, one field or one slice each, and does not create a React Context for `symbol`, pane sizes, or the draft. **Confirm failing**: the store module does not exist. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store" and ADR-FRONTEND-003 — "Decision". Files: `frontend/src/platform/workspace/useUrlSync.test.tsx`. Source: `data-model.md` — WorkspaceStore; `spec.md` — FR-016.

- [x] T010 [P] [US1] B3-T5, FR-020, SC-004. Write `frontend/src/app/router.chart-slot.test.tsx`. `/sandbox` shows an empty chart slot and no chart series. `/portfolio` shows no chart slot. Z3 empty shows `t('shell.z3.emptyInvitation')` and does not start a Case. An unknown track, a lowercase symbol, and `*` render the not-found frame inside the shell, with the four landmarks still present. The same frame renders for a supplied 404 and for a supplied 403. Do not add a Backend call or a Core-object screen. The Frontend does not decide access. No search params are read. Core-object paths are not routes. **Confirm failing**: the router does not exist. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation". Files: `frontend/src/app/router.chart-slot.test.tsx`. Source: `contracts/workspace-and-routes.md`; `spec.md` — FR-015 and FR-020.

- [x] T011 [P] [US1] B3-T5, row B3-D6, SC-005. Write `frontend/src/features/companion/draftStorage.test.ts`. The `sessionStorage` key is `dp-stock:z4-draft:${sessionId}:${conversationId}`. The value is the draft text and nothing else. Same-tab reload restores it. Send removes the key. Stop, idle timeout, and `interrupted` leave the key in place. **Confirm failing**: the draft module does not exist. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store" and "6.3 SSE client". Files: `frontend/src/features/companion/draftStorage.test.ts`. Source: `data-model.md` — Draft storage; `spec.md` — FR-011.

- [x] T012 [P] [US1] B3-T4 and B3-T5, FR-019. Write `frontend/src/features/companion/companionRun.test.tsx`. States are `idle`, `streaming`, `done`, `interrupted`, and `error`. Stop, and the delivery 1 idle timeout, move `streaming` to `interrupted` and keep the draft and the partial message. "Tạo lại" sends the same user message as a new run and sends no request until activated. The thread has `aria-live="polite"` and does not announce per token. Assert the chat body still omits `sessionId` (`frontend/src/platform/api/sessionRef.ts`). Do not add a resume or cancel request. **Confirm failing**: `features/companion` does not exist. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client" and "7. Accessibility and responsive behaviour". Files: `frontend/src/features/companion/companionRun.test.tsx`. Source: `spec.md` — FR-018 and FR-019.

- [x] T013 [P] [US1] Rows B3-D8 and B3-D9, SC-007. Plant fixtures `frontend/eslint-fixtures/b3-feature-color.tsx` (a hex literal), `frontend/eslint-fixtures/b3-jsx-literal.tsx` (a JSX string outside `·`, `—`, `/`, `%`, `₫`, `+`, `−`), and `frontend/eslint-fixtures/b3-legacy-components-import.ts` (an import from `src/components/**`). Write `frontend/src/test/b3-d8-d9-lint.test.ts` so ESLint reports an error on each fixture once the B3 rules exist, and so `frontend/src/App.css` and `frontend/src/index.css` are absent. **Confirm failing**: `react/jsx-no-literals` is off, so the JSX fixture is not an error yet. Do not enable the rule in this task. Do not put the planted literals under `frontend/src/`. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement". Files: `frontend/eslint-fixtures/b3-feature-color.tsx`, `frontend/eslint-fixtures/b3-jsx-literal.tsx`, `frontend/eslint-fixtures/b3-legacy-components-import.ts`, `frontend/src/test/b3-d8-d9-lint.test.ts`. Source: `spec.md` — FR-013 and FR-014; `research.md` R7.

### Implementation for User Story 1

> Do not edit the test files from T004–T013 or the three `b3-*` eslint fixtures.

- [x] T014 [US1] After T004–T013 are confirmed failing. Add `react-router-dom`, `zustand`, `@tanstack/react-query`, `react-resizable-panels`, `react-markdown`, and `remark-gfm` to `frontend/package.json` and refresh `frontend/package-lock.json`. Do not add `openapi-fetch`, `eslint-plugin-boundaries`, Style Dictionary, `eventsource-parser`, Tailwind, Radix, shadcn, `lucide-react`, `lightweight-charts`, or `chart.js`. Implements `docs/domains/frontend/ARCHITECTURE.md` — "5.1 Decided" for the packages this delivery adopts, and `research.md` R1, R2, and R3 for the ones it does not. Files: `frontend/package.json`, `frontend/package-lock.json`. Source: `plan.md` — Technical Context.

- [x] T015 [P] [US1] After T014 starts. Add catalogue keys in `frontend/src/platform/i18n/messages/vi-VN.ts`: `shell.z2.emptySymbol` is exactly `Chưa chọn mã`. Add `shell.skipToWorkspace`, `shell.zone.z1`, `shell.zone.z2`, `shell.zone.z3`, `shell.zone.z4`, `shell.z1.lifecycle`, and `shell.z3.emptyInvitation` as vi-VN strings. `shell.z1.lifecycle` names the empty lifecycle frame and does not name a stage. Tests must keep asserting the key, not a fixed sentence, except `shell.z2.emptySymbol`. The Z3 invitation must not say a Case was started. Do not fill `delta.up`, `delta.down`, or `delta.flat`. Do not add an i18n library. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam". Files: `frontend/src/platform/i18n/messages/vi-VN.ts`. Source: `plan.md` — Open items O1 and O2; `spec.md` — FR-003.

- [x] T016 [P] [US1] B3-T5. Add pure `parseTrack` and `parseSymbol` in `frontend/src/platform/workspace/routeParams.ts` so T008 passes. Do not add a character class beyond "non-empty and no lowercase letter". Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation". Files: `frontend/src/platform/workspace/routeParams.ts`. Source: `research.md` R10.

- [x] T017 [US1] B3-T5, after T014 and T016. Add the Zustand store and `useUrlSync` so T009 passes. One store, slices `workspace`, `context`, `layout`, and `ui`. `useUrlSync` is the only writer of `symbol`, `coreObjectRef`, and `activeTrack`. Persist `context` and pane sizes to `sessionStorage`. `ui.theme` is the literal `dark` with no `light` member and no switcher. Export narrow selectors only, one field or one slice each. Do not put `symbol`, pane sizes, or the draft in a React Context. Devtools middleware only when `import.meta.env.DEV` is true. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store" and `docs/domains/frontend/ARCHITECTURE.md` — "6.1 State ownership matrix". Files: `frontend/src/platform/workspace/store.ts`, `frontend/src/platform/workspace/useUrlSync.ts`, `frontend/src/platform/workspace/index.ts`. Source: `data-model.md`; `spec.md` — FR-016.

- [x] T018 [P] [US1] After T014. Add `frontend/src/platform/api/keys.ts` with `qk.health()`, `qk.config()`, and `qk.models(provider)` only. Add `frontend/src/app/providers.tsx` with `QueryClientProvider`. Do not set `staleTime`, `retry`, or `refetchOnWindowFocus`. Do not call a prices key. Keep the hand-written client. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.3 Query key taxonomy". Files: `frontend/src/platform/api/keys.ts`, `frontend/src/app/providers.tsx`. Source: `research.md` R15; `spec.md` — FR-017; `plan.md` — Open item O3.

- [x] T019 [P] [US1] Add `frontend/src/platform/observability/reportError.ts` as a console sink and `frontend/src/app/layout/ZoneHost.tsx` so T006 passes. A throw sets that zone to `data-state="error"` and passes the zone id to `reportError`. Do not add a vendor SDK. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts" and "3.5 Shell and zone component contracts". Files: `frontend/src/platform/observability/reportError.ts`, `frontend/src/app/layout/ZoneHost.tsx`. Source: `spec.md` — FR-010; `plan.md` — Open item O6.

- [x] T020 [US1] B3-T4, after T015. Add `frontend/src/design-system/patterns/ZoneFrame/ZoneFrame.tsx` and `index.ts` so T005 passes. User-facing strings go through `t()`. Implements `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix" and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts". Files: `frontend/src/design-system/patterns/ZoneFrame/ZoneFrame.tsx`, `frontend/src/design-system/patterns/ZoneFrame/index.ts`. Source: `spec.md` — FR-009.

- [x] T021 [US1] B3-T4, after T014 and T015. Add `frontend/src/design-system/patterns/MessageBody/MessageBody.tsx` and `index.ts` so T007 passes. Use `react-markdown` and `remark-gfm`. No `rehype-raw`. `skipHtml` on. Default `urlTransform`. Links use `rel="noopener noreferrer nofollow"` and `target="_blank"`. Images off. No `dangerouslySetInnerHTML`. Provenance colour stays in the design-system token layer, not in a feature file. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output". Files: `frontend/src/design-system/patterns/MessageBody/MessageBody.tsx`, `frontend/src/design-system/patterns/MessageBody/index.ts`. Source: `spec.md` — FR-012; `research.md` R14.

- [x] T022 [US1] B3-T4 and B3-T5, after T015, T017, T018, T019, T020, and T021. Add `frontend/src/main.tsx`, `frontend/src/app/router.tsx`, and `frontend/src/app/layout/WorkspaceShell.tsx` so T004 and T010 pass. Point `frontend/index.html` at `/src/main.tsx`. Keep the existing noscript sentence. `/` redirects to `/sandbox`. Z1 includes the empty lifecycle frame from T004. Routes are only the M-000 set. Do not read search params. A supplied 404 or 403 uses the same not-found frame as an unknown track. Do not add a Core-object route. Feature route elements are `React.lazy`. No performance budget. Z2 is fixed. Z1, Z3, and Z4 use `react-resizable-panels` and the handles are keyboard operable. Below 1440 px, Z4 is an overlay drawer opened from the Z2 utilities corner with `aria-expanded`. At 1440 px and above that toggle is not the opener. Below 1024 px, Z1 is a 56 px rail: both track icons have an `aria-label` and a tooltip, text labels only on hover or focus, and the active track has a visible mark. Do not assert 240 px or 440 px. No account menu. Move `frontend/src/components/models/ModelSelector.tsx` into `frontend/src/features/models/` and compose it in the Z4 header. The feature's public import is `index.ts` only. Delete `frontend/src/App.tsx`, `frontend/src/index.tsx`, and the legacy model file. No new file imports `src/components/**`. Implements `docs/domains/frontend/ARCHITECTURE.md` — "4.1 Shell zones" and "4.3 Building blocks", and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree" and "3.5 Shell and zone component contracts". Files: `frontend/src/main.tsx`, `frontend/src/app/router.tsx`, `frontend/src/app/layout/WorkspaceShell.tsx`, `frontend/src/features/models/index.ts`, `frontend/index.html`, `frontend/src/App.tsx`, `frontend/src/index.tsx`, `frontend/src/components/models/ModelSelector.tsx`. Source: `contracts/shell-zones.md`; `spec.md` — FR-004, FR-005, FR-006, FR-007, FR-008, and FR-014; `research.md` R9 and R12.

- [x] T023 [US1] B3-T4, after T017 and T022. Add `frontend/src/features/companion/` so T011 and T012 pass. Hold `sessionRef` once on the run. Do not copy it into the workspace slices. Call the delivery 1 stream. Do not send `sessionId` on the wire. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.1 Ownership" and "6.3 SSE client". Files: `frontend/src/features/companion/index.ts`, `frontend/src/features/companion/draftStorage.ts`, `frontend/src/features/companion/Companion.tsx`. Source: `spec.md` — FR-011, FR-018, and FR-019; `plan.md` — Open item O5.

- [x] T024 [US1] After T022 and T023. Enable `react/jsx-no-literals` on `frontend/src/app/`, `frontend/src/features/`, and `frontend/src/design-system/patterns/` with the allowed strings `·`, `—`, `/`, `%`, `₫`, `+`, `−`. Extend core `no-restricted-imports` so `platform` and `design-system` cannot import `app` or `features`, and so a feature cannot deep-import another feature. Do not add `eslint-plugin-boundaries`. Leave `react/no-danger` as an error. Point the new fixtures at those rules so T013 passes. Exclude `frontend/eslint-fixtures` from `tsc`. Do not edit the fixtures or T013. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement". Files: `frontend/eslint.config.js`, `frontend/tsconfig.json`. Source: `research.md` R7 and R8; `spec.md` — FR-013.

**Checkpoint**: From `frontend/`, `npm run lint`, `npx tsc --noEmit`, and `npx vitest run` pass. T004 through T013 were confirmed failing before T014 and are unchanged. G2, G3, and the XSS cases are green. Rows B3-D2, B3-D3, and B3-D6 are not green yet. Their Playwright files are Phase 4. Source: `quickstart.md` — "B3 proof"; `spec.md` — SC-001 through SC-007.

- [x] T025 [US1] Run the B3 checkpoint and change no test file. If `npm run lint` or `npx vitest run src/app src/features src/platform/workspace src/design-system/patterns src/test/b3-d8-d9-lint.test.ts` fails, fix production code only. Files read: `specs/005-m000-b-frontend-foundation-shell-qa/quickstart.md`. Source: `spec.md` — FR-001 and FR-026.

---

## Phase 4: User Story 2 — MSW, minimal Storybook, and Frontend CI (B5) (Priority: P2)

**Goal**: The same OpenAPI-typed handlers in Vitest and in the browser, a dark compact Storybook set of 11 to 15 stories, Playwright with axe, and CI steps after the delivery 1 skeleton. Nothing from MSW or Storybook in `dist/`.

**Independent Test**: From `frontend/`, `npm run build-storybook` and `npx playwright test` pass, and `rg -l "msw|mockServiceWorker" dist` prints nothing. Source: `spec.md` — User Story 2 Independent Test; `quickstart.md` — "B5 proof".

**Depends on**: Phase 3 checkpoint. The shell those Playwright tests measure must already exist.

### Tests for User Story 2

> Write these tests first. **Confirm failing** before T031. Implementation must not edit these files. Keep `frontend/e2e/b4-t4-fonts.spec.ts` as delivery 1 left it.

- [x] T026 [P] [US2] FR-021. Write `frontend/src/test/b5-handlers.test.ts`. Import the shared handler list from `frontend/src/mocks/handlers.ts`. Assert it covers `getHealth` (`GET /api/health`), `getConfig` (`GET /api/config`), `postChat` (`POST /api/chat`, delivery 1 SSE frames), and the five model operations `listOpenAIModels`, `refreshOpenAIModels`, `getSelectedModel`, `selectModel`, and `setDefaultModel`. Assert no other operation and no `GET /api/market/prices/{symbol}`. Assert `frontend/src/test/setup.ts` uses that same list. **Confirm failing**: `frontend/src/mocks/handlers.ts` does not exist, and today's `frontend/src/test/msw/handlers.ts` is chat only. Implements ADR-FRONTEND-008 — "Decision" and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client". Files: `frontend/src/test/b5-handlers.test.ts`. Source: `contracts/msw-storybook-ci.md`; `spec.md` — FR-021.

- [x] T027 [P] [US2] Row B5-S1, SC-009. Write `frontend/src/test/b5-story-bound.test.ts`. Collect `**/*.stories.tsx` under `frontend/src`. Assert the count is 11 to 15. Assert exactly 7 `ZoneFrame` stories, one per state. Assert at least one story each for `PriceCell`, `Delta`, `StatusBadge`, and `MessageBody`. Assert a count of 22 fails. Assert the preview sets `data-theme="dark"` and `data-density="compact"`. Assert no light theme, no theme-toggle story, and no snapshot story. **Confirm failing**: the count is 0. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Files: `frontend/src/test/b5-story-bound.test.ts`. Source: `spec.md` — FR-023; `research.md` R5.

- [x] T028 [P] [US2] B5-T7, rows B3-D2, B3-D3, B3-D6, and B5-S2, SC-008. Write `frontend/e2e/b3-d2-keyboard.spec.ts`, `frontend/e2e/b3-d3-widths.spec.ts`, `frontend/e2e/b3-d6-draft.spec.ts`, and `frontend/e2e/b5-s2-axe.spec.ts`. Keyboard test at 1920 px only: skip link, then Z2, Z1, Z3, Z4, and a `:focus-visible` outline of at least 2 px. Widths exactly 1920, 1440, 1024, and 768. At 1440 and above, four zones are side by side and the drawer toggle is not the opener. Below 1440, Z4 is an overlay drawer with `aria-expanded` on the Z2 toggle. Below 1024, Z1 is 56 px and both track icons have an `aria-label`. At 768, Z3 is at least 712 px. Bounding boxes do not overlap. `scrollWidth <= clientWidth`. Draft test: type in the Z4 composer, reload, the text remains, send, the `sessionStorage` key is gone. Axe on the shell route fails the test on a serious or critical violation. SNR-7.2.1 stays P2. Do not add an `F6` test. Do not add a 1920-and-768-only project. Assert the page was served with mocks (`document.documentElement.dataset.mocks === 'on'`), which is absent until T032. **Confirm failing**: `npx playwright test e2e/b3-d2-keyboard.spec.ts` fails on that mock marker or on a missing shell. Do not edit `frontend/e2e/b4-t4-fonts.spec.ts`. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour" and "9.1 Pyramid". Files: `frontend/e2e/b3-d2-keyboard.spec.ts`, `frontend/e2e/b3-d3-widths.spec.ts`, `frontend/e2e/b3-d6-draft.spec.ts`, `frontend/e2e/b5-s2-axe.spec.ts`. Source: `contracts/msw-storybook-ci.md`; `spec.md` — FR-024; `plan.md` — Open item O9.

- [x] T029 [P] [US2] FR-025, SC-011. Write `frontend/src/test/b5-ci-order.test.ts`. Read `.github/workflows/frontend-ci.yml` and assert the job order is lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`, then Storybook (`build-storybook` and the story axe run), then Playwright. Read `.github/workflows/build-push-dockerhub.yml` and assert `on:` is still `push` to `main` and `workflow_dispatch`. **Confirm failing**: the workflow has no Storybook or Playwright step. Do not edit either workflow in this task. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run". Files: `frontend/src/test/b5-ci-order.test.ts`. Source: `contracts/msw-storybook-ci.md`; `research.md` R16.

- [x] T030 [P] [US2] Row B5-S3, SC-010. Write `frontend/src/test/b5-s3-bundle.test.ts`. Assert `frontend/src/mocks/browser.ts` exists and is imported from `frontend/src/main.tsx` only behind `import.meta.env.VITE_USE_MOCKS === 'true'` via a dynamic `import()`. Assert a production build command does not set that flag. When `frontend/dist` exists, assert `rg -l "msw|mockServiceWorker" dist` would print nothing (search the dist text from the test). Assert Storybook runtime strings are absent from `dist/`. **Confirm failing**: `frontend/src/mocks/browser.ts` does not exist. Implements ADR-FRONTEND-008 — "Decision". Files: `frontend/src/test/b5-s3-bundle.test.ts`. Source: `spec.md` — FR-022.

### Implementation for User Story 2

> Do not edit the test files from T026–T030 or the Playwright specs from T028.

- [x] T031 [US2] After T026–T030 are confirmed failing. Move the chat handler to `frontend/src/mocks/handlers.ts` and add health, config, and the five model operations, typed from `frontend/src/platform/api/generated/schema.d.ts`. Point `frontend/src/test/setup.ts` at that module. Keep `frontend/src/test/msw/chat-frames.ts` as the SSE body. Do not add a price handler. Do not let a feature import `msw`. Make T026 pass. Implements ADR-FRONTEND-008 — "Decision" and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client". Files: `frontend/src/mocks/handlers.ts`, `frontend/src/test/setup.ts`, `frontend/src/test/msw/handlers.ts`. Source: `spec.md` — FR-021; `research.md` R6.

- [x] T032 [US2] After T031. Add `frontend/src/mocks/browser.ts`. Start the worker only when `import.meta.env.VITE_USE_MOCKS === 'true'`. Set `document.documentElement.dataset.mocks = 'on'` in that branch only. Dynamic-import it from `frontend/src/main.tsx`. Make T030 pass. Do not edit T030. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run". Files: `frontend/src/mocks/browser.ts`, `frontend/src/main.tsx`. Source: `spec.md` — FR-022.

- [x] T033 [US2] After T020 and T021, and after the T027 failing run. Add Storybook with the Vitest addon. Scripts `build-storybook` and the story test script the CI step will call. Preview sets `data-theme="dark"` and `data-density="compact"`. Ship 11 to 15 stories: exactly 7 `ZoneFrame` stories, plus at least one each for `PriceCell`, `Delta`, `StatusBadge`, and `MessageBody`. Up, down, zero, missing, and the three `MessageBody` cases are variants when they are not their own stories. Run axe on every rendered case. A serious or critical issue fails. Do not add a light theme, a theme toggle, token pages, visual snapshots, or a 22-file catalogue. Tier D button and input stories are not required. Leave `delta.up`, `delta.down`, and `delta.flat` as `[NEEDS CLARIFICATION]`. Make T027 pass. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Files: `frontend/package.json`, `frontend/package-lock.json`, `frontend/.storybook/preview.tsx`, `frontend/src/design-system/patterns/ZoneFrame/ZoneFrame.stories.tsx`, `frontend/src/design-system/patterns/PriceCell/PriceCell.stories.tsx`, `frontend/src/design-system/patterns/Delta/Delta.stories.tsx`, `frontend/src/design-system/patterns/StatusBadge/StatusBadge.stories.tsx`, `frontend/src/design-system/patterns/MessageBody/MessageBody.stories.tsx`. Source: `spec.md` — FR-023; `research.md` R5; `plan.md` — Open item O4.

- [x] T034 [US2] B5-T7, after T032 and T033. Add `@axe-core/playwright`. Add `npm run e2e` as `playwright test`. Set the existing webServer command so `VITE_USE_MOCKS=true` for the e2e run. Make T028 pass. Do not edit the four new spec files or `frontend/e2e/b4-t4-fonts.spec.ts`. Do not add `F6`. Do not reduce the matrix to two widths. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour" and "9.1 Pyramid". Files: `frontend/package.json`, `frontend/playwright.config.ts`. Source: `spec.md` — FR-024; `research.md` R4.

- [x] T035 [US2] After T033 and T034. Extend `.github/workflows/frontend-ci.yml` so Storybook and then Playwright follow the existing five steps. Make T029 pass. Do not edit `.github/workflows/build-push-dockerhub.yml`. Do not edit T029. Implements `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run". Files: `.github/workflows/frontend-ci.yml`. Source: `spec.md` — FR-025; `research.md` R16.

**Checkpoint**: From `frontend/`, `npm run build-storybook`, `npx playwright test`, and `npm run build` pass, and `rg -l "msw|mockServiceWorker" dist` prints nothing. T026 through T030 are unchanged. `frontend/e2e/b4-t4-fonts.spec.ts` still passes. Source: `quickstart.md` — "B5 proof"; `spec.md` — SC-008 through SC-011.

- [x] T036 [US2] Run the B5 checkpoint and change no test file. If a new spec fails, fix production code, Storybook config, or CI only. Files read: `specs/005-m000-b-frontend-foundation-shell-qa/quickstart.md`, `frontend/e2e/b4-t4-fonts.spec.ts`. Source: `spec.md` — FR-001 and FR-026.

---

## Phase 5: Polish and cross-cutting proof

**Purpose**: Re-run the shared proof. Do not add product behavior. Do not edit long-lived docs. There is no traceability-refresh task. Constitution 2.7.0 defers that refresh.

- [x] T037 From `frontend/`, run `npm ci`, `npx tsc --noEmit`, `npx vitest run`, and `npm run build`. Then run `npm run lint`, `npm run build-storybook`, and `npx playwright test`. Change no source file in this task. Files read: `specs/005-m000-b-frontend-foundation-shell-qa/quickstart.md`, `frontend/package.json`. Source: `spec.md` — FR-026 and SC-012.

- [x] T038 [P] Confirm the test files from T004–T013 and T026–T030, and the Playwright specs from T028, have no implementation-task edits. A diff that changes an assertion fails this task. Fix by reverting the test edit, not by weakening the assertion. Files read: `frontend/src/app/layout/WorkspaceShell.test.tsx`, `frontend/src/design-system/patterns/ZoneFrame/ZoneFrame.test.tsx`, `frontend/src/app/layout/ZoneHost.test.tsx`, `frontend/src/design-system/patterns/MessageBody/MessageBody.test.tsx`, `frontend/src/platform/workspace/routeParams.test.ts`, `frontend/src/platform/workspace/useUrlSync.test.tsx`, `frontend/src/app/router.chart-slot.test.tsx`, `frontend/src/features/companion/draftStorage.test.ts`, `frontend/src/features/companion/companionRun.test.tsx`, `frontend/src/test/b3-d8-d9-lint.test.ts`, `frontend/src/test/b5-handlers.test.ts`, `frontend/src/test/b5-story-bound.test.ts`, `frontend/src/test/b5-ci-order.test.ts`, `frontend/src/test/b5-s3-bundle.test.ts`, `frontend/e2e/b3-d2-keyboard.spec.ts`, `frontend/e2e/b3-d3-widths.spec.ts`, `frontend/e2e/b3-d6-draft.spec.ts`, `frontend/e2e/b5-s2-axe.spec.ts`. Source: `spec.md` — FR-001 and SC-012.

- [x] T039 [P] Confirm the open items were not guessed. `frontend/package.json` has no Tailwind, Radix, `openapi-fetch`, `eslint-plugin-boundaries`, `eventsource-parser`, `lightweight-charts`, or `chart.js`. No query default was copied from the Proposed numbers. No performance budget was added. `delta.up`, `delta.down`, and `delta.flat` are still `[NEEDS CLARIFICATION]`. Chat requests still omit `sessionId`. No price handler exists. Files read: `frontend/package.json`, `frontend/src/platform/api/keys.ts`, `frontend/src/platform/i18n/messages/vi-VN.ts`, `frontend/src/mocks/handlers.ts`, `frontend/src/platform/api/sessionRef.ts`. Source: `plan.md` — Open items O3, O4, O5, O7, and O8.

- [x] T040 [P] Confirm `.github/workflows/build-push-dockerhub.yml` `on:` is unchanged. Confirm no task edited `docs/**`, an Accepted ADR, or `specs/spec-traceability.yaml`. Confirm SNR-7.2.1 is still P2 in the spec and that no `F6` test and no visual snapshot were added. Files read: `.github/workflows/build-push-dockerhub.yml`, `specs/005-m000-b-frontend-foundation-shell-qa/spec.md`, `frontend/e2e/`. Source: `spec.md` — FR-002 and FR-025; `.specify/memory/constitution.md` — "Recorded deferral when the delivery forbids the sync edit".

---

## Dependencies and execution order

### Phase dependencies

- **Phase 1**: No code dependency. T001 blocks implementation if Node is too old.
- **Phase 2**: After Phase 1. Blocks Phase 3.
- **Phase 3 (US1 / B3)**: After Phase 2. Blocks Phase 4.
- **Phase 4 (US2 / B5)**: After the Phase 3 checkpoint (T025).
- **Phase 5**: After T036.

### User story dependencies

- **US1 (B3)**: Depends on delivery 1, not on B5. This is the MVP.
- **US2 (B5)**: Depends on the shell, the store, `ZoneFrame`, and `MessageBody`. Playwright measures that shell. Storybook stories import those patterns.

### Within each story

- Tests are written and **confirmed failing** before that story's first implementation task.
- Implementation must not edit those tests.
- US1: T014 (packages) before modules that import them. T016 (route params) and T015 (catalogue) can follow T014 in parallel. T017 needs T016. T020 needs T015. T021 needs T014 and T015. T022 needs the store, the query provider, `ZoneHost`, `ZoneFrame`, and `MessageBody`. T023 needs the shell. T024 needs the new source tree. T025 is last.
- US2: T031 (handlers) before T032 (browser worker). T033 (Storybook) and T034 (Playwright) both edit `frontend/package.json`, so T034 follows T033. T035 follows both. T036 is last.

### Parallel opportunities

- T001 and T002.
- T004 through T013 (B3 tests), eleven files, no shared write.
- After T014: T015 and T016 together. T018 and T019 together.
- T026 through T030 (B5 tests).
- T038, T039, and T040 after the proofs.

---

## Parallel example: B3 tests, then B5 tests

```text
# After T003, one wave of failing B3 tests:
T004 WorkspaceShell.test.tsx
T005 ZoneFrame.test.tsx
T006 ZoneHost.test.tsx
T007 MessageBody.test.tsx
T008 routeParams.test.ts
T009 useUrlSync.test.tsx
T010 router.chart-slot.test.tsx
T011 draftStorage.test.ts
T012 companionRun.test.tsx
T013 b3 lint fixtures and b3-d8-d9-lint.test.ts

# After T025, one wave of failing B5 tests:
T026 b5-handlers.test.ts
T027 b5-story-bound.test.ts
T028 four Playwright specs
T029 b5-ci-order.test.ts
T030 b5-s3-bundle.test.ts
```

---

## Implementation strategy

### MVP first

1. Finish Phase 1 and Phase 2. Stop if Node or the delivery 1 files are missing.
2. Write T004–T013 and confirm each fails.
3. Implement T014–T024. Stop at T025. That is the shell MVP (G2, G3, XSS, B3-D1, B3-D4, B3-D5, B3-D7, B3-D8, B3-D9).
4. Do not start Storybook or Playwright implementation before that checkpoint.

### Incremental delivery

1. B3 Vitest bar (T025).
2. B5 handlers and the production-bundle guard (T031, T032).
3. Storybook bound and axe (T033).
4. Four-width Playwright, keyboard order, draft reload (T034).
5. CI extension (T035) and the shared proof (T037).

### What this file leaves undone

Light theme, theme switching, the contrast script, visual snapshots (B5-S4), `F6`, Tier D primitive stories as a done bar, chart content, price mocks, core-object routes, identity, saved presets, typed stream events, resume, cancel, widths below 768 px, a performance budget, Tailwind, Radix, and any edit to `docs/**` or `specs/spec-traceability.yaml`. Source: `spec.md` — "Out of Scope"; `plan.md` — Complexity Tracking.

---

## Open items (do not guess)

| ID | Item | Task that stops rather than guessing |
|---|---|---|
| O1 | vi-VN sentences for the skip link and the four zone labels | T004 and T015 lock the catalogue key. They do not lock the sentence |
| O2 | `shell.z2.emptySymbol` is `Chưa chọn mã` | T005 and T015. Do not rename the sentence |
| O3 | Query timings stay at library defaults | T018 does not copy the Proposed numbers |
| O4 | Delta direction phrases stay `[NEEDS CLARIFICATION]` | T015 and T033 do not invent them |
| O5 | `sessionId` stays off `POST /api/chat` | T012 and T023 |
| O6 | Error reporter is a console sink | T019 adds no vendor SDK |
| O7 | No performance budget | T022 uses `React.lazy` and sets no number |
| O8 | No Tailwind or Radix | T014 and T039 |
| O9 | No two-width Playwright fallback unless the Product Owner records that the week ran short | T028 and T034 keep four widths |

Source: `plan.md` — Open items; `research.md` R2, R3, R10, R15, R19.

---

## Notes

- Test-first proof for SC-012 is the failing run recorded before T014 and before T031, plus unchanged test files (T038).
- Role names: Product Owner, Software Engineer.
- Do not commit, push, or open a pull request from a task.

## Phase 6: Convergence

- [x] T041 Keep Z1 beside Z3 below 1440 px, use the 56 px rail below 1024 px, keep Z3 at least 712 px wide at 768 px, and do not stack zones. Z2 stays the top banner. Z4 below 1440 px stays an overlay drawer opened from the Z2 toggle. per FR-008 (contradicts)
- [x] T042 Put a tab stop in Z2 at 1920 px so Tab order is the skip link, then Z2, Z1, Z3, Z4, and change the Playwright keyboard test so it asserts the focused node's closest zone instead of a locator that is always truthy. per FR-007 (partial)
- [x] T043 Abort the delivery 1 chat-stream handle when the investor stops a streaming run, leave the run `interrupted`, and keep the draft and the partial message. Do not add a cancel request. per FR-019 (partial)
- [x] T044 Announce the Z4 thread at message end through `aria-live="polite"`, not once per token. per FR-019 (partial)
- [x] T045 Load the M-000 feature route elements with `React.lazy`. Do not add a performance budget. per FR-015 (partial)
- [x] T046 Compose `ModelSelector` from the shell into the Z4 header so `features/companion` does not import `features/models`. per FR-005 (contradicts)
- [x] T047 Read and update OpenAI models through TanStack Query with `qk.models` only. Do not set `staleTime`, `retry`, or `refetchOnWindowFocus`, and do not add a prices key. per FR-017 (partial)
- [x] T048 Add Storybook variants for `PriceCell`, `Delta`, and `StatusBadge` (up, down, zero, missing) and for `MessageBody` (investor origin and one XSS fixture). Keep the set inside 11 to 15 stories, dark compact only, and leave the delta phrases as `[NEEDS CLARIFICATION]`. per FR-023 (partial)
- [x] T049 Run axe on every rendered Storybook case through the Vitest addon, fail on a serious or critical issue, and run that story axe step in `.github/workflows/frontend-ci.yml` after `build-storybook` and before Playwright. per FR-025 (missing)
- [x] T050 Merge the feature colour selectors into the existing `no-restricted-syntax` rule so files under `src/features/**` still fail on stream-event literals and on `var(--market-*)` and `var(--state-*)` design-token reads. per US2 agent constraints (contradicts)
- [x] T051 Drive pane sizes and the Z4 collapsed flag from the workspace layout slice, and persist pane sizes to `sessionStorage`. per FR-016 (partial)
- [x] T052 Type the five OpenAI model MSW handlers from `frontend/src/platform/api/generated/schema.d.ts`. Do not add a price handler. per FR-021 (partial)
- [x] T053 Remove the fabricated volume figure from the investor-facing shell. Keep the delivery 1 font markers (`data-ui="shell"`, the `h1`, and `data-fmt` whose text is not `25.30`) that `frontend/e2e/b4-t4-fonts.spec.ts` already requires. per Constitution III (unrequested)

## Phase 7: Verification remediation

Verification findings E1, E2, E3, and D1. F1 (FR-002 named worktree) is not a file move: this branch is already checked out in the primary tree and at `wt-004-b0-phase1`. T058 records that limit. G1 stays low and has no task. Do not edit `docs/**`, Accepted ADRs, or `specs/spec-traceability.yaml`. Do not add `lucide-react`. Do not add an `F6` test.

- [x] T054 Move the Storybook axe scan from `beforeEach` to `afterEach` in `frontend/.storybook/preview.tsx` so it runs after the story mounts. Keep the dark compact decorator. Fail on a serious or critical violation. Extend `frontend/src/test/b5-story-bound.test.ts` so the preview source calls `axe.run` from `afterEach` and does not call it from `beforeEach`. per FR-023 (E1)
- [x] T055 Run Playwright axe on the shell route at 1920, 1440, 1024, and 768 in `frontend/e2e/b5-s2-axe.spec.ts`. Fail on a serious or critical violation. Below 1440, open the Z4 drawer before the scan so Z4 is in the tree. Do not drop a width. per FR-024 (E2)
- [x] T056 On the rail below 1024 px, render a visible icon for each track inside Z1. Keep `aria-label` and `title` from `t()`. Keep the text label for hover or focus only. Keep the active-track mark beside the icon. Do not add `lucide-react`. Prove both icons in `frontend/e2e/b3-d3-widths.spec.ts`. per FR-008 (E3)
- [x] T057 At 1920 px, focus one Z1/Z3/Z4 resize handle and press `ArrowRight`. Assert that pane's width changes. Add the case to `frontend/e2e/b3-d2-keyboard.spec.ts`. Do not add an `F6` test. per FR-007 (D1)
- [x] T058 Confirm the named-worktree limit stays recorded: this checkout remains `features/pitch-m000-B-frontend-foundation`. Do not create another worktree, do not switch branches, and do not edit `backend/`, `docs/**`, Accepted ADRs, `specs/spec-traceability.yaml`, or `wt/m001-s3`. per FR-002 (F1)
