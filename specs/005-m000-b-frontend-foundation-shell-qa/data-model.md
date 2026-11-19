# Data model: M-000 shell and QA

Phase 1 for `specs/005-m000-b-frontend-foundation-shell-qa`. These are Frontend presentation and session objects. They are not Backend collections and they are not Investment Core records. The Backend still owns the thread.

Source: `spec.md` — "Key Entities"; `docs/domains/frontend/ARCHITECTURE.md` — "6.1 State ownership matrix"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "4.2 Zustand store" and "5. Routing and navigation". Decisions: `research.md` R10, R11, R13, R15.

## WorkspaceStore

One Zustand store. Four slices. Devtools middleware only when `import.meta.env.DEV` is true.

### workspace

| Field | Type | Owner | Rule |
|---|---|---|---|
| `symbol` | `string \| null` | URL mirror | Written only by `useUrlSync()` |
| `coreObjectRef` | `CoreObjectRef \| null` | URL mirror | Same. Core-object routes do not ship, so navigation in this delivery leaves it `null` |
| `activeTrack` | `'sandbox' \| 'portfolio'` | URL mirror | Same |
| `lastRouteByTrack` | `Record<'sandbox' \| 'portfolio', string \| null>` | store | Restored when the investor switches track |

`CoreObjectRef` is `{ type: string; id: string }`. The type list grows in later milestones. This delivery does not add a route that sets it.

### context

| Field | Type | Persistence |
|---|---|---|
| `bySymbol` | `Record<string, SymbolContext>` | `sessionStorage`, same tab |

`SymbolContext`:

| Field | Type | Notes |
|---|---|---|
| `lastCoreObjectRef` | `CoreObjectRef \| null` | Preference, not a URL |
| `chart` | `{ range: string; interval: string; seriesType: 'candle' \| 'line' }` | Data only. No chart is rendered |
| `z4ScrollTop` | `number` | Restored when the investor returns to that symbol |

The symbol key is the uppercase code (`FPT`, `VNINDEX`, `VN30`). Chart range, interval, and series type are not URL params.

### layout

| Field | Type | Persistence |
|---|---|---|
| `paneSizes` | `Record<'sandbox' \| 'portfolio', [z1: number, z3: number, z4: number]>` | `sessionStorage`, same tab |
| `collapsed` | `{ z1: boolean; z4: boolean }` | session UI |

Saved layout presets are M-009 and are not built. The Proposed 240 px and 440 px defaults are not the done bar (`research.md` R12).

### ui

| Field | Type | Rule |
|---|---|---|
| `theme` | `'dark'` | No `'light'` member. No switcher |
| `density` | `'compact'` | Comfortable density stays later |

## RouteParams

Pure functions in `platform/workspace/routeParams.ts`. No I/O.

| Function | Accepts | Rejects |
|---|---|---|
| `parseTrack` | `sandbox`, `portfolio` | Any other segment, including a different case |
| `parseSymbol` | Non-empty segment with no lowercase letter. Tests lock `FPT`, `VNINDEX`, `VN30` | A segment that contains a lowercase letter. No extra character class |

Search params are not read. `/:track/:symbol/:coreType/:coreId` is not a route.

## CompanionRun

Held in `features/companion`. Not copied into the workspace slices.

| Field | Type | Rule |
|---|---|---|
| `sessionRef` | `{ sessionId: string; conversationId: string }` | Opaque. One copy. `sessionId` stays off the chat wire (spec 004 O2) |
| `status` | `idle \| streaming \| done \| interrupted \| error` | See transitions |
| `draft` | `string` | Also the `sessionStorage` value |
| `partialMessage` | `string` | Kept on stop and on idle timeout |

### Run transitions

```text
idle → streaming        send
streaming → done        stream ends
streaming → interrupted stop, or the delivery 1 idle timeout
streaming → error       stream error
interrupted → streaming "Tạo lại" activated; same user message; new run
error → streaming       "Tạo lại" activated; same user message; new run
```

There is no transition that resumes a partial run. "Tạo lại" sends nothing until activated.

### Draft storage

| Item | Rule |
|---|---|
| Key | `dp-stock:z4-draft:${sessionId}:${conversationId}` |
| Value | Draft text only. Never a token or a credential |
| Restore | Same tab reload |
| Remove | Send |
| Keep | Stop, idle timeout, `interrupted` |
| Scope | `sessionStorage`. Another tab does not see it |

## ZoneFrame

| Field | Values |
|---|---|
| `zone` | `z1`, `z2`, `z3`, `z4` |
| `state` | `empty`, `loading`, `ready`, `stale`, `error`, `interrupted`, `streaming` |
| `data-state` | The state value |
| `data-zone` | The zone id |
| `aria-busy` | `true` while `loading` or `streaming` |

A throw inside one zone sets that zone's state to `error` and calls `reportError(error, { zone, route? })`. The other three zones are unchanged. `reportError` logs to the console.

Per-zone content for the empty and error frames follows `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix". Z4 interrupted shows "Tạo lại". Z2 empty shows "Chưa chọn mã" through `t('shell.z2.emptySymbol')`.

## AgentMessage

Rendered by `design-system/patterns/MessageBody`. Not HTML.

| Field | Values |
|---|---|
| `body` | Markdown string from the model or the investor |
| `data-origin` | `ai` or `investor` |
| Label | `t('ai.suggested')` or `t('ai.confirmed')` |
| Edge | Dashed for `ai`, solid for `investor` |

Validation: the XSS fixtures in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output" produce no event-handler attribute, no `script` element, and no `javascript:` href. Tables, lists, and bold still render.

## Query keys

Factory only. This delivery calls the first three.

| Key | Factory | Called |
|---|---|---|
| health | `qk.health()` | yes |
| config | `qk.config()` | yes |
| models | `qk.models(provider)` | yes, provider values the client already uses |
| prices, workspace, evidence, thesis, decision, positions | later milestones | no |

Timings stay at the TanStack Query defaults. The Proposed numbers in "4.3 Query key taxonomy" are not adopted.

## MswHandlerSet

| Operation | Path | In this set |
|---|---|---|
| `getHealth` | `GET /api/health` | yes |
| `getConfig` | `GET /api/config` | yes |
| `postChat` | `POST /api/chat` | yes, delivery 1 SSE frames |
| `listOpenAIModels`, `refreshOpenAIModels`, `getSelectedModel`, `selectModel`, `setDefaultModel` | `/api/models/openai` and its subpaths | yes |
| Any other `docs/openapi.yaml` operation | — | no |
| `GET /api/market/prices/{symbol}` | not in the contract | no |

Handlers are typed from the generated schema. The same module serves Vitest and the browser worker.

## Story

A Storybook entry. Dark compact only.

| Required | Count |
|---|---|
| `ZoneFrame` states | 7 stories, one state each |
| `PriceCell`, `Delta`, `StatusBadge`, `MessageBody` | at least one story each |
| Whole required set | 11 to 15 stories |

Variants cover up, down, zero, missing, and the three `MessageBody` cases when those are not separate stories. Axe runs on every rendered case. Light stories and snapshot stories are not in the model.
