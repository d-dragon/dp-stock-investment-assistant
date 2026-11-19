# Frontend application analysis

This note describes the frontend after the M-000 foundation. The October 2025 refinement plan that treated Create React App and a Socket.IO service as the target is retired. Do not bring that toolchain back.

## Stack

- React 18 and TypeScript 5.9
- Vite 6 for `npm run dev` and `npm run build` (output `dist/`)
- Vitest, jsdom, Testing Library, and MSW (`npx vitest run`)
- ESLint over `src` (`npm run lint`)
- Node `>=26.13.0` (`.nvmrc` is `26`)
- Public configuration is `VITE_*` only, in `.env.development`, `.env.production`, and `.env.test`. `.env.example` is a template and Vite does not load it.

## Communication

- The typed fetch client lives in `src/platform/api`. Credentials stay same-origin. The client does not send `Authorization` or `X-User-ID`.
- Chat uses server-sent events through `src/platform/stream/openChatStream.ts`.
- `fetch` stays inside `platform/api` and `platform/stream`.
- There is no Socket.IO client, no standalone WebSocket client, and no `EventSource` outside the stream module.

The dev server proxies `/api` to `http://127.0.0.1:5000`.

## Layout

```text
src/
├── App.tsx                      shell until the shell slice
├── components/models/           ModelSelector
├── platform/api/                fetch client
├── platform/stream/             SSE chat stream
├── platform/i18n/               vi-VN catalogue and t()
├── platform/format/             fmt
├── design-system/               dark tokens, self-hosted fonts, patterns
├── types/models.ts
└── index.tsx
```

Module folders are `features/` and `platform/`. The shell is still `App.tsx`. Shared UI is `design-system/`.

## Removed

These paths are gone and are not the design to recreate:

- Create React App, `react-scripts`, Webpack dev config, and `config-overrides.js`
- `REACT_APP_*` environment variables
- Jest
- `WebSocketTest`, `webSocketService`, and any `src/services/webSocket/` socket service
- `restApiClient.js`, `apiService.ts`, and `src/services/modelsApi.ts` (model calls are `modelsApi` on `src/platform/api/client.ts`)

## Checks

From `frontend/`:

```powershell
npm run dev
npm run lint
npx vitest run
npm run build
```

The font check is Playwright (`e2e/b4-t4-fonts.spec.ts`) against the Vite dev server. It is not part of the frontend CI workflow.
