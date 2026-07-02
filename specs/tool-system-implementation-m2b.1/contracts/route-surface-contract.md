# Contract: Route-Filtered Tool Surface

## Scope

This contract defines the feature-local route-surface behavior for M2B.1. It is consumed by implementation and tests before `StockAssistantAgent` builds or invokes the ReAct tool surface.

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| `route` | yes | Current `StockQueryRoute` value. |
| `locale` | no | Missing locale must not broaden exposure. |
| `feature_flags` | yes | Flags controlling optional tool exposure. |
| `available_context` | yes | Safe request/session context used for admission. |
| `allowed_risk_classes` | yes | M2B.1 defaults to non-mutating classes only. |
| `registry_enabled_tools` | yes | Current enabled registry inventory. |
| `capability_descriptors` | yes | Reviewed model-safe descriptors. |
| `policy_descriptors` | yes | Internal policy descriptors. |

## Output

| Field | Required | Notes |
|-------|----------|-------|
| `route` | yes | Route evaluated. |
| `exposed_tools` | yes | Model-visible tool wrappers/descriptors for ReAct. |
| `hidden_tools` | yes | Internal list of hidden tools. |
| `filter_reasons` | yes | Internal reasons by tool name. |
| `descriptor_versions` | yes | Descriptor versions/hashes for exposed tools. |
| `surface_hash` | yes | Integrity marker for the built surface. |

## Required Rules

- Expose only tools that are registry-enabled, descriptor-valid, model-visible, route-eligible, feature-flag admitted, context-admitted, and within allowed risk class.
- Hide disabled, placeholder, scaffolded-but-not-admitted, unrelated, drifted, internal-only, risk-blocked, or license-blocked tools.
- Expose no tool when a route has no admitted M2B.1 tool.
- Never expose provider adapters as standalone model-visible tools.
- Keep `filter_reasons` internal.

## Route Fixture Expectations

| Route | M2B.1 expectation |
|-------|-------------------|
| `price_check` | Expose current admitted symbol lookup capability only if descriptor and policy pass. |
| `technical_analysis` | Expose no `TradingViewTool` while placeholder/non-exposed. |
| `fundamentals` | Expose only current admitted baseline tools, if any. |
| `market_watch` | Empty unless the current non-mutating `ReportingTool` scaffold is explicitly admitted for market summaries; no market-data substitute is exposed. |
| `portfolio` | Empty unless the current non-mutating `ReportingTool` scaffold is explicitly admitted; no portfolio-management substitute is exposed. |
| `news_analysis` | Empty in M2B.1 because generic web evidence is out of scope. |
| `ideas` | Empty or baseline-safe only; no unsupported recommendation tool exposure. |
| `general_chat` | Empty or baseline-safe only; unrelated financial tools must stay hidden. |
