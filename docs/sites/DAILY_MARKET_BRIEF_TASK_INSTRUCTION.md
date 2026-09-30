# Daily Market Brief — Task Instruction

**Status:** living document — this file is the source of truth. Chat history and the Grok automation prompt must not invent a parallel spec.
**Version:** 2.6.1
**Updated:** 2026-09-30 (GMT+7)
**Owner:** Phan Duy / DP Stock-Investment Assistant
**Canonical path:** `docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md` on branch `project-website-pages`
**Automation:** `Market daily brief` (`fc7b3b17-89d9-4107-a578-b4ce780a2911`) — the automation prompt only loads and follows this file.

**Proven:** v2.0 Pages JSON bind 2026-09-18. v2.1 dashboard. v2.1.1 UTF-8 + Be Vietnam Pro. v2.2 monthly/weekly + hash hub. v2.3 schema lock (golden `week-38.json`). v2.3.1–2.3.4 sources.json, news URLs, Prettier JSON, sources-first. v2.4 day shards after MCP could not push a fat week-39. v2.5 consolidates the live automation guardrails into this file. v2.5.1: day file MUST go through `gh api` Contents PUT (not MCP content=), never commit stubs. v2.6.0: raw + ranked news file + same-job analysis; no 25 KB news cap; newf319 sentiment; Phase 1 = Grok automation + git/`gh` only.

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
| 2026-09-30 | 2.6.1 | Analysis MD is a narrative investor note (coverage + takeaways). Hub right pane tab **Phân tích** renders `a/YYYY-MM-DD.md`. Catalog `analysisPath`. |
| 2026-09-30 | 2.6.0 | Phase 1 collector on this automation + git/`gh` only (no Grok bot). One 08:35 window = prior EOD + overnight + pre-open. Raw one-file + `n/` ranked feed (no 25 KB cap) + same-job `a/*.md`. Sentiment: FireAnt, F247, newf319.com (not f319.com). Loader scrolls impact-sorted feeds. |
| 2026-09-30 | 2.5.1 | Day-file transport: `gh api` PUT Contents from a local file. Ban stub/placeholder commits. Verify remote `size` == local bytes. MCP only for thin week + catalog. |
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

- Target **one Git commit per routine run** when possible. In practice: **day file via `gh api`**, then thin week + catalog via MCP if they stay small.
- Assemble the day JSON **on disk first**. Never paste the day body into MCP `create_or_update_file` / `push_files` `content` — that envelope truncates (~30–40 KB tool JSON) and produced the 2026-09-30 stubs (`see-local`, empty arrays).
- If a write fails, STOP and report. **Never** commit a placeholder, skeleton schema, stripped-diacritic draft, or `see-local` so the path exists.
- After every day PUT: remote `content.size` MUST equal local `wc -c`. If not, treat the commit as invalid.
- Commit message: `Publish daily market brief YYYY-MM-DD (dashboard v2.6 feed+shard)`.

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
  data/schema/news.schema.json          # ranked feed file
  data/YYYY-MM/week-WW.json             # thin index when schemaVersion=2.1.0
  data/YYYY-MM/d/YYYY-MM-DD.json        # tape + outlook + short news fallback
  data/YYYY-MM/n/YYYY-MM-DD.json        # full impact-ranked news + feeds
  data/YYYY-MM/raw/YYYY-MM-DD.json      # optional one-file raw (market/news_events/sentiment)
  data/YYYY-MM/a/YYYY-MM-DD.md          # same-job analysis / narrative
