# Contract: Tool Descriptors

## Scope

This contract defines feature-local M2B.1 descriptor expectations for `StockSymbolTool`, `TradingViewTool`, and `ReportingTool`. It is not a public API contract.

## ToolCapabilityDescriptor

Required fields:

| Field | Required | Model-visible | Notes |
|-------|----------|---------------|-------|
| `name` | yes | yes | Canonical tool name. |
| `display_name` | yes | yes | Human-readable safe label. |
| `purpose` | yes | yes | Model-safe purpose statement. |
| `input_schema` | yes | yes | Validated argument shape. |
| `route_coverage` | yes | yes | Allowed route names. |
| `output_kind` | yes | yes | M2B.1 coarse output classification only. |
| `locale_coverage` | yes | yes | Supported locales or `any`. |
| `examples` | no | yes | Safe examples only. |
| `enabled` | yes | yes | Runtime enablement state. |
| `model_visible` | yes | yes | Whether the descriptor may be exposed. |
| `non_exposed_reason` | conditional | yes | Required when `model_visible=false`. |
| `descriptor_version` | yes | yes | Reviewed descriptor version. |
| `descriptor_hash` | yes | yes | Integrity marker over canonical descriptor content. |

Forbidden model-visible fields:
- credentials
- credential owner
- provider fallback rules
- parser limits
- internal license policy
- timeout internals
- provider-specific implementation details
- raw gateway trace details

## ToolPolicyDescriptor

Required fields:

| Field | Required | Model-visible | Notes |
|-------|----------|---------------|-------|
| `tool_name` | yes | no | Must match a capability descriptor. |
| `risk_class` | yes | no | M2B.1 admits read-only or bounded non-mutating behavior only. |
| `license_mode` | yes | no | Blocks unclear or prohibited posture. |
| `freshness_policy` | yes | no | Used by gateway admission. |
| `cache_policy` | yes | no | Includes TTL posture where applicable. |
| `timeout_budget_ms` | yes | no | Maximum admission/execution budget. |
| `credential_owner` | yes | no | `none` is valid for tools without credentials. |
| `mutation_policy` | yes | no | Must be non-mutating for M2B.1. |
| `required_metadata` | yes | no | Trace and result metadata expected after execution. |
| `enabled_environments` | yes | no | Environment admission. |
| `exposure_status` | yes | no | `model_visible`, `hidden`, `disabled`, or `non_exposed`. |
| `allowed_routes` | yes | no | Route admission list. |
| `descriptor_version` | yes | no | Must align with capability descriptor. |
| `descriptor_hash` | yes | no | Integrity marker. |

## Baseline Tool Expectations

| Tool | M2B.1 descriptor expectation |
|------|------------------------------|
| `StockSymbolTool` | Descriptor complete; route-visible only where current behavior is admitted. |
| `TradingViewTool` | Descriptor complete; disabled/non-exposed while placeholder remains unregistered or not implemented. |
| `ReportingTool` | Descriptor complete; scaffold status explicit; route-visible only where admitted by policy. |

## Failure Semantics

- Missing descriptor: block exposure.
- Invalid descriptor: block exposure.
- Descriptor drift: block exposure and execution.
- Policy/capability mismatch: block exposure and execution.
- Disabled/non-exposed tool: hide from model; record internal filter reason.
