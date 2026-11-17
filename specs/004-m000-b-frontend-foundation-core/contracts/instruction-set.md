# Contract: B0 instruction set

**Slice**: B0

**Source**: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-004, FR-005, FR-006, FR-007.

## Files

| File | Obligation |
|---|---|
| `frontend/AGENTS.md` | Created. Under 10,000 characters. States the rules below |
| Root `AGENTS.md` | Frontend lines state the same rules |
| `.github/instructions/frontend-react.instructions.md` | States the same rules |
| `CLAUDE.md`, `.claude/rules`, `.cursor/rules` | Any entry that recommends Create React App, Jest, `REACT_APP_*`, or Socket.IO is removed or rewritten |

B0 does not change application source, tests, or config, and it does not add a test file.

## Rules the files state

- Vite and Vitest.
- `VITE_*` environment variables only.
- No `socket.io-client`, WebSocket, or `EventSource`.
- `fetch` only inside `platform/api` and `platform/stream`.
- Module folders are `features/` and `platform/`. The files do not tell a session to create `modules/`.
- Lint rules 1–3 from `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)", as B1 enables them.

ADR-FRONTEND-001 — "Implementation Direction" still says `modules/`. That sentence is stale for this delivery and is not the instruction text.

## Proof

From `frontend/`:

- `grok inspect` lists the new rules.
- A search of instruction files finds no recommendation of Create React App, Jest, `REACT_APP_*`, or Socket.IO.

There is no failing-test proof for B0.
