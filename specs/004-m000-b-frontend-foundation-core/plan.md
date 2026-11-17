# Implementation Plan: M-000 Frontend foundation core (delivery 1 of 2)

**Branch**: `features/pitch-m000-B-frontend-foundation` | **Date**: 2026-11-17 | **Spec**: `specs/004-m000-b-frontend-foundation-core/spec.md`

**Input**: Feature specification from `specs/004-m000-b-frontend-foundation-core/spec.md`

**Note**: This file is the `/speckit-plan` output. Phase 0 is `research.md`. Phase 1 is `data-model.md`, `contracts/`, and `quickstart.md`. `tasks.md` is a later command.

## Summary

Delivery 1 of Pitch B replaces the Frontend instruction set and the Create React App toolchain, then adds a same-origin typed client, an SSE chat reader, and the dark-token / vi-VN format seam. B3 (shell, router, store, `MessageBody`) and B5 (Storybook, browser MSW, Playwright width matrix) stay in a reserved feature.

The Software Engineer implements later, in a named git worktree on `features/pitch-m000-B-frontend-foundation`, not in the main tree. The Product Owner installs Node v26.13.1 before the first B1 run. Shared proof from `frontend/` is `npm ci`, `npx tsc --noEmit`, `npx vitest run`, and `npm run build`.

Design choices are in `research.md`. Each one cites a path and a section heading, an ADR ID, an SRS ID, or a pitch slice. Packages the technical design still marks Proposed are not selected.

Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — "User Scenarios & Testing" and FR-001 through FR-032; `specs/pitches/M-000-B-frontend-foundation.md` — "Slices" and "Delivery workflow (agentic)".

## Technical Context

**Language/Version**: TypeScript 5.9 or newer, as a direct dependency, on Node `>=26.13.0`. Prerequisite runtime: Node v26.13.1. React 18 type packages, aligned with React 18. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Node pin and Known traps); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step "T1 types fix".

**Primary Dependencies**: Vite, Vitest, jsdom, React Testing Library, MSW for the test base, `openapi-typescript` for `src/platform/api/generated/schema.d.ts`, Tailwind config that exposes no `market` or `state` colour utilities. Not selected in this plan: `openapi-fetch`, `eslint-plugin-boundaries`, Style Dictionary, an SSE parser package, an i18n library, `lightweight-charts`, `chart.js`, React Router, Zustand, TanStack Query. Source: ADR-FRONTEND-002 — "Decision"; ADR-FRONTEND-008 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items"; `research.md` R4, R5, R8, R11, R13, R16.

**Storage**: None. This delivery does not add the shell store, `sessionStorage` draft behavior, or a Backend collection. `sessionRef` is an opaque pair on the client type only. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — "Key Entities" and "Out of Scope" (B3).

**Testing**: B0 is `grok inspect` plus an instruction search, with no test file. B1, B2, and B4 are test-first on Vitest (jsdom). B2 adds the codegen drift check and `rg socket.io dist`. B4 adds exact `fmt` tests, a chart-import lint fixture, a dark-token fixture, and one Playwright font check (B4-T4) that is not a CI-skeleton job. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-001 and Success Criteria; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.1 Pyramid" and "9.2 Tests mapped to gates".

**Target Platform**: Browser SPA built by Vite to static `dist/`. Dev server proxies `/api` to port 5000. Image `node:26-alpine` packages `dist`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run"; ADR-SYS-001 — "Decision".

**Project Type**: Frontend package inside this repository (`frontend/`). Backend, agent, and data stores are out of this delivery.

**Performance Goals**: Not set. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items" leaves performance budgets TBD until after the Vite step. This plan does not invent a number (`research.md` R20).

**Constraints**: No `socket.io-client`, WebSocket, or `EventSource`. `fetch` only in `platform/api` and `platform/stream`. `VITE_*` only. Every user-facing string through `t()`. No edits to `backend/`, `docs/**`, Accepted ADRs, `main`, the main tree, or the `wt/m001-s3` worktree. Work happens in a worktree. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" (Agent constraints for every slice).

**Scale/Scope**: One Frontend package. Slices B0, B1, B2, and thin B4. B3 and B5 are reserved. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — "Out of Scope".

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

Governing file: `.specify/memory/constitution.md`. Memory loaded for this command: `constitution.md`, `architecture.md`, the five architecture view files, `architecture-repo-facts.md`, and `sync-impact-report-v1.0.0.md`. The architecture memory describes the agent runtime. It does not add a Frontend stack rule beyond the constitution principles below.

