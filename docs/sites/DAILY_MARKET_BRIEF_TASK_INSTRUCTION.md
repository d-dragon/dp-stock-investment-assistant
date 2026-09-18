# Daily Market Brief — Task Instruction

**Status:** living document — edit this file; do not treat chat history as the source of truth  
**Version:** 2.1.1  
**Updated:** 2026-09-18 (GMT+7)  
**Owner:** Phan Duy / DP Stock-Investment Assistant  
**Canonical path in repo:** `docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md` on branch `project-website-pages`  
**Proven:** v2.0.0 ran 2026-09-18 on GitHub Pages. v2.1.0 dashboard rendered the same day. v2.1.1 restores UTF-8 Vietnamese + Be Vietnam Pro after ASCII-stripped chrome/news on Pages.

---

## How to use this file

1. Daily automation MUST load this file from GitHub first (`get_file_contents` on this path, ref `refs/heads/project-website-pages`).
2. After each run, log gaps in **Changelog** and tighten the contract here.
3. Do not put market numbers in this file. Numbers live in `docs/sites/data/YYYY-MM-DD/report.json`.

---

## Changelog

| Date | Version | Change |
|---|---|---|
| 2026-09-18 | 2.1.1-run2 | Closed-session refresh 16:54 GMT+7. Restored UTF-8 chrome in `report-app.js` (`đã đóng cửa`, `thị trường`, `Vĩ mô Việt Nam`). Gaps: tự doanh/cá nhân null; chuỗi VN-Index 5D chỉ 17–18/9; foreign buy/sell chi tiết chưa có bảng tổng hợp mới. |
| 2026-09-18 | 2.1.1 | UTF-8 mandatory. Never strip Vietnamese diacritics when pushing JS/JSON. Load Be Vietnam Pro. Daily automation must fetch this file from the repo before running. |
| 2026-09-18 | 2.1.0 | Multi-pane dashboard. Vietnamese UI. Paginated news + impact. Chart tabs VN-Index / World / Crypto. No TradingView HOSE:VNINDEX. |
| 2026-09-18 | 2.0.0 | Split HTML into template + CSS/JS + JSON. |
| 2026-09-18 | 1.0.0 | Monolithic HTML brief. |

---

## Role

Financial research analyst + front-end engineer. Produce a GitHub Pages daily market brief by separating: reusable multi-pane dashboard UI, persistence-ready JSON, thin HTML that binds JSON. Do not ship a monolithic HTML file with hardcoded numbers.

## Mission

For today in Asia/Ho_Chi_Minh collect: global news + impact, Vietnam macro news + impact, VN-Index/volume/value/foreign/proprietary/retail, world + crypto series, listed-company events, outlook.

## Repository

- Repo: `https://github.com/d-dragon/dp-stock-investment-assistant`
- Branch: `project-website-pages`
- Pages root: `docs/`
- Daily hub: `docs/sites/index.html`

## Target site structure

```text
docs/sites/
  DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md   # this living spec
  index.html
  assets/css/report.css
  assets/js/report-app.js
  assets/js/schema-validate.js
  templates/daily-report.html
  data/index.json
  data/YYYY-MM-DD/report.json
  data/YYYY-MM-DD/sources.json
  YYYY-MM-DD.html
```

## Layout

Dense multi-pane dashboard (not stacked cards). Vietnamese visible copy, English JSON keys.
Required panes: Header; KPI ticker; Tin thế giới; Vĩ mô Việt Nam; Biểu đồ tabs (VN-Index | Thế giới | Crypto); Doanh nghiệp; Triển vọng; Footer.
News = inner scroll + pagination. Charts = Chart.js from JSON. Never embed TradingView `?symbol=HOSE:VNINDEX`.
Webfont required: Google Fonts Be Vietnam Pro + Noto Sans / IBM Plex Sans fallback. charset=UTF-8.

## Honesty / UTF-8

Visible strings must keep Vietnamese diacritics (`Bản tin`, `đã đóng cửa`, `thế giới`). After every push, spot-check that `report.json` and `report-app.js` still contain ` ệ` / ` ư` / ` ả`. Missing numbers = null + note. Impact is reasoning, not a buy/sell call.

## JSON contract (required top-level)

schemaVersion, id, type=daily_market_brief, locale=vi-VN, timezone=Asia/Ho_Chi_Minh, generatedAt, coverage, marketSession, disclaimer, ui, snapshot, globalNews, vietnamNews, vietnamMacro, equityMarket, worldMarkets, cryptoMarkets, companies, outlook, series.
Every news/company/outlook item has impact{direction,horizon,assets,text}. Series include vnindex, world 1Y ids, btcUsd, vnindexVolume5d, foreignNet5dVndBn.

## Publish

Update data + daily HTML + catalog. Commit: `Publish daily market brief YYYY-MM-DD (dashboard v2.1)`. Reply with links, snapshot, gaps. No raw HTML dump in chat.

## Agent prompt

```text
FIRST: load docs/sites/DAILY_MARKET_BRIEF_TASK_INSTRUCTION.md from repo d-dragon/dp-stock-investment-assistant branch project-website-pages (ref refs/heads/project-website-pages). Follow that file (v2.1.1+). Do not invent a parallel spec from chat history.
Output a GitHub Pages daily market brief for TODAY in Asia/Ho_Chi_Minh.
UTF-8 only: never strip Vietnamese diacritics in JS chrome or JSON.
After push, spot-check that "ệ" or "ư" still exists in report.json and report-app.js.
```
