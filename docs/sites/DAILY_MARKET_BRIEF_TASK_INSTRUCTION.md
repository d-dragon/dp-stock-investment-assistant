# Daily Market Brief — Task Instruction

**Status:** living document — edit this file; do not treat chat history as the source of truth  
**Version:** 2.2.0  
**Updated:** 2026-09-21 (GMT+7)  
**Owner:** Phan Duy / DP Stock-Investment Assistant  
**Canonical path in repo:** `docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md` on branch `project-website-pages`  
**Proven:** v2.0.0 ran 2026-09-18 on GitHub Pages. v2.1.0 dashboard rendered the same day. v2.1.1 restores UTF-8 Vietnamese + Be Vietnam Pro after ASCII-stripped chrome/news on Pages. v2.2.1 migrates to monthly/weekly JSON + hash-routed single `index.html`.

---

## How to use this file

1. Daily automation MUST load this file from GitHub first (`get_file_contents` on this path, ref `refs/heads/project-website-pages`).
2. After each run, log gaps in **Changelog** and tighten the contract here.
3. Do not put market numbers in this file. Numbers live in weekly day payloads under `docs/sites/data/YYYY-MM/week-WW.json` → `days[].report`.

---

## Changelog

| Date | Version | Change |
|---|---|---|
| 2026-09-21 | 2.2.0 | Data layout: monthly folders + weekly JSON (`days[]` with report+sources). Catalog `schemaVersion` 2.0.0, `layout: monthly-weekly`. Single hub `index.html` with hash routes `#/` and `#/YYYY-MM-DD`. Daily HTML files become redirect stubs. Publish upserts into week file; do **not** create new `YYYY-MM-DD.html` dashboards. |
| 2026-09-20 | 2.1.1-run4 | Weekend brief 08:36 GMT+7. HOSE đóng cửa Chủ nhật; snapshot VN lấy 18/9. Tin mới: Vanguard ~2,5 tỷ USD; UNGA Trump–GCC 22/9. Chuỗi VN-Index đủ 14–18/9. Gaps: tự doanh/cá nhân vẫn null; KLGD 15–17/9 vẫn null; NDX trên ticker là Nasdaq Composite (đồng nhất schema cũ), không phải Nasdaq-100. |
| 2026-09-19 | 2.1.1-run3 | Weekend brief 08:36 GMT+7. HOSE đóng cửa cuối tuần; snapshot VN lấy 18/9. Bổ sung bảng ngoại theo mã (PNJ/HPG/VIC). Gaps: tự doanh/cá nhân vẫn null; chuỗi VN-Index 5D chỉ 17–18/9; KLGD 17/9 vẫn null; NDX trên ticker là Nasdaq Composite (đồng nhất schema cũ), không phải Nasdaq-100. |
| 2026-09-18 | 2.1.1-run2 | Closed-session refresh 16:54 GMT+7. Restored UTF-8 chrome in `report-app.js` (`đã đóng cửa`, `thị trường`, `Vĩ mô Việt Nam`). Gaps: tự doanh/cá nhân null; chuỗi VN-Index 5D chỉ 17–18/9; foreign buy/sell chi tiết chưa có bảng tổng hợp mới. |
| 2026-09-18 | 2.1.1 | UTF-8 mandatory. Never strip Vietnamese diacritics when pushing JS/JSON. Load Be Vietnam Pro. Daily automation must fetch this file from the repo before running. |
| 2026-09-18 | 2.1.0 | Multi-pane dashboard. Vietnamese UI. Paginated news + impact. Chart tabs VN-Index / World / Crypto. No TradingView HOSE:VNINDEX. |
| 2026-09-18 | 2.0.0 | Split HTML into template + CSS/JS. |
| 2026-09-18 | 1.0.0 | Monolithic HTML brief. |

---

## Role

Financial research analyst + front-end engineer. Produce a GitHub Pages daily market brief by separating: reusable multi-pane dashboard UI, persistence-ready JSON, thin hash-routed hub that binds weekly JSON. Do not ship a monolithic HTML file with hardcoded numbers.

## Mission

For today in Asia/Ho_Chi_Minh collect: global news + impact, Vietnam macro news + impact, VN-Index/volume/value/foreign/proprietary/retail, world + crypto series, listed-company events, outlook.

## Repository

- Repo: `https://github.com/d-dragon/dp-stock-investment-assistant`
- Branch: `project-website-pages`
- Pages root: `docs/`
- Daily hub (only primary page): `docs/sites/index.html`

## Target site structure

```text
docs/sites/
  DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md   # this living spec
  index.html                               # hub + day dashboards (hash routing)
  assets/css/report.css
  assets/js/report-app.js
  assets/js/schema-validate.js
  templates/daily-report.html              # reference notes only
  data/index.json                          # catalog schemaVersion 2.0.0
  data/YYYY-MM/week-WW.json                # ISO week, zero-padded
  YYYY-MM-DD.html                          # redirect stub → index.html#/YYYY-MM-DD (bookmarks only)
```

Legacy `bao-cao-*.html` monoliths stay in place; do not delete.

### Weekly file shape (`data/YYYY-MM/week-WW.json`)