### Pre-research gate

| Principle | Result | Why |
|---|---|---|
| I. Spec-Driven, Traceable Delivery | Pass with recorded deviation | This plan cites the spec, the pitch, the frontend design set, ADR-FRONTEND-001..008, ADR-SYS-001, and the SRS IDs the pitch names. It does not edit `docs/` or `specs/spec-traceability.yaml`. That edit is forbidden for this delivery (`research.md` R21). Traceability refresh waits for a later change that is allowed to touch those files. |
| II. Layered Boundaries and Explicit Ownership | Pass | Browser calls only the Backend, through `platform/api` and `platform/stream`. This delivery does not touch routes, services, repositories, the agent runtime, or checkpointer payloads. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "2. Domain scope and boundaries"; `.specify/memory/constitution.md` — "II. Layered Boundaries and Explicit Ownership". |
| III. Evidence-Grounded Financial Intelligence | Pass | Formatters format numbers they are given. `PriceCell` does not compute reference, ceiling, or floor. No chart engine and no market feed are added. Source: ADR-FRONTEND-004 — "Decision"; ADR-FRONTEND-005 — "Decision"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-029. |
| IV. Prompts, Memory, and Fine-Tuning Control Behavior, Not Truth | Not applicable | No prompt, STM, or fine-tune surface is in this delivery. |
| V. Deterministic Tools and Contracted Interfaces | Pass | The client consumes `docs/openapi.yaml` and does not change it. SSE frames stay the current contract. Socket.IO stays out. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract"; SNR-8.1.2. |
| VI. Testability and Observability Are First-Class | Pass | Proving commands are in `quickstart.md`. B0's proof is `grok inspect` plus search, which the spec exempts from the failing-test rule. `reportError` and production telemetry stay out of this delivery (`docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items", error reporting tool still open). |
| VII. Secure, Simple, Reversible Change | Pass | `NoAuthAdapter`, no token in the bundle, same-origin cookies later, CRA removed rather than kept beside Vite. Rollback is the worktree, not a second build system. Source: ADR-FRONTEND-002 — "Guardrails"; ADR-SYS-001 — "Decision". |

### Document-referencing obligation

`speckit.plan` lists affected long-lived documents and whether their anchors need updates. This command updates none of them.

