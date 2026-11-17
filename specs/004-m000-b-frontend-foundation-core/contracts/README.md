# Contracts

Interfaces for delivery 1 of Pitch B (B0, B1, B2, thin B4). Behavior that is still open is marked in `../research.md` and is not decided here.

| Contract | Slice | Covers |
|---|---|---|
| `instruction-set.md` | B0 | Instruction files and the `grok inspect` proof |
| `toolchain-and-ci.md` | B1 | Node pin, Vite, T0 deletions, G1 smoke, lint rules 1–3, CI skeleton |
| `platform-api.md` | B2 | `openapi-typescript` output, client hooks, allowed paths |
| `chat-stream.md` | B2 | `openChatStream`, today's frames, idle timeout, Socket.IO removal |
| `format-catalogue-tokens.md` | B4 | `fmt`, `t()`, dark tokens, patterns, chart-import lint |

Shared commands from `frontend/`: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`. See `../quickstart.md`.
