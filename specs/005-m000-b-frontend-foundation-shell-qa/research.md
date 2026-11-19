# Research: M-000 Frontend foundation shell and QA (delivery 2 of 2)

Phase 0 for `specs/005-m000-b-frontend-foundation-shell-qa`. Each decision cites a repository path and a heading, an ADR ID, an SRS ID, or a pitch row. Nothing the technical design still marks Proposed is selected. Spec 004 open items that this spec closes are named. The rest stay open.

Source: `specs/005-m000-b-frontend-foundation-shell-qa/spec.md`; `docs/domains/frontend/ARCHITECTURE.md`; `docs/domains/frontend/TECHNICAL_DESIGN.md`.

## R1 — Shell packages that the architecture already decided

- **Decision**: This delivery adds `react-router-dom` (`createBrowserRouter`), `zustand`, `@tanstack/react-query`, and `react-resizable-panels`. `MessageBody` adds `react-markdown` and `remark-gfm`.
- **Rationale**: Routing, Zustand, and TanStack Query are the M-000 target in `docs/domains/frontend/ARCHITECTURE.md` — "5.1 Decided". Pane resize is the same table (`react-resizable-panels` on Z1, Z3, and Z4; Z2 fixed). `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" names that panel group, "4.2 Zustand store" names the store, "5. Routing and navigation" names the data router, and "6.5 Safe rendering of Agent output" names `react-markdown` + `remark-gfm` with `skipHtml`, no `rehype-raw`, the default `urlTransform`, and images off.
- **Alternatives considered**: A hand-rolled router, React Context for workspace state, and `dangerouslySetInnerHTML`. Rejected. The first two break ADR-FRONTEND-002 and ADR-FRONTEND-003. The third is already an ESLint error (`react/no-danger`) and fails the XSS cases in "6.5 Safe rendering of Agent output".

## R2 — Packages that stay unselected

- **Decision**: Do not add `openapi-fetch`, `eslint-plugin-boundaries`, Style Dictionary, `eventsource-parser`, an i18n library, `lightweight-charts`, `chart.js`, a chart engine, or an error-reporting product. Do not set query `staleTime`, `retry`, or `refetchOnWindowFocus`. Do not set a performance budget. Do not invent vi-VN copy for `delta.up`, `delta.down`, or `delta.flat`.
- **Rationale**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items" still marks those libraries Proposed. "4.3 Query key taxonomy" marks the timings Proposed. The spec says this delivery does not choose them (`spec.md` — "Out of Scope" and "Assumptions"). Spec 004 left O1, O3, O6, and O10 open on purpose. Delta phrases in `frontend/src/platform/i18n/messages/vi-VN.ts` stay `[NEEDS CLARIFICATION]`.
- **Alternatives considered**: Picking the Proposed package so the shell "looks finished". Rejected. That would be a guess the spec forbids.

## R3 — Tailwind package and Radix primitives

- **Decision**: Do not install Tailwind or Radix / shadcn in this delivery. The shell uses the committed dark token CSS from delivery 1, semantic landmarks, and `:focus-visible`. `react-resizable-panels` supplies the keyboard-operable resize handles.
- **Rationale**: `docs/domains/frontend/ARCHITECTURE.md` — "5.1 Decided" and "8.1 Current → Target" name Tailwind + Radix as the Pitch B complete UI cell. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" says the Tailwind package and Radix primitives are not installed, and "7. Accessibility and responsive behaviour" names Radix for focus management. Delivery 1 (B4) was the step that was supposed to add them and did not (`specs/004-m000-b-frontend-foundation-core/plan.md` — Complexity Tracking). This spec's done bar does not include a primitive layer. FR-023 cuts Tier D button and input stories. No dialog or account menu ships (FR-018). Installing the primitive set would exceed the thin slice.
- **Alternatives considered**: Installing both because the architecture target column says Pitch B complete. Rejected for this plan. The gap is recorded in `plan.md` Complexity Tracking. A later change that is allowed to extend the design system can add them. This plan does not pretend the gap is closed.
- **Done bar that still holds**: landmarks and focus order (B3-D1, B3-D2), zone geometry (B3-D3), and token CSS already on `<html data-theme="dark" data-density="compact">`.

## R4 — Playwright and axe are required

- **Decision**: Playwright + axe is in this delivery. `@playwright/test` is already a devDependency (`frontend/package.json`). Add `@axe-core/playwright` for the shell run. The script name is `e2e`, matching `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.1 Pyramid" (`npm run e2e`). Widths are 1920, 1440, 1024, and 768. One keyboard-order test at 1920 px. A serious or critical axe issue fails the run. SNR-7.2.1 stays P2.
- **Rationale**: The pitch and the spec resolve the older "Proposed" label. `spec.md` — "Source conflicts" (Playwright). Governing rows: B3-D2, B3-D3, B5-S2. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "7. Accessibility and responsive behaviour" and "9.2 Tests mapped to gates" (G5). `docs/domains/frontend/ARCHITECTURE.md` — "5.2 Candidates" still says the tool is undecided. That row is stale for this delivery. The plan does not edit the architecture file (FR-002).
- **Alternatives considered**: The two-width fallback (1920 and 768 only). The spec allows it only when the Product Owner records that the week ran short. The Software Engineer does not take that cut.

