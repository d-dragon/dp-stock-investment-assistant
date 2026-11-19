---
pitch: M-000-B
slices: [B3, B5]
rows: [B3-D1, B3-D2, B3-D3, B3-D4, B3-D5, B3-D6, B3-D7, B3-D8, B3-D9, B5-S1, B5-S2, B5-S3]
deferred_rows: [B5-S4]  # moved to M-001
---
# Feature Specification: M-000 Frontend foundation shell and QA (delivery 2 of 2)

**Feature Branch**: `features/pitch-m000-B-frontend-foundation`

**Created**: 2026-11-17

**Status**: Implemented

**Lifecycle Status Rule**: `Draft` until the last open question is resolved. `Clarified` once that ambiguity is closed and planning can start. `Planned`, `Implemented`, and `Verified` wait for that phase's evidence. Source: [Spec Persistence and Feature Status Semantics](../../.specify/memory/constitution.md#spec-persistence-and-feature-status-semantics).

**Input**: Delivery 2 of Pitch B (M-000 Frontend foundation), the reserved half: slice B3 (modular shell, state, and safe rendering; T4 + T5) and thin slice B5 (MSW browser handlers, minimal dark-only Storybook, Frontend CI extended with Storybook and Playwright). B0, B1, B2, and B4 are prerequisites delivered by `specs/004-m000-b-frontend-foundation-core`. Source of truth: `specs/pitches/M-000-B-frontend-foundation.md`, with the frontend architecture, technical design, design lock, design system, ADR-FRONTEND-001..008, and ADR-SYS-001.

## Slice header

