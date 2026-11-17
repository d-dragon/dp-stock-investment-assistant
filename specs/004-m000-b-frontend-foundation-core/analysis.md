# Specification Analysis Report

**Feature**: `specs/004-m000-b-frontend-foundation-core`
**Branch**: `features/pitch-m000-B-frontend-foundation`
**Artifacts read**: `spec.md`, `plan.md`, `tasks.md`. Supporting reads: `research.md`, `data-model.md`, the pitch, and the named frontend sources.
**Date**: 2026-11-17
**Command**: `/speckit-analyze` (read-only on `spec.md`, `plan.md`, and `tasks.md` when this report was first written). Resolutions below were applied later the same day.

Memory loaded for this command: the nine Markdown files in `.specify/memory/`. The constitution is the governance check below. The architecture memory files do not add a Frontend stack rule beyond those principles.

## Findings resolution

Recorded 2026-11-17. The findings table keeps each original issue. This section is the resolution. `docs/**`, Accepted ADRs, and `specs/spec-traceability.yaml` were not edited.

| ID | Resolution | Written to |
|---|---|---|
| C1 | Recorded deferral under constitution 2.7.0. This delivery does not edit `docs/**`, Accepted ADRs, or `specs/spec-traceability.yaml` to add a Governance Context section, section anchors, or a traceability task. A later change that is allowed to touch those files refreshes anchors and traceability. | `.specify/memory/constitution.md` — "Recorded deferral when the delivery forbids the sync edit". `plan.md` — "Complexity Tracking" already held the note. `spec.md` and `tasks.md` were not edited to clear C1. |
| G1 | `.github/workflows/frontend-ci.yml`. One job runs lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`. The `on` trigger of `.github/workflows/build-push-dockerhub.yml` stays unchanged. T016 writes the fifth step. T021 adds the `gen:api` script that step calls. | `spec.md` — FR-014, FR-015, User Story 2 scenario 8; `plan.md` — O8; `tasks.md` — T016, T044; `research.md` — R18; `contracts/toolchain-and-ci.md` — "CI skeleton" |
| I1 | Zero `Delta` is `0.00` and `0.00%`, no sign, coloured `market.ref`. The zero clause inside verbatim B4-T3 is superseded by row P2 and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Do not add a sign on zero. Direction phrases stay O6. | `spec.md` — FR-027, User Story 4 scenario 6, "Source conflicts"; `tasks.md` — T032, T039; `contracts/format-catalogue-tokens.md` — B4-T3 |
| G2 | Rules 1 and 2 use core ESLint `no-restricted-imports` path patterns. Do not add `eslint-plugin-boundaries`. | `spec.md` — FR-031, User Story 2 scenario 10; `plan.md` — O4; `tasks.md` — T006, T015; `research.md` — R11; `contracts/toolchain-and-ci.md` — "Lint enabled here" |
| G3 | This delivery commits hand-written two-part dark variables. `--market-up` is `#2EBD6B`. A two-part id such as `market.down` becomes `--market-down`. Do not name Style Dictionary or any other generator. Do not invent three-part `ai.*` custom property names. Full B4-T1 generation and the `npm run tokens` drift check stay out of this delivery. | `spec.md` — FR-025, User Story 4 scenario 4; `plan.md` — O5; `tasks.md` — T030, T037; `research.md` — R13 |
| X1 | B4 sets `data-density="compact"` on `<html>` beside `data-theme="dark"`. Do not use another density. | `spec.md` — FR-025; `plan.md` — O9; `tasks.md` — T037; `research.md` — R19; `contracts/format-catalogue-tokens.md` |

