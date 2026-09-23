# Daily Market Brief — Task Instruction

**Status:** living document — edit this file; do not treat chat history as the source of truth
**Version:** 2.3.4
**Updated:** 2026-09-23 (GMT+7)
**Owner:** Phan Duy / DP Stock-Investment Assistant
**Canonical path in repo:** `docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md` on branch `project-website-pages`
**Proven:** v2.0.0 Pages JSON bind 2026-09-18. v2.1 dashboard same day. v2.1.1 UTF-8 + Be Vietnam Pro. v2.2 monthly/weekly JSON + hash hub. v2.3 locks weekly payload to `data/schema/week.schema.json` (golden file `data/2026-09/week-38.json`). v2.3.1 integrates canonical `data/sources.json` for web scraping and attribution. v2.3.2 adds strict data output rules (append-only weekly file, clickable news links, diacritics preservation). v2.3.3 enforces Prettier JSON formatting standard (2-space indentation, single-space colons, unescaped UTF-8). v2.3.4 establishes mandatory Data Source Prioritization (instructed sources-first scraping and domain-constrained search).

---

## How to use this file

1. Daily automation MUST load this file first (`get_file_contents`, ref `refs/heads/project-website-pages`).
2. Then load `docs/sites/data/schema/week.schema.json`, `docs/sites/data/schema/README.md`, and `docs/sites/data/sources.json`.
3. If a field is ambiguous, copy the shape from `docs/sites/data/2026-09/week-38.json` — not from week-39.
4. After each run, log gaps in **Changelog**. Do not put market numbers in this file.

---

## Changelog

| Date | Version | Change |
|---|---|---|
| 2026-09-23 | 2.3.4 | Strict Data Source Prioritization Rule: mandate that agent prioritizes scraping/searching registered sources from sources.json (using target URLs or domain-restricted queries) over unconstrained generic search. |
| 2026-09-23 | 2.3.3 | Enforce Prettier JSON formatting standard (2-space indentation, single space after colon, clean unescaped UTF-8). Ban bare PowerShell ConvertTo-Json formatting artifacts (depth runaway bloat, \u0026 / \u0027 escaping). |
| 2026-09-23 | 2.3.2 | Explicit data output rules: append to weekly file without rewriting, clickable news source links, strict UTF-8 diacritics preservation. |
| 2026-09-23 | 2.3.1 | Add canonical sources directory (`data/sources.json`) for web scraping references and source ID attribution. |
| 2026-09-22 | 2.3.0 | Formal weekly schema (`data/schema/week.schema.json` + `catalog.schema.json`). Agent must validate before push. Size cap + query-oriented compact keys taken from week-38. UI validator + outlook-array guard so drifted files still render. |
| 2026-09-21 | 2.2.0 | Monthly folders + weekly JSON. Catalog 2.0.0. Single hub `index.html` hash routes. |
| 2026-09-18 | 2.1.1 | UTF-8 mandatory. Be Vietnam Pro. Fetch this file before running. |
| 2026-09-18 | 2.1.0 | Multi-pane dashboard. Chart.js. No TradingView HOSE:VNINDEX. |
| 2026-09-18 | 2.0.0 | Split HTML into template + CSS/JS. |

---

## Role / mission

Financial research analyst + front-end engineer. For **today in Asia/Ho_Chi_Minh (GMT+7)** collect global news + impact, Vietnam news + macro, VN-Index / volume / value / foreign / proprietary / retail, world + crypto quotes and series, listed-company events, outlook. Publish as structured weekly JSON bound by the existing dashboard. Do not ship a monolithic HTML file with hardcoded numbers.

---

## Repository

- Repo: `https://github.com/d-dragon/dp-stock-investment-assistant`
- Branch: `project-website-pages`
- Pages root: `docs/`
- Hub: `docs/sites/index.html`

```text
docs/sites/
  DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md
  index.html
  assets/css/report.css
  assets/js/report-app.js
  assets/js/schema-validate.js
  templates/daily-report.html
  data/index.json
  data/sources.json                     # Canonical scrapable sources
  data/schema/week.schema.json          # ENFORCE
  data/schema/catalog.schema.json
  data/schema/README.md
  data/YYYY-MM/week-WW.json
```

Do **not** create `data/YYYY-MM-DD/` folders or a new `YYYY-MM-DD.html` dashboard.

---

## Schema lock (v2.3 — non-negotiable)

Machine contract: `docs/sites/data/schema/week.schema.json`.
Human map: `docs/sites/data/schema/README.md`.
Golden payload: `docs/sites/data/2026-09/week-38.json`.

Week file top-level (`additionalProperties: false`):

```json
{
  "schemaVersion": "2.0.0",
  "yearMonth": "2026-09",
  "week": { "isoYear": 2026, "isoWeek": 38, "id": "2026-W38", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "updatedAt": "ISO-8601+07:00",
  "days": [{ "date": "YYYY-MM-DD", "report": {}, "sources": {} }]
}
```