## R5 — Storybook shape and count

- **Decision**: Dark compact Storybook only. `data-theme="dark"` and `data-density="compact"`. The required set is 11 to 15 stories: exactly 7 `ZoneFrame` stories (one state each), plus at least one story each for `PriceCell`, `Delta`, `StatusBadge`, and `MessageBody`. Up, down, zero, missing, and the three `MessageBody` cases render as variants when they are not their own stories. Axe runs on every rendered case. A catalogue of 22 story files fails the bound. Tier D primitive stories are not required. No light theme, no theme-toggle story, no token pages, no visual snapshots (B5-S4 stays in M-001).
- **Rationale**: Product Owner, 2026-11-17 and 2026-11-19. `spec.md` — FR-023 and the 2026-11-19 clarification. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules" sizes the set at about 15 dark compact stories. The pitch row B5-S1 names the runner as "Storybook test runner / addon-vitest".
- **Runner**: Use Storybook's Vitest addon (`addon-vitest`) so story tests stay on Vitest. Do not add a second unit runner. Do not add a visual-regression addon.
- **Alternatives considered**: One file per named case (22). Rejected. The spec says that reading is not in the authored documents and fails the bound.

## R6 — MSW handler set and the browser worker

- **Decision**: One handler module, typed from `src/platform/api/generated/schema.d.ts`, used by Vitest and by the browser when `VITE_USE_MOCKS` is the string `true`. Paths are only those already in `docs/openapi.yaml` for health, config, models, and chat:
  - `getHealth` — `GET /api/health`
  - `getConfig` — `GET /api/config`
  - `postChat` — `POST /api/chat` (the delivery 1 SSE fixture stays)
  - `listOpenAIModels`, `refreshOpenAIModels`, `getSelectedModel`, `selectModel`, `setDefaultModel` — the `/api/models/openai` operations
