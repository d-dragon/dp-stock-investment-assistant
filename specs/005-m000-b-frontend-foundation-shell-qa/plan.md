# Implementation Plan: M-000 Frontend foundation shell and QA (delivery 2 of 2)

**Branch**: `features/pitch-m000-B-frontend-foundation` | **Date**: 2026-11-19 | **Spec**: `specs/005-m000-b-frontend-foundation-shell-qa/spec.md`

**Input**: Feature specification from `specs/005-m000-b-frontend-foundation-shell-qa/spec.md`

**Note**: This file is the `/speckit-plan` output. Phase 0 is `research.md`. Phase 1 is `data-model.md`, `contracts/`, and `quickstart.md`. `tasks.md` is a later command.

## Summary

Delivery 2 of Pitch B builds the Z1–Z4 shell, the URL-owned workspace store, and safe markdown rendering, then adds the browser MSW worker, a dark-only Storybook set of 11 to 15 stories, and Playwright with axe. B0, B1, B2, and B4 stay in `specs/004-m000-b-frontend-foundation-core` and are reused.

The Software Engineer implements later, in a named git worktree on `features/pitch-m000-B-frontend-foundation`. Shared proof from `frontend/` is `npm ci`, `npx tsc --noEmit`, `npx vitest run`, and `npm run build`. B3 also passes `npm run lint` with the G2, G3, and XSS tests. B5 also passes `npm run build-storybook`, `npx playwright test`, and a production bundle that contains no MSW and no Storybook.

Design choices are in `research.md`. Each one cites a path and a heading, an ADR ID, an SRS ID, or a pitch row. Packages and numbers the technical design still marks Proposed are not selected. Two architecture target cells (Tailwind + Radix, and the traceability refresh) are recorded gaps. They are not silent omissions.

Source: `spec.md` — "User Scenarios & Testing" and FR-001 through FR-026; `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering" and "B5 — MSW, minimal Storybook, and Frontend CI".

## Technical Context

**Language/Version**: TypeScript 5.9 or newer, already a direct dependency, on Node `>=26.13.0`. React 18. Source: `frontend/package.json`; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".

**Primary Dependencies**: Already present: Vite, Vitest, jsdom, React Testing Library, MSW 2, `openapi-typescript`, `@playwright/test`, ESLint with `eslint-plugin-react`. Added for this delivery: `react-router-dom`, `zustand`, `@tanstack/react-query`, `react-resizable-panels`, `react-markdown`, `remark-gfm`, `@axe-core/playwright`, and Storybook with the Vitest addon. Not selected: `openapi-fetch`, `eslint-plugin-boundaries`, Style Dictionary, `eventsource-parser`, an i18n library, Tailwind, Radix / shadcn, `lucide-react`, `lightweight-charts`, `chart.js`. Source: `docs/domains/frontend/ARCHITECTURE.md` — "5.1 Decided"; `research.md` R1, R2, R3, R4, R5.

**Storage**: `sessionStorage` in the same tab for the Z4 draft, the per-symbol context slice, and pane sizes. The draft key is `dp-stock:z4-draft:${sessionId}:${conversationId}` (`data-model.md`). The URL owns `track`, `symbol`, and `coreObjectRef`. No new Backend collection. Source: `docs/domains/frontend/ARCHITECTURE.md` — "6.1 State ownership matrix"; `data-model.md`.

**Testing**: Test-first. B3 is Vitest + React Testing Library + MSW for G2, G3, XSS, and rows B3-D1, B3-D4, B3-D5, B3-D7, B3-D8, plus ESLint. B5 is Playwright + axe at four widths, Storybook render and axe, and a `dist/` scan. Source: `spec.md` — FR-001 and FR-026; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.1 Pyramid" and "9.2 Tests mapped to gates".

**Target Platform**: Browser SPA built by Vite to static `dist/`. Dev server proxies `/api` to port 5000. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".

**Project Type**: Frontend package inside this repository (`frontend/`). Backend, agent, and data stores are out of this delivery.

**Performance Goals**: Not set. Feature route elements are `React.lazy` because `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation" says so. `docs/domains/frontend/ARCHITECTURE.md` — "7.2 Quality floor" leaves budgets TBD and marks that performance row Target M-001. This plan does not invent a number (`research.md` R19).