Each `days[].report` keeps `schemaVersion: "1.0.0"` and **exactly** these keys (same as week-38):

`schemaVersion`, `id`, `type` (`daily_market_brief`), `locale` (`vi-VN`), `timezone` (`Asia/Ho_Chi_Minh`), `generatedAt`, `coverage`, `marketSession`, `disclaimer`, `ui`, `snapshot`, `globalNews`, `vietnamNews`, `vietnamMacro`, `equityMarket`, `worldMarkets`, `cryptoMarkets`, `companies`, `outlook`, `series`

Hard rules:

- `outlook` is an **object** `{ watchpoints, levels, events }`. Never an array.
- `series` must include all ten ids: `vnindex`, `dji`, `ndx`, `spx`, `dxy`, `nky`, `hsi`, `btcUsd`, `vnindexVolume5d`, `foreignNet5dVndBn`.
- Numbers are JSON numbers. Missing print = `null` + `note`. Never invent an official close.
- Visible strings are Vietnamese with diacritics. Keys stay English.
- Do not add keys outside the schema (`category`, `region`, `tags`, `asOf`, `venue`, `outlook` as list).
- **Data output & JSON formatting**:
  - The daily data output must be appended to the weekly data file (as an object in array `days[]`) at `docs/sites/data/YYYY-MM/week-WW.json`. MUST not rewrite the whole data file.
  - Each news item must have a hyperlink to its source in its `id` or `url` (or both) field.
  - Never strip Vietnamese diacritics in JS chrome or JSON (UTF-8 encoding).
  - **Prettier JSON format**: All output JSON files (`week-WW.json` and `index.json`) MUST be formatted with standard **2-space indentation** (Prettier / `JSON.stringify(..., null, 2)` style, matching `week-38.json`).
  - **Single space after colon**: Format keys as `"key": "value"`, never `"key":  "value"`.
  - **Ban bare PowerShell `ConvertTo-Json` formatting artifacts**: Do not leave exponential indentation bloat (40+ spaces deep on nested quotes/sources), double spaces after colons, or HTML entity escaping (`\u0026` for `&`, `\u0027` for `'`, `\u003c` for `<`, `\u003e` for `>`). If generating or upserting JSON, serialize with clean 2-space indentation before saving.
- **Data source prioritization (instructed sources-first rule)**:
  - The agent **MUST prioritize** collecting data directly from the registered targets in `docs/sites/data/sources.json`.
  - When searching the web (e.g. via search engines), the agent **MUST prioritize domain-constrained queries** targeting registered source domains (e.g. `site:cafef.vn`, `site:vietstock.vn`, `site:sbv.gov.vn`, `site:gso.gov.vn`, `site:vneconomy.vn`, `site:barrons.com`, `site:bloomberg.com`) rather than unconstrained generic web searches.
  - Unconstrained generic web searches are ONLY allowed as a secondary fallback if an instructed source is unreachable or lacks coverage for a specific breaking event. Every collected item must be attributed to an authentic registered source in `days[].sources.sources[]`.

### Minima (so panes are not empty)

| Field | Min | Max |
|---|---|---|
| `snapshot.quotes` | 10 | 16 |
| `globalNews` / `vietnamNews` | 8 | 12 |
| `vietnamMacro` | 8 | 12 |
| `worldMarkets.quotes` | 6 | 10 |
| `cryptoMarkets.quotes` | 2 | 6 |
| `companies` | 5 | 8 |
| `outlook.watchpoints` / `levels` / `events` | 2 | 6 |
| `days[].sources.sources` | 4 | 32 |
| line series `points` | 2 | 40 |

Required ticker symbols (snapshot): `VNINDEX`, `HNX`, `DXY`, `DJI`, `NDX`, `SPX`, `NKY`, `HSI`, `WTI`, `XAU`, `BTC`, plus `USDVND` when available.
World board: `DXY`, `DJI`, `NDX`, `SPX`, `RUT`, `FTSE`, `NKY`, `HSI` (drop RUT/FTSE only if truly missing, keep ≥6).
Crypto board: `BTC`, `ETH`.

### Size

Target ≤ 25 KB pretty-printed JSON per day (week-38 days are ~19–21 KB). Cap string lengths, omit `image` when there is no real thumbnail, do not paste articles, do not dump dense intraday ticks.

### Binding (must keep working)

`index.html` → `data/index.json` → `data/{weekPath}` → `days[date].report` + `days[date].sources`.
`report-app.js` reads the paths in `data/schema/README.md`. Renaming a key breaks the dashboard.

Catalog (`data/index.json`): `schemaVersion: "2.0.0"`, `layout: "monthly-weekly"`, reports newest-first with `weekId`, `weekPath`, `path: "index.html#/YYYY-MM-DD"`.

---

## Publish

