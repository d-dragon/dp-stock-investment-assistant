---
description: Frontend target stack for Vite, Vitest, and the features/platform tree
applyTo: "frontend/**"
---

# Frontend target stack

Follow the same rules as `frontend/AGENTS.md`. Governing sections: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)".

- Vite and Vitest.
- `VITE_*` environment variables only.
- No `socket.io-client`, WebSocket, or EventSource.
- `fetch` only inside `platform/api` and `platform/stream`.
- Module folders are `features/` and `platform/`. The shell is `app/` and shared UI is `design-system/`.
- Lint rules 1–3, as B1 enables them: dependency direction `app` → `features` → `platform` / `design-system`; no sibling-feature or deep imports; only `platform` talks to the Backend.

Do not recommend Create React App, Jest, `REACT_APP_*`, or Socket.IO.