```json
{
  "schemaVersion": "2.0.0",
  "yearMonth": "2026-09",
  "week": {
    "isoYear": 2026,
    "isoWeek": 38,
    "id": "2026-W38",
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD"
  },
  "updatedAt": "ISO-8601+07:00",
  "days": [
    {
      "date": "2026-09-18",
      "report": { },
      "sources": { }
    }
  ]
}
```

ISO weeks (Monday start). Upsert: on daily publish, open or create the week file and replace/insert the matching `days[]` entry.

### Catalog (`data/index.json`)

```json
{
  "schemaVersion": "2.0.0",
  "updatedAt": "…",
  "layout": "monthly-weekly",
  "reports": [
    {
      "id": "daily-brief-2026-09-18",
      "date": "2026-09-18",
      "title": "…",
      "status": "closed|preopen|intraday",
      "weekId": "2026-W38",
      "weekPath": "2026-09/week-38.json",
      "path": "index.html#/2026-09-18"
    }
  ]
}
```

Sort `reports` newest-first.

## Routing / UI

- `#/` or empty hash → hub (fetch `./data/index.json`, list → `#/YYYY-MM-DD`).
- `#/YYYY-MM-DD` → resolve catalog entry → fetch `./data/{weekPath}` → find `days[]` → render multi-pane v2.1 dashboard from that day's `report` + `sources`.
- Cache weekly JSON in memory when navigating days in the same week.
- Cache-bust `report-app.js` query param when shipping JS changes (e.g. `?v=20260921w`).

## Layout

Dense multi-pane dashboard (not stacked cards). Vietnamese visible copy, English JSON keys.
Required panes: Header; KPI ticker; Tin thế giới; Vĩ mô Việt Nam; Biểu đồ tabs (VN-Index | Thế giới | Crypto); Doanh nghiệp; Triển vọng; Footer.
News = inner scroll + pagination. Charts = Chart.js from JSON. Never embed TradingView `?symbol=HOSE:VNINDEX`.
Webfont required: Google Fonts Be Vietnam Pro + Noto Sans / IBM Plex Sans fallback. charset=UTF-8.

## Honesty / UTF-8

Visible strings must keep Vietnamese diacritics (`Bản tin`, `đã đóng cửa`, `thế giới`). After every push, spot-check that `report.json` day payloads and `report-app.js` still contain `ệ` / `ư` / `ả`. Missing numbers = null + note. Impact is reasoning, not a buy/sell call.

## JSON contract (required top-level inside each day's `report`)

schemaVersion, id, type=daily_market_brief, locale=vi-VN, timezone=Asia/Ho_Chi_Minh, generatedAt, coverage, marketSession, disclaimer, ui, snapshot, globalNews, vietnamNews, vietnamMacro, equityMarket, worldMarkets, cryptoMarkets, companies, outlook, series.
Every news/company/outlook item has impact{direction,horizon,assets,text}. Series include vnindex, world 1Y ids, btcUsd, vnindexVolume5d, foreignNet5dVndBn.

## Publish

1. Compute ISO week for today → `data/YYYY-MM/week-WW.json` (create month folder + week file if missing).
2. Upsert `days[]` entry `{ date, report, sources }` (full previous report.json + sources.json objects).
3. Update `data/index.json` catalog entry (weekId, weekPath, path=`index.html#/YYYY-MM-DD`, status, title). Newest-first.
4. Do **NOT** create a new `YYYY-MM-DD.html` dashboard. Hub is always `index.html`. Optional: leave/refresh a tiny redirect stub for old bookmarks.
5. Do **NOT** write `data/YYYY-MM-DD/` folders anymore.
6. Commit message example: `Publish daily market brief YYYY-MM-DD (dashboard v2.2 weekly)`. Reply with links, snapshot, gaps. No raw HTML dump in chat.

## Agent prompt

```text
FIRST: load docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md from repo d-dragon/dp-stock-investment-assistant branch project-website-pages (ref refs/heads/project-website-pages). Follow that file (v2.2.0+). Do not invent a parallel spec from chat history.
Output a GitHub Pages daily market brief for TODAY in Asia/Ho_Chi_Minh.
Write weekly files under docs/sites/data/YYYY-MM/week-WW.json (upsert days[]). Update data/index.json. Do not create a new YYYY-MM-DD.html dashboard — hub is index.html with hash routing.
UTF-8 only: never strip Vietnamese diacritics in JS chrome or JSON.
After push, spot-check that "ệ" or "ư" still exists in the week JSON day payload and report-app.js.
```

## Navigation (v2.2.1)

- Sites hub routes: `#/` year list · `#/y/YYYY` · `#/y/YYYY/m/MM` · `#/YYYY-MM-DD` day dashboard · `#/latest` jumps to newest catalog date.
- Docs home (`docs/index.html`) Market card opens `#/latest`. Project Docs opens `docs/explorer/` (filterable tree + markdown viewer). Architecture folder index redirects into the explorer.

## Navigation (v2.2.2)

- No year/month hub. #/ and #/latest open the newest brief (#/YYYY-MM-DD).
- Calendar date picker (header tooltip) lists days that have reports.
- Docs home (docs/index.html) is the landing + file explorer; docs/explorer/ redirects there.

