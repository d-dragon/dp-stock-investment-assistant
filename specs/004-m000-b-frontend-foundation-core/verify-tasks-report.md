# Verify-tasks report: 004-m000-b-frontend-foundation-core

**Date**: 2026-11-18 (T043 re-checked and the shared proof re-run; T001–T042 and T044 carried forward from 2026-11-17)
**Scope**: `all` (diff `origin/main` to the working tree, plus untracked files). This invocation filtered to T043.
**Branch**: `features/pitch-m000-B-frontend-foundation`
**Completed tasks checked**: 44 (T001–T044)
**Git**: available, not a shallow clone. Base ref `origin/main`. Changed set: 62 tracked paths plus 158 untracked paths.
**Prerequisites**: `.specify/scripts/bash/check-prerequisites.sh` is not in this repo. The Windows script `.specify/scripts/powershell/check-prerequisites.ps1 -Json` resolved `FEATURE_DIR` to this directory. `spec.md`, `plan.md`, and `tasks.md` are present.

> ⚠️ **FRESH SESSION ADVISORY**: For maximum reliability, run `/speckit.verify-tasks` in a **separate** agent session from the one that performed `/speckit.implement`. The implementing agent's context biases it toward confirming its own work. This report was produced in the same session that implemented Phases 1–5. Doubt was resolved by flagging.

## Summary scorecard

| Verdict | Count |
|---|---|
| ✅ VERIFIED | 43 |
| 🔍 PARTIAL | 1 |
| ⚠️ WEAK | 0 |
| ❌ NOT_FOUND | 0 |
| ⏭️ SKIPPED | 0 |

## Flagged items

### T013 — 🔍 PARTIAL

**Task**: B1-T1. Replace `process.env.REACT_APP_*` reads and remove the hard-coded `http://localhost:5000` so calls use the empty `VITE_API_BASE_URL` and the dev proxy. Files: `frontend/src/config.ts`, `frontend/src/services/modelsApi.ts`, `frontend/src/App.tsx`, `frontend/src/index.tsx`.

| Layer | Result | Evidence |
|---|---|---|
| 1 File existence | negative | `frontend/src/services/modelsApi.ts` is absent. `config.ts`, `App.tsx`, and `index.tsx` exist. |
| 2 Git diff | positive | The three surviving files are in the `all` change set. `modelsApi.ts` is also in that set as a deletion. |
| 3 Content | positive | `config.ts` reads `import.meta.env.VITE_API_BASE_URL` and defaults to `''`. No `REACT_APP_` match under `frontend/src`. `client.ts` exports `modelsApi`. |
| 4 Dead code | positive | `App.tsx` imports `getConfig` and `getHealth` from `platform/api/client`. `ModelSelector.tsx` imports `modelsApi` from that client. |
| 5 Semantic | positive ⚠️ Interpretive | The Vite base URL and proxy path are implemented. The missing file is the deletion T025 requires (fold `modelsApi.ts` into the platform client). This is a sequenced deletion, not an empty stub. Layer 1 still fails because the path named on T013 does not exist now. |

## Verified items