- No other operation is mocked. `GET /api/market/prices/{symbol}` is not added. Features do not import MSW. The browser worker is a dynamic import from the app entry, so a production build (`VITE_USE_MOCKS` absent or not `true`) contains no `msw` and no `mockServiceWorker.js`. When that worker starts, it sets `document.documentElement.dataset.mocks` to `on`. The flag-off path and the production build do not set it. The attribute is a Playwright signal, not a product control.
- **Rationale**: `spec.md` — FR-021, FR-022. ADR-FRONTEND-008 — "Decision". `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client" and "10.1 Build and run". Today's handler file (`frontend/src/test/msw/handlers.ts`) covers only `POST /api/chat`. This delivery extends that set. It does not edit `docs/openapi.yaml`.
- **Layout**: Shared handlers live under `frontend/src/mocks/`, which is the production-exclusion path named in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3a Mock price data" (the price fixtures in that section stay out). Vitest setup imports the same handlers. The existing chat frames move with the handler module. Price fixtures in `src/mocks/fixtures/prices/` are not created.
- **Alternatives considered**: Leaving handlers only under `src/test/msw/` and stubbing the browser with a different module. Rejected. ADR-FRONTEND-008 says the same handlers serve both.

## R7 — `react/jsx-no-literals` (closes spec 004 O7 for this delivery)

- **Decision**: Enable `react/jsx-no-literals` on `src/app/`, `src/features/`, and `src/design-system/patterns/`. Allowed JSX strings are the punctuation and symbols named in the spec: `·`, `—`, `/`, `%`, `₫`, `+`, `−`. Tickers and numbers come from data and are not allow-listed. `react/no-danger` stays an error with no exceptions.
- **Rationale**: `spec.md` — FR-013 and row B3-D8. Spec 004 left O7 open (`specs/004-m000-b-frontend-foundation-core/research.md` — R17). This spec assigns the rule to B3. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement" and "8.3 i18n and locale seam" say the rule is the target and is off today.
- **Alternatives considered**: Leaving the rule off and relying on review. Rejected. B3-D8 is a lint failure in CI.

## R8 — Boundary rules 1 and 2 apply to real folders

- **Decision**: Once `src/app/` and `src/features/` exist, core ESLint `no-restricted-imports` enforces rule 1 (no reverse import of `app` or `features` from `platform` or `design-system`) and rule 2 (a feature imports another feature only through that feature's `index.ts`; no deep import). Do not add `eslint-plugin-boundaries`. Rule 3 (no `fetch` outside `platform/api` and `platform/stream`) and rule 5 (chart libraries) stay as delivery 1 left them.
- **Rationale**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement" says rules 1 and 2 are on fixtures until `app/` and `features/` exist, and that `eslint-plugin-boundaries` stays proposed. `docs/domains/frontend/ARCHITECTURE.md` — "4.3 Building blocks" rules 1–3 are the dependency direction. Spec 004 resolved the plugin choice (plan O4). This delivery turns the same core rule onto the new folders. It does not rebuild rules 1–3 from scratch.
- **Alternatives considered**: `eslint-plugin-boundaries`. Rejected. Still Proposed, and the Product Owner already chose core ESLint.

## R9 — Module paths, not the pitch hint

- **Decision**: `ZoneFrame` and `MessageBody` live under `frontend/src/design-system/patterns/`. The shell lives under `frontend/src/app/` (`WorkspaceShell`, `ZoneHost`, router, providers). The store lives under `frontend/src/platform/workspace/`. Companion chat lives under `frontend/src/features/companion/`. The model selector lives under `frontend/src/features/models/` and is composed into the Z4 header. There is no `modules/` tree and no `src/platform/zone-frame/` or `src/platform/message-body/`.
- **Rationale**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree" and "3.2 Feature module contract". `spec.md` — "Source conflicts" (folder name, pattern directory, model selector placement). The pitch file paths are a hint. ADR-FRONTEND-001 — "Implementation Direction" still says `modules/`. That sentence is stale and is not edited here.
- **Entry**: `frontend/src/main.tsx` replaces `frontend/src/index.tsx` as the entry, and `frontend/index.html` points at it. That is the target tree in "3.1 Module tree". `App.tsx` is removed when the shell ships. `frontend/src/components/models/ModelSelector.tsx` moves into `features/models`. No new module imports `src/components/**`.
- **Legacy CSS**: `src/App.css` and `src/index.css` are already absent in this tree. Row B3-D9 still requires that absence, plus the token and base layer as the only global stylesheet.

## R10 — URL-owned state and the store

- **Decision**: Routes are only `/` → `/sandbox`, `/:track` with `sandbox` | `portfolio`, `/:track/:symbol`, and `*` not-found inside the shell. Core-object routes do not ship. No search params. Parsing is pure functions in `platform/workspace/routeParams.ts`.
- **Symbol rule**: A symbol segment is accepted when it is non-empty and contains no lowercase letter. Unit tests lock `FPT`, `VNINDEX`, and `VN30` as valid and a lowercase segment as not-found. This plan does not add a character class, a length limit, or an exchange suffix. The technical design says "validated by pattern" and does not give the pattern (`spec.md` — "Assumptions").
- **Write rule**: `useUrlSync()` is the only writer of `symbol`, `coreObjectRef`, and `activeTrack`. A component that changes them calls `navigate()`. A unit test asserts a direct store write does not stick. `lastRouteByTrack` is restored on a track switch.
- **Slices**: One Zustand store, slices `workspace`, `context`, `layout`, and `ui`. `ui.theme` is the literal `'dark'` only. This delivery does not add a `'light'` member and does not switch theme, even though `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store" writes the union `'dark' | 'light'`. The light member is M-001 (`spec.md` — FR-016). Devtools middleware is development-only. Features use narrow selectors. React Context does not carry fast-changing values.
- **Persistence**: `context` and pane sizes persist to `sessionStorage` for the same tab. The Z4 draft is a separate `sessionStorage` entry. The key is `dp-stock:z4-draft:${sessionId}:${conversationId}`. It holds draft text only. Send removes that key. Stop, the delivery 1 idle timeout, and `interrupted` do not. Another tab does not share `sessionStorage`.
- **`sessionRef`**: Held once on the Z4 companion run. The workspace slices do not store a second copy. The client still omits `sessionId` on the wire (spec 004 O2). This delivery does not choose a wire field.
- **Rationale**: ADR-FRONTEND-003 — "Decision". `docs/domains/frontend/ARCHITECTURE.md` — "4.2 Workspace context ownership" and "6.1 State ownership matrix". `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.1 Ownership", "4.2 Zustand store", "5. Routing and navigation". SR-1.4.2.

## R11 — Zone frames, errors, and the empty chart slot

- **Decision**: `ZoneFrame` states are `empty`, `loading`, `ready`, `stale`, `error`, `interrupted`, and `streaming`, with `data-state` set to that value. Error has a retry control. Interrupted shows "Tạo lại" from `t('stream.retry')` and sends no request until activated (MSW count stays 0 for 5 seconds). Streaming shows stop. `aria-busy="true"` on loading and on streaming. Z2 empty shows the catalogue value "Chưa chọn mã" through `t()`, which means a new catalogue key. The technical design does not give the key name. The plan uses `shell.z2.emptySymbol`. Tests assert the accessible name comes from `t()`, not a JSX literal.
- **Throw**: `ZoneHost` is an error boundary per zone. A throw sets that zone to `data-state="error"` and calls `reportError(error, { zone })`. The other three zones keep their content. `reportError` writes to the console. No vendor sink (`docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items").
- **Chart slot**: Sandbox Z3 includes an empty slot element. Portfolio does not. A route test asserts presence on `/sandbox` and absence on `/portfolio`. Z3 empty shows an invitation through `t()` and does not start a Case. No `ChartEngine`, no `StatChart`, no chart content, no price query.
- **Rationale**: `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix" and "1. Shell geometry". `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts". `spec.md` — FR-009, FR-010, FR-020. Pitch row B3-D4 names `aria-busy` for loading. The streaming case is the technical design row, which the spec adopts (FR-009).

## R12 — Geometry done bar versus the proposed pixel defaults

- **Decision**: Tests assert the pitch row, not the Proposed defaults. At 1440 px and above, four zones sit side by side and the Z4 toggle is not the opener. Below 1440, Z4 is an overlay drawer opened from the Z2 utilities corner with `aria-expanded`. Below 1024, Z1 is a 56 px rail: both track icons have an `aria-label` and a tooltip, text labels show only on hover or focus, and the active track has a visible mark. At 768 px, Z3 is at least 712 px wide. Zone boxes do not overlap. `scrollWidth <= clientWidth`. Zones do not stack. The 240 px and 440 px defaults in `docs/domains/frontend/DESIGN_LOCK.md` — "1.1 Viewport and zone width budget" are Proposed and are not the done bar. Widths below 768 px are out of scope. The Z2 utilities corner has no account menu (FR-018). Identity stays with Pitch A.
- **Rationale**: `spec.md` — FR-008 and the 2026-11-19 clarifications. `docs/domains/frontend/DESIGN_LOCK.md` — "1. Shell geometry" still draws an account menu in the Z2 diagram. The spec resolves that diagram for this delivery. The file is not edited.

## R13 — Companion run

- **Decision**: The Z4 stream keeps using `platform/stream` from delivery 1. Run states are `idle`, `streaming`, `done`, `interrupted`, and `error`. Stop, and the idle timeout, move the run to `interrupted` and keep the draft and any partial message. Activated "Tạo lại" sends the same user message again as a new run. There is no mid-run resume, no typed stream events, and no cancel request. The thread uses `aria-live="polite"` and announces at message end, not per token.
- **Rationale**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client" and "7. Accessibility and responsive behaviour". `spec.md` — FR-019. The 2026-11-17 idle-timeout decision is already in the delivery 1 client.

## R14 — Provenance

- **Decision**: `data-origin="ai"` renders a dashed edge and the label from `t('ai.suggested')` ("AI gợi ý"). `data-origin="investor"` renders a solid edge and `t('ai.confirmed')` ("Đã xác nhận"). Hue alone does not carry the difference. Both strings already exist in the catalogue. DESIGN_SYSTEM names Lucide `sparkles` and `check` beside those labels. This delivery does not add `lucide-react`. The done bar is the edge plus the visible `t()` label (row B3-D7). The edge colours are the dark values already in the token sheet (`ai.suggested` / `ai.confirmed` in `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance"). If those CSS variables are not in the committed token file, the pattern uses the dark hex from that table through the token layer, not a feature-level colour literal.
- **Rationale**: `docs/domains/frontend/DESIGN_LOCK.md` — "4.3 Colour and provenance rules". `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance". `spec.md` — FR-012. Feature files still fail lint on a hex literal (B3-D8), so the colour stays in the design-system token or pattern layer.

## R15 — Query keys

- **Decision**: Server data goes through TanStack Query. The M-000 factory entries used here are `health`, `config`, and `models` only, in `platform/api/keys.ts` if that module is added, matching `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.3 Query key taxonomy". The `prices` key and every later key are not called. Library defaults stand in for the Proposed timings (R2).
- **Rationale**: `spec.md` — FR-017. ADR-FRONTEND-002 — "Decision".

## R16 — CI extension

- **Decision**: `.github/workflows/frontend-ci.yml` keeps its five steps in order: lint, `tsc --noEmit`, Vitest, build, `gen:api` drift. After those, the job runs `npm run build-storybook` and the story axe run, then Playwright (`npm run e2e`). The `on` trigger of `.github/workflows/build-push-dockerhub.yml` stays `push` to `main` and `workflow_dispatch`. It is not edited.
- **Rationale**: `spec.md` — FR-025. Delivery 1 put the drift check after build (`.github/workflows/frontend-ci.yml`). The spec says Storybook and Playwright follow the build. Removing the drift step would undo a resolved delivery 1 decision. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".

## R17 — Where the work is written

- **Decision**: Implementation of B3 and B5 runs in a named git worktree on `features/pitch-m000-B-frontend-foundation`. It does not modify `backend/`, `docs/**`, Accepted ADRs, `main`, the Product Owner's main tree, or the `wt/m001-s3` worktree. These planning artifacts are written in the checkout that holds the spec, because `setup-plan.ps1` resolved the feature directory here and the spec file already lives here. That does not relax FR-002 for the implementation.
- **Rationale**: `spec.md` — FR-002. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" records that delivery 1 was made in the primary checkout and that the worktree rule still stands.

## R18 — Traceability and the agent-context script

- **Decision**: This plan does not edit `docs/**`, Accepted ADRs, or `specs/spec-traceability.yaml`. It does not run `python scripts/sync_spec_status.py --gate`. The feature stays unmapped until a later change that is allowed to touch the registry. Citations in this plan still name a repository-relative path and a heading, ADR ID, SRS ID, or pitch row.
- **Decision**: `.specify/scripts/powershell/update-agent-context.ps1` is not run. `AGENTS.md` exists, so the script would rewrite it. Its fallback when no agent file exists is to create `CLAUDE.md`. Delivery 1 (B0) owns those instruction files and removed the stale `CLAUDE.md`. This delivery does not rewrite them (`spec.md` — Dependencies, B0). The plan path is this directory's `plan.md`. There is no `<!-- SPECKIT START -->` marker to update.
- **Rationale**: `.specify/memory/constitution.md` — "Recorded deferral when the delivery forbids the sync edit" (version 2.7.0). `spec.md` — FR-002 and "Sync targets".

## R19 — Lazy routes without a budget

- **Decision**: M-000 feature route elements are `React.lazy`. No performance number is set. The chart engine is not lazy-loaded because it is not imported. `docs/domains/frontend/ARCHITECTURE.md` — "7.2 Quality floor" marks the performance row, including route code-splitting, as Target M-001 and leaves budgets TBD. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "5. Routing and navigation" still says route components are lazy. This delivery follows the routing section for the feature routes and does not set a budget (`spec.md` — "Source conflicts", route code-splitting label).
- **Alternatives considered**: Treating the architecture performance row as a ban on `lazy()`. Rejected. The spec already resolved that pair, and a lazy route is not a budget.

## R20 — What delivery 1 already provides

- **Decision**: Reuse, do not rebuild: Vite, Vitest, jsdom, the MSW test server, `platform/api` (hand-written `fetch`), `platform/stream`, `NoAuthAdapter`, `t()` and the vi-VN catalogue, `fmt`, dark tokens, `PriceCell`, `Delta`, `StatusBadge`, chart-import lint, and `react/no-danger`. Node stays `>=26.13.0` with `.nvmrc` of `26`. Commands run from `frontend/`.
- **Rationale**: `spec.md` — Dependencies. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree" (Current, verified spec 004).
