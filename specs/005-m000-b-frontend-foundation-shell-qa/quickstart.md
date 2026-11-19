# Quickstart: M-000 shell and QA

Commands run from `frontend/` unless a path says otherwise. Node is `>=26.13.0` (`.nvmrc` is `26`). The prerequisite toolchain, client, tokens, and `t()` catalogue come from `specs/004-m000-b-frontend-foundation-core`.

Implementation of these steps happens in a named git worktree on `features/pitch-m000-B-frontend-foundation`. Do not implement them in the Product Owner's main tree. Source: `spec.md` — FR-002; `research.md` R17.

## Shared proof

```powershell
npm ci
npx tsc --noEmit
npx vitest run
npm run build
```

## B3 proof

Write the Vitest tests first and confirm they fail. Then implement. Do not edit the tests in the implementation change. Source: `spec.md` — FR-001.

```powershell
npm run lint
npx vitest run
```

`npm run lint` must still fail a planted `dangerouslySetInnerHTML`. The G2 shell test, the G3 store and route tests, and the XSS cases are the behavior proofs. Rows in Vitest: B3-D1, B3-D4, B3-D5, B3-D7, B3-D8. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates".

## B5 proof

Write the Playwright, Storybook, and bundle-scan proofs first and confirm they fail. Then implement.

```powershell
npm run build-storybook
npx playwright test
npm run build
rg -l "msw|mockServiceWorker" dist
```

`rg` must print nothing. Playwright covers B3-D2, B3-D3, and B3-D6. Source: `contracts/msw-storybook-ci.md`.

## Dev server

```powershell
npm run dev
```

Leave `VITE_API_BASE_URL` empty so `/api` proxies to `http://127.0.0.1:5000`. Set `VITE_USE_MOCKS=true` only when the browser should start the MSW worker. A production build does not set that flag. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".

## Do not run

- `python scripts/sync_spec_status.py --gate` for this delivery. The spec forbids edits to `docs/**` and `specs/spec-traceability.yaml`. Source: `.specify/memory/constitution.md` — "Recorded deferral when the delivery forbids the sync edit"; `research.md` R18.
- Edits to `backend/`, `docs/openapi.yaml`, Accepted ADRs, `main`, or the `wt/m001-s3` worktree.
