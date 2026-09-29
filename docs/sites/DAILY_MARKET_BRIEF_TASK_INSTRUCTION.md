# Daily Market Brief — Task Instruction

**Status:** living document — this file is the source of truth. Chat history and the Grok automation prompt must not invent a parallel spec.
**Version:** 2.5.0
**Updated:** 2026-09-29 (GMT+7)
**Owner:** Phan Duy / DP Stock-Investment Assistant
**Canonical path:** `docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md` on branch `project-website-pages`
**Automation:** `Market daily brief` (`fc7b3b17-89d9-4107-a578-b4ce780a2911`) — the automation prompt only loads and follows this file.

**Proven:** v2.0 Pages JSON bind 2026-09-18. v2.1 dashboard. v2.1.1 UTF-8 + Be Vietnam Pro. v2.2 monthly/weekly + hash hub. v2.3 schema lock (golden `week-38.json`). v2.3.1–2.3.4 sources.json, news URLs, Prettier JSON, sources-first. v2.4 day shards after MCP could not push a fat week-39. v2.5 consolidates the live automation guardrails into this file.

---

## How to use this file

1. Automation MUST load this file first (`get_file_contents`, owner `d-dragon`, repo `dp-stock-investment-assistant`, path `docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md`, ref `refs/heads/project-website-pages`).
2. Then load `docs/sites/data/schema/day.schema.json`, `week.schema.json`, `catalog.schema.json`, `docs/sites/data/schema/README.md`, and `docs/sites/data/sources.json`.
3. If a field is ambiguous, copy the **report shape** from `docs/sites/data/2026-09/week-38.json` `days[].report` — not from a drifted week-39 blob.
4. After each run, log process gaps in **Changelog**. Do not put market numbers in this file.

---

## Changelog

| Date | Version | Change |
|---|---|---|
| 2026-09-29 | 2.5.0 | Migrated live automation guardrails (branch lock, one-commit rule, day-shard publish, MCP size) into this file. Automation prompt reduced to “load and follow this file”. |
| 2026-09-26 | 2.4.0 | Day shards: publish `data/YYYY-MM/d/YYYY-MM-DD.json` + thin `week-WW.json`. Loader prefers `catalog.dayPath`. week-38 stays embedded. |
| 2026-09-23 | 2.3.4 | Sources-first: scrape/search registered `sources.json` domains before unconstrained search. |
| 2026-09-23 | 2.3.3 | Prettier JSON (2-space, single-space colon, unescaped UTF-8). Ban PowerShell `ConvertTo-Json` artifacts. |
| 2026-09-23 | 2.3.2 | Append-only week updates, clickable news URLs, keep Vietnamese diacritics. |
| 2026-09-23 | 2.3.1 | Canonical `data/sources.json`. |
| 2026-09-22 | 2.3.0 | Formal `week.schema.json` + `catalog.schema.json`. Golden `week-38.json`. |
| 2026-09-21 | 2.2.0 | Monthly folders + weekly JSON. Catalog 2.0. Hash hub. |
| 2026-09-18 | 2.1.1 | UTF-8 mandatory. Be Vietnam Pro. |
| 2026-09-18 | 2.1.0 | Multi-pane dashboard. Chart.js. No TradingView HOSE:VNINDEX. |
| 2026-09-18 | 2.0.0 | Split HTML into template + CSS/JS. |

---

## Role / mission

Financial research analyst + front-end engineer. For **today in Asia/Ho_Chi_Minh (GMT+7)** collect global news + impact, Vietnam news + macro, VN-Index / volume / value / foreign / proprietary / retail, world + crypto quotes and series, listed-company events, outlook. Publish structured JSON bound by the existing dashboard. Do not ship a monolithic HTML file with hardcoded numbers.

---

## Branch and commit guardrails (from live automation)

- Repo: `https://github.com/d-dragon/dp-stock-investment-assistant`
- Write **only** on branch `project-website-pages` (`refs/heads/project-website-pages`).
- **Never** commit, push, create/update files, or add GitHub Actions workflows on `main`, `master`, or any other branch.
- **Never** use a temporary CI/workflow-on-main (or any out-of-scope branch) as a large-file or MCP push workaround. If a file cannot be pushed on `project-website-pages`, STOP, leave a local handoff artifact, and report the blocker to Phan.
- Do not merge to `main` unless Phan explicitly asks in that run.
- Before reporting success, verify the publish commit is on `project-website-pages`, not `main`.
- Follow skill: GitHub branch guardrail.

