# Stock Investment Assistant Frontend

React 18 SPA for the DP Stock Investment Assistant. The package is built with Vite and tested with Vitest.

## Requirements

- Node `>=26.13.0` (`.nvmrc` is `26`; the proven runtime is v26.13.1)
- npm with `engine-strict=true` (`.npmrc`)

## Scripts

From `frontend/`:

```powershell
npm ci
npm run dev
npm run lint
npx tsc --noEmit
npx vitest run
npm run build
```

`npm run dev` starts the Vite dev server. The browser stays on that origin. Vite proxies `/api` to `http://127.0.0.1:5000`.

`npm run build` writes static files to `dist/`.

## Environment

Public settings are `VITE_*` only. Vite loads:

| File | When |
|---|---|
| `.env.development` | `npm run dev` |
| `.env.production` | `npm run build` |
| `.env.test` | Vitest |
| `.env.example` | Template. Vite does not load it |

```text
VITE_API_BASE_URL=
VITE_STREAM_IDLE_TIMEOUT_MS=60000
```

Leave `VITE_API_BASE_URL` empty so calls stay on the same origin. `VITE_STREAM_IDLE_TIMEOUT_MS` is the chat-stream idle window, in milliseconds. Change it in the env file. The client does not hard-code that number.

## Stack

- Vite and Vitest, jsdom, React Testing Library, and MSW for the test base
- TypeScript 5.9 or newer, React 18 type packages
- `fetch` only inside `platform/api` and `platform/stream`
- Chat transport is SSE through `openChatStream`
- Dark tokens, vi-VN copy through `t()`, and self-hosted Be Vietnam Pro and IBM Plex Mono

Module folders are `features/` and `platform/`. The shell is `app/` (the current chat shell still lives in `src/App.tsx` until the shell slice). Shared UI is `design-system/`.

## Layout

```text
frontend/
├── index.html
├── vite.config.ts
├── vitest.config.ts
├── eslint.config.js
├── public/fonts/
└── src/
    ├── platform/api/          # typed client and generated OpenAPI types
    ├── platform/stream/       # SSE chat reader
    ├── platform/format/       # vi-VN board formatters
    ├── platform/i18n/         # t() and the vi-VN catalogue
    ├── design-system/         # tokens and PriceCell, Delta, StatusBadge
    └── components/models/     # model selector
```

## Backend

The Flask API listens on port 5000. The client calls health, config, `models/*`, and chat. It sends `credentials: 'same-origin'` and does not send `Authorization` or `X-User-ID`.

## Image

From the repository root:

```powershell
docker build -f frontend/Dockerfile -t dp-stock/frontend:dev .
```

The image uses `node:26-alpine` and packages `dist`.
