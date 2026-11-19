# T043 shared proof

**Date**: 2026-11-18
**Where**: `frontend/`
**Node**: v26.13.1
**npm**: `npm ci` reported adding 468 packages and auditing 469 packages

| Command | Exit |
|---|---|
| `npm ci` | 0 |
| `npx tsc --noEmit` | 0 |
| `npx vitest run` | 0 (Vitest 3.2.7, 17 files, 43 tests) |
| `npm run build` | 0 (Vite 6.4.6, 40 modules, 1.26s) |

Build output:

- `dist/index.html` 0.84 kB
- `dist/assets/index-VvXXoI33.css` 1.03 kB
- `dist/assets/index-w6qlaSI1.js` 158.95 kB

`grok inspect` from `frontend/` (version 1.0.88) lists root `Agents.md` and `frontend/Agents.md`.

`npm ci` reported 21 vulnerabilities (1 low, 1 moderate, 17 high, 2 critical). `npm audit fix` was not run. Install scripts for `esbuild@0.25.12` and `msw@2.15.0` were not approved. The typecheck, tests, and build still exited 0.

## Follow-up: dev server and image build

**Date**: 2026-11-18
**Node**: v26.13.1
**Docker**: 28.3.2

| Command | Exit |
|---|---|
| `npm run dev` (from `frontend/`) | served HTTP 200, then the process was stopped |
| `docker build -f frontend/Dockerfile .` (from the repository root) | 0 |

`npm run dev` printed Vite v6.4.6 ready in 736 ms at `http://localhost:5173/`. `GET /` returned 200 with `lang="vi"` and `/src/index.tsx`. `GET /src/index.tsx` and `GET /src/design-system/tokens/generated/fonts.css` returned 200. The process was then stopped, and `http://localhost:5173/` no longer answered.

The image build ran `npm run build` (Vite v6.4.6, 43 modules, 5.17s). Output inside the image:

- `dist/index.html` 0.93 kB
- `dist/assets/index-VvXXoI33.css` 1.03 kB
- `dist/assets/index-CdnfV6w_.js` 163.20 kB

The production bundle inlines the idle window from `.env.production` as `6e4` (60000) and still throws when that value is missing or not positive. `npm ci` in the image warned that install scripts for `esbuild@0.25.12` and `msw@2.15.0` were not approved. `npm audit fix` was not run. The exported image was untagged (`sha256:23cea7800cf7d7b0437f46a5596bb907e9b99f3269a4392acabf01ce1b7aa035`) and was removed after this check.
