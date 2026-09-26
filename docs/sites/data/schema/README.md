# Weekly + daily data schema (v2.4)

Canonical files:

- `week.schema.json` — thin week index `data/YYYY-MM/week-WW.json` (v2.1.0) **or** legacy embedded week (v2.0.0, golden `2026-09/week-38.json`)
- `day.schema.json` — one trading day `data/YYYY-MM/d/YYYY-MM-DD.json`
- `catalog.schema.json` — `data/index.json`

Why shards: GitHub Contents API accepts ~1 MB, but the **connected GitHub MCP tools truncate / fail around 30–40 KB payloads**. A 5-day embedded week (~100 KB) cannot be pushed reliably. One day file is ~18–29 KB.

## Load order for the daily agent

1. `docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md`
2. This folder (`week.schema.json` + `day.schema.json` + this README)
3. Existing target **day file** `YYYY-MM/d/TODAY.json` (create if missing)
4. Thin week index `YYYY-MM/week-WW.json` — upsert today’s pointer only
5. Golden **report shape** still = `2026-09/week-38.json` `days[].report` if a field is ambiguous

## Publish unit (v2.4)

Push **three small files**, never one fat week blob:

1. `data/YYYY-MM/d/YYYY-MM-DD.json` — today’s report + sources only
2. `data/YYYY-MM/week-WW.json` — thin index (`storage: "day-shards"`, each day is `{date, dayPath, status}`)
3. `data/index.json` — catalog row with both `weekPath` and `dayPath`

Do **not** embed `report` inside `week-WW.json` for new days. Leave week-38 embedded as-is.

## Size rules

Target: **≤ 25 KB pretty-printed per day file**.

Do:

- Keep the nested objects the UI queries (`snapshot.quotes`, `equityMarket.index.latest`, `series.vnindex.points`).
- Numbers as JSON numbers (`1815.66`), never `"1.815,66"`.
- Short Vietnamese strings. `impact.text` ≤ 280 chars. No article paste.
- Series: 2–40 `{t,v}` points. Prefer official closes, not dense ticks.
- Reuse `src-*` ids. One source registry per day.

Do not:

- Add keys that are not in the schema.
- Duplicate yesterday’s full news block “for context”.
- Embed images as data-URLs.
- Create `data/YYYY-MM-DD/` folders or a new dashboard HTML file.
- Overwrite a sibling day file when publishing today.
- Replace `week-WW.json` `days` with `[todayOnly]`.

## Binding map (do not rename)

`index.html` → `data/index.json` → prefer `reports[].dayPath` → else `weekPath` + `days[date]`.

| UI pane | JSON path |
|---|---|
| Header session / time | `report.marketSession`, `report.generatedAt`, `report.timezone` |
| Ticker | `report.snapshot.quotes[]` → `symbol`, `price`, `changePct` |
| Tin thế giới | `report.globalNews[]` |
| Vĩ mô VN | `report.vietnamMacro[]` + `report.vietnamNews[]` |
| Chart VN | `report.equityMarket.*` + `series.vnindex` + volume/foreign 5d |
| Chart thế giới | `report.worldMarkets.quotes[]` + `series.dji\|ndx\|spx\|dxy\|nky\|hsi` |
| Chart crypto | `report.cryptoMarkets.quotes[]` + `series.btcUsd` |
| Doanh nghiệp | `report.companies[]` |
| Triển vọng | `report.outlook.watchpoints\|levels\|events` (**object**, never array) |
| Footer links | `sources.sources[]` keyed by `id` |

## Forbidden drift

- `outlook` as array → right pane empty.
- `series` missing any of the ten ids → charts empty.
- News/macro/company below minima → panes look broken.
- Fat week file rewrite that drops sibling dates.
