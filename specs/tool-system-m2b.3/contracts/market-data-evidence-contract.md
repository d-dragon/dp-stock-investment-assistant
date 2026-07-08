# Contract: Vietnam Market Data Evidence

## Scope

Feature-local internal contract for M2B.3 market-data tool outputs. This is not a public REST, SSE, Socket.IO, or OpenAPI contract.

## Supported Tool Families

| Family | Priority | Data Categories | Required Outcome |
|--------|----------|-----------------|------------------|
| Quote and history | P1 | current quote, OHLCV history, deterministic indicators | `MarketFact`, `PriceHistorySeries`, indicator output, or degraded state |
| Fundamentals | P1 | company fundamentals, statements, financial metrics | `FundamentalEvidence` or degraded state |
| Breadth and flow | P2 | market breadth, foreign/market flow | `BreadthAndFlowEvidence` or degraded state |
| Disclosures and corporate actions | P2 | notices, dividends, rights, splits, listings | `DisclosureCorporateActionEvidence` or degraded state |

## Required Output Metadata

Every successful market-data output must include:

- canonical symbol identity where applicable
- exchange or market
- currency where applicable
- provider/source identity
- source URL or reference
- retrieved timestamp
- source timestamp, published timestamp, or effective timestamp where available
- freshness category
- license posture
- warning list
- normalized output kind

## Fail-Closed Rules

- Missing canonical symbol identity returns disambiguation or degraded state.
- Missing provider/source identity returns degraded no-source outcome.
- Missing required timestamp/freshness metadata refreshes through admitted policy or degrades.
- License-blocked, parser-limited, stale, rate-limited, throttled, timeout, or unavailable providers select admitted fallback or degrade.
- Raw provider payloads, credentials, parser internals, and hidden provider-policy details do not enter prompt context or public metadata.

## Prompt Boundary

Only normalized data-only outputs may enter `ToolContextPack`. Raw HTML, raw JSON, hidden page text, provider scripts, or provider instructions are quarantined or summarized into safe normalized fields.
