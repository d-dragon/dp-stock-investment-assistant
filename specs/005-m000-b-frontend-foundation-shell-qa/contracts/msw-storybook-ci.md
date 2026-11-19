# Contract: MSW, Storybook, and Frontend CI

**Slice**: B5

**Source**: ADR-FRONTEND-008 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules", "9.1 Pyramid", "9.2 Tests mapped to gates", and "10.1 Build and run"; `spec.md` — FR-021 through FR-026. Decisions: `research.md` R4, R5, R6, R16.

## Handlers

One module under `frontend/src/mocks/`. Typed from `frontend/src/platform/api/generated/schema.d.ts`. Vitest and the browser import that module. Features do not.

| When | Worker |
|---|---|
| Vitest | The node server from the same handlers |
| `vite` dev and `VITE_USE_MOCKS=true` | Browser worker, dynamic import |
| Production build, flag absent or not `true` | Worker is not started. `src/mocks/` is not in the bundle. `dataset.mocks` is absent |

When the browser worker starts, it sets `document.documentElement.dataset.mocks` to `on`. Playwright asserts that value (`e2e/b3-d2-keyboard.spec.ts` and the other B5 shell specs). The attribute is a test signal. It is not a product control, and a production build does not set it.

The chat handler keeps the delivery 1 SSE frames. Health, config, and the five `/api/models/openai` operations gain handlers. No other path is added. No price handler.

`rg -l "msw|mockServiceWorker" dist` returns nothing after `npm run build`. The scan is a CI step (B5-S3). Storybook runtime is also absent from `dist/`.

## Storybook (B5-S1)

Dark compact only: the preview sets `data-theme="dark"` and `data-density="compact"`.

| Stories | Bound |
|---|---|
| `ZoneFrame` | 7, one per state |
| `PriceCell` | at least 1. Variants cover up, down, zero, missing |
| `Delta` | at least 1. Same variants. Direction phrases stay `[NEEDS CLARIFICATION]` |
| `StatusBadge` | at least 1. Same variants |
| `MessageBody` | at least 1. Variants cover `ai`, `investor`, and one XSS fixture |
| Required set | 11 to 15 stories total |
| Forbidden | 22 story files, light theme, theme toggle, token pages, visual snapshots, Tier D as a done bar |

Runner: Storybook Vitest addon. Axe runs on every rendered case, not only the default args. A serious or critical violation fails the run. `npm run build-storybook` passes.

## Playwright (B5-S2)

`npm run e2e` is Playwright with `@axe-core/playwright`. The shell route is served with MSW. Viewports: 1920, 1440, 1024, 768. The run shows B3-D3. Axe has no serious or critical issue. One test at 1920 px checks skip link, then Z2, Z1, Z3, Z4 (B3-D2). The draft reload test (B3-D6) is in this Playwright set.

`F6` tests are absent. Visual snapshot tests are absent. The 1920-and-768-only subset is absent unless the Product Owner records that the week ran short.

SNR-7.2.1 stays P2. The contrast script is not added.

## CI

File: `.github/workflows/frontend-ci.yml`. Existing order stays, then the new steps.

1. `npm run lint`
2. `npx tsc --noEmit`
3. `npx vitest run`
4. `npm run build`
5. `npm run gen:api && git diff --exit-code src/platform/api/generated`
6. Storybook build and the story axe run
7. Playwright

`.github/workflows/build-push-dockerhub.yml` is not edited. Its trigger stays `push` on `main` and `workflow_dispatch`.

## Proof

From `frontend/`:

- B3: `npm run lint` passes with `react/no-danger` still an error. G2, G3, and XSS tests pass.
- B5: `npx playwright test` and `npm run build-storybook` pass. `rg -l "msw|mockServiceWorker" dist` returns nothing.
- Shared: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`.