Source: [Governance §2.4](../../docs/system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md#24-slice-header-template-top-of-each-spec-kit-specmd). The Given/When/Then text for each row stays in the user stories below, copied from the pitch tables. This header owns the SRS binding.

| Field | Value |
|---|---|
| Slice | B3 modular shell, state, and safe rendering; B5 MSW, minimal Storybook, and Frontend CI |
| ID | `specs/005-m000-b-frontend-foundation-shell-qa` |
| Status | Implemented |
| SRS IDs | [SR-1.4.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-1), [SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2) (shell side), [SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4), [SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-7-usability-accessibility-and-responsive-behavior), [SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-7-usability-accessibility-and-responsive-behavior) (axe baseline only; priority stays P2) |
| Journey step | None delivered. The shell is the Z1–Z4 frame in [Journeys §1.3](../../docs/system/USER_JOURNEYS_WITH_WIREFRAMES.md#13-shell-and-locks-pointers) and [W1](../../docs/system/USER_JOURNEYS_WITH_WIREFRAMES.md#32-w1-empty-adaptive-workspace-shell). J-TFI-1 and J-TFI-2 stay with later Canvas work. |
| IA zone | Z1–Z4 |
| ADRs | [ADR-FRONTEND-001](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md#decision), [ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md#decision), [ADR-FRONTEND-003](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md#decision), [ADR-FRONTEND-008](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md#decision). [ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md#decision) stays with Pitch A. |
| Pitch | [M-000 Frontend foundation](../pitches/M-000-B-frontend-foundation.md) slices [B3](../pitches/M-000-B-frontend-foundation.md#b3-modular-shell-zone-frames-safe-render) and [B5](../pitches/M-000-B-frontend-foundation.md#b5-storybook-minimum-msw-ci) |
| Appetite | Inside the pitch's 1-week budget for B0–B5. This delivery is B3 plus thin B5. |
| Out of scope | B0, B1, B2, B4 (delivery 1); light theme, theme switching, contrast script, visual snapshots (B5-S4); charts and price mocks; identity and `/api/auth/*`; widths below 768 px |

### UX acceptance criteria (owned by the UX Designer)

Each line is one pitch row. The full Given/When/Then is in the matching story below.

- UX-1 (SR-1.4.1): B3-D1, four zone landmarks and `/` to `/sandbox`.
- UX-2 (SR-1.4.1): B3-D2, skip link then Z2, Z1, Z3, Z4 at 1920 px.
- UX-3 (SNR-7.1.1): B3-D3, widths 1920, 1440, 1024, and 768.
- UX-4 (SR-1.4.1): B3-D4, the seven `ZoneFrame` states.
- UX-5 (SR-1.4.1): B3-D5, one zone's error leaves the other three up.
- UX-6 (SR-1.4.2): B3-D6, the Z4 draft survives a same-tab reload and is cleared on send.
- UX-7 (SR-1.4.1): B3-D7, AI versus investor provenance on `MessageBody`.
- UX-8 (SNR-6.1.4): B3-D8, feature files fail lint on colour literals and raw JSX text.
- UX-9 (SR-1.4.1): B3-D9, legacy stylesheets and `src/components/**` imports are gone.
- UX-10 (SNR-6.1.4): B5-S1, every in-scope dark story renders and axe reports no serious or critical issue.
- UX-11 (SNR-7.1.1, SNR-7.2.1): B5-S2, Playwright at the four widths, including B3-D3, with the same axe bar. SNR-7.2.1 stays P2.
- UX-12 (SNR-6.1.4): B5-S3, the production build has no MSW and no Storybook.
- B5-S4 is moved to M-001 and is not a UX criterion of this slice.

## Governance Context *(mandatory)*

Specify obligation: [Document Referencing](../../.specify/memory/constitution.md#document-referencing-in-spec-kit-workflows). This delivery does not edit `docs/**`, Accepted ADRs, or `specs/spec-traceability.yaml`. The registry note that still says Draft is a recorded deferral, not a second status.

**Source requirements**:

- [SR-1.4.1 Modular zone shell](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-1)
- [SR-1.4.2 In-session workspace context](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2)
- [SNR-6.1.4 Frontend testability baseline](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4)
- [SNR-7 Usability, Accessibility, and Responsive Behavior](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-7-usability-accessibility-and-responsive-behavior) for SNR-7.1.1 and SNR-7.2.1
- [SR-5.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-1-2), [SNR-8.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-8-1-2), [SR-5.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-1), and [SR-5.2.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-2) are not re-opened here

**Authoritative inputs**:

- [Pitch M-000-B, B3 and B5](../pitches/M-000-B-frontend-foundation.md#solution-sketch-foundation-shell-not-canvas-product-ui)
- [Pitch B5 stories](../pitches/M-000-B-frontend-foundation.md#b5-storybook-minimum-msw-ci) and [cut order](../pitches/M-000-B-frontend-foundation.md#cut-order-inside-the-design-criteria)
- [TECHNICAL_DESIGN §3.1 Module tree](../../docs/domains/frontend/TECHNICAL_DESIGN.md#31-module-tree)
- [TECHNICAL_DESIGN §3.3 Boundary enforcement](../../docs/domains/frontend/TECHNICAL_DESIGN.md#33-boundary-enforcement-target-g2)
- [TECHNICAL_DESIGN §3.5 Shell and zone component contracts](../../docs/domains/frontend/TECHNICAL_DESIGN.md#35-shell-and-zone-component-contracts-target-g2)
- [TECHNICAL_DESIGN §4.2 Zustand store](../../docs/domains/frontend/TECHNICAL_DESIGN.md#42-zustand-store-target-g3)
- [TECHNICAL_DESIGN §5 Routing and navigation](../../docs/domains/frontend/TECHNICAL_DESIGN.md#5-routing-and-navigation-target-g3)
- [TECHNICAL_DESIGN §6.5 Safe rendering of Agent output](../../docs/domains/frontend/TECHNICAL_DESIGN.md#65-safe-rendering-of-agent-output-target-m-000-must)
- [TECHNICAL_DESIGN §8.2 Pattern rules](../../docs/domains/frontend/TECHNICAL_DESIGN.md#82-pattern-rules)
- [TECHNICAL_DESIGN §9.2 Tests mapped to gates](../../docs/domains/frontend/TECHNICAL_DESIGN.md#92-tests-mapped-to-gates)
- [TECHNICAL_DESIGN §10.1 Build and run](../../docs/domains/frontend/TECHNICAL_DESIGN.md#101-build-and-run-target)
- [DESIGN_LOCK §1 Shell geometry](../../docs/domains/frontend/DESIGN_LOCK.md#1-shell-geometry-w1) and [§1.1 Viewport and zone width budget](../../docs/domains/frontend/DESIGN_LOCK.md#11-viewport-and-zone-width-budget-proposed)
- [DESIGN_LOCK §5 Zone state matrix](../../docs/domains/frontend/DESIGN_LOCK.md#5-zone-state-matrix)
- [ARCHITECTURE §4.1 Shell zones](../../docs/domains/frontend/ARCHITECTURE.md#41-shell-zones-ia-26-design_lockmd)
- [ADR-FRONTEND-003 Decision](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md#decision)
- [ADR-FRONTEND-008 Decision](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md#decision)

**Traceability target**:

- `specs/spec-traceability.yaml` feature `005-m000-b-frontend-foundation-shell-qa` is `mapped` to the system SRS at partial coverage. The derived status is `implemented`. `.verify-done` is absent, so the feature is not `verified`. The generated `pitch-trace` block names slices B3 and B5.

**Sync targets** (deferred for this delivery):

- `docs/**`, Accepted ADRs, and `specs/spec-traceability.yaml` stay unchanged. A later change that is allowed to touch them refreshes anchors and the registry note.

## Clarifications

### Session 2026-11-17

- Q: Which Storybook theme set does this delivery ship? → A: Dark-only minimal set. Light theme, theme switching, the contrast script, and visual snapshots move to M-001. Product Owner, 2026-11-17. Governing: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI" and "B5: Storybook minimum, MSW, CI"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules".
- Q: Which folder names does this delivery use? → A: `features/` and `platform/`. Product Owner, 2026-11-17. Governing: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack". ADR-FRONTEND-001 — "Implementation Direction" (`modules/`) is stale on this point.

### Session 2026-11-19

- Q: Is the Storybook inventory one story file per M-tier case (22), or about 15 stories that still cover every named case? → A: About 15, and every named M-tier case still renders. The Product Owner decision of 2026-11-17, repeated in the pitch and in [TECHNICAL_DESIGN §8.2](../../docs/domains/frontend/TECHNICAL_DESIGN.md#82-pattern-rules), sizes the set at about 15 dark compact stories for zone states, `PriceCell`, `Delta`, `StatusBadge`, and `MessageBody`. The stories table requires `ZoneFrame` as one story per state (7). It names the other cases without requiring one file per case. Tier D primitive stories are the first cut and are not required. A 22-file reading is not in the authored documents. The testable bound is 11 to 15 stories: exactly 7 `ZoneFrame` stories, plus at least one story each for `PriceCell`, `Delta`, `StatusBadge`, and `MessageBody`, and no more than 15 stories in that required set. Up, down, zero, and missing, and the three `MessageBody` cases, render as variants when they are not their own stories. Axe runs on every rendered case, not only the default args.
- Q: What sits in the Z2 utilities corner? → A: No account menu and no sign-in control. Below 1440 px the corner holds the Z4 drawer toggle with `aria-expanded`. At 1440 px and above Z4 is docked and that toggle is not the opener. Governing: pitch row B3-D3; [DESIGN_LOCK §1](../../docs/domains/frontend/DESIGN_LOCK.md#1-shell-geometry-w1) and [§1.1](../../docs/domains/frontend/DESIGN_LOCK.md#11-viewport-and-zone-width-budget-proposed). Identity stays with Pitch A.
- Q: What does the Z1 rail show below 1024 px? → A: A 56 px rail with both track icons. Each icon has an `aria-label` and a tooltip. Text labels show on hover or focus only. The active track has a visible mark besides the icon. Governing: pitch row B3-D3; [DESIGN_LOCK §1.1](../../docs/domains/frontend/DESIGN_LOCK.md#11-viewport-and-zone-width-budget-proposed).
- Q: Does stop, idle timeout, or "Tạo lại" clear the Z4 draft? → A: No. Stop, and the delivery 1 idle timeout, move the run to `interrupted` and keep the draft and any partial message. "Tạo lại" sends no request until activated; once activated it sends the same user message again as a new run. Only send clears the draft. There is no mid-run resume. Governing: pitch row B3-D6 and the 2026-11-17 idle-timeout decision; [TECHNICAL_DESIGN §6.3](../../docs/domains/frontend/TECHNICAL_DESIGN.md#63-sse-client-target-g1-g6).
- Q: Does B3 mount a chart? → A: No chart engine and no chart content. Sandbox Z3 still has an empty chart slot. Portfolio does not. Z3 empty shows an invitation through `t()` and does not start a Case. Governing: pitch No-gos; [DESIGN_LOCK §5](../../docs/domains/frontend/DESIGN_LOCK.md#5-zone-state-matrix); [TECHNICAL_DESIGN §5](../../docs/domains/frontend/TECHNICAL_DESIGN.md#5-routing-and-navigation-target-g3).
- Q: Which MSW handlers are required? → A: The same handlers for health, config, `models/*`, and chat, in Vitest and in the browser when `VITE_USE_MOCKS` is true. No other paths. No price handler. Governing: pitch No-gos; [TECHNICAL_DESIGN §6.1](../../docs/domains/frontend/TECHNICAL_DESIGN.md#61-typed-rest-client-target-g1-types-when-codegen-wired).

## User Scenarios & Testing *(mandatory)*

Stories follow slice order. B3 is P1. Thin B5 is P2 and starts after B3. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Slices" and "Delivery workflow (agentic)".

Each story is tested on its own. Both assume the delivery 1 toolchain, client, tokens, format module, and `t()` catalogue already exist. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Agent constraints for every slice"; `specs/004-m000-b-frontend-foundation-core`.

Design-row convention for every scenario below: user-facing text is a catalogue key through `t()`, not a JSX literal; tests select by `data-zone`, `data-state`, `data-origin`, and ARIA role, never by CSS class. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Design acceptance criteria (UX)".

### User Story 1 - Modular shell, state, and safe rendering (B3) (Priority: P1)

The Software Engineer splits the app into a shell and feature modules, hosts zones Z1–Z4 as composition slots, shares in-session workspace context without copying Backend session state, and renders Agent text through `MessageBody` so the XSS cases stay inert.

**Why this priority**: Later Canvas work mounts into this shell. Safe Agent rendering closes the T4 half of the XSS disposition. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering" and "Problem"; SR-1.4.1; SR-1.4.2.

**Independent Test**: From `frontend/`, `npm run lint` passes with `react/no-danger` still an error, and the G2, G3, and XSS tests pass. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering" (Proving commands); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G2, G3) and "6.5 Safe rendering of Agent output".

**Acceptance Scenarios**:

1. **Given** the shell at `/` at 1920 px, **When** it renders, **Then** row B3-D1 holds, `/` redirects to `/sandbox`, and Z2 is not resizable. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D1; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation (Target G3)" and "9.2 Tests mapped to gates" (G2); SR-1.4.1.
2. **Given** the shell has loaded at 1920 px, **When** the user presses Tab repeatedly, **Then** row B3-D2 holds. `F6` zone-cycling tests are not in this delivery. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D2; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" and "7. Accessibility and responsive behaviour"; `docs/domains/frontend/DESIGN_LOCK.md` — "6. Quality floor".
3. **Given** widths 1920, 1440, 1024, and 768, **When** the shell renders, **Then** row B3-D3 holds, including the DESIGN_LOCK width budget (Z1 rail 56 px below 1024, Z3 at least 712 px at 768, Z4 overlay drawer below 1440). Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D3; `docs/domains/frontend/DESIGN_LOCK.md` — "1.1 Viewport and zone width budget"; SNR-7.1.1.
4. **Given** a `ZoneFrame`, **When** `state` is each of `empty`, `loading`, `ready`, `stale`, `error`, `interrupted`, and `streaming`, **Then** row B3-D4 holds. Z2 empty shows the catalogue value "Chưa chọn mã". Z4 interrupted shows "Tạo lại" and does not resume automatically. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D4; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "8. Patterns" (Stream message); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts".
5. **Given** a component in one zone throws, **When** the shell renders, **Then** row B3-D5 holds and `reportError` is called for that zone. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D5; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" and "3.4 Platform contracts"; `docs/domains/frontend/ARCHITECTURE.md` — "7.2 Quality floor".
6. **Given** text typed in the Z4 input, **When** the page reloads in the same tab, **Then** row B3-D6 holds. The stored value is draft text only. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D6; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store (Target G3)"; `docs/domains/frontend/DESIGN_LOCK.md` — "2. Workspace context seam"; ADR-FRONTEND-003 — "Decision".
7. **Given** `MessageBody` renders a message, **When** `data-origin` is `ai` or `investor`, **Then** row B3-D7 holds. **When** the XSS fixtures in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output" are rendered, **Then** they are inert and markdown tables, lists, and bold still render. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D7 and "B3 — Modular shell, state, and safe rendering"; `docs/domains/frontend/DESIGN_LOCK.md` — "4.3 Colour and provenance rules"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance" and "8. Patterns".
8. **Given** any file under `src/features/**`, **When** lint runs, **Then** row B3-D8 holds. `react/jsx-no-literals` also covers `app/` and `design-system/patterns/` with the allowed punctuation list in the technical design. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D8; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)".
9. **Given** the new shell, **When** it ships, **Then** row B3-D9 holds. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D9; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" (fresh rebuild and step T6's deletion end state).
10. **Given** the URL `/sandbox/FPT`, **When** the shell loads, **Then** the store mirrors match that deep link, a track switch navigates and restores `lastRouteByTrack`, and the store does not change `symbol`, `coreObjectRef`, or track except by navigating. An unknown track renders the not-found frame inside the shell. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store (Target G3)", "5. Routing and navigation (Target G3)", and "9.2 Tests mapped to gates" (G3); ADR-FRONTEND-003 — "Decision"; SR-1.4.2.

**Agent constraints** (copied from `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering"):

- T-steps: T4 + T5.
- Files: `src/app/**`, `src/features/**`, `MessageBody`.
- Proving commands: `npm run lint` passes with `react/no-danger`; the G2 / G3 and XSS tests pass.

T-step mapping. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" (Pitch B slice ↔ step map) and "9.2 Tests mapped to gates":

| Step | Change this delivery uses | Evidence |
|---|---|---|
| T4 | Split the app into `app/` shell + `features/companion` + `features/models`; add `MessageBody`; keep `react/no-danger` as an error | G2 shell assertions; XSS cases inert |
| T5 | React Router, `platform/workspace`, `useUrlSync`, zone wiring | G3 |

`react/no-danger` is already enabled by delivery 1. This slice does not turn it on a second time and does not turn it off. Source: `specs/004-m000-b-frontend-foundation-core` (B1 lint); `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering". The "turn on `react/no-danger`" clause in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step T4 is stale. See "Source conflicts".

Resolved paths, because the pitch line is a hint and the module tree is the realization. `MessageBody` and `ZoneFrame` live under `design-system/patterns/`. The shell lives under `src/app/` (`WorkspaceShell`, `ZoneHost`, router, providers). The workspace store lives under `platform/workspace`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)", "3.5 Shell and zone component contracts", "4.2 Zustand store (Target G3)", and "6.5 Safe rendering of Agent output". See "Source conflicts".

#### Design acceptance criteria (copied verbatim)

Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B3: modular shell, zone frames, safe render".

| # | Tier | Given / When / Then | Proven by |
|---|---|---|---|
| B3-D1 | M | **Given** the shell at `/` at 1920 px, **when** it renders, **then** there are four zones: Z2 `role=banner`, Z1 `role=navigation`, Z3 `role=main`, Z4 `role=complementary`, each with `data-zone="z1".."z4"` and an `aria-label` key. | Vitest + RTL |
| B3-D2 | M | **Given** the shell has loaded, **when** the user presses Tab repeatedly, **then** focus goes skip link first, then Z2 → Z1 → Z3 → Z4 (checked by the focused element's closest `data-zone`), and every focused element has a visible focus ring (`:focus-visible` outline ≥ 2 px). One Playwright test at 1920 px; F6 zone cycling and the full keyboard suite are deferred to M-001. | Playwright |
| B3-D3 | M | **Given** widths 1920, 1440, 1024, 768, **when** the shell renders, **then**: at ≥ 1440 all four zones are side by side; below 1440 Z4 is an overlay drawer opened from a Z2 toggle with `aria-expanded`; below 1024 Z1 is a 56 px rail where both track icons have an `aria-label`; at 768 Z3 is ≥ 712 px wide; zones never overlap (bounding boxes) and the page never scrolls horizontally (`scrollWidth <= clientWidth`). | Playwright, 4 widths |
| B3-D4 | M | **Given** a `ZoneFrame`, **when** `state` is each of `empty, loading, ready, stale, error, interrupted, streaming`, **then** it renders `data-state` with that value and the DESIGN_LOCK §5 frame: error has a retry button; interrupted shows the "Tạo lại" action and sends **no** request until clicked (MSW request count stays 0 for 5 s); streaming shows a stop button; loading has `aria-busy="true"`. | Vitest + RTL + MSW |
| B3-D5 | M | **Given** a component in one zone throws, **when** the shell renders, **then** that zone shows `data-state="error"` and the other three zones still render their content. | Vitest + RTL |
| B3-D6 | M | **Given** text typed in the Z4 input, **when** the page reloads in the same tab, **then** the text is restored from `sessionStorage` (key namespaced by `sessionRef`); **when** the message is sent, **then** the key is removed. | Playwright |
| B3-D7 | M | **Given** `MessageBody` renders a message with `data-origin="ai"`, **then** the edge is dashed and the "AI gợi ý" label is visible; with `data-origin="investor"` the edge is solid and "Đã xác nhận" is visible. Both labels come from `t()` keys, never JSX literals. Hue alone never carries the difference. | Vitest + RTL |
| B3-D8 | M | **Given** any file under `src/features/**`, **when** lint runs, **then** it fails on a hex, `rgb(` or `hsl(` colour literal, and on raw JSX text (`react/jsx-no-literals`). | ESLint in CI |
| B3-D9 | M | **Given** the clean rebuild (Product Owner, 2026-11-17: fresh frontend, refactoring the current app is acceptable), **when** the new shell ships, **then** the legacy `src/App.css` and `src/index.css` are deleted, the only global stylesheet is the token and base layer from B4, and no new module imports a legacy component from `src/components/**`. Legacy behaviour worth keeping is rebuilt on `ZoneFrame` and `MessageBody`, not restyled in place. | ESLint `no-restricted-imports` + file check in CI |

Files in scope (hint in the pitch): `src/app/shell/**`, `src/platform/zone-frame/**`, `src/platform/message-body/**`. This spec follows the module tree instead of that hint. See "Source conflicts". Must not change: `docs/**`, Backend code. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B3: modular shell, zone frames, safe render".

---

### User Story 2 - MSW, minimal Storybook, and Frontend CI (B5) (Priority: P2)

The Software Engineer serves the same OpenAPI-typed MSW handlers in development and in Vitest, ships a minimal dark-only Storybook set, and extends the delivery 1 Frontend CI skeleton with Storybook and Playwright with axe. Neither MSW nor Storybook ships in the production bundle.

**Why this priority**: B5 is the thin QA slice after the shell exists. It is the same milestone bet, and it is the checkpoint for the Playwright rows named on B3. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Slices", "B5 — MSW, minimal Storybook, and Frontend CI", and "Delivery workflow (agentic)"; ADR-FRONTEND-008 — "Decision".

**Independent Test**: From `frontend/`, `npx playwright test` and `npm run build-storybook` pass, and `rg -l "msw|mockServiceWorker" dist` returns nothing. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI" (Proving commands).

**Acceptance Scenarios**:

1. **Given** the MSW handlers typed from the OpenAPI-generated types, **When** the app runs in development with `VITE_USE_MOCKS` true and **When** Vitest runs, **Then** both use those same handlers. Features do not import MSW. A production build (`VITE_USE_MOCKS` absent or false) does not start the worker. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI" (Acceptance); ADR-FRONTEND-008 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".
2. **Given** a handler path, **When** this delivery adds or keeps a handler, **Then** the path is already in `docs/openapi.yaml`. `GET /api/market/prices/{symbol}` is not added. Price mocks are not added. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client, OpenAPI types, SSE-only transport, and Socket.IO removal" (Agent constraints) and "No-gos".
3. **Given** the M-tier stories in the stories table, **When** CI runs them in the dark compact theme, **Then** row B5-S1 holds. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B5-S1 and "B5: Storybook minimum, MSW, CI"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules".
4. **Given** the shell route served by MSW, **When** Playwright runs at 1920, 1440, 1024, and 768 px, **Then** row B5-S2 holds, which includes B3-D3, and the one keyboard-order test at 1920 px (skip link, then Z2, Z1, Z3, Z4) passes. SNR-7.2.1 stays P2. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B5-S2 and "B5 — MSW, minimal Storybook, and Frontend CI"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour"; SNR-7.1.1; SNR-7.2.1.
5. **Given** a production build, **When** `dist/` is scanned, **Then** row B5-S3 holds. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B5-S3; ADR-FRONTEND-008 — "Decision".
6. **Given** the delivery 1 CI skeleton, **When** this delivery extends it, **Then** the skeleton order stays lint, then `tsc --noEmit`, then Vitest, then build, and Storybook plus Playwright follow the build. The trigger of the existing Docker workflow is unchanged. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Acceptance) and "B5 — MSW, minimal Storybook, and Frontend CI" (Agent constraints); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run" (CI).

Rows B3-D2, B3-D3, and B3-D6 are B3 behavior. Their Playwright execution is this story's checkpoint, because T7 owns Playwright. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" (Pitch B slice ↔ step map).

**Agent constraints** (copied from `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI"):

- T-steps: T7 + Storybook, CI, and Playwright.
- The new CI file must not change the trigger of the existing Docker workflow.
- Proving commands: `npx playwright test` and `npm run build-storybook` pass; `rg -l "msw|mockServiceWorker" dist` returns nothing.

T-step mapping. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" and "9.2 Tests mapped to gates" (G5):

| Step | Change this delivery uses | Evidence |
|---|---|---|
| T7 remainder | Playwright + axe at the four widths; one keyboard-order test at 1920 px | G5 axe and keyboard portion; B3-D2, B3-D3, B3-D6 |
| Storybook | Minimal dark-only set in "B5: Storybook minimum, MSW, CI" | B5-S1; `npm run build-storybook` |
| CI | Extend the delivery 1 skeleton; production-bundle scan | B5-S3; Docker workflow trigger unchanged |

Chart-library import lint, token lint, and lint rules 1–3 stay as delivery 1 left them. This slice does not rebuild those rules. Source: `specs/004-m000-b-frontend-foundation-core`; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" (B4 takes the chart-library part of T7).

#### Design acceptance criteria (copied verbatim)

Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5: Storybook minimum, MSW, CI".

The Storybook minimum that fits the week (about 15 stories):

| Tier | Stories |
|---|---|
| M | `ZoneFrame`: one story per state (7) |
| M | `PriceCell`, `Delta`, `StatusBadge`: up, down, zero, missing (the P1–P4 cases) |
| M | `MessageBody`: ai and investor origin, one XSS fixture |
| D | Primitives (button, input), dark theme only |
| Moved to M-001 | A theme toggle story, and the light half of the dark/light matrix for every story |

| # | Tier | Given / When / Then | Proven by |
|---|---|---|---|
| B5-S1 | M | **Given** the stories above, **when** CI runs, **then** every story renders without error and axe reports no serious or critical issue in it. | Storybook test runner / addon-vitest |
| B5-S2 | M | **Given** the shell route served by MSW, **when** Playwright runs at 1920, 1440, 1024 and 768 px, **then** B3-D3 holds and axe reports no serious or critical issue (SNR-7.2.1 stays P2). | Playwright + axe |
| B5-S3 | M | **Given** a production build, **then** `dist/` contains no `msw`, no `mockServiceWorker.js` and no Storybook code. | Script over `dist/` in CI |
| B5-S4 | Moved to M-001 | **Given** each `ZoneFrame` state story, **when** it renders in both themes, **then** the screenshot matches the approved baseline. | Visual snapshot (defer: flaky in week 1) |

---

### Edge Cases

- A throw in one zone shows that zone's error frame and leaves the other three rendering. `reportError` records the zone. The reporting tool stays a console sink. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" and "12. Domain-specific constraints and open items".
- `ZoneFrame` state `interrupted` shows "Tạo lại" and sends no request until the control is activated. The MSW request count stays 0 for 5 seconds. Stop and the idle timeout both land here and keep the draft and any partial message. Activated "Tạo lại" sends the same user message again as a new run. There is no automatic resume. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D4 and the 2026-11-17 idle-timeout decision; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client".
- `ZoneFrame` state `loading` sets `aria-busy="true"`. `streaming` also sets `aria-busy="true"`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D4; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts".
- The Z4 thread uses `aria-live="polite"` and announces at message end, not per token. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour".
- A reload in the same tab restores the Z4 draft from `sessionStorage` keyed by `sessionRef`. Send removes the key. The value is draft text only, never a token or credential. Another tab does not share that `sessionStorage` entry. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D6; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store (Target G3)".
- A deep link `/sandbox/FPT` sets the mirrors. `/sandbox/VNINDEX` and `/sandbox/VN30` are valid symbol examples. A track outside `{sandbox, portfolio}` renders the not-found frame inside the shell. A lowercase symbol segment renders not-found. Search params are not part of M-000 routes. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation (Target G3)".
- A direct store write of `symbol`, `coreObjectRef`, or track without `navigate()` does not stick. `useUrlSync()` is the only writer of those mirrors. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store (Target G3)"; ADR-FRONTEND-003 — "Decision".
- Chart range, interval, and series type are per-symbol store preferences when the store holds them. They are not URL params. Sandbox Z3 has an empty chart slot and no chart content. Portfolio has no chart slot. Z3 empty shows an invitation through `t()` and does not start a Case. Source: `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation (Target G3)"; ADR-FRONTEND-003 — "Decision".
- XSS fixtures `<img src=x onerror=alert(1)>`, `<script>alert(1)</script>`, `[x](javascript:alert(1))`, and an `<a onclick>` render inert: no event-handler attribute, no `script` element, no `javascript:` href. Markdown tables, lists, and bold still render. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output".
- Hue alone does not distinguish AI-suggested from investor-confirmed. The edge (dashed vs solid) and the visible `t()` label both carry the difference. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D7; `docs/domains/frontend/DESIGN_LOCK.md` — "4.3 Colour and provenance rules".
- At 1440 px and above, all four zones are side by side and the Z4 drawer toggle is not the opener. Below 1440, Z4 is an overlay drawer opened from the Z2 utilities corner, with `aria-expanded`. Below 1024, Z1 is a 56 px rail: both track icons have an `aria-label` and a tooltip, text labels show only on hover or focus, and the active track has a visible mark. At 768 px, Z3 is at least 712 px wide. Zones do not overlap and the page does not scroll horizontally. Widths below 768 px are out of scope. The proposed 240 px and 440 px defaults are not the done bar. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D3; `docs/domains/frontend/DESIGN_LOCK.md` — "1.1 Viewport and zone width budget"; SNR-7.1.1.
- Focus order is skip link, then Z2, Z1, Z3, Z4. The visible focus ring is a `:focus-visible` outline of at least 2 px. Focus rings also meet the contrast floor in `docs/domains/frontend/DESIGN_LOCK.md` — "6. Quality floor" (SC 1.4.11, at least 3:1 against adjacent colours). Resize handles on Z1, Z3, and Z4 are keyboard operable. Z2 has no resize handle. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D2; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts".
- `VITE_USE_MOCKS` true starts the MSW browser worker in development. Absent or false, a production build contains no `msw` and no `mockServiceWorker`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run"; ADR-FRONTEND-008 — "Decision".
- axe on shell routes and on in-scope stories reports no serious or critical issue. SNR-7.2.1 stays P2. A serious or critical issue fails the check. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B5-S1 and B5-S2; SNR-7.2.1.
- The four Playwright widths are the acceptance. The two-width fallback (1920 and 768 px only) applies only when the Product Owner says the week ran short. The Software Engineer does not take that cut alone. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Appetite" and "B5 — MSW, minimal Storybook, and Frontend CI".
- A planted hex, `rgb(`, or `hsl(` literal under `src/features/**`, a planted JSX string literal outside the allowed punctuation list, a planted `dangerouslySetInnerHTML`, or a planted import from `src/components/**` fails lint. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B3-D8 and B3-D9; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" and "6.5 Safe rendering of Agent output".

## Requirements *(mandatory)*

### Test-first rule

- **FR-001**: For B3 and for B5, the Software Engineer MUST write the tests, confirm they fail, and only then implement, without editing those tests. B3's failing tests are the Vitest proofs for the G2 shell assertions, the G3 store and route assertions, the XSS cases, and the Vitest rows B3-D1, B3-D4, B3-D5, B3-D7, and B3-D8. B5's failing tests are the Playwright proofs (including B3-D2, B3-D3, and B3-D6), the Storybook render and axe proofs, and the production-bundle scan. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" (Spec Kit rules).

### Agent constraints for every in-scope slice

Copied from `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" (Agent constraints for every slice). All commands run from `frontend/`.

- Proving commands: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`.
- Must not change: `backend/`; `docs/**`, including `docs/openapi.yaml`; the Accepted ADRs; `main`; the Product Owner's main tree (work in a worktree); the `wt/m001-s3` worktree.
- No `socket.io-client`, WebSocket, or EventSource; `fetch` only in `platform/api` and `platform/stream`; `VITE_*` environment variables only.
- "AI gợi ý" and "Đã xác nhận", like every user-facing string, go through `t()`.

- **FR-002**: Implementation of B3 and B5 MUST run in a named git worktree on `features/pitch-m000-B-frontend-foundation`. It MUST NOT modify `backend/`, `docs/**` (including `docs/openapi.yaml`), the Accepted ADRs, `main`, the Product Owner's main tree, or the `wt/m001-s3` worktree. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)".
- **FR-003**: This delivery MUST keep the target Frontend free of `socket.io-client`, a WebSocket client, and `EventSource`. `fetch` MUST remain only in `platform/api` and `platform/stream`. Public build settings MUST remain `VITE_*` only. Every user-facing string, including "AI gợi ý", "Đã xác nhận", "Tạo lại", "Chưa chọn mã", and "Không có dữ liệu", MUST come from the vi-VN catalogue through `t()`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Agent constraints for every slice"; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix" and "8. Translation-ready copy"; ADR-FRONTEND-005 — "Decision".
- **FR-004**: New feature code MUST live under `features/`. Platform code for the workspace store MUST live under `platform/`. This delivery MUST NOT introduce a `modules/` tree. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)"; `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack". Product Owner, 2026-11-17.

### Functional Requirements

#### B3

- **FR-005**: B3 MUST implement T4 and T5. T4 MUST split the current app into the `app/` shell, `features/companion`, and `features/models`, and MUST add `MessageBody`. T5 MUST add React Router, the `platform/workspace` store, `useUrlSync`, and zone wiring. A feature folder MUST expose only `index.ts` to the outside, MUST NOT import another feature, and MUST NOT call `fetch`. The shell composes features. `platform/` MUST NOT import `features/` or `app/`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)", "3.2 Feature module contract", "3.3 Boundary enforcement (Target G2)", and "10.2 CRA → Vite migration"; ADR-FRONTEND-001 — "Decision" and "Guardrails"; ADR-FRONTEND-002 — "Decision".
- **FR-006**: The shell MUST render four zone landmarks as in row B3-D1: Z2 `role=banner`, Z1 `role=navigation`, Z3 `role=main`, Z4 `role=complementary`, each with `data-zone` of `z1` through `z4` and an `aria-label` whose value comes from `t()`. `/` MUST redirect to `/sandbox`. Z1 MUST show both tracks at once (Sandbox and Portfolio) plus an empty lifecycle frame. Z2 MUST NOT contain Z1 content. The model selector MUST render in the Z4 header, not in Z2. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D1; `docs/domains/frontend/DESIGN_LOCK.md` — "1. Shell geometry"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" (Z4 slot) and "5. Routing and navigation (Target G3)"; `docs/domains/frontend/ARCHITECTURE.md` — "4.1 Shell zones"; SR-1.4.1.
- **FR-007**: Keyboard order MUST match row B3-D2: skip link first, then Z2, Z1, Z3, Z4, with a `:focus-visible` outline of at least 2 px, proven by one Playwright test at 1920 px. The skip link's visible text MUST come from `t()`. The technical design describes that link as skip-to-workspace; the catalogue holds the vi-VN string. `F6` zone cycling and the full keyboard suite MUST NOT be built here. Z1, Z3, and Z4 resize handles MUST be keyboard operable. Z2 MUST NOT be resizable. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D2; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" and "7. Accessibility and responsive behaviour"; `docs/domains/frontend/DESIGN_LOCK.md` — "6. Quality floor"; `docs/domains/frontend/ARCHITECTURE.md` — "5.1 Decided".
- **FR-008**: At the widths in row B3-D3 the shell MUST keep four zones side by side at 1440 px and above; below 1440 px Z4 MUST be an overlay drawer opened from a Z2 toggle with `aria-expanded`; below 1024 px Z1 MUST be a 56 px rail whose two track icons each have an `aria-label` and a tooltip, with text labels only on hover or focus, and a visible active-track mark besides the icon; at 768 px Z3 MUST be at least 712 px wide; zone boxes MUST NOT overlap; the page MUST NOT scroll horizontally. Zones MUST NOT stack. The proposed 240 px and 440 px defaults in the design lock are not the done bar. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D3; `docs/domains/frontend/DESIGN_LOCK.md` — "1.1 Viewport and zone width budget"; SNR-7.1.1.
- **FR-009**: `ZoneFrame` MUST implement row B3-D4 for `empty`, `loading`, `ready`, `stale`, `error`, `interrupted`, and `streaming`, including `data-state`, the error retry control, the interrupted "Tạo lại" control that sends no request until activated (MSW request count stays 0 for 5 seconds), the streaming stop control, and `aria-busy="true"` while loading. `aria-busy="true"` MUST also be set while streaming. On Z4, both the error retry and the interrupted action use the visible label "Tạo lại" from `t()`. Z4 interrupted MUST NOT auto-resume. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D4; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "8. Patterns".
- **FR-010**: A throw inside one zone MUST render that zone at `data-state="error"` with retry and MUST call `reportError` with the zone. The other three zones MUST still render their content. The error-reporting tool MUST stay a console sink. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D5; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts", "3.5 Shell and zone component contracts", and "12. Domain-specific constraints and open items"; `docs/domains/frontend/ARCHITECTURE.md` — "4.3 Building blocks".
- **FR-011**: The unsent Z4 composer text MUST be saved to `sessionStorage` under a key namespaced by `sessionRef`, restored on reload in the same tab, and removed when the message is sent. Stop, idle timeout, and `interrupted` MUST NOT remove that key. The entry MUST hold draft text only. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D6 and the 2026-11-17 idle-timeout decision; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store (Target G3)" and "6.3 SSE client"; `docs/domains/frontend/DESIGN_LOCK.md` — "2. Workspace context seam"; ADR-FRONTEND-003 — "Decision".
- **FR-012**: `MessageBody` MUST render model text with markdown and MUST NOT parse raw HTML. Unsafe URL schemes, including `javascript:`, MUST be blocked. Links MUST use `rel="noopener noreferrer nofollow"` and `target="_blank"`. Images MUST stay off. The XSS fixtures in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output" MUST render inert, and markdown tables, lists, and bold MUST still render. Row B3-D7 MUST hold for `data-origin="ai"` and `data-origin="investor"`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D7 and "B3 — Modular shell, state, and safe rendering"; `docs/domains/frontend/DESIGN_LOCK.md` — "4.3 Colour and provenance rules"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance" and "8. Patterns".
- **FR-013**: Lint MUST fail on a hex, `rgb(`, or `hsl(` colour literal under `src/features/**`, and on raw JSX text via `react/jsx-no-literals` in `app/`, `features/`, and `design-system/patterns/`. The allowed-strings list is the punctuation and symbols named in the technical design (`·`, `—`, `/`, `%`, `₫`, `+`, `−`). Tickers and numbers come from data and MUST NOT need allow-listing. `react/no-danger` MUST remain an error with no exceptions. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D8 and "B3 — Modular shell, state, and safe rendering"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)".
- **FR-014**: When the shell ships, `src/App.css` and `src/index.css` MUST be absent. The only global stylesheet MUST be the token and base layer from delivery 1 (B4). No new module MUST import a legacy component from `src/components/**`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D9; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration".
- **FR-015**: Routes MUST be the M-000 set only: `/` redirects to `/sandbox`; `/:track` accepts `sandbox` or `portfolio` and any other track renders the not-found frame inside the shell; `/:track/:symbol` accepts an uppercase ticker or index code, including the examples `FPT`, `VNINDEX`, and `VN30`; a lowercase symbol renders not-found; `*` renders the not-found frame inside the shell. Core-object routes (`/:track/:symbol/:coreType/:coreId`) MUST NOT ship. No search params ship. Parsing MUST live in pure functions in `platform/workspace/routeParams.ts` with unit tests. A Backend 404 or 403 for a ref the shell did request MUST render not-found. The Frontend MUST NOT decide access. M-000 feature route elements MUST be lazy. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation (Target G3)"; ADR-FRONTEND-003 — "Decision" and "Consequences". `docs/domains/frontend/ARCHITECTURE.md` — "7.2 Quality floor" marks the performance row, including route code-splitting, as Target M-001 and leaves budgets TBD. This delivery follows the routing section for lazy feature routes and does not set a performance budget or lazy-load a chart engine.
- **FR-016**: Shareable state (`track`, `symbol`, `coreObjectRef`) MUST be owned by the URL. The Zustand workspace mirrors MUST be written only by `useUrlSync()`. A component that changes symbol, object, or track MUST call `navigate()`. A unit test MUST assert the store never changes those fields without a navigation. The store MUST own session UI (pane sizes, collapsed flags, UI flags) and per-symbol context (last open object, and chart range, interval, and series type as data only). `context` and pane sizes MUST persist to `sessionStorage` for the same tab. `ui.theme` MUST stay `dark` only. This delivery MUST NOT switch theme and MUST NOT add a `light` value. Durable per-user preferences and saved layout presets MUST NOT be built. Features MUST select the store with narrow selectors. React Context MUST NOT carry fast-changing values. One store MUST use the four slices `workspace`, `context`, `layout`, and `ui`. Devtools middleware MUST be development-only. Source: ADR-FRONTEND-003 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.1 Ownership" and "4.2 Zustand store (Target G3)"; `docs/domains/frontend/DESIGN_LOCK.md` — "2. Workspace context seam"; `docs/domains/frontend/ARCHITECTURE.md` — "4.2 Workspace context ownership" and "6.1 State ownership matrix"; SR-1.4.2.
- **FR-017**: Server data MUST go through TanStack Query. The M-000 query keys MUST be the factory entries for health, config, and models only. This delivery MUST NOT add a prices query, a market-price call, or a handler for `GET /api/market/prices/{symbol}`. Query `staleTime`, `retry`, and `refetchOnWindowFocus` numbers stay Proposed in the technical design. This spec does not choose them. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.1 Ownership" and "4.3 Query key taxonomy"; `specs/pitches/M-000-B-frontend-foundation.md` — "No-gos"; ADR-FRONTEND-002 — "Decision".
- **FR-018**: `sessionRef` MUST stay an opaque `{sessionId, conversationId}` held once with the Z4 companion run and sent with chat requests through the delivery 1 client. The workspace mirrors MUST NOT store a second copy. The Frontend MUST NOT copy the Backend thread. No global `X-User-ID`, no `Authorization` header, and no token in JavaScript, storage, or fixtures. `/api/auth/*` and sign-in UI MUST NOT be built. The Z2 utilities corner MUST NOT render an account menu. Below 1440 px that corner MUST hold the Z4 drawer toggle with `aria-expanded`. At 1440 px and above that toggle MUST NOT be the opener, because Z4 is docked. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D3 and "B3 — Modular shell, state, and safe rendering"; `docs/domains/frontend/DESIGN_LOCK.md` — "1. Shell geometry" and "1.1 Viewport and zone width budget"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.1 Ownership" and "3.4 Platform contracts"; ADR-FRONTEND-003 — "Decision"; ADR-SYS-001 — "Decision"; SR-1.4.2.
- **FR-019**: The Z4 stream MUST keep using `platform/stream` from delivery 1. Companion run states MUST remain `idle`, `streaming`, `done`, `interrupted`, and `error`. Stop from `streaming`, and the delivery 1 idle timeout, MUST move the run to `interrupted` and MUST keep the Z4 draft and any partial message. "Tạo lại" MUST send the same user message again as a new run, and MUST NOT send until activated. There is no mid-run resume. The Z4 thread MUST use `aria-live="polite"` and MUST announce at message end, not per token. This delivery MUST NOT invent typed stream events, resume, or cancel. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client" and "7. Accessibility and responsive behaviour"; `specs/pitches/M-000-B-frontend-foundation.md` — "Open questions" (idle timeout, 2026-11-17) and "Rabbit holes".
- **FR-020**: This delivery MUST NOT build `ChartEngine` or `StatChart`, MUST NOT render chart content, MUST NOT add `lightweight-charts` or `chart.js` to `package.json`, and MUST NOT compute reference, ceiling, or floor prices. Sandbox Z3 MUST still include an empty chart slot. Portfolio MUST NOT include that slot. A route test MUST show the slot present on `/sandbox` and absent on `/portfolio`. Z3 empty MUST show an invitation whose text comes from `t()`, and MUST NOT start a Case. The chart-import lint from delivery 1 stays in force. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Rabbit holes" and "No-gos"; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix" and "7. Chart"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation (Target G3)"; ADR-FRONTEND-004 — "Decision".

#### B5

- **FR-021**: MSW handlers MUST be typed from the OpenAPI-generated types and MUST be the same handlers in the Vitest suites and in the browser when `VITE_USE_MOCKS` is true. `VITE_USE_MOCKS` MUST be a build-time setting. Features MUST call the API layer the same way in mock and live modes and MUST NOT import MSW or Storybook. The handler set MUST cover health, config, `models/*`, and chat, and MUST NOT cover any other path. This delivery MUST NOT add price mocks or `GET /api/market/prices/{symbol}`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI" and "No-gos"; ADR-FRONTEND-008 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client" and "10.1 Build and run"; SNR-6.1.4.
- **FR-022**: A production build MUST NOT bundle `src/mocks/`, MSW, `mockServiceWorker.js`, or Storybook. `rg -l "msw|mockServiceWorker" dist` MUST return nothing. Row B5-S3 MUST pass in CI. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B5-S3 and "B5 — MSW, minimal Storybook, and Frontend CI" (Proving commands); ADR-FRONTEND-008 — "Decision".
- **FR-023**: Storybook MUST ship a dark-only, compact-density set that covers the M-tier cases in the stories table: `ZoneFrame` one story per state (empty, loading, ready, stale, error, interrupted, streaming); `PriceCell`, `Delta`, and `StatusBadge` for up, down, zero, and missing; `MessageBody` for ai origin, investor origin, and one XSS fixture. Every story that ships MUST render without error, and axe MUST report no serious or critical issue in it (row B5-S1). The set MUST NOT include a light theme, a theme-toggle story, token pages, or visual snapshots (row B5-S4 stays moved to M-001). Tier D primitive stories (button, input, dark only) are the first cut and are NOT required for done. The required set is 11 to 15 stories: exactly 7 `ZoneFrame` stories, plus at least one story each for `PriceCell`, `Delta`, `StatusBadge`, and `MessageBody`, and no more than 15 stories in that set. Up, down, zero, missing, and the three `MessageBody` cases render as variants when they are not their own stories. Axe runs on every rendered case, not only the default args. A catalogue of 22 story files fails this bound. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5: Storybook minimum, MSW, CI", "B5 — MSW, minimal Storybook, and Frontend CI", and "Cut order inside the design criteria"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules".
- **FR-024**: Playwright with axe MUST run the shell route at 1920, 1440, 1024, and 768 px and MUST fail on a serious or critical axe issue. That run MUST show that row B3-D3 holds. One keyboard-order test at 1920 px MUST check skip link, then Z2, Z1, Z3, Z4. SNR-7.2.1 MUST stay P2. The 1920-and-768-only fallback MUST NOT be applied unless the Product Owner records that the week ran short. `F6` zone-cycling tests and visual snapshots MUST NOT be added. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B5-S2, "Appetite", and "B5 — MSW, minimal Storybook, and Frontend CI"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour" and "9.1 Pyramid"; SNR-7.1.1; SNR-7.2.1.
- **FR-025**: Frontend CI MUST keep the delivery 1 order (lint, then `tsc --noEmit`, then Vitest, then build) and MUST then run Storybook (`npm run build-storybook` and the story axe run) and Playwright. The new or extended CI file MUST NOT change the trigger of the existing Docker workflow. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI" (Agent constraints) and "B1 — Vite shell and subtract" (Acceptance); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".
- **FR-026**: From `frontend/`, the B3 checkpoint MUST pass `npm run lint` with `react/no-danger`, plus the G2, G3, and XSS tests. The B5 checkpoint MUST pass `npx playwright test` and `npm run build-storybook`, and `rg -l "msw|mockServiceWorker" dist` MUST return nothing. The shared commands `npm ci`, `npx tsc --noEmit`, `npx vitest run`, and `npm run build` MUST still pass. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering", "B5 — MSW, minimal Storybook, and Frontend CI", and "Agent constraints for every slice".

### Key Entities

- **Workspace context**: The URL-owned track, symbol, and Core-object reference, plus the store mirrors, per-symbol session context, pane sizes, and the single opaque `sessionRef` held with the Z4 run. The Backend owns the thread. Source: SR-1.4.2; ADR-FRONTEND-003 — "Decision"; `docs/domains/frontend/ARCHITECTURE.md` — "6.1 State ownership matrix".
- **Zone frame**: One of Z1–Z4, with a state of empty, loading, ready, stale, error, interrupted, or streaming, a landmark role, `data-zone`, and `data-state`. Source: `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix"; SR-1.4.1.
- **Agent message**: Markdown rendered by `MessageBody`, with `data-origin` of `ai` or `investor` and a `t()` label. Untrusted model text is not HTML. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output"; `docs/domains/frontend/DESIGN_LOCK.md` — "4.3 Colour and provenance rules".
- **MSW handler set**: Request handlers typed from generated OpenAPI types, shared by Vitest and the development browser worker, limited to paths already in `docs/openapi.yaml`. Source: ADR-FRONTEND-008 — "Decision".
- **Storybook story**: A dark, compact catalogue entry for a zone state or a named pattern case. Light and snapshot entries are not in this delivery. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5: Storybook minimum, MSW, CI".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The shell test shows four landmarks (Z2 banner, Z1 navigation, Z3 main, Z4 complementary), each with `data-zone` and an `aria-label` from `t()`, and `/` lands on `/sandbox`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D1; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G2); SR-1.4.1.
- **SC-002**: A thrown child in one zone leaves the other three zones rendering, and that zone shows `data-state="error"`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D5; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G2).
- **SC-003**: The XSS fixtures render with no event-handler attribute, no `script` element, and no `javascript:` href, and markdown tables, lists, and bold still render. `data-origin="ai"` shows a dashed edge and "AI gợi ý"; `data-origin="investor"` shows a solid edge and "Đã xác nhận". Both labels come from `t()`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output"; `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D7.
- **SC-004**: Loading `/sandbox/FPT` sets the store mirrors. A store write of symbol or track without navigation does not change the URL-owned values. An unknown track renders the in-shell not-found frame. `/sandbox` shows an empty chart slot and `/portfolio` shows none. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation (Target G3)" and "9.2 Tests mapped to gates" (G3); ADR-FRONTEND-003 — "Decision"; SR-1.4.2.
- **SC-005**: After reload in the same tab, the Z4 draft text is restored, and after send the `sessionStorage` key is gone. Stop and idle timeout leave that key in place, and the partial message stays visible. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D6; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client".
- **SC-006**: Each `ZoneFrame` state renders its `data-state`. Interrupted issues no request for 5 seconds. Loading and streaming set `aria-busy="true"`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B3-D4; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts".
- **SC-007**: Lint fails a planted feature colour literal, a planted JSX string literal, a planted `dangerouslySetInnerHTML`, and a planted import from `src/components/**`. `src/App.css` and `src/index.css` are absent. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B3-D8 and B3-D9.
- **SC-008**: Playwright passes at 1920, 1440, 1024, and 768 px with no horizontal scroll, the B3-D3 geometry, no serious or critical axe issue, and the 1920 px keyboard order skip link → Z2 → Z1 → Z3 → Z4. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B3-D2, B3-D3, and B5-S2; SNR-7.1.1; SNR-7.2.1.
- **SC-009**: `npm run build-storybook` passes. The required dark set has 11 to 15 stories, including 7 `ZoneFrame` stories and one story each for `PriceCell`, `Delta`, `StatusBadge`, and `MessageBody`. Every named case renders, and axe reports no serious or critical issue on any rendered case. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B5-S1 and "B5 — MSW, minimal Storybook, and Frontend CI" (Proving commands); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules".
- **SC-010**: `rg -l "msw|mockServiceWorker" dist` returns nothing, and the production build contains no Storybook runtime. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B5-S3.
- **SC-011**: CI runs lint, then `tsc --noEmit`, then Vitest, then build, then Storybook, then Playwright, and the existing Docker workflow trigger is unchanged. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI" (Agent constraints); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".
- **SC-012**: For B3 and for B5, the test log shows a failing run of the new tests before the implementation change, and those test files are unchanged by that implementation. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)".

## Dependencies

B0, B1, B2, and B4 are prerequisites. They are delivered by `specs/004-m000-b-frontend-foundation-core` and are not re-specified here. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Slices" and "Delivery workflow (agentic)". Product Owner operating rule for this specification.

- **B0** agent instructions on the target stack, including `features/` and `platform/`, Vite, Vitest, `VITE_*` only, and no Socket.IO. This delivery does not rewrite instruction files.
- **B1** Vite shell, Vitest with jsdom, the MSW base setup, the G1 smoke, the Frontend CI skeleton (lint, then `tsc --noEmit`, then Vitest, then build), lint rules 1–3, and `react/no-danger` as an error. Node 26 (`engines.node` `>=26.13.0`, `engine-strict=true`) is already required before `npm ci`.
- **B2** generated OpenAPI types, the `platform/api` client, the `platform/stream` reader, `NoAuthAdapter`, removal of `socket.io-client`, and the MSW stream fixture. This delivery uses that client and does not change the Backend stream.
- **B4** dark tokens, the `data-theme="dark"` hook, the vi-VN `t()` catalogue, `fmt`, self-hosted fonts, `PriceCell`, `Delta`, `StatusBadge`, and the chart-import lint. Light theme, theme switching, and the contrast script stay in M-001.

`docs/openapi.yaml` already describes the health, config, `models/*`, and chat paths. Those are the only handler paths (FR-021). This delivery does not edit that file. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client"; `specs/pitches/M-000-B-frontend-foundation.md` — "No-gos".

## Out of Scope

Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Cut order inside the design criteria", "Rabbit holes", "No-gos", and "Open questions" (cut line, 2026-11-17).

- B0, B1, B2, and B4, except consuming them. Delivery 1 owns those slices.
- Light theme, theme switching, the contrast script (rows B4-T5 and B4-T6), token Storybook pages, the light half of story matrices, and visual snapshots (row B5-S4).
- Tier D Storybook primitives (button, input) as a done-bar. They are the first cut.
- `F6` zone-cycling tests and the full keyboard suite.
- The 1920-and-768-only Playwright fallback, unless the Product Owner records that the week ran short.
- Chart interfaces, chart content, price mocks, `GET /api/market/prices/{symbol}`, and adding `lightweight-charts` or `chart.js`. The empty Sandbox chart slot stays (FR-020).
- Core-object routes and any M-001 Canvas zone content, including a working Decision gate.
- Identity, login, owner isolation, and `/api/auth/*` (Pitch A; ADR-SYS-001). This delivery keeps the delivery 1 same-origin client and `NoAuthAdapter`.
- A production market-data feed or licensed provider.
- Computing reference, ceiling, or floor prices.
- Micro-frontends (ADR-FRONTEND-001 rejected this for now).
- Generated UI (ADR-FRONTEND-006, Proposed — Future).
- Choosing an i18n library or shipping an English catalogue (ADR-FRONTEND-005, Future).
- Saved layout presets (M-009).
- Typed stream events, resume, or cancel.
- Backend stream headers, heartbeat emission, and HTTP/2 ingress.
- Raising SNR-7.2.1 from P2 to P1.
- Widths below 768 px (SNR-7.1.1, Future).
- Choosing the still-Proposed libraries named in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items" (`openapi-fetch`, `eslint-plugin-boundaries`, Style Dictionary, SSE parser, query default timings, the error-reporting product).
- Changes to `docs/**`, the pitch file, Accepted ADRs, `backend/`, `specs/spec-traceability.yaml`, `specs/004-m000-b-frontend-foundation-core`, or `.specify/feature.json` as part of this specification.

## Assumptions

- Delivery 1 is the prerequisite baseline this spec tests against. Where delivery 1 already enabled a lint rule, this delivery keeps it and does not restate the enabling work.
- The M-tier cases named in the B5 stories table are all in scope. Their packaging is the 11-to-15 story bound in FR-023, taken from the Product Owner's "about 15" size plus the explicit 7 `ZoneFrame` stories.
- Tier D primitive stories are out of the done bar for this thin slice. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Cut order inside the design criteria".
- The skip link and the four zone `aria-label` values are vi-VN catalogue entries through `t()`. Sources name the landmark roles and the skip-to-workspace intent. They do not give a fixed Vietnamese sentence for those five strings. Tests assert role, `data-zone`, and that the accessible name comes from `t()`, not a JSX literal.
- Symbol acceptance includes the technical design's examples `FPT`, `VNINDEX`, and `VN30`, uppercase only. Section 5 says "validated by pattern" and does not give the pattern. This spec does not invent a character class. Planning uses the examples, the uppercase rule, and the not-found rule. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation (Target G3)".
- Query `staleTime`, `retry`, and `refetchOnWindowFocus` stay at the technical design's Proposed numbers. This delivery does not adopt those numbers and does not test them. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.3 Query key taxonomy".
- The design lock's 240 px Z1 and 440 px Z4 defaults are marked Proposed. The done bar is the pitch row: the 56 px rail, Z3 at least 712 px at 768, and the breakpoint behavior in FR-008. Source: `docs/domains/frontend/DESIGN_LOCK.md` — "1.1 Viewport and zone width budget".
- `aria-busy="true"` on streaming is required in addition to the pitch row, which names loading. The pitch does not forbid the streaming case. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts".
- CI order after the delivery 1 skeleton is Storybook, then Playwright, matching the technical design's "build, then e2e" order. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".
- `sessionRef` lives once on the Z4 companion run. That single reference is the shared shell context the pitch names. The workspace slices do not duplicate it. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.1 Ownership"; `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering"; SR-1.4.2.
- Both-tracks-visible Z1 geometry is part of the shell frame. This delivery does not record SR-1.3.1 or SR-1.3.2 as verified Canvas behavior. Source: `docs/domains/frontend/DESIGN_LOCK.md` — "1. Shell geometry"; `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — "SR-1.4: Modular presentation shell".
- Reduced-motion token behavior stays with the B4 token pipeline. This delivery does not add a second motion system. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "6. Motion"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour".

## Source conflicts

Resolved by the Product Owner on 2026-11-17, or by the pitch's own "hint" versus the technical design, as noted. The story-count bound was closed on 2026-11-19 from those same authored sentences. Stale documents are a follow-up doc fix. They are not edited here. The requirements above are the resolved behavior.

- **Storybook theme and visual snapshots.** Resolved. Dark-only minimal set. Light theme, theme switching, the contrast script, and visual snapshots move to M-001. Governing: `specs/pitches/M-000-B-frontend-foundation.md` — "B5: Storybook minimum, MSW, CI" (stories table and row B5-S4) and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Stale: `docs/domains/frontend/DESIGN_SYSTEM.md` — "10. Quality" (pattern stories include both themes, and visual regression, from M-000); `docs/domains/frontend/DESIGN_LOCK.md` — "4.2 Token groups" (light built on the same tokens and contrast-checked from day one).

- **Feature folder name.** Resolved. `features/` and `platform/`. Governing: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack". Stale: ADR-FRONTEND-001 — "Implementation Direction", the `modules/` wording.

- **Pattern directory for `ZoneFrame` and `MessageBody`.** Resolved. They live under `design-system/patterns/`. The shell lives under `src/app/`. Governing: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)", "3.5 Shell and zone component contracts", and "6.5 Safe rendering of Agent output". The pitch says realization lives in the technical design and labels the other paths as a hint (`src/platform/zone-frame/**`, `src/platform/message-body/**`, `src/app/shell/**` in "B3: modular shell, zone frames, safe render"). This spec follows the module tree.

- **Model selector placement.** Resolved. The model selector renders in the Z4 header. Governing: `docs/domains/frontend/DESIGN_LOCK.md` — "1. Shell geometry" and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" (Z4 slot). Stale: the Z2 slot line in that same "3.5" table that still lists a `features/models` selector on Z2.

- **`react/no-danger` timing.** Resolved. Delivery 1 enables the rule. This delivery keeps it as an error and adds `MessageBody`. Stale: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step T4, the clause that turns the rule on there. Same resolution as `specs/004-m000-b-frontend-foundation-core` — "Source conflicts" (Lint-rule timing).

- **Legacy stylesheet deletion.** Resolved for the end state. Row B3-D9 requires `src/App.css` and `src/index.css` to be absent when this shell ships, and delivery 1's spec does not require that deletion. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step T6 also names the deletion under B4. This delivery owns the end-state check. If the files are already absent, the check still holds.

- **Playwright.** Resolved. Playwright + axe is required. Governing: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI" and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour" and "9.1 Pyramid". Still marked open in older rows: `docs/domains/frontend/ARCHITECTURE.md` — "5.2 Candidates" and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items" (E2E tool Proposed). The pitch acceptance names the tool.

- **Price fixtures versus ADR-FRONTEND-008.** Resolved. This delivery does not add price mocks or `GET /api/market/prices/{symbol}`. Governing: `specs/pitches/M-000-B-frontend-foundation.md` — "No-gos" and the 2026-11-17 cut line in "Open questions". ADR-FRONTEND-008 — "Decision" says fixtures follow the M-001 mock-data rules. That standard applies when M-001 adds those fixtures. It does not pull them into B5.

- **Where `sessionRef` is held.** Resolved. One opaque pair on the Z4 companion run, which is the shared reference. The workspace slices do not store a second copy, and the Frontend does not copy the thread. Governing together: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.1 Ownership"; `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering"; SR-1.4.2; ADR-FRONTEND-003 — "Decision".

- **Z2 utilities corner.** Resolved. No account menu. Below 1440 px the corner is the Z4 drawer toggle. At 1440 px and above Z4 is docked. See FR-018.
- **Chart slot versus chart content.** Resolved. Sandbox keeps an empty slot. Portfolio has none. No engine, no chart content, no Case. See FR-020.
- **Handler set.** Resolved. Health, config, `models/*`, and chat only. See FR-021.
- **Story count.** Resolved. The authored size is about 15 dark compact stories. `ZoneFrame` is 7 stories. The other named cases stay in the catalogue as stories or as variants, and the required set is 11 to 15 stories. A 22-file inventory is not required and fails the bound. See FR-023 and the 2026-11-19 clarification.

- **Route code-splitting label.** Resolved for the M-000 routes. Feature route elements are lazy. Governing: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation (Target G3)". `docs/domains/frontend/ARCHITECTURE.md` — "7.2 Quality floor" marks that performance row as Target M-001 and leaves budgets TBD. This delivery does not set a budget and does not lazy-load a chart engine.

## SRS mapping

| ID | Statement this delivery uses | Where it lands |
|---|---|---|
| SR-1.4.1 | Modular zone shell with Z1–Z4 as composition slots | B3 shell. This delivery's done bar for that ID. |
| SR-1.4.2 | In-session workspace context, shell side: track, symbol, Core-object reference, and `sessionRef` as references only | B3 store and companion reference. Identity and cross-device restore stay with Pitch A. |
| SNR-6.1.4 | Automated Frontend unit and component tests for the presentation shell and the workspace context store | B3 Vitest proofs, plus B5 Storybook and Playwright. Delivery 1 already covers the G1 path and the streaming-client seam. Coverage target stays TBD in the SRS text. |
| SNR-7.1.1 | Viewports 768–1920 px, 1920 px primary; below 768 px is Future | Exercised at 1920 / 1440 / 1024 / 768. 1920 / 768 only if the Product Owner applies the fallback. Priority stays P2. |
| SNR-7.2.1 | WCAG 2.2 AA target | axe baseline on shell routes and in-scope stories. Priority stays P2. The contrast script stays in M-001. |
| SR-5.1.2 | SSE with `text/event-stream` | Not re-opened. The shell uses the delivery 1 client. |
| SNR-8.1.2 | HTTPS+SSE, Frontend part | Not re-opened. Delivery 1 records "Frontend part verified" against the MSW fixture. |
| SR-5.2.1 | WebSocket real-time events | Remains Superseded. |
| SR-5.2.2 | WebSocket reconnection | Remains Superseded. |
| SR-1.3.1 | Both tracks visible | Shell frame only (Z1 shows both tracks). Canvas verification stays with M-001. |
| SR-1.3.2 | Context preserved on switching | Store seam only (`lastRouteByTrack`, per-symbol `sessionStorage`). Canvas verification stays with M-001. |
| SR-1.3.5 | Docked price chart | Out of scope (M-001). |

Source for the allocation: `specs/pitches/M-000-B-frontend-foundation.md` — "Requirements covered", "Slices", and "Done means"; `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — "SR-1.4: Modular presentation shell", "SR-1.3: Adaptive Visual Canvas", and the SNR-6.1.4, SNR-7.1.1, SNR-7.2.1, SNR-8.1.2, SR-5.1.2, SR-5.2.1, and SR-5.2.2 rows.

## References

Paths only. No document version numbers.

- `specs/pitches/M-000-B-frontend-foundation.md` — Problem; Appetite; Solution sketch (B3, B5); Delivery workflow (agentic); Design acceptance criteria (UX), including B3-D1..D9 and B5-S1..S4; Cut order inside the design criteria; Rabbit holes; Risks; No-gos; Done means; Open questions
- `specs/004-m000-b-frontend-foundation-core` — prerequisite delivery of B0, B1, B2, and B4
- `docs/domains/frontend/TECHNICAL_DESIGN.md` — 3.1 Module tree; 3.2 Feature module contract; 3.3 Boundary enforcement; 3.4 Platform contracts; 3.5 Shell and zone component contracts; 4.1 Ownership; 4.2 Zustand store; 4.3 Query key taxonomy; 5. Routing and navigation; 6.3 SSE client; 6.5 Safe rendering of Agent output; 7. Accessibility and responsive behaviour; 8.2 Pattern rules; 9.1 Pyramid; 9.2 Tests mapped to gates; 10.1 Build and run; 10.2 CRA → Vite migration; 12. Domain-specific constraints and open items
- `docs/domains/frontend/ARCHITECTURE.md` — 4.1 Shell zones; 4.2 Workspace context ownership; 4.3 Building blocks; 5.1 Decided; 5.2 Candidates; 5.3 Carve-outs; 6.1 State ownership matrix; 7.2 Quality floor
- `docs/domains/frontend/DESIGN_LOCK.md` — 1. Shell geometry; 1.1 Viewport and zone width budget; 2. Workspace context seam; 4.2 Token groups; 4.3 Colour and provenance rules; 5. Zone state matrix; 6. Quality floor; 7. Chart
- `docs/domains/frontend/DESIGN_SYSTEM.md` — 3.6 Provenance; 6. Motion; 7. Icons; 8. Patterns; 9. Content voice; 10. Quality
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md` — Decision; Implementation Direction; Guardrails
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md` — Decision
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md` — Decision; Consequences
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md` — Decision (chart work stays out of this delivery)
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-005-I18N-READINESS-SEAM.md` — Decision
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-006-GENERATED-UI-COMPONENT-REGISTRY.md` — Decision (Future; out of scope)
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-007-DESIGN-TOKEN-ARCHITECTURE.md` — Decision (dark tokens already delivered by B4; light stays in M-001)
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md` — Decision
- `docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md` — Decision (identity behavior stays in Pitch A)
- `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — SR-1.3: Adaptive Visual Canvas; SR-1.4: Modular presentation shell; SR-5.1.2; SR-5.2.1; SR-5.2.2; SNR-6.1.4; SNR-7.1.1; SNR-7.2.1; SNR-8.1.2
- `docs/openapi.yaml` — path list for MSW handlers; not edited by this delivery