Still open: G4, X2, X3 (medium); U1, P1, D1 (low); stops O1, O2, O3, O6, O7, O10, and O11. Do not guess those.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution | Resolved | `spec.md` (no `## Governance Context`); `plan.md` — "Complexity Tracking"; `tasks.md` (no anchor-check task, no traceability task); `.specify/memory/constitution.md` — "I. Spec-Driven, Traceable Delivery", "Recorded deferral when the delivery forbids the sync edit" | The constitution requires a Governance Context section, section-level anchors on `docs/` references, and task coverage for traceability refresh and long-lived doc sync when those surfaces are affected. These artifacts cite headings (`"3.1 Module tree (Target M-000)"`) and do not include those tasks. `plan.md` already records why: FR-002 forbids edits to `docs/**` and `specs/spec-traceability.yaml`. | Resolved by constitution 2.7.0. This is the recorded deferral for this delivery. Implementation must not repair it by editing `docs/**`, Accepted ADRs, or `specs/spec-traceability.yaml`. A later change that is allowed to touch those files refreshes anchors and traceability. |
| G1 | Coverage | Resolved | `spec.md` — FR-014, FR-015, User Story 2 scenario 8; `tasks.md` — T016, T044; `plan.md` — O8 | The Frontend CI skeleton and the codegen drift step had no workflow path. | Resolved by the Product Owner, 2026-11-17. File `.github/workflows/frontend-ci.yml`. One job: lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`. The Docker workflow trigger stays unchanged. |
| I1 | Inconsistency | Resolved | `spec.md` — User Story 4 scenario 6, verbatim row B4-T3, FR-027, row P2, "Source conflicts"; `tasks.md` — T032, T039 | Verbatim B4-T3 requires a sign or arrow for a positive, negative, or zero `Delta`. Row P2 and technical-design "8.2 Pattern rules" require zero to show `0.00` with no sign, coloured `market.ref`. | Resolved in `spec.md`. Zero follows P2 and "8.2 Pattern rules": `0.00` and `0.00%`, no sign, `market.ref`. The zero clause inside verbatim B4-T3 is marked superseded. Do not add a sign on zero. Direction phrases stay O6. |
| G2 | Coverage | Resolved | `spec.md` — FR-031; `tasks.md` — T006, T015; `plan.md` — O4 | Rules 1 and 2 had no selected mechanism. `eslint-plugin-boundaries` stays Proposed. | Resolved by the Product Owner, 2026-11-17. Rules 1 and 2 use core ESLint `no-restricted-imports` path patterns. Do not add `eslint-plugin-boundaries`. |
| G3 | Coverage | Resolved | `spec.md` — FR-025, User Story 4 scenario 4; `tasks.md` — T030, T037; `plan.md` — O5 | B4-T1 and "8.1 Token pipeline" ask for a generator and a `npm run tokens` drift check. Tasks committed two-part variables by hand. | Resolved by the Product Owner, 2026-11-17. This delivery commits hand-written two-part variables (`--market-up` is `#2EBD6B`). Do not name Style Dictionary. Do not invent three-part `ai.*` names. Full B4-T1 generation and the `npm run tokens` drift check stay out of this delivery. |
| X1 | Inconsistency | Resolved | `tasks.md` — T037; `plan.md` — O9; `spec.md` — FR-025 | The sources set compact as the M-000 default. T037 had forbidden `data-density`. | Resolved by the Product Owner, 2026-11-17. B4 sets `data-density="compact"` on `<html>` beside `data-theme="dark"`. Do not use another density. |
| X2 | Inconsistency | MEDIUM | `specs/pitches/M-000-B-frontend-foundation.md` — "B4: tokens, format, fonts" (Files in scope); `plan.md` — "Source code"; `tasks.md` — T030, T037; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" | The pitch files hint places tokens at `src/platform/tokens/**`. The technical-design module tree places them at `design-system/tokens/`. `spec.md` — "Source conflicts" does not record this. Tasks follow the technical design. | Keep `frontend/src/design-system/tokens/`. A later spec note can record the pitch hint as stale. Do not also create `src/platform/tokens/`. |
| X3 | Inconsistency | MEDIUM | `spec.md` — FR-024; `docs/domains/frontend/DESIGN_SYSTEM.md` — "9. Content voice"; `specs/pitches/M-000-B-frontend-foundation.md` — "Rabbit holes"; ADR-FRONTEND-005 — "Decision" | FR-024 forbids an English catalogue. The pitch rabbit hole says the same. DESIGN_SYSTEM "9. Content voice" still says English is kept as the second catalogue. `spec.md` — "Source conflicts" does not list that sentence. | This delivery ships the vi-VN catalogue only. The "9. Content voice" English-catalogue sentence is a follow-up doc fix. Do not edit DESIGN_SYSTEM in this feature, and do not add an English catalogue. |
| G4 | Coverage | MEDIUM | `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack"; `spec.md` — FR-006; `tasks.md` — T002, T003 | B0 names `AGENT.md` and `.grok/rules/*.md` as files Grok Build loads, and acceptance says no instruction file recommends Create React App, Jest, `REACT_APP_*`, or Socket.IO. The edit list and T002 cover `frontend/AGENTS.md`, root `AGENTS.md`, `CLAUDE.md`, `.claude/rules`, `.cursor/rules`, and `.github/instructions/frontend-react.instructions.md`. T003 stops if `AGENT.md` or `.grok/rules` recommend the old stack. A search during this analysis found that stale stack text in root `AGENTS.md`, which T001 covers. | Leave the T003 stop rule. Do not create `AGENT.md` or `.grok/rules`. If either path later recommends the old stack, that is [NEEDS CLARIFICATION], not a guessed rewrite. |
| U1 | Underspecification | LOW | `tasks.md` — T001 | T001 tells the Software Engineer to keep "the SPA clause in the opening summary". That clause is not in the B0 target-rule list or in FR-004. | Do not add a new SPA requirement. Rewrite the Frontend lines of root `AGENTS.md` so they state the B0 target rules. |
| P1 | Underspecification | LOW | `tasks.md` — T012; `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" (Spec Kit rules) | That pitch rule says each task names exact paths and stays at about 2–5 files. T012 names six paths (`package.json`, `vite.config.ts`, `index.html`, `tsconfig.json`, `config-overrides.js`, `webpack.config.dev.js`). | Behavior is still covered. A later tasks edit can split deletion of the dead Create React App configs from the Vite move. |
| D1 | Duplication | LOW | `spec.md` — FR-003, FR-006, FR-007, FR-020, SC-001, SC-006 | Socket.IO absence, and the B0 `grok inspect` proof, are stated as both requirements and success criteria. The copies agree. | Leave them. They do not change execution order. |

Overflow: none. Findings above are the full set.

## (a) Citations

Every functional requirement FR-001..FR-032 and every success criterion SC-001..SC-011 has a `Source:` citation (path plus section heading, ADR ID, SRS ID, or pitch slice).

Every task T001..T044 has a `Source:` line, and the implementation tasks also carry an `Implements` citation. One phrase inside an otherwise cited task is unsourced: the "SPA clause" in T001 (finding U1).

Plan design choices in "Summary", "Technical Context", "Constitution Check", "Design", "Complexity Tracking", and "Open items" cite a path and section, an ADR, an SRS ID, or a pitch slice, except the **Project Type** bullet, which only names the `frontend/` package. That bullet does not add a behavior beyond the sourced stack lines around it.

Open items that remain (O1, O2, O3, O6, O7, O10, O11) are cited to `research.md` and are marked [NEEDS CLARIFICATION] in the tasks that would otherwise guess. O4, O5, O8, and O9 were resolved by the Product Owner on 2026-11-17.

## (b) Pitch B0, B1, B2, and B4 items without a completing task

In-scope pitch items that have a task which can be executed as written are not repeated here. Rows B4-T5 and B4-T6 are "Moved to M-001" in the pitch and correctly have no task. B3 and B5 are reserved and correctly have no task in this file.

| Pitch item | Tasks | Closable as written? |
|---|---|---|
| B0 files and target rules (`frontend/AGENTS.md`, root `AGENTS.md`, `CLAUDE.md`, `.claude/rules`, `.cursor/rules`, `.github/instructions/frontend-react.instructions.md`); no T-step; instruction files only; `grok inspect` | T001, T002, T003 | Yes for the edit list. `AGENT.md` and `.grok/rules/*.md` have no edit task (G4). |
| B0 agent constraints: no source, test, or config change | T001–T003 | Yes |
| B1 T0 deletions, including `MessageFormatter.js` | T004, T008, T009 | Yes. `utils/performance.js` is deleted only when an import scan shows it is unreferenced, which matches technical-design step T0. |
| B1 T1 Vite build, config, environment, known traps, proxy, `VITE_API_BASE_URL` empty, no credentialed CORS | T012, T013 | Yes |
| B1 types alignment (technical-design "T1 types fix", not pitch T1) and Node pin | T007, T010, T011 | Yes. T007 stops until the Product Owner has installed Node v26.13.1 (O11). |
| B1 T2 Vitest, jsdom, MSW base, G1 smoke | T005, T014 | Yes |
| B1 lint rules 1–3 and `react/no-danger` | T006, T015 | Yes. Rules 1 and 2 use core ESLint `no-restricted-imports` (G2 resolved). |
| B1 CI skeleton and "do not change the Docker workflow trigger" | T016, T044 | Yes. File is `.github/workflows/frontend-ci.yml` (G1 resolved). |
| B1 Docker `node:26-alpine` packaging `dist`; proving `rg` command | T011, phase 2 checkpoint, T004 | Yes, once Node v26.13.1 is installed. The Docker build is a checkpoint, not its own task id. |
| B2 codegen from `docs/openapi.yaml`; commit generated types; local `git diff --exit-code` | T021, T016, phase 3 checkpoint | Yes. CI drift is the fifth step of `.github/workflows/frontend-ci.yml` (G1 resolved). |
| B2 T3 client, `NoAuthAdapter`, `sessionRef` shape, path allow-list, no `Authorization`, no `X-User-ID`, no token | T017, T018, T022, T023, T025 | Yes for the stated behavior. The wire field for `sessionRef.sessionId` stays omitted (O2). The HTTP client package stays unselected (O1); the task uses `fetch`. |
| B2 stream API, WHATWG fields, `legacyChatAdapter`, one stream per tab, idle timeout, `.env.example`, MSW 15000 ms, "Tạo lại" | T019, T024 | Yes. SSE parser package stays unselected (O3); the task keeps an in-file WHATWG split and does not add `eventsource-parser`. |
| B2 T8 Socket.IO removal, return lint, `rg socket.io dist`, SNR-8.1.2 "Frontend part verified" | T020, T026, T027 | Yes. Evidence is `specs/004-m000-b-frontend-foundation-core/evidence/snr-8.1.2.md`. `specs/spec-traceability.yaml` stays untouched (C1). |
| B2 agent constraint: do not change Backend stream headers, heartbeat emission, or HTTP/2 | No task edits `backend/` | Yes, by FR-002 and FR-021. |
| Shared agent constraints: worktree on `features/pitch-m000-B-frontend-foundation`; proving `npm ci`, `tsc --noEmit`, `vitest run`, `build`; `fetch` only in `platform/api` and `platform/stream`; `VITE_*` only; "AI gợi ý" and "Đã xác nhận" through `t()` | T015, T023, T029, T036, T043, phase checkpoints | Yes |
| B4-F1..F5 and P1..P4 exact strings, including the 1,000-value property test; `fmt.volume` not via the price formatter; `Intl` for dates only | T028, T029, T035 | Yes |
| B4-T1 dark variables, `--market-up` = `#2EBD6B`, no light values, fixture, `data-theme="dark"` | T030, T037 | Yes for the two-part hand-written scope (G3 and X1 resolved). Full generation and `npm run tokens` stay out. `track.a` and `track.b` correctly have no hex and no task value. |
| B4-T2 Tailwind has no `market` or `state` colour utilities; lint on `var(--market-*)`, `var(--state-*)`, and arbitrary Tailwind colours | T031, T038, T041 | Yes for the ESLint and Vitest rows in B4-T2. Technical-design rule 4 also names Stylelint for CSS files; that mechanism is Proposed and has no task. The pitch row's proof is Vitest plus ESLint. |
| B4-T3 `Delta` sign or arrow, accessible name includes direction | T032, T039 | Yes for the sign rule. Zero follows P2 (I1 resolved). Direction phrases stay [NEEDS CLARIFICATION] (O6): T036 adds keys marked `[NEEDS CLARIFICATION]` and does not invent vi-VN wording. |
| B4-T4 IBM Plex Mono, Be Vietnam Pro, self-hosted, no third-party font host | T033, T040 | Yes. Playwright stays outside the B1 CI skeleton. |
| B4 T6 tokens, format, i18n seam, three patterns, legacy `App.css` / `index.css` removal | T035–T040, T042 | Yes, with G3 and X1 still open. T039 does not add a Radix package for `PriceCell`, `Delta`, or `StatusBadge`. |
| B4 part of T7: `lightweight-charts` only in `platform/chart`, `chart.js` only in `platform/stat-chart`; neither package in `package.json`; no `ChartEngine` or `StatChart` | T034, T041 | Yes |
| B4 agent constraints: files under the token, format, i18n, chart, and stat-chart seams; proving `fmt` values and a planted chart-import lint failure | T028, T034, T035, T041, phase 4 checkpoint | Yes, subject to G3 |

## (c) Contradictions with the named sources

Recorded in the findings table:

- I1 — pitch row B4-T3 versus pitch row P2 and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Resolved in `spec.md`: P2 supersedes the zero clause.
- X1 — T037 versus `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" and `docs/domains/frontend/DESIGN_SYSTEM.md` — "5. Density, space, radius". Resolved: B4 sets `data-density="compact"`.
- X2 — pitch "B4: tokens, format, fonts" files hint versus `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)".
- X3 — FR-024 and the pitch rabbit hole versus `docs/domains/frontend/DESIGN_SYSTEM.md` — "9. Content voice".
- G3 — B4-T1 and "8.1 Token pipeline" (`npm run tokens`, generated files) versus T037's hand-written two-part CSS. Resolved: two-part hand-written variables are this delivery. Full generation and `npm run tokens` stay out.
- C1 — constitution traceability and anchor rules versus FR-002. Resolved by constitution 2.7.0 as the recorded deferral in `plan.md` — "Complexity Tracking".

These are not contradictions. The artifacts name them and follow the pitch or the later technical-design sentence:

- Light theme, theme switching, and the contrast script move to M-001 (pitch rows B4-T5 and B4-T6; technical-design "8.1 Token pipeline"). DESIGN_SYSTEM "1. Principles" and "10. Quality", and DESIGN_LOCK "4.2 Token groups", stay stale on purpose.
- Custom board formatters, with `Intl` only for dates, follow the price-board bullet in ADR-FRONTEND-005. The earlier "everything through `Intl`" sentence in that Decision is the stale one named in `spec.md` — "Source conflicts".
- Pitch T1/T2 labels versus technical-design step "T2 Vite", and the separate "T1 types fix" row, are the mapping FR-032 requires. Tasks use that mapping.
- Lint rules 1–3 and `react/no-danger` in B1 follow the pitch. Technical-design "10.2 CRA → Vite migration" still places `react/no-danger` on T4 and rules 1–3 on T7. `spec.md` — "Source conflicts" records that placement as stale for this delivery.
- Instruction folders are `features/` and `platform/`. ADR-FRONTEND-001 — "Implementation Direction" (`modules/`) is the stale sentence.
- B0 has no failing test. The blanket test-first sentence in the pitch "Delivery workflow (agentic)" does not apply to B0. The spec records that.
- Storybook, the browser MSW worker, the width matrix, and the axe baseline stay with reserved B5. This delivery still uses MSW inside Vitest (ADR-FRONTEND-008 — "Decision") and one Playwright font check for row B4-T4.
- `docs/domains/frontend/ARCHITECTURE.md` — "8.2 Gates G1–G6 → M-001" labels G5 "Vitest+RTL baseline green". `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" defines G5 as the full baseline (zone matrix, XSS, axe). This delivery's plan follows the technical-design G5 and keeps that full baseline out of scope. G1 and the Frontend half of G6 are in scope.

## Coverage summary

| Requirement key | Has task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 test-first for B1, B2, B4; B0 exempt | Yes | T004–T006, T017–T020, T028–T034 | B0 proof is T003 |
| FR-002 worktree and forbidden trees | Yes | T027 and the task constraints | No task edits `backend/`, `docs/**`, or `specs/spec-traceability.yaml` |
| FR-003 no Socket.IO, WebSocket, or EventSource; `fetch` and `VITE_*` limits | Yes | T015, T024, T026 | |
| FR-004 `frontend/AGENTS.md` and root Frontend lines | Yes | T001 | U1 |
| FR-005 Copilot instructions and stale Claude/Cursor files | Yes | T002 | |
| FR-006 `grok inspect` and instruction search | Yes | T003 | G4 |
| FR-007 B0 is instruction files only | Yes | T001–T003 | |
| FR-008 Vite replaces Create React App | Yes | T012 | P1 |
| FR-009 T0 deletions and the `rg` proof | Yes | T004, T008, T009 | |
| FR-010 traps, TypeScript 5.9+, React 18 types, `dist` image | Yes | T010, T011, T012, T013 | |
| FR-011 Node pin; Product Owner installs v26.13.1 | Yes | T007, T011 | O11 blocks the phase until the install |
| FR-012 same-origin proxy | Yes | T012 | |
| FR-013 Vitest, jsdom, MSW base, G1 | Yes | T005, T014 | |
| FR-014 CI skeleton; Docker trigger unchanged; image builds | Yes | T016, T044, T011 | G1 resolved. Image build is the phase 2 checkpoint |
| FR-015 codegen, committed types, CI drift | Yes | T021, T016 | G1 resolved. Drift is the fifth CI step |
| FR-016 same-origin client, CSRF, 401, `NoAuthAdapter` | Yes | T017, T018, T022, T023 | |
| FR-017 path allow-list and `sessionRef` shape | Yes | T017, T023 | O2: `sessionId` omitted on the wire |
| FR-018 SSE reader and event-name lint | Yes | T019, T020, T024, T026 | O3 |
| FR-019 idle timeout | Yes | T019, T024 | |
| FR-020 Socket.IO removal and SNR-8.1.2 evidence | Yes | T020, T026, T027 | |
| FR-021 Backend stream unchanged | Yes | T024 | Negative requirement |
| FR-022 `fmt` exact outputs | Yes | T028, T035 | |
| FR-023 `Intl` dates, locale settings | Yes | T029, T035 | Settings live in a small module. The Zustand `UiSlice` stays with B3 |
| FR-024 `t()` and vi-VN only | Yes | T029, T036 | X3. O7: `react/jsx-no-literals` stays off |
| FR-025 dark tokens | Yes | T030, T037 | G3 and X1 resolved. Two-part variables and `data-density="compact"`. Full generation stays out |
| FR-026 B4-T2 | Yes | T031, T038, T041 | |
| FR-027 `Delta` | Yes | T032, T039 | I1 resolved. O6 still blocks invented direction phrases |
| FR-028 B4-T4 fonts | Yes | T033, T040 | |
| FR-029 chart-import lint; no band math | Yes | T032, T034, T039, T041 | |
| FR-030 SNR-7.2.1 stays P2 | Yes | T044 | |
| FR-031 rules 1–3 and `react/no-danger` | Yes | T006, T015 | G2 resolved. Rules 1 and 2 use `no-restricted-imports` |
| FR-032 pitch T1/T2 labels beside the technical-design step | Yes | T010, T012, T014, pitch label map | |
| SC-001 | Yes | T003, T043 | |
| SC-002 | Yes | Phase 2 checkpoint, T043 | `npm run dev` and the Docker build are on the phase 2 checkpoint. T043 repeats `npm ci`, `tsc`, Vitest, and `build` |
| SC-003 | Yes | T004, T008, phase 2 checkpoint | |
| SC-004 | Yes | T005, T014 | |
| SC-005 | Yes | T021, T016 | G1 resolved |
| SC-006 | Yes | T026 | |
| SC-007 | Yes | T019, T024 | |
| SC-008 | Yes | T028, T035 | |
| SC-009 | Yes | T030, T034, T037, T041 | Chart-import lint is closable. Token scope is the two-part commit (G3 resolved) |
| SC-010 | Yes | T033, T040 | |
| SC-011 | Yes | Test tasks before implementation tasks; T003 for B0 | |

## Constitution alignment

- **C1 (resolved).** Constitution 2.7.0, Principle I and "Recorded deferral when the delivery forbids the sync edit", makes the Complexity Tracking note the compliant deferral. This delivery's FR-002 still forbids edits to `docs/**`, Accepted ADRs, and `specs/spec-traceability.yaml`. Implementation must not clear C1 by editing those files.
- Principles II, III, V, VI, and VII: the plan's constitution check matches the artifacts. The client stays in `platform/api` and `platform/stream`. Formatters do not invent prices. `PriceCell` does not compute reference, ceiling, or floor (ADR-FRONTEND-005 — "Decision"; pitch "No-gos"). No token is stored. B0's proof is `grok inspect` plus search, which the spec exempts from the failing-test rule.
- Principle IV: not applicable. No prompt, short-term memory, or fine-tune surface is in this delivery.
- **Pre-merge anchor checklist**: same recorded deferral as C1. Constitution 2.7.0 accepts that deferral when the plan records it and the governing spec forbids the sync edit.

## Unmapped tasks

None. T043 maps to SC-002. T044 maps to FR-014 and FR-030. T009's `Source:` line cites the feature contract "T0 deletions"; its `Implements` line cites `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration".

## Metrics

- Total functional requirements: 32 (FR-001..FR-032)
- Total success criteria: 11 (SC-001..SC-011)
- Total tasks: 44 (T001..T044)
- Coverage: 32/32 requirements have at least one task (100%)
- Closable without a new Product Owner decision: 32/32 for FR-001..FR-032 as amended on 2026-11-17. G1, G2, G3, X1, and I1 are resolved. O1, O2, O3, O6, O7, O10, and O11 remain stops that must not be guessed
- Ambiguity count: 1 (instruction-file scope in G4)
- Duplication count: 1 cluster (D1)
- Critical issues count: 0 open. C1 is a recorded deferral (constitution 2.7.0). G1 is resolved

## Open items

Carried forward from `plan.md` — "Open items". Do not guess a value during implementation.

| ID | Item |
|---|---|
| O1 | HTTP client package on top of `openapi-typescript`. T021 uses `fetch` and does not add `openapi-fetch`. |
| O2 | Wire field for `sessionRef.sessionId` on `POST /api/chat`. T023 omits it and does not use `ChatRequest.session_id`. |
| O3 | SSE parser package. T024 does not add `eventsource-parser`. |
| O4 | Resolved. Core ESLint `no-restricted-imports`. T015 does not add `eslint-plugin-boundaries`. |
| O5 | Resolved for this delivery. Two-part hand-written variables. No generator. No invented `ai.*` names. |
| O6 | vi-VN accessible-name phrases for `Delta` direction. T032 and T036 do not invent wording. |
| O7 | Which slice enables `react/jsx-no-literals`. T006, T015, and T036 do not enable it. |
| O8 | Resolved. `.github/workflows/frontend-ci.yml`. Drift is the fifth step, after build. |
| O9 | Resolved. B4 sets `data-density="compact"`. |
| O10 | Performance budgets. Technical-design status is TBD. No task sets a number. |
| O11 | Node v26.13.1 is not on the laptop (22.18). T007 stops B1 until the Product Owner installs it. |

Additional notes from this analysis, not new product decisions:

- [NEEDS CLARIFICATION] G4, only if `AGENT.md` or `.grok/rules` recommend Create React App, Jest, `REACT_APP_*`, or Socket.IO.
- I1 is resolved in `spec.md`. X2 and X3 remain specification/source mismatches. The behavior to implement is stated in the finding recommendations.

## Next actions

- G1, G2, G3, and X1 are resolved. Resolve O11 (Node v26.13.1) before any B1 install or test run.
- C1 is resolved as the recorded deferral in constitution 2.7.0. Do not edit `docs/**`, Accepted ADRs, or `specs/spec-traceability.yaml` to clear it inside this feature.
- O1, O2, O3, O6, and O7 remain stop-points on the tasks that would guess. O4, O5, O8, and O9 are resolved. Implementation can write the behavior those tasks already lock (hand-written `fetch`, omitted `sessionId`, in-file SSE split, core ESLint for rules 1 and 2, two-part colour variables, `data-density="compact"`, catalogue keys marked `[NEEDS CLARIFICATION]`, `react/jsx-no-literals` off).
- I1 is resolved. Implement zero change as `0.00` / `0.00%` with no sign and `market.ref`.
- Do not start B3 or B5 from `tasks.md`.
- I1 is recorded in `spec.md`. A later spec edit can still record X2 and X3.

## Remediation sketch

Items 1, 2, and 4 were applied on 2026-11-17. See "Findings resolution". Item 3 was not applied.

1. Applied. T016 writes `.github/workflows/frontend-ci.yml` with the drift check as the fifth step.
2. Applied. `spec.md` says row P2 and technical-design "8.2 Pattern rules" govern zero `Delta`, and the zero clause in verbatim B4-T3 does not.
3. Not applied. A spec "Source conflicts" note can list the pitch `src/platform/tokens/**` hint and the DESIGN_SYSTEM "9. Content voice" English-catalogue sentence as stale for this delivery.
4. Applied for O4 and O5. O6 stays blocked until the Product Owner names the vi-VN direction phrases.

## Extension hooks

**Skipped pre-hook**: git
Command: `/speckit-git-commit`
Reason: Product Owner operating rule. Every `speckit.git.*` hook is skipped. No branch, add, commit, stash, reset, checkout, restore, or push was run.

**Automatic pre-hook**: memory-loader
Command: `/speckit-memory-loader-load`
Result: read-only. Nine memory files. No git writes.

**Skipped post-hook**: git
Command: `/speckit-git-commit`
Reason: same Product Owner rule. Analysis results were not committed.