| Document | Anchors that disagree with this delivery | Updated here |
|---|---|---|
| `docs/domains/frontend/DESIGN_SYSTEM.md` — "1. Principles" and "10. Quality" | Light theme and both-theme Storybook stories are described as M-000 work | No. Follow-up doc fix. Spec "Source conflicts" |
| `docs/domains/frontend/DESIGN_LOCK.md` — "4.2 Token groups" | Light theme contrast-checked from day one | No. Same |
| `docs/domains/frontend/DECISIONS/ADR-FRONTEND-005-I18N-READINESS-SEAM.md` — "Decision" | One sentence sends every number through `Intl` | No. The later price-board bullet governs |
| `docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md` — "Implementation Direction" | Says `modules/` | No. Instructions say `features/` |
| `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" | Places `react/no-danger` on T4 and rules 1–3 on T7 | No. Pitch timing governs this delivery |
| `docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md` — "Decision" | Colour bullet replaced by ADR-FRONTEND-007. MSW / Storybook "later phases" bullet replaced by ADR-FRONTEND-008 | No. This plan does not restate the replaced bullets |
| `docs/openapi.yaml` | Contract input for codegen | No |
| `specs/spec-traceability.yaml` | Would record SNR-8.1.2 as "Frontend part verified" when implementation evidence exists | No. Out of scope for this delivery's edits |
| `frontend/AGENTS.md`, root `AGENTS.md`, `.github/instructions/frontend-react.instructions.md`, stale `CLAUDE.md` / `.claude/rules` / `.cursor/rules` | B0 rewrites these during implementation | Not in this planning command |

Source: `.specify/memory/constitution.md` — "Document Referencing in Spec-Kit Workflows" (`speckit.plan` row); `specs/004-m000-b-frontend-foundation-core/spec.md` — "Source conflicts" and FR-002.

### Post-design re-check

Phase 1 artifacts (`data-model.md`, `contracts/`, `quickstart.md`) stay inside this feature directory. They add no Backend route, no agent tool, no secret, and no second build system. The open items in `research.md` are named and are not filled with a package choice. Gate result is unchanged: pass, with the traceability deviation in the table below.

## Project Structure

### Documentation (this feature)

```text
specs/004-m000-b-frontend-foundation-core/
├── spec.md
├── plan.md                 # this file
├── research.md             # Phase 0
├── data-model.md           # Phase 1
├── quickstart.md           # Phase 1
├── contracts/              # Phase 1
│   ├── README.md
│   ├── instruction-set.md
│   ├── toolchain-and-ci.md
│   ├── platform-api.md
│   ├── chat-stream.md
│   └── format-catalogue-tokens.md
├── checklists/requirements.md
└── tasks.md                # not created by this command
```

### Source code (implementation targets, not created by this command)

Paths the later worktree is expected to touch. B3 and B5 paths are absent on purpose.

```text
frontend/
├── AGENTS.md                          # B0
├── .nvmrc                             # B1, contents: 26
├── .npmrc                             # B1, engine-strict=true
├── .env.example                       # B2, idle-timeout stopgap
├── Dockerfile                         # B1, node:26-alpine, dist
├── index.html                         # B1, moved to the Vite root
├── vite.config.ts                     # B1, proxy /api to :5000
├── package.json                       # B1 engines, scripts, dependency cuts
├── tsconfig.json                      # B1
├── eslint.config.js                   # B1 rules 1–3 and react/no-danger; B4 rules 4 and 5
├── tailwind.config.*                  # B4, no market or state colour utilities
├── public/fonts/                      # B4, self-hosted
└── src/
    ├── platform/api/                  # B2 client
    │   └── generated/schema.d.ts      # B2, openapi-typescript output
    ├── platform/stream/               # B2 SSE reader
    ├── platform/auth/                 # B2 NoAuthAdapter
    ├── platform/format/               # B4 fmt
    ├── platform/i18n/                 # B4 t() and vi-VN catalogue
    ├── platform/chart/                # B4 lint seam only
    ├── platform/stat-chart/           # B4 lint seam only
    ├── design-system/tokens/          # B4 source and generated CSS
    ├── design-system/patterns/PriceCell/
    ├── design-system/patterns/Delta/
    ├── design-system/patterns/StatusBadge/
    └── test/                          # B1 MSW base and G1 smoke

# Also B0, outside frontend/src:
AGENTS.md                              # Frontend lines only
.github/instructions/frontend-react.instructions.md
CLAUDE.md, .claude/rules, .cursor/rules   # stale stack lines only
.github/workflows/frontend-ci.yml            # B1 CI skeleton
```

Deleted in B1 when still unreferenced: `components/OptimizedApp.js`, `components/PerformanceProfiler.js`, `components/WebSocketTest.tsx`, `components/MessageFormatter.js`, `services/apiService.ts`, `utils/performance.js`, plus dead `config-overrides.js` and `webpack.config.dev.js`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step T0; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Known traps).

**Structure Decision**: The target tree is `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)", cut down to the slices in this delivery. Folders are `features/` and `platform/`, not `modules/` (`research.md` R12). `app/`, `features/companion`, `features/models`, `platform/workspace`, and `design-system/patterns/MessageBody` belong to B3 and are not created here. `platform/chart` and `platform/stat-chart` exist only so the import lint has a legal seam (`research.md` R11).

## Design

### Sequence

| Order | Slice | What the Software Engineer produces | Contract |
|---|---|---|---|
| 1 | B0 | Instruction files only | `contracts/instruction-set.md` |
| 2 | B1 | Vite, T0 deletions, types, Vitest + MSW + G1 smoke, lint rules 1–3, `react/no-danger`, CI skeleton, Docker `dist` | `contracts/toolchain-and-ci.md` |
| 3 | B2 and B4 together | Typed client, SSE reader, Socket.IO removal; dark tokens, `fmt`, `t()`, fonts, chart-import lint | `contracts/platform-api.md`, `contracts/chat-stream.md`, `contracts/format-catalogue-tokens.md` |

`tasks.md` will label the Vite move and the Vitest smoke with pitch T1 and T2, and will note the matching "10.2" step beside each. The React 18 `@types` alignment is the technical design's "T1 types fix" and is not labeled pitch T1. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-032.

### Behavior the contracts fix