**Constraints**: No `socket.io-client`, WebSocket, or `EventSource`. `fetch` only in `platform/api` and `platform/stream`. `VITE_*` only. Every user-facing string through `t()`, except the existing `<noscript>` sentence locked by delivery 1. No edits to `backend/`, `docs/**`, Accepted ADRs, `main`, the Product Owner's main tree, or the `wt/m001-s3` worktree. Implementation runs in a worktree. Source: `spec.md` — FR-002 and FR-003.

**Scale/Scope**: One Frontend package. Slices B3 and thin B5. Storybook's required set is 11 to 15 stories. Four Playwright widths. Source: `spec.md` — FR-023 and "Out of Scope".

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

Governing file: `.specify/memory/constitution.md` (2.7.0). Memory loaded for this command: `constitution.md`, `architecture.md`, the five architecture view files, `architecture-repo-facts.md`, and `sync-impact-report-v1.0.0.md`. The architecture memory describes the agent runtime (refreshed 2026-07-06). It does not add a Frontend stack rule. Frontend authority for this plan is `docs/domains/frontend/ARCHITECTURE.md` and `docs/domains/frontend/TECHNICAL_DESIGN.md`, then the design lock and the ADRs the spec names. The spec wins where it records a resolved conflict. Those conflicts are listed under Authority alignment. They are not edited in `docs/`.

### Pre-research gate

| Principle | Result | Why |
|---|---|---|
| I. Spec-Driven, Traceable Delivery | Pass with recorded deferral | The plan cites the spec, the pitch, the frontend architecture, the technical design, DESIGN_LOCK, DESIGN_SYSTEM, ADR-FRONTEND-001..008, and ADR-SYS-001. It does not edit `docs/**`, Accepted ADRs, or `specs/spec-traceability.yaml`. That refresh waits (`research.md` R18). |
| II. Layered Boundaries and Explicit Ownership | Pass | Shell composes features. Features do not call `fetch` and do not import each other except through `index.ts`. `platform` does not import features. Backend layering is untouched. Source: `docs/domains/frontend/ARCHITECTURE.md` — "4.3 Building blocks"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement". |
| III. Evidence-Grounded Financial Intelligence | Pass | No price is computed. No chart engine. No market feed. `PriceCell` and `Delta` stay the delivery 1 patterns. The empty Sandbox chart slot is a slot, not a series. Source: ADR-FRONTEND-004 — "Decision"; `spec.md` — FR-020. |
| IV. Prompts, Memory, and Fine-Tuning Control Behavior, Not Truth | Pass | The only new client memory is session UI and a text draft. Prices, metrics, and recommendations are not stored. `sessionRef` is an opaque pair, not a thread copy. Source: `.specify/memory/constitution.md` — "Memory and AI Runtime Boundaries"; `spec.md` — FR-011. |
| V. Deterministic Tools and Contracted Interfaces | Pass | MSW handlers are limited to operations already in `docs/openapi.yaml`. The file is not edited. SSE stays the delivery 1 client. Socket.IO stays out. Source: `contracts/msw-storybook-ci.md`. |
| VI. Testability and Observability Are First-Class | Pass | Proving commands are in `quickstart.md`. `reportError` is a console sink. A vendor reporter stays open in the technical design and is not chosen. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items". |
| VII. Secure, Simple, Reversible Change | Pass with recorded gap | `MessageBody` does not parse raw HTML. No token is stored. Tailwind and Radix are not installed. That is a gap against the Pitch B complete UI cell, justified in Complexity Tracking, because the spec cuts the primitive layer. Source: `research.md` R3; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output". |

### Document-referencing obligation

