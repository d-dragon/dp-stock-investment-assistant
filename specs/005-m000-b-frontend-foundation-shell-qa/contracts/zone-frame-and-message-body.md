# Contract: ZoneFrame and MessageBody

**Slice**: B3 (T4 patterns, exercised by the shell)

**Source**: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts", "6.5 Safe rendering of Agent output", and "8.2 Pattern rules"; `docs/domains/frontend/DESIGN_LOCK.md` — "4.3 Colour and provenance rules" and "5. Zone state matrix"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance"; `spec.md` — FR-009, FR-012, FR-013, FR-014. Decisions: `research.md` R7, R9, R11, R14.

Both components live under `frontend/src/design-system/patterns/`. They are not under `platform/`.

## ZoneFrame (B3-D4)

Prop `state` is one of `empty`, `loading`, `ready`, `stale`, `error`, `interrupted`, `streaming`. The root sets `data-state` to that value and `data-zone` when the host passes a zone.

| State | Required UI |
|---|---|
| `empty` | DESIGN_LOCK frame for that zone. Z2 shows "Chưa chọn mã" through `t('shell.z2.emptySymbol')` |
| `loading` | `aria-busy="true"` |
| `ready` | Children |
| `stale` | Stale frame from the matrix. This delivery does not invent a price cue |
| `error` | Retry control. On Z4 the visible label is "Tạo lại" from `t('stream.retry')` |
| `interrupted` | "Tạo lại" from `t('stream.retry')`. No request until activated. MSW request count stays 0 for 5 seconds. No automatic resume |
| `streaming` | Stop control. `aria-busy="true"` |

User-facing strings go through `t()`. `react/jsx-no-literals` is an error on `app/`, `features/`, and `design-system/patterns/`. Allowed JSX strings: `·`, `—`, `/`, `%`, `₫`, `+`, `−`.

## MessageBody (B3-D7 and the XSS cases)

| Rule | Contract |
|---|---|
| Parser | `react-markdown` + `remark-gfm` |
| HTML | No `rehype-raw`. `skipHtml` on |
| URLs | Default `urlTransform`. `javascript:` and other unsafe schemes do not become hrefs |
| Links | `rel="noopener noreferrer nofollow"` and `target="_blank"` |
| Images | Off |
| `data-origin="ai"` | Dashed edge. Visible label `t('ai.suggested')` ("AI gợi ý") |
| `data-origin="investor"` | Solid edge. Visible label `t('ai.confirmed')` ("Đã xác nhận") |
| Hue | Not the only difference |

XSS fixtures that must render inert:

- `<img src=x onerror=alert(1)>`
- `<script>alert(1)</script>`
- `[x](javascript:alert(1))`
- an `<a onclick>`

Inert means no event-handler attribute, no `script` element, and no `javascript:` href. Markdown tables, lists, and bold still render.

`react/no-danger` stays an error. There is no exception for this component. Lucide icons named in DESIGN_SYSTEM "3.6 Provenance" are not a dependency of this contract. The edge and the label are the done bar.

Provenance colours stay in the design-system token layer. A hex, `rgb(`, or `hsl(` literal under `src/features/**` fails lint.

## Legacy removal (B3-D9)

When the shell ships:

- `frontend/src/App.css` and `frontend/src/index.css` are absent. They are already absent. The check still holds.
- The only global stylesheet is the token and base layer from delivery 1.
- No new module imports `frontend/src/components/**`.
- `frontend/src/components/models/ModelSelector.tsx` is rebuilt under `features/models` and removed from the legacy path.
- `frontend/src/App.tsx` is removed. The entry is `frontend/src/main.tsx`. `frontend/index.html` points at that module. The existing `<noscript>` sentence stays. It is locked by the delivery 1 catalogue test and cannot call `t()`.
