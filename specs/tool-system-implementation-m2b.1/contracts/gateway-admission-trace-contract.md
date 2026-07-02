# Contract: Gateway Admission And Trace Metadata

## Scope

This contract defines feature-local M2B.1 admission and trace behavior for selected tool calls. It is internal to the agent/tool boundary and does not define public response schemas.

## Admission Inputs

| Input | Required | Notes |
|-------|----------|-------|
| `route` | yes | Classified route for the turn. |
| `tool_name` | yes | Selected tool name. |
| `args` | yes | Candidate arguments after schema parsing. |
| `capability_descriptor` | yes | Reviewed descriptor for selected tool. |
| `policy_descriptor` | yes | Internal policy for selected tool. |
| `registry_state` | yes | Registered and enabled status. |
| `provider_state` | conditional | Only where current tool behavior depends on provider/cache state. |
| `timeout_budget_ms` | yes | Admission and execution budget. |

## Admission Output

| Field | Required | Notes |
|-------|----------|-------|
| `outcome` | yes | `allowed`, `blocked`, or `degraded`. |
| `machine_code` | yes | Stable machine-readable reason. |
| `safe_message` | yes | Safe optional public wording. |
| `execute_underlying_tool` | yes | Must be false for blocked/degraded denial. |
| `trace_record` | yes | Internal trace metadata. |

## Denial Conditions

- Unknown selected tool.
- Tool not exposed for route.
- Tool disabled or non-exposed.
- Invalid arguments.
- Unsupported risk class.
- License posture unclear or blocked.
- Descriptor hash/version mismatch.
- Provider/cache/freshness state violates policy.
- Timeout budget missing or exceeded.

## TraceRecord Fields

| Field | Required | Notes |
|-------|----------|-------|
| `route` | yes | Classified route. |
| `exposed_tools` | yes | Names only, not full policy. |
| `selected_tool` | yes | Selected model-visible tool. |
| `selected_adapter` | conditional | Internal only, where applicable. |
| `descriptor_version` | yes | Capability/policy version. |
| `descriptor_hash` | yes | Integrity marker. |
| `admission_outcome` | yes | Admission result. |
| `cache_status` | conditional | `hit`, `miss`, `not_applicable`, or `unknown`. |
| `freshness` | conditional | Fresh/stale/not-applicable metadata. |
| `latency_ms` | yes | Gateway plus tool-path timing. |
| `warning` | no | Safe warning category. |
| `degraded_state_reason` | conditional | Required for blocked/degraded. |

## Security Rules

- Trace records must not include secrets, credentials, raw provider policy details, raw provider payloads, raw HTML/PDF content, or sensitive user data.
- Public response surfaces may receive only safe warning/degraded status metadata when already supported.
- Internal trace metadata must not be persisted as market truth or conversation memory.
