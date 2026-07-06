# Contract: Provider Policy and Adapter Descriptors

## Purpose

Define internal provider policy contracts below the model-visible tool layer. The model selects tools; deterministic policy selects providers.

## ProviderAdapterDescriptor

Required fields:

- `provider_id`
- `provider_class`
- `supported_markets`
- `supported_data_categories`
- `license_posture`
- `credential_owner`
- `freshness_policy`
- `parser_limits`
- `source_attribution_requirements`
- `production_eligible`
- `integrity_marker`

## ProviderSelectionPolicy

Required fields:

- `tool_name`
- `route`
- `provider_order`
- `fallback_eligibility`
- `market_session_rules`
- `freshness_expectations`
- `timeout_budget`
- `fail_closed_conditions`
- `degraded_state_mapping`

## Admission Rules

- Provider adapters are internal and hidden below tools.
- Unreviewed licensing, unclear redistribution posture, missing credential scope, or failed integrity checks block production eligibility.
- Provider-down, stale, parser-limited, market-closed, or unsupported-market outcomes produce `DegradedState` unless a reviewed fallback is eligible.
- Fallback must be explicit in trace metadata and normalized source metadata where applicable.

## Non-Responsibilities

- Does not enable concrete Vietnam quote/history/fundamental providers.
- Does not implement TradingView chart/widget expansion.
- Does not enable generic web fetch.
- Does not replace route-filtered model-visible tool exposure.

## Verification Expectations

- Descriptor fixtures classify provider class and license posture.
- Policy fixtures prove fail-closed behavior for license-unclear and production-ineligible providers.
- Fallback fixtures record fallback posture instead of silent success.
- Model-visible tool surface does not expose provider adapters directly.