| Task | Summary |
|---|---|
| T001 | `frontend/AGENTS.md` and root `AGENTS.md` state Vite, Vitest, `VITE_*`, no `socket.io-client` / WebSocket / EventSource, fetch only in `platform/api` and `platform/stream`, and `features/` + `platform/`. The frontend file is far under 10,000 characters and forbids recommending Create React App, Jest, `REACT_APP_*`, and Socket.IO. |
| T002 | `.github/instructions/frontend-react.instructions.md` states the same rules and the same prohibition. `CLAUDE.md`, `.claude/rules`, and `.cursor/rules` are absent, which the task allows. |
| T003 | The three instruction files contain the target rules and the prohibition. ⚠️ Interpretive: `grok inspect` was not re-run in this pass; the rule text is in the files that command lists. |
| T004 | `b1-t0-subtract.test.ts` exists. A search of `frontend/src` finds no `MessageFormatter`, `dangerouslySetInnerHTML`, or `REACT_APP_`. |
| T005 | G1 smoke, MSW chat frames, handlers, and `setup.ts` exist. |
| T006 | The four B1 lint fixtures exist (reverse import, deep import, fetch, `dangerouslySetInnerHTML`). |
| T007 | `node -v` is `v26.13.1`. `engines.node` is `>=26.13.0`. |
| T008 | `OptimizedApp.js`, `PerformanceProfiler.js`, `WebSocketTest.tsx`, and `MessageFormatter.js` are absent and listed in the diff. |
| T009 | `apiService.ts` and `performance.js` are absent and listed in the diff. |
| T010 | Direct `typescript` `^5.9.3`, `@types/react` `^18.3.24`, `@types/react-dom` `^18.3.7`. |
| T011 | `.nvmrc` is `26`, `.npmrc` is `engine-strict=true`, Dockerfile is `FROM node:26-alpine` and `COPY --from=build /app/dist`. |
| T012 | `dev` and `build` are Vite. Proxy sends `/api` to `http://127.0.0.1:5000`. `tsconfig` target is `ES2022`, `moduleResolution` is `bundler`, and `eslint-fixtures` is excluded. `config-overrides.js` and `webpack.config.dev.js` are absent. |
| T014 | `vitest.config.ts` uses `environment: 'jsdom'` and lists `setup.ts`. Dependencies include Vitest, Testing Library, jsdom, and MSW. No happy-dom fallback. |
| T015 | `eslint.config.js` sets `react/no-danger` to error and restricts `fetch`, `XMLHttpRequest`, `EventSource`, `WebSocket`, `socket.io-client`, and `axios`. `react/jsx-no-literals` is not enabled. `eslint-plugin-boundaries` is not a dependency. |
| T016 | `frontend-ci.yml` order is lint, `tsc --noEmit`, `vitest run`, build, then `gen:api` and `git diff --exit-code`. No Playwright or Storybook step. `build-push-dockerhub.yml` is unchanged; its `on:` is still `push` to `main` and `workflow_dispatch`. |
| T017 | Client tests exist and assert `same-origin`, no `Authorization`, no `X-User-ID`, 401 `onUnauthorized`, and omission of `session_id`. |
| T018 | `NoAuthAdapter.test.ts` and `fakeAuthAdapter.ts` exist. |
| T019 | Stream, adapter, and idle-timeout tests exist and import `openChatStream`, `legacyChatAdapter`, and `parseSse`. |
| T020 | Socket.IO and out-of-union stream-event fixtures exist. |
| T021 | `gen:api` runs `openapi-typescript` onto `schema.d.ts`. That file exports `paths` and `components`. `openapi-fetch` is not a dependency. |
| T022 | `NoAuthAdapter` returns null / empty headers and no-ops `signIn`, `signOut`, and `onUnauthorized`, as the task requires. `client.ts` imports it. |
| T023 | `apiFetch` forces `credentials: 'same-origin'`, applies `csrfHeaders()`, deletes `Authorization` and `X-User-ID`, and calls `onUnauthorized` on 401. `chatRequestFromSession` writes `conversation_id` and does not write `session_id`. |
| T024 | `openChatStream` uses the API client, `createSseParser`, and an idle timer defaulting to 60000. `frontend/.env.example` sets `VITE_API_BASE_URL` empty. `eventsource-parser` is not a dependency. |
| T025 | `restApiClient.js` and `modelsApi.ts` are absent. `App.tsx` and `ModelSelector.tsx` call the platform client. `App.tsx` is not split into `app/` and `features/`. |
| T026 | `socket.io-client` is not in `package.json`. `webSocketService.ts` is absent. `config.ts` has no `WEBSOCKET`. ESLint bans `socket.io-client`. |
| T027 | `evidence/snr-8.1.2.md` records status "Frontend part verified" against the MSW fixture and states that Backend headers, heartbeats, and HTTP/2 were not changed. |
| T028 | Format tests exist and import `fmt`. |
| T029 | Catalogue and `dateTime` tests exist. |
| T030 | Dark fixture and test exist. The test asserts `--market-up` `#2EBD6B`. |
| T031 | Tailwind test and the three colour fixtures exist. |
| T032 | Delta, PriceCell, and StatusBadge tests exist and select by role / `t()`, not by CSS class. |
| T033 | `e2e/b4-t4-fonts.spec.ts` asserts Be Vietnam Pro, IBM Plex Mono, and no third-party font host. It is not a CI step. |
| T034 | Chart-library fixtures import `lightweight-charts` and `chart.js`. Neither package is in `package.json`. |
| T035 | `fmt.price`, `change`, `pct`, `vnd`, and `volume` are custom formatters. `Intl` appears only in `dateTime`, which reads `localeSettings` (`vi-VN`, `Asia/Ho_Chi_Minh`). Volume does not call `price`. |
| T036 | `t()` returns the four vi-VN strings. Direction keys are `[NEEDS CLARIFICATION]`. No English catalogue file and no i18n library. |
| T037 | `tokens.css` sets `--market-up: #2EBD6B` and the other two-part dark variables. `index.html` has `data-theme="dark"` and `data-density="compact"`. |
| T038 | `tailwind.config.ts` colour keys are only `surface` and `accent`. |
| T039 | `PriceCell` colours by equality to ceiling, then floor, then comparison with reference. `Delta` shows an arrow plus `fmt` text and a `t('delta.*')` name. `StatusBadge` renders an `svg` and the label. |
| T040 | Three non-empty woff2 files (21168, 11532, 14708 bytes). `fonts.css` declares same-origin `@font-face`. `@playwright/test` is a devDependency. |
| T041 | `platform/chart` and `platform/stat-chart` are `export {}` and do not export `ChartEngine` or `StatChart`. ESLint tells outside imports to use those seams. |
| T042 | `App.css` and `index.css` are absent. `UI_CONFIG` has no `THEME`. `index.tsx` imports `tokens.css` and `fonts.css`. Platform and design-system sources do not import `components/`. |
| T043 | Re-run on 2026-11-18 from `frontend/` on Node v26.13.1. `npm ci`, `npx tsc --noEmit`, `npx vitest run` (17 files, 43 tests), and `npm run build` (Vite 6.4.6) all exited 0. `grok inspect` lists root `Agents.md` and `frontend/Agents.md`. Exit codes are in `evidence/t043-shared-proof.md`. |
| T044 | CI order matches T016. The font spec is outside that workflow. Docker `on:` is unchanged. |

