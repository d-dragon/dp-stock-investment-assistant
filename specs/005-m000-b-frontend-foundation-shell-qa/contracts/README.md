# Contracts

Interfaces for delivery 2 of Pitch B (B3 and thin B5). Behavior that stays open is marked in `../research.md` and is not decided here.

| Contract | Slice | Covers |
|---|---|---|
| `shell-zones.md` | B3 | Landmarks, focus order, widths, drawer, rail, zone isolation |
| `workspace-and-routes.md` | B3 | Router, store, `useUrlSync`, draft, query keys |
| `zone-frame-and-message-body.md` | B3 | Seven zone states, XSS, provenance |
| `msw-storybook-ci.md` | B5 | Handlers, Storybook bound, Playwright, CI, production bundle |

Shared commands from `frontend/` stay `npm ci`, `npx tsc --noEmit`, `npx vitest run`, and `npm run build`. B3 adds `npm run lint`. B5 adds `npm run build-storybook`, `npm run e2e`, and `rg -l "msw|mockServiceWorker" dist`. See `../quickstart.md`.

Source: `docs/domains/frontend/ARCHITECTURE.md` — "4.1 Shell zones" and "4.3 Building blocks"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree" and "9.2 Tests mapped to gates".
