# Contract: Internal Symbol Normalization

## Purpose

Define how M2B.2 evolves `StockSymbolTool` toward internal symbol-store lookup and normalization without making it the owner of live market-data facts.

## Inputs

- User query route from the existing stock query classifier.
- Symbol lookup, search, list, alias, identifier, coverage, tag, and stored metadata request.
- Optional exchange, market, locale, and currency hints.

## Admitted Outputs

- `SystemRecord` normalized output for a resolved internal symbol record.
- `DegradedState` when the request is ambiguous, missing, unsupported, stale, or invalid.
- `ToolExecutionEnvelope` wrapping either output.

## Required Behavior

- Resolve symbol identity using at least symbol, exchange, and currency where applicable.
- Normalize ticker-only ambiguity before prompt assembly.
- Include aliases, identifiers, coverage, tags, listing context, and stored snapshot metadata where available.
- Keep live quote, history, and fundamental retrieval outside the evolved `StockSymbolTool`.
- Treat Yahoo, YahooFinance, and DataManager-style live market access as non-target paths for this tool.

## Blocked Behavior

- No direct model-visible provider list.
- No raw provider payload in normalized output.
- No production symbol-store write behavior in M2B.2.
- No claim that stored symbol metadata is live market evidence.

## Failure Contract

| Condition | Result |
|-----------|--------|
| Ambiguous ticker without exchange/currency resolution | `DegradedState` |
| Missing symbol record | `DegradedState` |
| Request asks for live quote/history/fundamentals | Route or degrade to downstream market-data capability, not `StockSymbolTool` ownership |
| Write action requested | Disabled mutation receipt or degraded mutation outcome |

## Verification Expectations

- Fixtures cover Vietnam symbols and indexes.
- Ambiguous ticker fixtures degrade instead of silently choosing a record.
- Live market-data requests are not executed by `StockSymbolTool`.
- Outputs classify as `SystemRecord` or `DegradedState`.
