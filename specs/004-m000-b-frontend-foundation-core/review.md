# Verification Report: M-000 Frontend foundation core (delivery 1 of 2)

**Date**: 2026-11-18
**Command**: `/speckit-verify-run`
**Git branch**: `features/pitch-m000-B-frontend-foundation` (`6ea59aa` plus uncommitted delivery work)
**Feature directory**: `specs/004-m000-b-frontend-foundation-core`
**Prerequisite script**: exit 0. Its `BRANCH` label is `004-m000-b-frontend-foundation-core` (feature-directory fallback). `FEATURE_BRANCH` is true, so this is not a non-feature-branch run.
**Config**: `max_findings=50`
**Scope**: post-implementation review after the E1–E4 and G1 follow-up. No commit, push, or pull request.
**Lifecycle Status**: Verified

## Result

Delivery 1 is implemented. 44 of 44 tasks are marked done. 32 of 32 functional requirements have implementation evidence. This pass found no CRITICAL and no HIGH issues. Three residual notes remain (one MEDIUM process note, two LOW). The earlier E1, E2, E3, E4, and G1 findings are closed.

Lifecycle status is Verified as of 2026-11-18. The marker rests on this report, `.verify-done`, complete tasks, and a sync-gate result of `current`. M1, L1, and L2 stay in the table below. They do not block the marker. Phan still confirms M1 before any commit. This marker does not promote frontend target architecture to Current. The status closeout registers the feature in `specs/spec-traceability.yaml`. The task rows below still describe the verification pass, including T027's note that the traceability file was not edited during implementation.

Phan can review this checkout. A commit still needs Phan's explicit approval.

## Remediation wrap-up (closed)

These findings were open on the first verification pass and are closed on this pass.

| ID | Was | What changed | Evidence this pass |
|---|---|---|---|
| E1 | HIGH. Inline `system-ui` and light colors overrode dark tokens and Be Vietnam Pro. The font spec sampled `document.body` and a static `[data-fmt]` span. | Shell uses surface tokens and inherited Be Vietnam Pro. Warn and danger go through `StatusBadge`. Playwright reads the rendered `h1` and the first formatted time. The static probe span is gone. | `npx playwright test e2e/b4-t4-fonts.spec.ts` passed after the shell change. |
| E2 | MEDIUM. Shell English was not behind `t()`. | Current chrome in `App.tsx` and `ModelSelector.tsx` uses `t()`. Stream fallbacks use `stream.malformed`, `stream.fallback`, and `app.errorPrefix`. `index.html` title, description, and noscript match the catalogue. `delta.up`, `delta.down`, and `delta.flat` stay `[NEEDS CLARIFICATION]` (plan O6). | `catalogue.test.ts` locks the document strings. Full Vitest passed. |
| E3 | MEDIUM. Shared proof did not record `npm run dev` or the image build. | Follow-up section appended to `evidence/t043-shared-proof.md`. The original 2026-11-18 table was not rewritten. | `npm run dev` served HTTP 200 at `http://localhost:5173/` (Vite v6.4.6) and was then stopped. `docker build -f frontend/Dockerfile .` from the repo root exited 0. The untagged image was removed after the check. |
| E4 | MEDIUM. Live idle timeout fell back to a hard-coded `60000`. | `defaultIdleMs()` parses `VITE_STREAM_IDLE_TIMEOUT_MS` and throws when the value is missing or not positive. `.env.development`, `.env.production`, and `.env.test` hold `60000`. `.dockerignore` keeps those three files in the image context. | Source test forbids `\b60000\b` in `openChatStream.ts`. The production bundle inlines `6e4`. |
| G1 | LOW. Four frontend guides still described Create React App, Jest, `REACT_APP_*`, or Socket.IO. | `frontend/README.md`, `QUICK_START.md`, `REFINEMENT_SUMMARY.md`, and `FRONTEND_ANALYSIS.md` describe Vite, Vitest, and `VITE_*`. Naming those stacks in order to forbid them is allowed. | Search of those four files finds no recommendation to install or adopt them. |

`npx eslint src` exited 0 on the shell and guide changes. `npx tsc --noEmit` exited 0 on 2026-11-18 after the follow-up. `npx vitest run` exited 0: Vitest 3.2.7, 17 files, 45 tests (the pre-follow-up proof was 43 tests).