**Commits**

- Target **one Git commit per routine run** covering the day file + thin week pointer + catalog.
- Prefer assemble locally, then one create/update that lands the complete result.
- Exception (MCP payload cap ~30–40 KB): if a combined commit is too large, push the three small files as **separate commits of the same payload**, never extra probe/restore/cleanup commits. If a write fails, stop and report — do not pile retries.
- Commit message: `Publish daily market brief YYYY-MM-DD (dashboard v2.5 day-shard)`.

---

## Repository layout

Pages root: `docs/`. Hub: `docs/sites/index.html`.

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
  data/schema/week.schema.json          # week index (v2.0 embedded | v2.1 shards)
  data/schema/day.schema.json           # ENFORCE per-day payload
  data/schema/catalog.schema.json
  data/schema/README.md
  data/YYYY-MM/week-WW.json             # thin index when schemaVersion=2.1.0
  data/YYYY-MM/d/YYYY-MM-DD.json        # one day — the publish unit
```

Do **not** create `data/YYYY-MM-DD/` folders or a new `YYYY-MM-DD.html` dashboard.
Do **not** embed today’s report inside `week-WW.json` — that file exceeds the GitHub MCP push cap by mid-week.
Do **not** edit `report-app.js` / CSS unless the schema change requires it.

---

## Schema lock (v2.5 — non-negotiable)

Machine contract: `docs/sites/data/schema/day.schema.json` + `week.schema.json`.
Human map: `docs/sites/data/schema/README.md`.
Golden **report shape**: `docs/sites/data/2026-09/week-38.json` `days[].report` (do not copy week-38 as the publish unit).

Day file (publish unit, target ≤ 25 KB pretty / ~18 KB minified):

```json
{
  "schemaVersion": "1.0.0",
  "date": "YYYY-MM-DD",
  "report": {},
  "sources": { "schemaVersion": "1.0.0", "sources": [] }
}
```

Thin week index (`schemaVersion: "2.1.0"`, `storage: "day-shards"`):

```json
{
  "schemaVersion": "2.1.0",
  "yearMonth": "2026-09",
  "week": { "isoYear": 2026, "isoWeek": 39, "id": "2026-W39", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "updatedAt": "ISO-8601+07:00",
  "storage": "day-shards",
  "days": [{ "date": "YYYY-MM-DD", "dayPath": "2026-09/d/YYYY-MM-DD.json", "status": "closed" }]
}
```

Each `report` keeps `schemaVersion: "1.0.0"` and **exactly** these keys:

`schemaVersion`, `id`, `type` (`daily_market_brief`), `locale` (`vi-VN`), `timezone` (`Asia/Ho_Chi_Minh`), `generatedAt`, `coverage`, `marketSession`, `disclaimer`, `ui`, `snapshot`, `globalNews`, `vietnamNews`, `vietnamMacro`, `equityMarket`, `worldMarkets`, `cryptoMarkets`, `companies`, `outlook`, `series`

Hard rules:

- `outlook` is an **object** `{ watchpoints, levels, events }`. Never an array.
- `series` must include all ten ids: `vnindex`, `dji`, `ndx`, `spx`, `dxy`, `nky`, `hsi`, `btcUsd`, `vnindexVolume5d`, `foreignNet5dVndBn`.
- Numbers are JSON numbers. Missing print = `null` + `note`. Never invent an official close.
- Visible strings are Vietnamese with diacritics. Keys stay English.
- Do not add keys outside the schema (`category`, `region`, `tags`, `asOf`, `venue`, `outlook` as list).
- Each news item must have a clickable source in `url` and/or `id` (http/https). `report-app.js` uses `resolveNewsUrl`.
- UTF-8 only. Never strip Vietnamese diacritics (`ệ`, `ư`, `ả`) in JSON or JS chrome.

### JSON formatting

- 2-space indentation (`JSON.stringify(..., null, 2)` / Prettier), matching `week-38.json`.
- Single space after colon: `"key": "value"`, never `"key":  "value"`.
- Ban PowerShell `ConvertTo-Json` artifacts: no 40+ space depth, no `\u0026` / `\u0027` / `\u003c` / `\u003e` entity escaping.

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
| `sources.sources` | 4 | 32 |
| line series `points` | 2 | 40 |

Required snapshot symbols: `VNINDEX`, `HNX`, `DXY`, `DJI`, `NDX`, `SPX`, `NKY`, `HSI`, `WTI`, `XAU`, `BTC`, plus `USDVND` when available.
World board: `DXY`, `DJI`, `NDX`, `SPX`, `RUT`, `FTSE`, `NKY`, `HSI` (drop RUT/FTSE only if missing, keep ≥6).
Crypto board: `BTC`, `ETH`.

Cap string lengths. Omit `image` unless there is a real thumbnail. Do not paste articles. Do not dump dense intraday ticks.

### Binding (must keep working)

`index.html` → `data/index.json` → prefer `reports[].dayPath` → else `weekPath` + `days[date]` (legacy week-38 embedded).
`report-app.js` `resolveDay()` loads `./data/{dayPath}`. Renaming a key breaks the dashboard.

Catalog (`data/index.json`): `schemaVersion: "2.0.0"`, `layout: "monthly-weekly"`, reports newest-first with `weekId`, `weekPath`, `dayPath`, `path: "index.html#/YYYY-MM-DD"`.

Routes: `#/` and `#/latest` open the newest brief (`#/YYYY-MM-DD`). Header calendar lists catalog dates only.

---

## Publish (every run)

1. Compute ISO week (Monday start) and today’s date in `Asia/Ho_Chi_Minh`.
2. Collect data (sources-first, below). Build the day payload. Validate with `schema-validate.js` `validateDayFile`.
3. Write **only** `docs/sites/data/YYYY-MM/d/YYYY-MM-DD.json`.
4. Fetch existing thin `docs/sites/data/YYYY-MM/week-WW.json`. If it is still an embedded v2.0 blob, convert to `schemaVersion: "2.1.0"` / `storage: "day-shards"` **without deleting sibling dates**. Upsert today’s `{date, dayPath, status}` pointer. Never put `report` back into the week file. Never replace `days` with `[todayOnly]`.
5. Upsert `docs/sites/data/index.json` newest-first with `weekPath` + `dayPath`.
6. Push those files on `project-website-pages` (one commit if possible; split only for MCP size).
7. Spot-check UTF-8 (`ệ` / `ư` / `ả`) in the **day** JSON. Confirm the commit SHA is on `project-website-pages`.
8. Do not create a new dashboard HTML.

`week-38.json` stays embedded (legacy). New weeks use day shards.

---

## Data sources (sources-first)

Load `docs/sites/data/sources.json` as the canonical registry (`src-*` ids, URLs, categories, reliability).

Priority:

1. **Direct fetch** of registered URLs (`reliability: "primary"` first).
2. **Domain-constrained search** on registered domains (`site:cafef.vn`, `site:vietstock.vn`, `site:sbv.gov.vn`, `site:gso.gov.vn` / `site:nso.gov.vn`, `site:vneconomy.vn`, `site:barrons.com`, `site:bloomberg.com`).
3. **Unconstrained search** only if a registered source is unreachable or lacks a breaking item. Attribute every item to a real source in `sources.sources[]` with today’s `accessedAt`.

Categories in `sources.json`:

- Vietnam market / indices: CafeF, Vietstock, StockBiz, 24hMoney, Yahoo VN.
- Vietnam macro / policy: SBV/NHNN, NSO/GSO, VnEconomy, VietnamBiz.
- Global / commodities / crypto: Barron’s, Bloomberg Asia, Yahoo BTC.

Do not invent official HOSE prints. Every quote, news item, company item, and macro metric must have a valid `sourceId` mirrored in `sources.sources[]`.

---

## Automation prompt (keep in sync)

The Grok automation named **Market daily brief** must contain only this text (plus the schedule). All operating rules live above.

```text
Load and follow docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md
from repo d-dragon/dp-stock-investment-assistant
branch project-website-pages (ref refs/heads/project-website-pages).

That file is the only spec. Do not invent a parallel workflow from chat history
or from a previous automation prompt.

Then run today's daily market brief for Asia/Ho_Chi_Minh exactly as the file
instructs (day-shard publish, thin week pointer, catalog upsert, sources-first,
schema + UTF-8 checks). Report the project-website-pages commit SHA or the blocker.
```
