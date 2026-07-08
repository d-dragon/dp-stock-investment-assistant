# Contract: TradingView Visualization Provenance

## Scope

Feature-local internal contract for TradingView chart, widget, deep-link, symbol-validation, ticker-tape, heatmap, and screener outputs.

## Output Classification

Every TradingView output must be classified as `VisualizationProvenance`.

## Required Fields

- symbol
- exchange or market where available
- visualization kind
- interval or view configuration where applicable
- widget payload or deep-link payload
- generated timestamp
- validation status
- warning list
- provenance metadata

## Evidence Boundary

TradingView numeric values, indicators, heatmap rows, or screener values must not be used as canonical market evidence by default. Factual answers must use admitted market-data evidence or return degraded state when no evidence exists.

## Degraded Visualization States

Return degraded visualization state when:

- symbol validation fails
- symbol is ambiguous
- requested visualization kind is unsupported
- required widget or link input is missing
- TradingView output contains numeric data that a caller tries to use as evidence

## Public Surface

Public responses may expose safe visualization links, widget configuration, validation status, and user-facing caveats. Internal provider policy, credentials, parser details, and raw traces remain private.
