# Contract: format, catalogue, tokens, and patterns

**Slice**: B4

**Source**: `specs/pitches/M-000-B-frontend-foundation.md` — "B4: tokens, format, fonts" and "B4 — Dark tokens..."; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline", "8.2 Pattern rules", and "8.3 i18n and locale seam"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette", "4. Typography", and "8. Patterns"; `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy"; ADR-FRONTEND-005 — "Decision" (price-board bullet); ADR-FRONTEND-007 — "Decision"; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-022 through FR-028.

## Format

Custom functions, not `Intl`: `fmt.price`, `fmt.change`, `fmt.pct`, `fmt.vnd`, `fmt.volume`.

| Call | Output |
|---|---|
| `fmt.price(25300)` | `25.30` |
| `fmt.pct(0.0698)` | `+6.98%` |
| `fmt.pct(-0.0698)` | `−6.98%` (U+2212) |
| `fmt.pct(0)` | `0.00%` |
| `fmt.volume(1234500)` | `1,234,500` |
| `fmt.volume(0)` | `0` |
| `fmt.vnd(25300000)` | `25,300,000 ₫` |
| `fmt.change(1750)` | `+1.75` |
| `fmt.change(-450)` | `−0.45` (U+2212) |
| `fmt.change(0)` | `0.00` |
| any numeric `fmt.*` of `null`, `undefined`, or `NaN` | `—`, accessible name from `t()` key "Không có dữ liệu" |

`fmt.dateTime` uses `Intl` with locale `vi-VN` and time zone `Asia/Ho_Chi_Minh`. `Intl` is not used for the numeric functions. A property test of 1,000 random values asserts that the dot only marks a decimal and the comma only groups thousands.

## Catalogue

`t(key)` reads the vi-VN catalogue. No English catalogue. No i18n library.

Required strings: "Tạo lại", "Không có dữ liệu", "AI gợi ý", "Đã xác nhận".

`Delta` direction phrases are `[NEEDS CLARIFICATION]` (`research.md` R15). Until those phrases exist, the accessible-name requirement in row B4-T3 cannot be given exact copy. The structural requirement still holds: the name includes the direction and comes from `t()`.

## Tokens

The build generates CSS variables whose dark values equal the dark column in `data-model.md`. `--market-up` is `#2EBD6B`. Light values are absent. `<html>` has `data-theme="dark"`.

The generator package is not selected. Style Dictionary stays Proposed (`research.md` R13).

`track.a` and `track.b` are omitted. Zone surface aliases without a hex are omitted.

`<html>` carries `data-theme="dark"` and `data-density="compact"` (`research.md` R19, resolved).

## Tailwind and patterns

| Rule | Contract |
|---|---|
| B4-T2 | Tailwind exposes no `market` or `state` colour utilities |
| B4-T2 | Lint fails if `var(--market-*)` is read outside `PriceCell` / `Delta` |
| B4-T2 | Lint fails if `var(--state-*)` is read outside `StatusBadge` |
| B4-T2 | Lint fails if an arbitrary Tailwind colour (`text-[#…]`, `bg-[var(--market-up)]`) appears outside `design-system/patterns/` |
| B4-T3 | A positive or negative `Delta` shows a sign or an arrow as well as colour. Zero shows `0.00` and `0.00%` with no sign, coloured `market.ref` (row P2). The zero clause inside verbatim B4-T3 is superseded |
| B4-T4 | On-screen `fmt.*` computed `font-family` starts with `IBM Plex Mono`. UI text starts with `Be Vietnam Pro` |
| B4-T4 | Fonts are files under `public/fonts`. The network log shows no third-party font host |

B4-T4 is proven with Playwright. That run is not a job in the B1 CI skeleton (`research.md` R18).

`PriceCell` receives reference, ceiling, and floor as inputs. It does not compute them.

`MessageBody`, Storybook stories, and the contrast script are not this contract.

## Chart import seam

Lint fails on `lightweight-charts` imported outside `platform/chart`, and on `chart.js` imported outside `platform/stat-chart`. Neither package is added to `package.json`. The `ChartEngine` and `StatChart` interfaces are not implemented.

Source: ADR-FRONTEND-004 — "Decision" and "Considered Options"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" rule 5; `specs/004-m000-b-frontend-foundation-core/spec.md` — FR-029.