`speckit.plan` lists affected long-lived documents and whether their anchors need updates. This command updates none of them. The omission is the recorded deferral in `.specify/memory/constitution.md` — "Recorded deferral when the delivery forbids the sync edit".

| Document | Anchors that disagree with this delivery | Updated here |
|---|---|---|
| `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" | Z2 slot still lists a `features/models` selector | No. Model selector is in the Z4 header |
| `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store" | `ui.theme` union includes `'light'` | No. This delivery stores `'dark'` only |
| `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" | T4 says turn on `react/no-danger` | No. Delivery 1 already did. This delivery keeps the error |
| `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.1 Pyramid" and "12. Domain-specific constraints" | Playwright + axe marked Proposed | No. The pitch acceptance names the tool |
| `docs/domains/frontend/ARCHITECTURE.md` — "5.1 Decided" and "8.1 Current → Target" | Pitch B complete UI cell is Tailwind + Radix | No. This plan does not install them (`research.md` R3) |
| `docs/domains/frontend/ARCHITECTURE.md` — "5.2 Candidates" | E2E tool undecided | No. Same Playwright resolution |
| `docs/domains/frontend/ARCHITECTURE.md` — "7.2 Quality floor" | Route code-splitting marked Target M-001 | No. Lazy feature routes still follow the routing section (`research.md` R19) |
| `docs/domains/frontend/DESIGN_LOCK.md` — "1. Shell geometry" | Z2 diagram includes an account menu | No. This delivery has no account menu |
| `docs/domains/frontend/DESIGN_LOCK.md` — "1.1 Viewport and zone width budget" | 240 px and 440 px defaults are Proposed | No. They are not the done bar |
| `docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md` — "Implementation Direction" | Says `modules/` | No. Folders are `features/` and `platform/` |
| `docs/domains/frontend/DESIGN_SYSTEM.md` — "10. Quality" | Both-theme stories and visual regression described as M-000 | No. Dark only. B5-S4 stays in M-001 |
| `docs/openapi.yaml` | Handler input only | No |
| `specs/spec-traceability.yaml` | Feature `005-m000-b-frontend-foundation-shell-qa` stays `unmapped` | No |

Source: `spec.md` — "Source conflicts", FR-002, and "Sync targets".

### Post-design re-check

Phase 1 artifacts stay inside this feature directory. They add no Backend route, no agent tool, no secret, and no second build system. Open items below are named and are not filled with a package choice or a number. Gate result is unchanged: pass, with the deferral and the Tailwind / Radix gap in Complexity Tracking.

The agent-context script was not run (`research.md` R18). `AGENTS.md` is the B0 instruction set. The script would rewrite it. There is no `<!-- SPECKIT START -->` marker in the repository. The plan reference is this file.

Analysis findings about stale sentences in `TECHNICAL_DESIGN.md` §3.5 (model selector on the Z2 slot), `ARCHITECTURE.md` §5.1 and §8.1 (Tailwind and Radix), and `DESIGN_LOCK.md` §1 (account menu) stay deferred. This delivery does not edit those files. Tasks follow the spec: selector in the Z4 header, no Tailwind or Radix, no account menu.

## Project Structure

### Documentation (this feature)

```text
specs/005-m000-b-frontend-foundation-shell-qa/
├── spec.md
├── plan.md                          # this file
├── research.md                      # Phase 0
├── data-model.md                    # Phase 1
├── quickstart.md                    # Phase 1
├── contracts/                       # Phase 1
│   ├── README.md
│   ├── shell-zones.md
│   ├── workspace-and-routes.md
│   ├── zone-frame-and-message-body.md
│   └── msw-storybook-ci.md
├── checklists/requirements.md
└── tasks.md                         # not created by this command
```

### Source code (implementation targets, not created by this command)

Paths the later worktree is expected to touch. Delivery 1 paths stay, except where this list moves or deletes a legacy file.

