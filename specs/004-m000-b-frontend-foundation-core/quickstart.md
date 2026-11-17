# Quickstart: prove M-000 Frontend foundation core

**Date**: 2026-11-17

This file is the proof sequence for a later implementation. It does not run that implementation. Planning does not install Node, does not change `frontend/`, and does not create a worktree.

**Sources**: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)", "B0 — Agent instructions on the target stack", "B1 — Vite shell and subtract", "B2 — API client...", and "B4 — Dark tokens..."; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run"; `specs/004-m000-b-frontend-foundation-core/spec.md` — "Prerequisites" and Success Criteria SC-001 through SC-011.

## Prerequisite

The Product Owner installs Node v26.13.1 before the first B1 command. The laptop that prompted this plan has Node 22.18. With `engine-strict=true`, `npm ci` on 22.18 fails fast. That failure is the expected guard, not a signal to lower `engines.node`.

## Where the Software Engineer works

A named git worktree on `features/pitch-m000-B-frontend-foundation`. Not the Product Owner's main tree. Not `main`. Not the `wt/m001-s3` worktree.

Do not change `backend/`, `docs/**` (including `docs/openapi.yaml`), or the Accepted ADRs.

## Order

1. B0 instruction files.
2. B1 toolchain (pitch T0, T1, T2).
3. B2 and B4, alongside each other, after B1.

B3 and B5 are a different feature. Do not start them from this quickstart.

For B1, B2, and B4: write the new tests, watch them fail, then implement without editing those tests. B0 has no test file.

## B0 proof

From `frontend/`:

- `grok inspect` lists the new rules.
- A search of instruction files finds no recommendation of Create React App, Jest, `REACT_APP_*`, or Socket.IO.

`frontend/AGENTS.md` is under 10,000 characters.

## Shared proof

From `frontend/` on Node v26.13.1, after B1, and again after B2 and B4:

```text
npm ci
npx tsc --noEmit
npx vitest run
npm run build
```

## B1 proof, in addition

- `npm run dev` serves the Vite app.
- `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` returns nothing.
- The image built from `frontend/Dockerfile` succeeds and packages `dist` with `node:26-alpine`.
- The CI skeleton runs lint, then `tsc --noEmit`, then Vitest, then build, and does not change the trigger of `.github/workflows/build-push-dockerhub.yml`.
- The G1 chat smoke renders streamed tokens from the MSW handler.

## B2 proof, in addition

From `frontend/`:

```text
npm run gen:api && git diff --exit-code src/platform/api/generated
rg socket.io dist
```

The second command returns nothing. A fake-timer test at 15000 ms accepts `:` comments and moves a silent stream to `interrupted`, with the draft and any partial message still present. The retry label is "Tạo lại" through `t()`.

## B4 proof, in addition

- Vitest exact-output tests match rows B4-F1..F5 and P1..P4, including the 1,000-value property test.
- A planted import of `lightweight-charts` or `chart.js` outside the adapter seams fails lint.
- A fixture copied from `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette" matches the generated dark variables, including `--market-up` = `#2EBD6B`. Light variables are absent.
- Playwright checks computed style and the network log for row B4-T4: `fmt.*` starts with `IBM Plex Mono`, UI text starts with `Be Vietnam Pro`, and no request goes to a third-party font host.

Playwright is not part of the B1 CI skeleton.

## Stop conditions

- Node is still 22.18. Stop before B1.
- A proof above fails. Stop on that slice.
- A design choice marked `[NEEDS CLARIFICATION]` in `research.md` is required to write the next file. Stop and record the question. Do not pick a Proposed package (`openapi-fetch`, `eslint-plugin-boundaries`, Style Dictionary, SSE parser) or invent `track.a` / `track.b` hex values.