```

Do **not** create `data/YYYY-MM-DD/` folders or a new `YYYY-MM-DD.html` dashboard.
Do **not** embed today’s report inside `week-WW.json`.
Hub loader (`report-app.js`) prefers `catalog.newsPath` for the scrollable news list.

---

## Schema lock (v2.6 — non-negotiable)

Machine contract: `docs/sites/data/schema/day.schema.json` + `week.schema.json` + `news.schema.json`.
Human map: `docs/sites/data/schema/README.md`.
Golden **report shape**: `docs/sites/data/2026-09/week-38.json` `days[].report` (do not copy week-38 as the publish unit).

Day file (`d/`, tape + outlook; keep compact):

```json
{
  "schemaVersion": "1.0.0",
  "date": "YYYY-MM-DD",
  "newsPath": "2026-09/n/YYYY-MM-DD.json",
  "report": {},
  "sources": { "schemaVersion": "1.0.0", "sources": [] }
}
```

There is **no 25 KB product cap on news/feeds**. Put the long ranked list in `n/YYYY-MM-DD.json`. Soft engineering warning only: keep any one JSON under ~1 MB.

Thin week index (`schemaVersion: "2.1.0"`, `storage: "day-shards"`):

```json
{
  "schemaVersion": "2.1.0",
  "yearMonth": "2026-09",
  "week": { "isoYear": 2026, "isoWeek": 39, "id": "2026-W39", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
  "updatedAt": "ISO-8601+07:00",
  "storage": "day-shards",
  "days": [{ "date": "YYYY-MM-DD", "dayPath": "2026-09/d/YYYY-MM-DD.json", "newsPath": "2026-09/n/YYYY-MM-DD.json", "status": "preopen" }]
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
| `globalNews` / `vietnamNews` fallback inside `d/` | 8 | 12 |
| Ranked feed `n/*.json` `items` | 8 | none (collect as many as sources yield) |
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

Cap string lengths in the **day shard**. The feed file may keep a short `excerpt` per item. Omit `image` unless there is a real thumbnail. Do not dump dense intraday ticks.

### Binding (must keep working)

`index.html` → `data/index.json` → `reports[].dayPath` + optional `newsPath`.
`report-app.js` `resolveDay()` loads `./data/{dayPath}`; `attachNewsFeed()` loads `./data/{newsPath}` or `YYYY-MM/n/YYYY-MM-DD.json` and sorts by `impactScore`.

Catalog (`data/index.json`): `schemaVersion: "2.0.0"`, `layout: "monthly-weekly"`, reports newest-first with `weekId`, `weekPath`, `dayPath`, optional `newsPath`, `path: "index.html#/YYYY-MM-DD"`.

Routes: `#/` and `#/latest` open the newest brief (`#/YYYY-MM-DD`). Header calendar lists catalog dates only.

---

## Phase 1 collector (Grok automation + git/`gh` only)

Do **not** use a separate Grok bot, DataFeed API, Vietstock login, Drive, or Gist in this phase.

**Clock:** one run at 08:35 Asia/Ho_Chi_Minh.

- `briefDate` = calendar D
- `eodDate` = last completed session (usually D−1, skip weekend)
- `briefKind` = `eod_prev+overnight+preopen`
- `marketSession` / catalog `status` = `preopen` unless an official D close already exists
- Never invent today’s HOSE close. Label prior close vs pre-open.

**Pipeline**

1. Load this file + schemas + `sources.json` + catalog + yesterday shard.
2. Collect public sources only (Vietstock public pages + RSS, CafeF, Yahoo, SBV/NSO when relevant).
3. Sample public community threads: FireAnt, F247, **https://newf319.com/**. Do not use shutdown `f319.com`. Sentiment is color, not a print.
4. Write one raw file `data/YYYY-MM/raw/YYYY-MM-DD.json` with objects `market`, `news_events`, `sentiment`, `gaps`.
5. Rank every usable headline/feed item by impact (`high` / `medium` / `low` + `impactScore` 0–100). Heuristic: official prints and exchange actions first; VN30 / foreign-flow extremes; overnight US/Asia gap risk; sector-wide stories; single-name color; community last.
6. Write the full ranked list to `data/YYYY-MM/n/YYYY-MM-DD.json` (`news.schema.json`). No 25 KB cap.
7. Compose `d/YYYY-MM-DD.json` (schema-locked report). Keep a short news fallback inside `d/` so the hub still works if `n/` is late.
8. Write `a/YYYY-MM-DD.md` in the **same** run using the **Analysis note** template below.
9. Upsert thin week + catalog with `dayPath`, `newsPath`, and `analysisPath`.
10. Publish large files with `gh` / git — never MCP `content=`.

**Feed item**

```json
{
  "id": "n-YYYY-MM-DD-001",
  "impact": "high",
  "impactScore": 86,
  "rank": 1,
  "kind": "news",
  "board": "vn",
  "title": "",
  "url": "https://...",
  "sourceId": "src-vietstock",
  "publishedAt": "2026-09-30T07:12:00+07:00",
  "tickers": ["VCB"],
  "excerpt": "",
  "whyImpact": ""
}
```

`kind`: `news` | `disclosure` | `macro` | `market` | `community`. Community rows must stay labeled.

## Analysis note (`a/YYYY-MM-DD.md`)

This file is the **reasoner output** the hub tab **Phân tích** renders. Vietnamese, diacritics on. 500–900 words. Not a bullet dump of the shard. Do not invent a close. Cite `sourceId` or outlet in prose.

**Required sections (use these headings):**

```markdown
# Nhật ký phiên YYYY-MM-DD — [một câu thesis]

**Cửa sổ:** EOD {eodDate} + overnight + pre-open {briefDate} (GMT+7).
**Thesis:** [1–2 sentences: what the tape is saying and what would invalidate it]

## Nhà đầu tư nắm gì
- [3–5 grab-able insights: bias for the session, sectors/tickers in play, risk that would change the plan]
- Mỗi ý: hành động hoặc quan sát được, không khẩu hiệu.

## Bức tranh phiên
Narrative 1 short paragraph: index, breadth, liquidity vs 20-session feel, who supplied/demanded.

## Dòng tiền
Foreign / proprietary / retail if known. Name the 3–5 tickers that explain the print. Say what is *not* known.

## Thế giới chồng lên VN
What overnight US/Asia/FX/rates/oil actually transmits to VN today. Skip decoration quotes.

## Sự kiện & cổ phiếu
Rights, floors, weight names, sector tapes that can gap the index.

## Sentiment (không phải print)
FireAnt / F247 / newF319 tone vs the tape. One sentence on agreement or disagreement.

## Kế hoạch phiên
- Kịch bản cơ sở / nghiêng / rủi ro
- Mốc: hỗ trợ — kháng cự (from raw/outlook, labeled)
- Ấn số còn lại (today’s official close if pre-open, scheduled data)
```

**Quality bar**

- Lead with a thesis an investor can use before the open or into the session.
- Cover: tape, liquidity, three investor groups when data exists, overnight transmission, 2–4 names, community only as color.
- Insights must be falsifiable (“mất 1.760 thì bias đổi”, not “thị trường sẽ tăng”).
- No buy/sell order. No invented prints. Community ≠ foreign flow.

Hub: `report-app.js` loads `analysisPath` or `YYYY-MM/a/YYYY-MM-DD.md` into the right-pane tab **Phân tích**. Companies + compact outlook stay on tab **Doanh nghiệp**.

## Publish (every run)

1. Compute ISO week (Monday start) and today’s date in `Asia/Ho_Chi_Minh`.
2. Collect data (sources-first, Phase 1 collector above). Validate `d/` with `schema-validate.js` `validateDayFile`.
3. Write `raw/`, `n/`, `d/`, and `a/` for today.
4. Fetch existing thin `docs/sites/data/YYYY-MM/week-WW.json`. If it is still an embedded v2.0 blob, convert to `schemaVersion: "2.1.0"` / `storage: "day-shards"` **without deleting sibling dates**. Upsert today’s `{date, dayPath, newsPath, status}` pointer. Never put `report` back into the week file. Never replace `days` with `[todayOnly]`.
5. Upsert `docs/sites/data/index.json` newest-first with `weekPath` + `dayPath` + `newsPath` + `analysisPath`.
6. Publish on `project-website-pages` with **`gh` / git** (required for `raw/`, `n/`, `d/`, `a/`):
   1. Assemble files on disk.
   2. Prefer `git add && git commit && git push origin project-website-pages`.
   3. Or `gh api --method PUT repos/.../contents/... --input` from a local payload file.
   4. MCP `create_or_update_file` is allowed **only** for thin week + catalog (a few KB). Never paste `n/` or `raw/` into an MCP `content` field.
7. Spot-check UTF-8 (`ệ` / `ư` / `ả`) in the remote JSON. Confirm commit SHA is on `project-website-pages`.
8. Do not create a new dashboard HTML.

### Day-file transport (`gh api` — required)

GitHub Contents API accepts ~1 MB. Connected MCP tools wrap `content` in a JSON tool call; that envelope failed on 2026-09-30 (local 23347 B valid file became remote 9 B then 1045 B stubs). Official MCP server does not cap file size; the Grok tool-argument packer does.

Required pattern (sandbox `gh` + `GH_TOKEN`):

```bash
REPO=d-dragon/dp-stock-investment-assistant
PATH_IN_REPO=docs/sites/data/YYYY-MM/d/YYYY-MM-DD.json
LOCAL_FILE=/path/to/YYYY-MM-DD.json
SHA=$(gh api "repos/${REPO}/contents/${PATH_IN_REPO}?ref=project-website-pages" --jq .sha || true)
python3 -c 'import base64,json,pathlib,sys; raw=pathlib.Path(sys.argv[1]).read_bytes(); body={"message":sys.argv[2],"content":base64.b64encode(raw).decode(),"branch":"project-website-pages"};
print("local",len(raw)); pathlib.Path("/tmp/put-day.json").write_text(json.dumps(body),encoding="utf-8")' "$LOCAL_FILE" "Publish daily market brief YYYY-MM-DD (dashboard v2.5 day-shard)"
# add sha into /tmp/put-day.json when updating an existing file
gh api --method PUT "repos/${REPO}/contents/${PATH_IN_REPO}" --input /tmp/put-day.json
```

Reject the commit unless returned `content.size` equals local byte length and `snapshot.quotes` length is at least 10.

`week-38.json` stays embedded (legacy). New weeks use day shards.

---

## Data sources (sources-first)

Load `docs/sites/data/sources.json` as the canonical registry (`src-*` ids, URLs, categories, reliability).

Priority:

1. **Direct fetch** of registered URLs (`reliability: "primary"` first).
2. **Domain-constrained search** on registered domains (`site:cafef.vn`, `site:vietstock.vn`, `site:finance.vietstock.vn`, `site:sbv.gov.vn`, `site:gso.gov.vn` / `site:nso.gov.vn`, `site:vneconomy.vn`, `site:barrons.com`, `site:bloomberg.com`, `site:fireant.vn`, `site:newf319.com`).
3. **Unconstrained search** only if a registered source is unreachable or lacks a breaking item. Attribute every item to a real source in `sources.sources[]` with today’s `accessedAt`.

Categories in `sources.json`:

- Vietnam market / indices: CafeF, Vietstock, StockBiz, 24hMoney, Yahoo VN.
- Vietnam macro / policy: SBV/NHNN, NSO/GSO, VnEconomy, VietnamBiz.
- Global / commodities / crypto: Barron’s, Bloomberg Asia, Yahoo BTC.
- Community sentiment (not prints): FireAnt, F247, **newF319** (`https://newf319.com/`).

Do not invent official HOSE prints. Every quote, news item, company item, and macro metric must have a valid `sourceId` mirrored in `sources.sources[]`. Community items use `src-fireant` / `src-f247` / `src-newf319` and `kind: "community"`.

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
instructs (Phase 1 collector, ranked n/ feed, day-shard, analysis md,
thin week pointer, catalog upsert, sources-first, gh/git publish,
schema + UTF-8 checks). Report the project-website-pages commit SHA or the blocker.
```