```text
frontend/
├── index.html                       # script src → /src/main.tsx
├── package.json                     # dependencies in Technical Context; scripts e2e, build-storybook
├── eslint.config.js                 # jsx-no-literals; rules 1–2 on app/ and features/
└── src/
    ├── main.tsx                     # entry, providers, router; replaces index.tsx
    ├── app/
    │   ├── providers.tsx
    │   ├── router.tsx
    │   └── layout/
    │       ├── WorkspaceShell.tsx
    │       └── ZoneHost.tsx
    ├── features/
    │   ├── companion/               # public index.ts only
    │   └── models/                  # selector, composed into the Z4 header
    ├── platform/
    │   ├── workspace/               # store, useUrlSync, routeParams.ts
    │   ├── observability/           # reportError console sink
    │   └── api/keys.ts              # health, config, models
    ├── design-system/patterns/
    │   ├── ZoneFrame/
    │   └── MessageBody/
    ├── mocks/                       # shared handlers + browser worker
    └── test/                        # Vitest setup imports the shared handlers

# Removed when the shell ships:
frontend/src/App.tsx
frontend/src/index.tsx
frontend/src/components/models/ModelSelector.tsx

# CI, extended, not replaced:
.github/workflows/frontend-ci.yml
# Read only. Trigger unchanged:
.github/workflows/build-push-dockerhub.yml
```

