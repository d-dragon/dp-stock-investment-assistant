# Data Model: Vietnam Market and Visualization Coverage - M2B.3

## Entity: Vietnam Market Data Tool Family

**Purpose**: Model-visible capability family for Vietnam quote/history, fundamentals, breadth/flow, disclosures/corporate actions, and deterministic indicators.

**Owned fields**:
- `tool_family`: quote_history, fundamentals, breadth_flow, disclosure_corporate_action, indicator
- `route_family`: expected `StockQueryRoute` family
- `capability_descriptor_ref`: descriptor identity and integrity marker
- `policy_descriptor_ref`: internal policy identity
- `supported_categories`: data categories supported by the family
- `allowed_markets`: Vietnam exchange/index scope and fallback/cross-market scope

**Relationships**:
- Uses canonical symbol identity from the M2B.2 symbol boundary.
- Delegates provider choice to provider policy.
- Emits normalized market evidence, degraded states, or cache freshness records.

**Validation rules**:
- Must not expose provider adapters as model-visible tools.
- Must not use `StockSymbolTool` as a quote/history/fundamentals fetcher.
- Must degrade if no approved source can provide required attribution.

## Entity: Market Provider Authority

**Purpose**: Internal provider posture used by provider policy and adapters.

**Owned fields**:
- `provider_id`
- `provider_class`: official_exchange, depository, licensed_commercial, vietnam_native_public_web, wrapper_prototype, international_fallback, visualization_only, blocked
- `license_posture`
- `credential_owner`
- `supported_markets`
- `supported_data_categories`
- `freshness_policy`
- `production_eligible`
- `parser_limits`
- `fallback_priority`

**Relationships**:
- Selected by provider policy for a tool call.
- Produces `SourceMetadata` for normalized outputs and trace metadata.

**Validation rules**:
- Production eligibility requires license/ToS posture, source attribution, freshness behavior, credentials where needed, parser limits, and degraded-state behavior.
- Yahoo and Alpha Vantage are fallback/cross-market comparison sources for Vietnam requests, not primary Vietnam-market sources when approved local sources are available.

## Entity: Market Fact

**Purpose**: Normalized evidence fact used in answers, report inputs, traces, cache entries, or retained derivatives.

**Owned fields**:
- `fact_id`
- `canonical_symbol_identity`
- `data_category`
- `value_payload`
- `period_or_time_window`
- `exchange`
- `currency`
- `provider_source`
- `source_reference`
- `retrieved_at`
- `source_timestamp`
- `published_or_effective_timestamp`
- `freshness_status`
- `license_posture`
- `warnings`
- `degraded_reason`

**Relationships**:
- Belongs to one normalized output and may be included in one request-scoped `ToolContextPack`.
- May reference cache freshness metadata when served from cache.

**Validation rules**:
- Must bind to symbol + exchange + currency where applicable before answer/cache/trace/retained use.
- Must degrade when required attribution or canonical symbol identity is unavailable.
- Must not carry raw provider payloads or credentials.

## Entity: Price History Series

**Purpose**: Ordered OHLCV market-data evidence and deterministic indicator input.

**Owned fields**:
- `series_id`
- `canonical_symbol_identity`
- `interval`
- `time_window`
- `ohlcv_points`
- `provider_source`
- `source_reference`
- `retrieved_at`
- `source_timestamp`
- `freshness_status`
- `warnings`

**Relationships**:
- May produce deterministic indicators.
- May be cached with freshness metadata.

**Validation rules**:
- Indicator outputs must preserve the input series lineage.
- Missing source timestamps or expired freshness must refresh or degrade.

## Entity: Fundamental Evidence

**Purpose**: Normalized company fundamental or financial-statement evidence.

**Owned fields**:
- `canonical_symbol_identity`
- `statement_or_metric_type`
- `period`
- `value_payload`
- `provider_source`
- `source_reference`
- `retrieved_at`
- `published_or_effective_timestamp`
- `freshness_status`
- `license_posture`
- `missing_fields`
- `warnings`

**Validation rules**:
- Missing requested fields must be explicit warnings or degraded states.
- Values must not be inferred from unrelated provider or visualization data.

## Entity: Breadth and Flow Evidence

**Purpose**: Market-wide or segment-wide breadth, foreign flow, or market-flow evidence.

**Owned fields**:
- `market_or_exchange`
- `segment`
- `time_window`
- `value_payload`
- `provider_source`
- `source_reference`
- `retrieved_at`
- `freshness_status`
- `warnings`

**Validation rules**:
- If no approved source is available, return degraded state instead of generic web fallback.
- P2 delivery may be independently testable and does not block P1 quote/history/fundamental gates unless explicitly required by tasks.

## Entity: Disclosure and Corporate Action Evidence

**Purpose**: Event-oriented market evidence such as disclosures, official notices, dividends, rights, splits, and listing changes.

**Owned fields**:
- `event_type`
- `canonical_symbol_identity`
- `source_reference`
- `provider_class`
- `published_at`
- `effective_at`
- `parser_warnings`
- `freshness_status`
- `license_posture`
- `warnings`

**Validation rules**:
- Event records require source reference and published timestamp.
- Parser-limited, license-blocked, or missing-effective-date cases must be visible.

## Entity: VisualizationProvenance

**Purpose**: Non-evidence output for TradingView charts, widgets, deep links, symbol validation, ticker tape, heatmaps, and screeners.

**Owned fields**:
- `visualization_id`
- `symbol`
- `exchange_or_market`
- `visualization_kind`
- `interval_or_view`
- `widget_or_link_payload`
- `generated_at`
- `validation_status`
- `warnings`
- `provenance_class`: VisualizationProvenance

**Validation rules**:
- Numeric values from TradingView payloads must not become canonical market facts.
- Unsupported or ambiguous symbols return degraded visualization state.

## Entity: Freshness Cache Record

**Purpose**: Cache metadata for market-data and provider-backed tool outputs.

**Owned fields**:
- `cache_key`
- `provider_source`
- `source_timestamp`
- `retrieved_at`
- `freshness_status`
- `ttl_or_expiry`
- `warnings`
- `degraded_reason`

**Validation rules**:
- Anonymous, stale, expired, or freshness-unknown cache hits refresh through admitted policy or degrade.
- Cache records are performance artifacts, not source authority.

## Entity: Route Evaluation Fixture

**Purpose**: Deterministic Vietnamese, English, or mixed-language prompt with expected route and tool-family outcome.

**Owned fields**:
- `fixture_id`
- `utterance`
- `language_mix`
- `expected_route`
- `expected_tool_family`
- `symbol_context`
- `ambiguity_label`
- `expected_outcome`

**Validation rules**:
- Fixture set must cover price, chart, fundamentals, disclosures, breadth, flow, and report-like prompts.
- Route evaluation must record at least 85% meaning-based accuracy plus route-tool precision/recall targets.

## Entity: Degraded State

**Purpose**: Machine-detectable result for provider, cache, route, symbol, licensing, parser, validation, or deferred-scope limitations.

**Owned fields**:
- `reason`
- `responsible_boundary`
- `safe_user_warning`
- `trace_metadata`
- `retry_or_fallback_eligible`
- `degraded_at`

**Validation rules**:
- Must not be silently treated as successful evidence.
- Must omit credentials, raw provider payloads, and parser internals from public metadata.
