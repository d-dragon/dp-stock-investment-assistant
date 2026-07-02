# Data Model: Tool Contract and Gateway Baseline - M2B.1

This model defines feature-local implementation concepts for planning and testing. It does not define public API schemas or durable database collections.

## Baseline Tool Inventory

**Purpose**: The named M2B.1 inventory that must have descriptors.

**Fields**:
- `tool_name`: canonical registry/tool name.
- `tool_class`: current implementation class.
- `implementation_status`: `active`, `scaffold`, or `placeholder`.
- `registry_status`: `registered`, `unregistered`, or `disabled`.
- `model_exposure_default`: `visible`, `hidden`, or `non_exposed`.
- `descriptor_status`: `complete`, `missing`, `invalid`, or `drifted`.

**Validation rules**:
- `StockSymbolTool`, `TradingViewTool`, and `ReportingTool` must all appear.
- Placeholder/scaffold tools may be descriptor-complete while still disabled and non-exposed.
- Missing descriptors block exposure.

## ToolCapabilityDescriptor

**Purpose**: Model-safe descriptor for one tool capability.

**Fields**:
- `name`
- `display_name`
- `purpose`
- `input_schema`
- `route_coverage`
- `output_kind`
- `locale_coverage`
- `examples`
- `enabled`
- `model_visible`
- `non_exposed_reason`
- `descriptor_version`
- `descriptor_hash`

**Validation rules**:
- Must exclude credentials, license policy details, parser limits, provider fallback rules, credential owner, and provider-specific implementation details.
- `descriptor_hash` must be generated from canonical descriptor content.
- `model_visible=false` requires a non-empty `non_exposed_reason`.

## ToolPolicyDescriptor

**Purpose**: Internal policy descriptor for exposure and gateway admission.

**Fields**:
- `tool_name`
- `risk_class`
- `license_mode`
- `freshness_policy`
- `cache_policy`
- `timeout_budget_ms`
- `credential_owner`
- `mutation_policy`
- `required_metadata`
- `enabled_environments`
- `exposure_status`
- `allowed_routes`
- `descriptor_version`
- `descriptor_hash`

**Validation rules**:
- Policy descriptors are never model-visible.
- License-unclear, drifted, disabled, or unsupported-environment policy blocks exposure or execution.
- Mutation policy for M2B.1 must be `none` or non-mutating.

## RouteSurfaceRequest

**Purpose**: Inputs used to build a model-visible tool surface for one turn.

**Fields**:
- `route`
- `locale`
- `feature_flags`
- `available_context`
- `allowed_risk_classes`
- `registry_enabled_tools`
- `capability_descriptors`
- `policy_descriptors`

**Validation rules**:
- Missing optional locale/context must not broaden exposure.
- Unknown route returns an empty or baseline-safe surface.
- Provider adapters are never valid surface entries.

## RouteFilteredToolSurface

**Purpose**: The compact model-visible tool list for one ReAct invocation.

**Fields**:
- `route`
- `exposed_tools`
- `hidden_tools`
- `filter_reasons`
- `descriptor_versions`
- `surface_hash`

**Validation rules**:
- Every exposed tool must be enabled, route-admitted, model-visible, and descriptor-valid.
- Routes without admitted tools expose an empty tool list.
- Filter reasons remain internal trace metadata.

## GatewayAdmissionDecision

**Purpose**: Execution-time decision before a selected tool call reaches the underlying registry-backed tool.

**Fields**:
- `route`
- `tool_name`
- `arguments_status`
- `route_match`
- `risk_status`
- `license_status`
- `freshness_status`
- `provider_state`
- `descriptor_integrity`
- `timeout_budget_ms`
- `outcome`
- `degraded_reason`

**Validation rules**:
- `outcome` is `allowed`, `blocked`, or `degraded`.
- Blocked/degraded decisions must not execute the underlying tool.
- Descriptor drift or invalid arguments fail closed.
- `provider_state` and `freshness_status` may be `not_applicable` when the selected M2B.1 baseline path has no provider-backed or freshness-aware state to inspect.

## ToolTraceRecord

**Purpose**: Internal audit metadata for exposure and execution.

**Fields**:
- `route`
- `exposed_tools`
- `selected_tool`
- `selected_adapter`
- `descriptor_version`
- `descriptor_hash`
- `admission_outcome`
- `cache_status`
- `freshness`
- `latency_ms`
- `warning`
- `degraded_state_reason`

**Validation rules**:
- Must exclude secrets, credentials, raw provider policy details, and sensitive user data.
- May be summarized into safe public degraded/warning metadata only when response surfaces already support it.
- Is not a durable market fact or conversation memory record.
- Conditional fields such as `selected_adapter`, `cache_status`, `freshness`, `warning`, and `degraded_state_reason` are populated only when applicable or marked with a safe not-applicable value.