**Structure Decision**: The tree is `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree", cut to B3 and B5. Folders are `features/` and `platform/`, not `modules/` (`research.md` R9). `ZoneFrame` and `MessageBody` are patterns, not platform modules. `platform/chart` and `platform/stat-chart` stay empty seams from delivery 1.

## Design

### Sequence

| Order | Slice | What the Software Engineer produces | Contract |
|---|---|---|---|
| 1 | B3, tests first | Shell landmarks, `ZoneFrame`, `MessageBody`, router, store, draft, lint for literals and feature colour | `contracts/shell-zones.md`, `contracts/workspace-and-routes.md`, `contracts/zone-frame-and-message-body.md` |
| 2 | B5, tests first | Shared MSW handlers, browser worker, dark Storybook, Playwright + axe, CI steps, bundle scan | `contracts/msw-storybook-ci.md` |

`tasks.md` will label the shell split and the store with pitch T4 and T5, and the Playwright remainder with T7. Storybook and the CI extension sit with B5. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" (Pitch B slice ↔ step map). The clause in step T4 that turns on `react/no-danger` is stale. The rule is already an error.

### Authority alignment

This is the check the planning request asked for: the plan follows the frontend architecture and the technical design, and it records every place the spec already resolved a stale sentence.

| Authority | What this plan implements | Where it differs, and why |
|---|---|---|
| `ARCHITECTURE.md` — "4.1 Shell zones" | Z2 chrome, Z1 both tracks, Z3 workspace, Z4 companion over SSE | Z3 chart dock is an empty Sandbox slot. Chart content is M-001 (ADR-FRONTEND-004, FR-020) |
| `ARCHITECTURE.md` — "4.2" and "6.1" | URL owns track, symbol, and core-object ref. Store mirrors. Draft in `sessionStorage` | `sessionRef` stays on the companion run, one copy (FR-018) |
| `ARCHITECTURE.md` — "4.3" | Shell → features → platform / design system. Error boundary per zone. `reportError` hook | Reporter is a console sink. Tooling is still open in the technical design |
| `ARCHITECTURE.md` — "5.1 Decided" | React Router, Zustand, TanStack Query, `react-resizable-panels`, Vite, Vitest, MSW, Storybook | Tailwind and Radix are not installed (`research.md` R3) |
| `ARCHITECTURE.md` — "5.2 Candidates" | Playwright + axe is required | The candidate row is stale. The spec resolved it. The file is not edited |
| `ARCHITECTURE.md` — "5.3 Carve-outs" | No Socket.IO, no chart engine, no auth, no saved presets, no generated UI | Matches the spec out-of-scope list |
| `ARCHITECTURE.md` — "6.3" runtime views | Deep link mirrors the store. Z4 uses the existing SSE client. Stop aborts. No `Last-Event-ID` | Resume and cancel stay Transition. This delivery does not add them |
| `ARCHITECTURE.md` — "6.5" | Agent output is sanitized markdown | `MessageBody` is the Frontend half. `MessageFormatter.js` is already gone |
| `ARCHITECTURE.md` — "7.2 Quality floor" | Four widths, keyboard path, per-zone error boundary, `vi-VN` | Performance budgets stay TBD. Lazy routes still follow the routing section (`research.md` R19). SNR-7.2.1 stays P2 |
| `TECHNICAL_DESIGN.md` — "3.1" and "3.2" | `app/`, `features/companion`, `features/models`, `platform/workspace`, patterns | Pitch hint paths (`platform/zone-frame`, `modules/`) are not used |
| `TECHNICAL_DESIGN.md` — "3.3" | Rules 1 and 2 move onto the new folders with core ESLint. `jsx-no-literals` turns on. `react/no-danger` stays | `eslint-plugin-boundaries` stays proposed |
| `TECHNICAL_DESIGN.md` — "3.4" and "3.5" | `ZoneHost`, `ZoneFrame`, `reportError`, keyboard path, `aria-busy` on loading and streaming | Z2 slot line that places the model selector in Z2 is not followed |
| `TECHNICAL_DESIGN.md` — "4.2" and "4.3" | Four slices, `useUrlSync`, query keys for health, config, and models | No `'light'` value. Proposed query timings are not adopted |
| `TECHNICAL_DESIGN.md` — "5" | M-000 routes only. Sandbox chart slot. Portfolio has none | Symbol pattern is the uppercase rule plus the three examples. No invented character class |
| `TECHNICAL_DESIGN.md` — "6.1", "6.3", "6.5" | Same client and stream. Handlers for health, config, models, chat. `MessageBody` rules as written | Price mocks in "6.3a" stay out |
| `TECHNICAL_DESIGN.md` — "7" and "8.2" | Skip link, four widths, polite live region, dark compact stories | Radix is not the focus implementation (`research.md` R3). Story count is 11 to 15, not 22 |
| `TECHNICAL_DESIGN.md` — "9.2" | G2 and G3 are this delivery. G5 gains axe, the zone matrix, and `MessageBody`. G1, G4 partial, and the Frontend half of G6 stay as delivery 1 left them | G5 does not add the contrast script or `F6` |
| `TECHNICAL_DESIGN.md` — "10.1" | CI skeleton extended after the existing five steps | Docker workflow trigger unchanged |
| `DESIGN_LOCK.md` — "1" and "5" | Zone roles, state matrix, drawer below 1440, rail below 1024 | Account menu is absent. 240 px and 440 px are not asserted |
| ADR-FRONTEND-003 | URL is the source of shareable state | — |
| ADR-FRONTEND-008 | Same handlers in browser and Vitest. Neither in the production bundle | Price fixtures named in the follow-up wait for M-001 |
| ADR-SYS-001 | Identity stays in Pitch A. `NoAuthAdapter` stays | — |

### Behavior the contracts fix

- Four landmarks, `/` redirects to `/sandbox`, Z2 is not resizable, model selector in the Z4 header. Z1 shows both tracks and an empty lifecycle frame (`t('shell.z1.lifecycle')`, no stage rows). Source: `contracts/shell-zones.md`.
- Focus order is skip link, then Z2, Z1, Z3, Z4, at 1920 px. Source: pitch row B3-D2.
- Drawer, 56 px rail, Z3 at least 712 px at 768, no overlap, no horizontal scroll. Source: pitch row B3-D3.
- Seven `ZoneFrame` states, including `aria-busy` on streaming. Interrupted sends no request for 5 seconds. Source: `contracts/zone-frame-and-message-body.md`.
- XSS fixtures inert. Dashed "AI gợi ý" versus solid "Đã xác nhận". Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output".
- `/sandbox/FPT` sets mirrors. A store write without `navigate()` does not stick. Unknown track, a lowercase symbol, a supplied 404, and a supplied 403 render the same not-found frame inside the shell. No search params. Narrow selectors only. No React Context for `symbol`, pane sizes, or the draft. Source: `contracts/workspace-and-routes.md`; `spec.md` — FR-015 and FR-016.
- Draft survives reload and stop. Send removes the key `dp-stock:z4-draft:${sessionId}:${conversationId}`. Source: `spec.md` — FR-011; `data-model.md` — Draft storage.
- Storybook 11 to 15 dark stories. Axe on every rendered case. The browser worker sets `document.documentElement.dataset.mocks` to `on`. Production `dist/` has no `msw` and no Storybook. Source: `contracts/msw-storybook-ci.md`.

### Explicit non-goals

Light theme, theme switching, the contrast script, visual snapshots, `F6`, Tier D primitive stories as a done bar, chart content, price mocks, core-object routes, identity and `/api/auth/*`, saved presets, typed stream events, resume, cancel, widths below 768 px, a performance budget, and any edit to `docs/**` or `specs/spec-traceability.yaml`. SNR-7.2.1 stays P2. SR-5.2.1 and SR-5.2.2 stay Superseded. SR-1.3.1 and SR-1.3.2 are shell-frame only. Canvas verification stays with M-001.

### SRS landing

| ID | This delivery |
|---|---|
| SR-1.4.1 | B3 shell. This is the done bar for that ID |
| SR-1.4.2 | B3 store and the single `sessionRef` on the companion run. Identity stays with Pitch A |
| SNR-6.1.4 | B3 Vitest proofs plus B5 Storybook and Playwright. Coverage target stays TBD in the SRS |
| SNR-7.1.1 | Exercised at 1920, 1440, 1024, and 768. Priority stays P2 |
| SNR-7.2.1 | axe baseline on the shell and on in-scope stories. Priority stays P2 |
| SR-5.1.2, SNR-8.1.2 | Not re-opened. The shell uses the delivery 1 client |
| SR-5.2.1, SR-5.2.2 | Remain Superseded |
| SR-1.3.1, SR-1.3.2 | Shell frame and `lastRouteByTrack` only |
| SR-1.3.5 | Out of scope |

Source: `spec.md` — "SRS mapping". The registry row is not written in this command (`research.md` R18).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Constitution I and golden rule 3 ask for a traceability refresh. This plan does not edit `docs/**` or `specs/spec-traceability.yaml`, and it does not run the sync gate. | The governing spec forbids those edits (FR-002). Constitution 2.7.0 says the refresh is deferred, not waived. | Running the gate would rewrite the forbidden files. A later change that is allowed to touch them carries the refresh. |
| `docs/domains/frontend/ARCHITECTURE.md` — "5.1 Decided" and "8.1 Current → Target" name Tailwind + Radix as the Pitch B complete UI. This plan does not install them. `TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour" names Radix for focus management. | Delivery 1 left the packages uninstalled. FR-023 cuts Tier D primitive stories. No dialog or account menu ships. The done bar is semantic landmarks, `:focus-visible`, the token CSS, and `react-resizable-panels`. | Installing the primitive set would add a design-system slice the spec marks as the first cut. The gap stays visible here so tasks do not "finish" it by accident. |
| `TECHNICAL_DESIGN.md` — "4.2 Zustand store" types `theme` as `'dark' \| 'light'`. This plan uses `'dark'` only. | FR-016 forbids a light value and a switcher. Light theme is M-001. | Adding the union member would put a light value in the delivery the spec excluded. |
| Symbol validation. "5. Routing and navigation" says "validated by pattern" and does not give the pattern. | The spec forbids inventing a character class. Tests lock `FPT`, `VNINDEX`, `VN30`, and reject a lowercase segment. | A ticker regex would be a guess. |

## Open items

These are not resolved by guessing. `tasks.md` must not pick a value for them.

| ID | Item | Where |
|---|---|---|
| O1 | vi-VN sentences for the skip link and the four zone `aria-label`s. Tests assert `t()`, not a fixed sentence | `spec.md` — "Assumptions"; `contracts/shell-zones.md` |
| O2 | Catalogue key `shell.z2.emptySymbol` is the plan's name for "Chưa chọn mã". The technical design does not name the key. Tasks may keep this key. They must not invent a different sentence | `research.md` R11 |
| O3 | Query `staleTime`, `retry`, and `refetchOnWindowFocus` stay at library defaults. Do not copy the Proposed numbers | `research.md` R2; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.3 Query key taxonomy" |
| O4 | `delta.up`, `delta.down`, and `delta.flat` stay `[NEEDS CLARIFICATION]` in the catalogue. Delta stories render the pattern. They do not invent the phrases | Spec 004 O6; `research.md` R2 |
| O5 | `sessionId` stays off `POST /api/chat`. Do not choose a wire field | Spec 004 O2; `research.md` R10 |
| O6 | Error-reporting product. `reportError` logs to the console | `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items" |
| O7 | Performance budgets. Do not invent one. Lazy feature routes are still in scope | `research.md` R19 |
| O8 | Tailwind and Radix. Do not add them in tasks unless the Product Owner extends the slice | `research.md` R3 |
| O9 | Playwright two-width fallback. Do not apply it unless the Product Owner records that the week ran short | `spec.md` — FR-024 |

## References

Paths only. No document version numbers.

- `specs/005-m000-b-frontend-foundation-shell-qa/spec.md` — Clarifications; User Scenarios; FR-001..FR-026; Success Criteria; Dependencies; Out of Scope; Assumptions; Source conflicts; SRS mapping
- `specs/005-m000-b-frontend-foundation-shell-qa/research.md` — R1..R20
- `specs/005-m000-b-frontend-foundation-shell-qa/data-model.md`
- `specs/005-m000-b-frontend-foundation-shell-qa/quickstart.md`
- `specs/005-m000-b-frontend-foundation-shell-qa/contracts/` — shell-zones, workspace-and-routes, zone-frame-and-message-body, msw-storybook-ci
- `specs/004-m000-b-frontend-foundation-core` — prerequisite B0, B1, B2, B4
- `specs/pitches/M-000-B-frontend-foundation.md` — B3 and B5, including rows B3-D1..D9 and B5-S1..S4
- `docs/domains/frontend/ARCHITECTURE.md` — 4.1 Shell zones; 4.2 Workspace context ownership; 4.3 Building blocks; 5.1 Decided; 5.2 Candidates; 5.3 Carve-outs; 6.1 State ownership matrix; 6.3 Runtime views; 6.5 Security; 7.2 Quality floor; 8.1 Current → Target
- `docs/domains/frontend/TECHNICAL_DESIGN.md` — 3.1 Module tree; 3.2 Feature module contract; 3.3 Boundary enforcement; 3.4 Platform contracts; 3.5 Shell and zone component contracts; 4.1 Ownership; 4.2 Zustand store; 4.3 Query key taxonomy; 5. Routing and navigation; 6.1 Typed REST client; 6.3 SSE client; 6.5 Safe rendering of Agent output; 7. Accessibility and responsive behaviour; 8.2 Pattern rules; 9.1 Pyramid; 9.2 Tests mapped to gates; 10.1 Build and run; 10.2 CRA → Vite migration; 12. Domain-specific constraints and open items
- `docs/domains/frontend/DESIGN_LOCK.md` — 1. Shell geometry; 1.1 Viewport and zone width budget; 2. Workspace context seam; 4.3 Colour and provenance rules; 5. Zone state matrix
- `docs/domains/frontend/DESIGN_SYSTEM.md` — 3.6 Provenance
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md` — Decision; Implementation Direction
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md` — Decision
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md` — Decision
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md` — Decision
- `docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md` — Decision
- `.specify/memory/constitution.md` — I. Spec-Driven, Traceable Delivery; Recorded deferral when the delivery forbids the sync edit
- `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — SR-1.4.1; SR-1.4.2; SNR-6.1.4; SNR-7.1.1; SNR-7.2.1