## Verification Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| M1 | Design & Structure | MEDIUM | FR-002; primary checkout | The delivery is on `features/pitch-m000-B-frontend-foundation`, and `main` was not edited. The files live in the primary working tree. The named worktree `wt-004-b0-phase1` is the same branch and commit `6ea59aa` and does not contain the B1–B4 tree, so the follow-up could not be made there. | Phan confirms this checkout before any commit. Do not copy the tree into another worktree as part of this review. |
| L1 | Design & Structure | LOW | `frontend/REACT_SETUP_GUIDE.md:149` | That guide still tells the reader to `npm install react react-dom react-scripts`. It is outside the B0 instruction set and outside the four guides named by G1. `frontend/UI_IMPROVEMENTS.md` only records that an unused `WebSocketTest` import was removed. | Leave both unless Phan wants the historical guides retired or rewritten. |
| L2 | Scenario & Test Coverage | LOW | `catalogue.test.ts`, `openChatStream.test.ts`, `e2e/b4-t4-fonts.spec.ts` | SC-011 says the story implementation leaves its test files unchanged. The E1/E2/E4 follow-up extended these three files so the font probe, the document strings, and the idle-timeout source stay locked. | Keep the extensions. Reverting them would reopen E1 and E4. |

No overflow. Findings shown: 3. Configured cap: 50.

## Task Summary

44 tasks, all `[x]`. Incomplete: 0. Expected deletions are absent: `OptimizedApp.js`, `PerformanceProfiler.js`, `WebSocketTest.tsx`, `MessageFormatter.js`, `apiService.ts`, `modelsApi.ts`, `restApiClient.js`, `webSocketService.ts`, `performance.js`, `config-overrides.js`, `webpack.config.dev.js`, `App.css`, `index.css`, and `frontend/public/index.html`. `CLAUDE.md`, `.claude/rules`, `.cursor/rules`, `.grok/rules`, and `AGENT.md` are absent, so T002 and T003 did not need to rewrite them.

| Task ID | Status | Referenced files | Notes |
|---------|--------|------------------|-------|
| T001 | Done | `frontend/AGENTS.md`, `AGENTS.md` | `frontend/AGENTS.md` is 808 bytes. |
| T002 | Done | `.github/instructions/frontend-react.instructions.md` | Stale Claude and Cursor rule paths are absent. |
| T003 | Done | B0 files, read only | Checkpoint is the instruction search plus `grok inspect` recorded in the T043 proof. |
| T004 | Done | `src/test/b1-t0-subtract.test.ts` | Passing under the full Vitest run. |
| T005 | Done | G1 smoke and MSW fixtures | Passing. |
| T006 | Done | `eslint-fixtures/b1-*` | Fixtures stay outside `eslint src` and outside `tsc`. |
| T007 | Done | `frontend/package.json` (read) | This machine is Node v26.13.1. `engines` was not loosened. |
| T008 | Done | Four unused component files | Absent. |
| T009 | Done | `apiService.ts`, `performance.js` | Absent. |
| T010 | Done | `package.json`, lockfile | TypeScript `^5.9.3`. React 18 types. |
| T011 | Done | `.nvmrc`, `.npmrc`, `Dockerfile` | `engines.node` is `>=26.13.0`. Image is `node:26-alpine` and packages `dist`. |
| T012 | Done | Vite config, root `index.html`, `tsconfig.json` | Proxy `/api` → `127.0.0.1:5000`. CRA configs absent. |
| T013 | Done | `config.ts`, `App.tsx`, `index.tsx` | `modelsApi.ts` was removed later by T025. That absence is not a missing deliverable. |
| T014 | Done | `vitest.config.ts` | jsdom. No happy-dom fallback. |
| T015 | Done | `eslint.config.js` | Rules 1–3 and `react/no-danger`. No `eslint-plugin-boundaries`. |
| T016 | Done | `.github/workflows/frontend-ci.yml` | Order is lint, tsc, Vitest, build, OpenAPI drift. |
| T017 | Done | `client.test.ts`, `client.scope.test.ts` | Passing. |
| T018 | Done | `NoAuthAdapter.test.ts` | Passing. |
| T019 | Done | stream tests | Extended after the story for the idle-env lock (L2). Passing, 4 tests in `openChatStream.test.ts`. |
| T020 | Done | socket and stream-event fixtures | Present. |
| T021 | Done | `schema.d.ts`, `gen:api` | Generated file is present. Drift step is in CI. This pass did not re-run `gen:api`. |
| T022 | Done | `platform/auth/` | `NoAuthAdapter` present. |
| T023 | Done | `platform/api/client.ts` | Same-origin client. `sessionId` is omitted on chat (O2). |
| T024 | Done | `openChatStream.ts`, adapter, `parseSse.ts` | No hard-coded `60000`. No `EventSource`. |
| T025 | Done | `App.tsx`, `ModelSelector.tsx` | Old REST and models clients are gone. Callers use `platform/api`. |
| T026 | Done | `package.json`, `eslint.config.js`, `config.ts` | `socket.io-client` is not a dependency. `API_CONFIG.WEBSOCKET` is gone. |
| T027 | Done | `evidence/snr-8.1.2.md` | Frontend part of SNR-8.1.2. Traceability file was not edited. |
| T028 | Done | format tests | Passing, including the 1,000-value property test. |
| T029 | Done | `catalogue.test.ts`, `dateTime.test.ts` | Catalogue test extended for document strings (L2). Passing. |
| T030 | Done | dark-token fixture and test | Passing. |
| T031 | Done | Tailwind test and colour fixtures | Passing. `--state-*` outside `StatusBadge` fails lint; the shell now uses `StatusBadge`. |
| T032 | Done | `Delta`, `PriceCell`, `StatusBadge` tests | Passing. Direction copy is not invented. |
| T033 | Done | `e2e/b4-t4-fonts.spec.ts` | Assertion now targets the rendered shell (L2). Playwright passed. Not in `frontend-ci.yml`. |
| T034 | Done | chart import fixtures | Present. Packages are not dependencies. |
| T035 | Done | `platform/format/` | Custom formatters. `Intl` only in `dateTime`. |
| T036 | Done | `t()`, `messages/vi-VN.ts` | Launch strings plus shell keys. Delta keys remain marked. No i18n library. No English catalogue. |
| T037 | Done | `tokens.css`, `index.html` | `data-theme="dark"` and `data-density="compact"`. |
| T038 | Done | `tailwind.config.ts` | No market or state colour utilities. |
| T039 | Done | three patterns | `PriceCell` does not compute bands. |
| T040 | Done | `public/fonts/`, `fonts.css` | Self-hosted. Playwright saw no third-party font host. |
| T041 | Done | `platform/chart`, `platform/stat-chart`, eslint | Empty seams. Rule 4 and rule 5 enabled. |
| T042 | Done | `index.tsx`, `config.ts` | `App.css` and `index.css` are gone. Shell rebuild stays B3. |
| T043 | Done | `evidence/t043-shared-proof.md` | Original shared proof plus the dev-server and image-build follow-up. |
| T044 | Done | `frontend-ci.yml` | Lint, tsc, Vitest, build, drift. No Playwright or Storybook job. Docker Hub workflow trigger was not changed. SNR-7.2.1 stays P2. |

