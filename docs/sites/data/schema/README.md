# Weekly data schema (v2.3)

Canonical files:

- `week.schema.json` — `docs/sites/data/YYYY-MM/week-WW.json`
- `catalog.schema.json` — `docs/sites/data/index.json`

Golden payload (do not “improve” its shape): `docs/sites/data/2026-09/week-38.json`.

`report-app.js` binds **only** this shape. A drifted file (see `week-39.json` before v2.3) leaves panes empty or throws when `outlook` is an array.

## Load order for the daily agent

1. `docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md`
2. This folder (`week.schema.json` + this README)
3. Canonical sources registry: `docs/sites/data/sources.json` (strictly prioritize scraping/searching these sources)
4. Existing target `week-WW.json` (upsert; never replace sibling days)
5. Golden file `2026-09/week-38.json` if unsure about a field

## Data collection priority (Sources-First Rule)

- The agent must strictly prioritize extracting data from the canonical targets in `docs/sites/data/sources.json`.
- Web searches should prioritize domain-restricted filters matching instructed sources (`site:cafef.vn`, `site:vietstock.vn`, `site:sbv.gov.vn`, `site:vneconomy.vn`, `site:barrons.com`, etc.).
- Broad generic web searches are only fallbacks if an instructed target is inaccessible or missing the data point.

## Size rules (keep the week file small, keep it queryable)

Target: **≤ 25 KB per day** of pretty-printed JSON (week-38 days are ~19–21 KB report + 3–5 KB sources).

Do:

- Keep the nested objects the UI queries (`snapshot.quotes`, `equityMarket.index.latest`, `series.vnindex.points`).
- Numbers as JSON numbers (`1815.66`), never `"1.815,66"`.
- Short Vietnamese strings. `impact.text` ≤ 280 chars. No article paste.
- Series: 2–40 `{t,v}` points. Prefer official closes, not dense intraday ticks.
- Reuse `src-*` ids. One source registry per day, not per paragraph.

Do not:

- Add keys that are not in the schema (`category`, `region`, `tags`, `asOf`, `venue`, `outlook.stance` as a replacement for the object, `outlook` as array).
- Duplicate yesterday’s full news block “for context”.
- Embed images as data-URLs. `image` is optional; omit it when there is no real thumbnail (UI has a fallback).
- Write a new `YYYY-MM-DD/` folder or a new dashboard HTML file.
- Overwrite other `days[]` entries when publishing today.

## Binding map (do not rename)

| UI pane | JSON path |
|---|---|
| Header session / time | `report.marketSession`, `report.generatedAt`, `report.timezone` |
| Ticker | `report.snapshot.quotes[]` → `symbol`, `price`, `changePct` |
| Tin thế giới | `report.globalNews[]` → `date`, `title`, `summary`, `impact.text`, `image.url`, `sourceId`, `url` / `id` (source hyperlink) |
| Vĩ mô VN | `report.vietnamMacro[]` → `nameVi`, `value`, `unit` + `report.vietnamNews[]` (`url` / `id` source hyperlink) |
| Chart VN | `report.equityMarket.*` + `series.vnindex` + `series.vnindexVolume5d` + `series.foreignNet5dVndBn` |
| Chart thế giới | `report.worldMarkets.quotes[]` + `series.dji\|ndx\|spx\|dxy\|nky\|hsi` |
| Chart crypto | `report.cryptoMarkets.quotes[]` + `series.btcUsd` |
| Doanh nghiệp | `report.companies[]` → `ticker`, `headline`, `metrics.changePct`, `impact.text`, `sourceId` |
| Triển vọng | `report.outlook.watchpoints\|levels\|events` (**object**, never array) |
| Footer links | `days[].sources.sources[]` keyed by `id` |

## Forbidden drift (observed on week-39)

- `outlook` became a list → right pane “Theo dõi / Mốc / Sự kiện” binds to `undefined`.
- `series` dropped to only `vnindex` → world/crypto/volume charts empty.
- News/macro/company arrays shrank below minima → panes look broken.
- Snapshot quote count dropped below 10 → ticker incomplete.

Publish is invalid unless `schema-validate.js` / `week.schema.json` accept the file.

## JSON formatting standard (Prettier / 2 spaces)

All weekly files (`docs/sites/data/YYYY-MM/week-WW.json`) and `data/index.json` must be formatted cleanly:
- **Indentation**: Exactly 2 spaces per nesting level (matching `week-38.json`).
- **Colons**: Single space after colon (`"key": "value"`). Never double spaces.
- **Escapes**: Do not HTML-escape `&` as `\u0026` or `'` as `\u0027`.
- **PowerShell warning**: Never write raw `ConvertTo-Json` output from Windows PowerShell 5.1 directly to disk without reformatting, as it causes 40+ spaces deep indentation bloat, double-spaced colons, and entity escaping.
- **Serialization**: Use `JSON.stringify(payload, null, 2)` (JS), `json.dumps(payload, indent=2, ensure_ascii=False)` (Python), or `scripts/format-weekly-json.ps1` before committing.

