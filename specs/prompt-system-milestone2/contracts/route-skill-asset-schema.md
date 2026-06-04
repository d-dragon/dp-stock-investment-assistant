# Route-Skill Asset Contract

**Date**: 2026-06-04
**Authority**: TECHNICAL_DESIGN.md §2.3 (ADR taxonomy), ADR-AGENT-003

## Frontmatter Schema

Every route-skill `.md` asset under `src/prompts/skills/routes/` MUST contain YAML frontmatter with the following schema:

```yaml
---
name: <string>                    # Required. Human-readable identifier.
version: <semver>                 # Required. Semantic version string (e.g. "1.0.0").
agent_role: <string>              # Required. Target agent role (e.g. "react_analyst").
route_scope:                      # Required. List of canonical route names.
  - <StockQueryRoute member>      # Must match StockQueryRoute enum exactly.
status: <active|draft|deprecated> # Required. Asset lifecycle status.
variant: <string>                 # Optional. Default "baseline".
locale: <string>                  # Optional. Default "en".
parity_group: <string>            # Optional. Default "".
---
```

## Canonical Route Names

Route names MUST exactly match `StockQueryRoute` enum members (case-sensitive):

| Enum Member | Asset Filename |
|-------------|----------------|
| `PRICE_CHECK` | `src/prompts/skills/routes/price_check.md` |
| `NEWS_ANALYSIS` | `src/prompts/skills/routes/news_analysis.md` |
| `PORTFOLIO` | `src/prompts/skills/routes/portfolio.md` |
| `TECHNICAL_ANALYSIS` | `src/prompts/skills/routes/technical_analysis.md` |
| `FUNDAMENTALS` | `src/prompts/skills/routes/fundamentals.md` |
| `IDEAS` | `src/prompts/skills/routes/ideas.md` |
| `MARKET_WATCH` | `src/prompts/skills/routes/market_watch.md` |
| `GENERAL_CHAT` | `src/prompts/skills/routes/general_chat.md` |

## Content Rules

1. Route-skill content MUST narrow task framing within the route domain.
2. Route-skill content MUST NOT weaken shared policy safety, evidence, or disclosure rules.
3. Route-skill content MUST NOT redefine tool behavior or risk envelopes.
4. Route-skill content MUST NOT contain substitute instructions for missing route skills.
5. Route-skill content SHOULD reference route-specific personas, data sources, and response styles.

## Example

```markdown
---
name: price_check_skill_v1
version: 1.0.0
agent_role: react_analyst
route_scope:
  - PRICE_CHECK
status: active
variant: baseline
locale: en
---

You are a real-time market data specialist. When the user asks about stock prices,
quotes, or market cap:

1. Use the stock_symbol tool to fetch current price data.
2. Present the information in a clear tabular format with symbol, price, change,
   change %, and volume.
3. Include the data source (Yahoo Finance) and timestamp in your response.
4. Do not make price predictions or forward-looking statements based on current
   price movements alone.
5. If the price data shows unusual movement (>5%), note the change factually
   without speculating on causes unless you also retrieve news to support a
   causal statement.
```