## Unassessable items

None.

## Machine-parseable verdicts

| T001 | ✅ VERIFIED | Instruction files state the target stack and forbid the old stacks. |
| T002 | ✅ VERIFIED | Scoped instruction file matches; optional CLAUDE/cursor paths were not created. |
| T003 | ✅ VERIFIED | Instruction search matches the target rules; grok inspect was not re-run here. |
| T004 | ✅ VERIFIED | Subtract test exists; forbidden strings are gone from src. |
| T005 | ✅ VERIFIED | G1 smoke and MSW fixtures exist. |
| T006 | ✅ VERIFIED | Four B1 lint fixtures exist. |
| T007 | ✅ VERIFIED | Node is v26.13.1 and engines stay >=26.13.0. |
| T008 | ✅ VERIFIED | Four unused component files are deleted. |
| T009 | ✅ VERIFIED | apiService.ts and performance.js are deleted. |
| T010 | ✅ VERIFIED | TypeScript 5.9 and React 18 type packages are direct dependencies. |
| T011 | ✅ VERIFIED | Node pin, engine-strict, and node:26-alpine dist image are in place. |
| T012 | ✅ VERIFIED | Vite proxy, root index.html, and ES2022 tsconfig replaced CRA config. |
| T013 | 🔍 PARTIAL | modelsApi.ts is gone; VITE_API_BASE_URL and the platform modelsApi export remain. |
| T014 | ✅ VERIFIED | Vitest jsdom, setup file, and test dependencies are wired. |
| T015 | ✅ VERIFIED | ESLint rules 1–3 and react/no-danger are enabled without jsx-no-literals. |
| T016 | ✅ VERIFIED | CI skeleton order is correct; Docker trigger is unchanged. |
| T017 | ✅ VERIFIED | Client tests lock same-origin, csrf, and ApiError behavior. |
| T018 | ✅ VERIFIED | NoAuthAdapter tests and fake adapter exist. |
| T019 | ✅ VERIFIED | Stream, adapter, and idle-timeout tests exist. |
| T020 | ✅ VERIFIED | Socket.IO and stream-event fixtures exist. |
| T021 | ✅ VERIFIED | gen:api writes schema.d.ts; openapi-fetch was not added. |
| T022 | ✅ VERIFIED | NoAuthAdapter no-ops are implemented and used by the client. |
| T023 | ✅ VERIFIED | One fetch client omits sessionId and strips identity headers. |
| T024 | ✅ VERIFIED | openChatStream, parseSse, and the idle default are implemented. |
| T025 | ✅ VERIFIED | Legacy REST clients are folded into platform/api. |
| T026 | ✅ VERIFIED | socket.io-client, webSocketService, and API_CONFIG.WEBSOCKET are gone. |
| T027 | ✅ VERIFIED | SNR-8.1.2 evidence records frontend-only verification. |
| T028 | ✅ VERIFIED | Format tests exist. |
| T029 | ✅ VERIFIED | Catalogue and dateTime tests exist. |
| T030 | ✅ VERIFIED | Dark-token fixture and test assert #2EBD6B. |
| T031 | ✅ VERIFIED | Tailwind test and colour fixtures exist. |
| T032 | ✅ VERIFIED | Delta, PriceCell, and StatusBadge tests exist. |
| T033 | ✅ VERIFIED | Playwright font spec exists and is outside CI. |
| T034 | ✅ VERIFIED | Chart import fixtures exist; packages were not added. |
| T035 | ✅ VERIFIED | Custom vi-VN formatters; Intl only in dateTime. |
| T036 | ✅ VERIFIED | vi-VN catalogue and clarification keys; no i18n library. |
| T037 | ✅ VERIFIED | Dark tokens and data-theme/data-density are on the page. |
| T038 | ✅ VERIFIED | Tailwind config has no market or state colour keys. |
| T039 | ✅ VERIFIED | PriceCell, Delta, and StatusBadge implement the pattern rules. |
| T040 | ✅ VERIFIED | Self-hosted woff2 files and @font-face are present. |
| T041 | ✅ VERIFIED | Empty chart seams; lint rejects outside chart imports. |
| T042 | ✅ VERIFIED | Legacy stylesheets and UI_CONFIG.THEME are removed. |
| T043 | ✅ VERIFIED | Shared proof re-run on 2026-11-18: npm ci, tsc, vitest 43, and vite build exited 0. grok inspect lists both AGENTS files. |
| T044 | ✅ VERIFIED | CI order and the untouched Docker trigger match the task. |

## Walkthrough Log

| Item | Task | Disposition |
|---|---|---|
| 1 of 2 | T013 | Fix applied on 2026-11-18. No source edit. `frontend/src/services/modelsApi.ts` stays deleted. `modelsApi` remains the export in `frontend/src/platform/api/client.ts`. `config.ts` keeps the empty `VITE_API_BASE_URL` default. The verdict row above is unchanged. |
| 2 of 2 | T043 | Investigated on 2026-11-18, then the walkthrough ended on `done`. Later the same day the user asked to fix T043. The shared proof was re-run from `frontend/` on Node v26.13.1: `npm ci` 0, `npx tsc --noEmit` 0, `npx vitest run` 0 (17 files, 43 tests), `npm run build` 0. `grok inspect` lists root `Agents.md` and `frontend/Agents.md`. Results are in `evidence/t043-shared-proof.md`. Verdict updated from PARTIAL to VERIFIED. |
