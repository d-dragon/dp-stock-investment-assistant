# Contract: toolchain, lint, and CI

**Slices**: B1, with B2 and B4 rules landing on the same ESLint config

**Source**: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract", "Delivery workflow (agentic)", and "B5 — MSW, minimal Storybook, and Frontend CI"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)", "9.2 Tests mapped to gates" (G1), "10.1 Build and run", and "10.2 CRA → Vite migration"; ADR-FRONTEND-002 — "Decision" and "Guardrails"; ADR-SYS-001 — "Decision"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-008 through FR-014, FR-031, FR-032.

## Node

| File | Value |
|---|---|
| `frontend/.nvmrc` | `26` |
| `engines.node` | `>=26.13.0` |
| `frontend/.npmrc` | `engine-strict=true` |
| Image | `node:26-alpine` |
| Prerequisite | Node v26.13.1 on the machine that runs B1. Node 22.18 fails `npm ci` |

## Vite

| Item | Contract |
|---|---|
| Scripts | `npm run dev` and `npm run build` run on Vite |
| Proxy | `/api` → port 5000, same origin |
| `VITE_API_BASE_URL` | Default empty |
| CORS | No credentialed CORS in the dev setup |
| Env | `VITE_*` only. No `REACT_APP_*` |
| TypeScript | Direct dependency, 5.9 or newer |
| `@types/react`, `@types/react-dom` | Aligned with React 18 |
| tsconfig | Not left on `target es5` and `moduleResolution node` in a way that blocks `tsc --noEmit` |
| Dead CRA files | `config-overrides.js` and `webpack.config.dev.js` removed |
| Docker | `frontend/Dockerfile` packages Vite `dist`, not `/app/build` |
| `App.tsx` | The hard-coded `http://localhost:5000` is removed so calls use the proxy |

`tasks.md` labels (when that file is written): pitch T1 is the Vite build, config, and environment move, noted beside `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step "T2 Vite". Pitch T2 is Vitest, the MSW base, and the G1 smoke, noted beside that same "T2 Vite" row. The `@types/react` alignment is the "T1 types fix" row and is not labeled pitch T1.

## T0 deletions

When still unreferenced:

- `components/OptimizedApp.js`
- `components/PerformanceProfiler.js`
- `components/WebSocketTest.tsx`
- `components/MessageFormatter.js`
- `services/apiService.ts`
- `utils/performance.js`

`MessageFormatter.js` is deleted, not patched.

Proof from `frontend/`: `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` returns nothing.

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step T0 and "6.5 Safe rendering of Agent output".

## Tests in B1

Vitest uses jsdom. No happy-dom fallback. MSW is wired for tests. One component test sends a chat and renders streamed tokens from an MSW handler that uses the frames in `contracts/chat-stream.md`.

Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G1); SNR-6.1.4 (path only).

## Lint enabled here

| When | Rule |
|---|---|
| B1 | Rule 1. `app` → `features` → `platform` / `design-system`, never reverse |
| B1 | Rule 2. No sibling-feature imports. No deep imports past a feature public entry |
| B1 | Rule 3. Only `platform/api` and `platform/stream` may use `fetch`. `XMLHttpRequest`, `EventSource`, and `WebSocket` are blocked outside those modules. `socket.io-client` and `axios` imports are blocked |
| B1 | `react/no-danger` is an error |
| B2 | `no-restricted-imports` keeps `socket.io-client` out, and stream event names stay in the union and the adapter |
| B4 | Rule 4. Market and state CSS variables and arbitrary Tailwind colours, as in `contracts/format-catalogue-tokens.md` |
| B4 | Rule 5, chart libraries only. See that same contract |

Rules 1 and 2 use core ESLint `no-restricted-imports` path patterns. Do not add `eslint-plugin-boundaries` (`research.md` R11, resolved). `react/jsx-no-literals` is not assigned to a slice (`research.md` R17).

## CI skeleton

File: `.github/workflows/frontend-ci.yml`.

Order in one job: lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`.

The workflow does not change the `on` trigger of `.github/workflows/build-push-dockerhub.yml`.

Playwright and Storybook are not steps in this skeleton. Source: `research.md` R18, resolved 2026-11-17 (analysis G1).

## Shared proving commands

From `frontend/`, on Node v26.13.1:

```text
npm ci
npx tsc --noEmit
npx vitest run
npm run build
```

B1 also requires `npm run dev` and a successful Docker image build. B0 does not use these four commands as its proof.

## Test-first

For B1, B2, and B4 the Software Engineer writes the tests, confirms they fail, then implements without editing those tests. B0 is exempt.

Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-001.