1. Compute ISO week (Monday start) → open or create `data/YYYY-MM/week-WW.json`.
2. Fetch the existing week file. **Upsert only today's** `days[]` row. Never delete or rewrite sibling days.
3. Format the whole week file with standard Prettier 2-space indentation (matching `week-38.json`) and validate against `week.schema.json` / `schema-validate.js`. If invalid or unformatted, fix JSON — do not push a partial or bloated day.
4. Upsert `data/index.json` (newest-first, formatted with 2 spaces).
5. Do not edit `report-app.js` / CSS unless the schema change requires it (v2.3 already guards `outlook` arrays).
6. Commit: `Publish daily market brief YYYY-MM-DD (dashboard v2.3 schema)`.
7. Spot-check UTF-8 (`ệ` / `ư` / `ả`) still present in the pushed week JSON.

### Data sources & Scraping Priority (Sources-First Execution)

When performing web scraping and data collection, agents **MUST load and strictly prioritize `docs/sites/data/sources.json`** as the canonical registry of scraping targets, URLs, categories, descriptions, and attribution source IDs (`src-*`).

#### Data Collection Priority Hierarchy:
1. **Tier 1 (Direct Target Scraping / High Priority)**: Always start by directly querying or fetching the canonical URLs registered in `sources.json` (favoring `reliability: "primary"`).
2. **Tier 2 (Domain-Constrained Search)**: When utilizing search engines (e.g. `search_web`), the agent **MUST prioritize domain-constrained queries** targeting registered source domains (e.g. `site:cafef.vn "VN-Index"`, `site:vietstock.vn "khối ngoại"`, `site:sbv.gov.vn "tỷ giá"`, `site:nso.gov.vn "CPI"`, `site:barrons.com "market data"`).
3. **Tier 3 (Unconstrained Search as Last-Resort Fallback)**: Unconstrained generic web searches are ONLY permitted if an instructed source is unreachable or truly lacks critical breaking coverage. Any newly discovered external outlet must be registered with proper attribution in `days[].sources.sources[]`.

Sources in `sources.json` are organized by `category`:
- **`Vietnam Market Data & Indices`**: Quotes, trading volumes, corporate actions, official foreign trading statistics, liquidity, and historical series (`src-cafef`, `src-cafef-data`, `src-vietstock`, `src-stockbiz`, `src-yahoo-vn`, `src-24h`).
- **`Vietnam Macro & Policy`**: SBV central exchange & policy rates, NSO/GSO macro indicators (CPI, FDI, GDP), and policy news (`src-nhnn`, `src-nso`, `src-vneconomy`, `src-vietnambiz`).
- **`Global & Commodities / Crypto`**: US equity index futures, bond yields (10Y UST), DXY, commodities, and benchmark crypto (`src-barrons`, `src-bloomberg`, `src-yahoo-btc`).

> **Attribution rule**: Any quote, news item, company item, or macro metric published in `days[].report` must reference a valid `sourceId` registered in `docs/sites/data/sources.json` and mirrored in `days[].sources.sources[]` (with today's `accessedAt` timestamp). Do not invent official HOSE prints.

---

## Agent prompt

```text
FIRST: load docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md from repo d-dragon/dp-stock-investment-assistant branch project-website-pages (ref refs/heads/project-website-pages). Follow that file (v2.3.0+). Do not invent a parallel spec from chat history.

SECOND: load docs/sites/data/schema/week.schema.json, docs/sites/data/schema/README.md, and docs/sites/data/sources.json.
DATA SOURCE PRIORITY: You MUST strictly prioritize searching, scraping, and collecting data directly from the instructed sources in sources.json (using target URLs or domain-restricted searches e.g. site:cafef.vn, site:vietstock.vn, site:sbv.gov.vn). Do NOT rely on unconstrained generic web searches when instructed sources cover the required quotes, news, macros, or market data. The weekly JSON MUST validate against that schema. Golden shape = docs/sites/data/2026-09/week-38.json. Do NOT copy the drifted shape of week-39.json (outlook-as-array, truncated series/news).

Output a GitHub Pages daily market brief for TODAY in Asia/Ho_Chi_Minh.

Write weekly files under docs/sites/data/YYYY-MM/week-WW.json (upsert today's days[] only — never overwrite other days). Update data/index.json. Do not create a new YYYY-MM-DD.html dashboard — hub is index.html with hash routing.

Keep the payload compact (≤25 KB/day) but complete: snapshot ≥10 quotes, ≥8 globalNews, ≥8 vietnamNews, ≥8 vietnamMacro, ≥5 companies, outlook object {watchpoints,levels,events}, series ids vnindex/dji/ndx/spx/dxy/nky/hsi/btcUsd/vnindexVolume5d/foreignNet5dVndBn.

Format output JSON cleanly with standard Prettier 2-space indentation (matching week-38.json). Avoid PowerShell ConvertTo-Json artifacts (no double spaces after colons, no 40+ space depth runaway bloat, unescape \u0026 to &, \u0027 to ').

UTF-8 only: never strip Vietnamese diacritics in JS chrome or JSON.
After push, spot-check that "ệ" or "ư" still exists in the week JSON day payload and report-app.js.

```