## Requirement coverage

All of FR-001 through FR-032 have code, tests, or recorded proof. Coverage of the behavior is 32/32.

FR-002 is the exception on location only (finding M1): the behavior is on the assigned branch, and the named-worktree clause was not met.

SC-001 through SC-010 have evidence from the implementation and from this pass (`tsc`, full Vitest, Playwright fonts, dev server, image build, instruction search of the B0 files and the four guides). SC-005's `gen:api` drift command was not re-run in this pass; the CI step and the generated file are present, and the earlier T043 proof recorded that command. SC-006's `rg socket.io dist` was not re-run; `package.json` has no `socket.io` dependency and lint blocks the import. SC-011 holds for the original story implementation. The follow-up edited three test files (L2).

## Constitution alignment

No constitution MUST is violated by the implementation behavior.

Principle I (traceability refresh) stays the recorded deviation in `plan.md` — "Complexity Tracking". This delivery does not edit `docs/**`, Accepted ADRs, or `specs/spec-traceability.yaml`. This pass did not re-walk every `docs/` anchor. The plan names the stale anchors and leaves them for a later change that is allowed to touch those files.

Principles II through VII match the plan's constitution check: browser calls stay in `platform/api` and `platform/stream`; formatters do not invent prices; `PriceCell` does not compute bands; no prompt or agent-tool surface was added; the client does not edit `docs/openapi.yaml`; proofs are executable; `NoAuthAdapter` sends no token.

## Open items left as specified

Still open, and still not guessed: O1 (no `openapi-fetch`), O2 (`sessionId` omitted on chat), O3 (no `eventsource-parser`), O6 (delta direction phrases), O7 (`react/jsx-no-literals` stays off), O10 (no performance budget).

Resolved in the plan and still resolved in code: O4, O5, O8, O9.

O11's blocker is cleared on this machine (Node v26.13.1). `plan.md` still describes the laptop as Node 22.18. That sentence was not edited.

B3 and B5 stay reserved. The shell remains `frontend/src/App.tsx`.

## Metrics

- Total tasks: 44 completed / 44 total
- Requirement coverage: 32 / 32 with implementation evidence (FR-002 location is M1)
- Files checked this pass: the task deliverable set above, the four guides, the font spec, the idle-timeout source, and the CI workflow
- Critical issues: 0
- High issues: 0
- Medium issues: 1
- Low issues: 2

## Next actions

Lifecycle status is Verified. Residual findings M1, L1, and L2 stay in the table above. Do not commit, push, or open a pull request until Phan approves that action.

Before a commit, Phan should accept M1 (this primary checkout) and decide whether L1's setup guide is in or out of the change.

## Remediation offer

Would you like concrete remediation edits for the top issues (M1, L1, L2)? They will not be applied unless you ask.