- Same-origin `/api` proxy, empty `VITE_API_BASE_URL`, `credentials: 'same-origin'`, CSRF hook, 401 hook, no `Authorization`, no `X-User-ID`, `NoAuthAdapter`. Source: ADR-SYS-001 — "Decision" and "Follow-ups"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client".
- `openChatStream` keeps WHATWG fields, adapts today's frames, aborts the previous stream in the tab, and idles from `VITE_STREAM_IDLE_TIMEOUT_MS` (default 60000). Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client".
- Dark CSS variables match `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette". `--market-up` is `#2EBD6B`. No light values. Source: ADR-FRONTEND-007 — "Decision"; pitch row B4-T1.
- `fmt` outputs match pitch rows B4-F1..F5 and P1..P4. `Intl` is for dates only. Source: ADR-FRONTEND-005 — "Decision" (price-board bullet); `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy".

### Explicit non-goals

React Router, Zustand, TanStack Query, zone shells, `MessageBody`, Storybook, the browser MSW worker, the Playwright width matrix, the axe baseline, light tokens, theme switching, the contrast script, chart interfaces, and `GET /api/market/prices/{symbol}`. SNR-7.2.1 stays P2. SR-5.2.1 and SR-5.2.2 stay Superseded. Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — "Out of Scope" and "SRS mapping"; `docs/domains/frontend/ARCHITECTURE.md` — "8.2 Gates G1–G6 → M-001" (G2, G3, and the full G5 baseline are not this delivery; G1 and the Frontend half of G6 are).

### SRS landing

| ID | This delivery |
|---|---|
| SR-5.1.2 | B2 client and reader. Backend unchanged |
| SNR-8.1.2 | Frontend part verified on the MSW fixture only |
| SNR-6.1.4 | G1 path and the streaming-client seam. Shell coverage stays B3. Coverage target stays TBD in the SRS |
| SNR-7.1.1 | Recorded. Width runs stay B5. Priority stays P2 |
| SNR-7.2.1 | Stays P2. Contrast script is B4-T6 and moves to M-001. Axe stays B5 |
| SR-1.4.1 | Out of scope (B3) |
| SR-1.4.2 | Opaque `sessionRef` shape only. Store is B3 |
| SR-5.2.1, SR-5.2.2 | Remain Superseded |

Source: `specs/004-m000-b-frontend-foundation-core/spec.md` — "SRS mapping"; `specs/pitches/M-000-B-frontend-foundation.md` — "Requirements covered" and "Done means".

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Constitution I asks delivered work to refresh traceability and long-lived docs. This plan does not edit `docs/**` or `specs/spec-traceability.yaml`. | The spec and the Product Owner put those files out of scope for this delivery, including the stale sentences named under "Source conflicts". | Editing the Accepted ADRs or DESIGN_SYSTEM inside this plan would violate FR-002. A later sync change can fix anchors after implementation is verified. |
| ADR-FRONTEND-002 — "Decision" includes React Router, Zustand, TanStack Query, and Radix as the modernization stack. This plan does not add them. | The pitch assigns the shell and the store to B3 (T4 + T5). This directory is delivery 1. | Pulling B3 into this plan would merge two features the spec separated. |
| `openapi-fetch` and the SSE parser stay unnamed. | `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items" marks them Proposed. | Naming one package here would be a guess. The contracts specify the observable behavior instead. Rules 1 and 2 use core ESLint. The token generator is not selected. |

## Open items

These are not resolved by guessing. `tasks.md` must not pick a value for them.

| ID | Item | Where |
|---|---|---|
| O1 | HTTP client package, if any, on top of `openapi-typescript` | `research.md` R5 |
| O2 | Wire field for `sessionRef.sessionId` on `POST /api/chat`. Do not use deprecated `ChatRequest.session_id` | `research.md` R7 |
| O3 | SSE parser: in-house or `eventsource-parser` | `research.md` R8 |
| O4 | Resolved. Rules 1 and 2 use core ESLint `no-restricted-imports`. Do not add `eslint-plugin-boundaries`. | `research.md` R11. Product Owner, 2026-11-17 (analysis G2) |
| O5 | Resolved for this delivery. Hand-written two-part variables only. No generator. No invented `ai.*` names. Full B4-T1 generation and `npm run tokens` drift stay out. | `research.md` R13. Product Owner, 2026-11-17 (analysis G3) |
| O6 | vi-VN accessible-name phrases for `Delta` direction | `research.md` R15 |
| O7 | Which slice enables `react/jsx-no-literals` | `research.md` R17 |
| O8 | Resolved. File `.github/workflows/frontend-ci.yml`. Fifth step after build: `npm run gen:api && git diff --exit-code src/platform/api/generated`. | `research.md` R18. Product Owner, 2026-11-17 (analysis G1) |
| O9 | Resolved. B4 sets `data-density="compact"` beside `data-theme="dark"`. | `research.md` R19. Product Owner, 2026-11-17 (analysis X1) |
| O10 | Performance budgets | `research.md` R20. Status in the technical design is TBD |
| O11 | Node v26.13.1 is not on the laptop (22.18). B1 waits for the Product Owner install | `research.md` R2 |

`track.a` and `track.b` have no hex. This plan does not treat that as a question. The fixture omits them. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.2 Track (`track.*`)".

## References

Paths only. No document version numbers.

- `specs/004-m000-b-frontend-foundation-core/spec.md` — Clarifications; User Scenarios & Testing; Requirements FR-001..FR-032; Success Criteria; Prerequisites; Out of Scope; Assumptions; Source conflicts; SRS mapping
- `specs/004-m000-b-frontend-foundation-core/research.md` — R1..R21
- `specs/004-m000-b-frontend-foundation-core/data-model.md`
- `specs/004-m000-b-frontend-foundation-core/quickstart.md`
- `specs/004-m000-b-frontend-foundation-core/contracts/` — instruction-set, toolchain-and-ci, platform-api, chat-stream, format-catalogue-tokens
- `specs/pitches/M-000-B-frontend-foundation.md` — Slices (B0, B1, B2, B4, B5); Delivery workflow (agentic); Design acceptance criteria (UX), including B4-F1..F5, P1..P4, B4-T1..T4; Risks; No-gos; Done means
- `docs/domains/frontend/TECHNICAL_DESIGN.md` — 2. Domain scope and boundaries; 3.1 Module tree (Target M-000); 3.3 Boundary enforcement (Target G2); 3.4 Platform contracts; 4.1 Ownership (from ARCHITECTURE §6.1); 6.1 Typed REST client; 6.2 Today's stream contract; 6.3 SSE client; 6.4 Socket.IO removal; 6.5 Safe rendering of Agent output; 8.1 Token pipeline; 8.2 Pattern rules; 8.3 i18n and locale seam; 9.1 Pyramid; 9.2 Tests mapped to gates; 10.1 Build and run; 10.2 CRA → Vite migration; 12. Domain-specific constraints and open items
- `docs/domains/frontend/ARCHITECTURE.md` — 2. Scope & boundaries; 4.3 Building blocks (target); 5.1 Decided; 5.3 Carve-outs; 8.2 Gates G1–G6 → M-001
- `docs/domains/frontend/DESIGN_LOCK.md` — 4.2 Token groups (stale on light theme); 5. Zone state matrix; 8. Translation-ready copy
- `docs/domains/frontend/DESIGN_SYSTEM.md` — 1. Principles (stale on light theme); 2. Token architecture; 3. Palette; 3.1 Surface and market / state (both themes); 3.2 Track (`track.*`); 3.3 Accent; 3.6 Provenance (`ai.*`); 4. Typography; 5. Density, space, radius; 8. Patterns; 9. Content voice; 10. Quality (stale on Storybook theme matrix)
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md` — Decision; Implementation Direction (stale `modules/` wording); Guardrails
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md` — Decision; Carve-outs; Guardrails
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md` — Decision (B3; out of scope)
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md` — Decision; Considered Options
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-005-I18N-READINESS-SEAM.md` — Decision
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-006-GENERATED-UI-COMPONENT-REGISTRY.md` — Decision (Future; out of scope)
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-007-DESIGN-TOKEN-ARCHITECTURE.md` — Decision
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md` — Decision
- `docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md` — Decision; Follow-ups
- `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — SR-1.4.1; SR-1.4.2; SR-5.1.2; SR-5.2.1; SR-5.2.2; SNR-6.1.4; SNR-7: Usability, Accessibility, and Responsive Behavior; SNR-7.1.1; SNR-7.2.1; SNR-8.1.2
- `docs/openapi.yaml` — `ChatRequest` and the health, config, models, and chat paths. Not edited
- `.github/workflows/build-push-dockerhub.yml` — `on` (trigger that the new CI file must not change)
- `.specify/memory/constitution.md` — Core Principles I–VII; Document Referencing in Spec-Kit Workflows
