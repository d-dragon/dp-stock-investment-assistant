# Data Model: Internal Symbol and Normalization Backbone - M2B.2

This model is feature-local and internal. It describes target implementation contracts for M2B.2 without creating public API schemas or promoting target architecture concepts to current status before implementation evidence exists.

## CanonicalSymbolIdentity

**Purpose**: Disambiguate symbol identity before tool output, retention, or prompt assembly.

**Fields**:
- `symbol`: normalized symbol code.
- `exchange`: exchange or market identifier where applicable.
- `currency`: trading or reporting currency where applicable.
- `asset_type`: equity, index, fund, or other admitted type.
- `aliases`: alternate names or tickers known to the internal store.
- `identifiers`: provider-neutral identifiers where available.
- `locale`: market or locale classification.

**Validation**:
- `symbol` is required.
- `exchange` and `currency` are required when ambiguity exists.
- Ticker-only ambiguity must resolve to one identity or produce `DegradedState`.

## InternalSymbolRecord

**Purpose**: Represent a symbol-store record admitted for `StockSymbolTool` target behavior.

**Fields**:
- `identity`: `CanonicalSymbolIdentity`.
- `display_name`: human-readable issuer, index, or instrument name.
- `coverage`: supported capability tags for the symbol.
- `tags`: domain tags such as market, sector, or curated group.
- `stored_snapshot_metadata`: optional metadata about retained internal snapshots, not live quote facts.
- `source_record_reference`: internal source or repository reference.
- `updated_at`: record update timestamp where available.

**Validation**:
- Must not contain raw external provider payloads.
- Must not be treated as live quote/history/fundamental evidence.

## ProviderAdapterDescriptor

**Purpose**: Describe an internal provider adapter below model-visible tools.

**Fields**:
- `provider_id`
- `provider_class`: official, licensed, public_web, wrapper, international_fallback, internal_system, or visualization.
- `supported_markets`
- `supported_data_categories`
- `license_posture`
- `credential_owner`
- `freshness_policy`
- `parser_limits`
- `source_attribution_requirements`
- `production_eligible`
- `integrity_marker`

**Validation**:
- Unreviewed license, missing credential scope, or unclear redistribution posture blocks production eligibility.
- Provider descriptors are internal and must not be emitted as model-visible tool choices.

## ProviderSelectionPolicy

**Purpose**: Decide whether and how an internal provider adapter can be selected for a tool call.

**Fields**:
- `tool_name`
- `route`
- `provider_order`
- `fallback_eligibility`
- `market_session_rules`
- `freshness_expectations`
- `timeout_budget`
- `fail_closed_conditions`
- `degraded_state_mapping`

**Validation**:
- A missing eligible provider returns `DegradedState`; it must not silently fallback or silently succeed.
- Policy must preserve provider identity and fallback posture for trace metadata and normalized outputs where applicable.

## ProviderSelectionDecision

**Purpose**: Capture one deterministic provider selection outcome.

**Fields**:
- `selected_adapter`
- `admission_outcome`
- `fallback_used`
- `freshness_status`
- `license_status`
- `cache_status`
- `degraded_reason`
- `warnings`

**Validation**:
- If `admission_outcome` is not allowed, no provider call is executed.
- If fallback is used, source metadata must record fallback posture.

## ToolExecutionEnvelope

**Purpose**: Wrap every governed tool result in an inspectable internal outcome record.

**Fields**:
- `route`
- `selected_tool`
- `selected_adapter`
- `descriptor_identity`
- `admission_outcome`
- `normalized_output_ref`
- `cache_status`
- `freshness_status`
- `warnings`
- `degraded_state_reason`
- `trace_metadata`

**Validation**:
- Must reference exactly one normalized output or degraded outcome.
- Must not expose credentials, raw provider payloads, parser internals, or hidden trace details publicly.

## NormalizedOutput

**Purpose**: Classify all admitted tool outputs before prompt assembly or retained derivative handling.

**Kinds**:
- `EvidenceFact`
- `EvidenceSnippet`
- `EvidenceDocument`
- `SystemRecord`
- `MutationReceipt`
- `VisualizationProvenance`
- `GeneratedArtifact`
- `DegradedState`

**Common Fields**:
- `kind`
- `content`
- `source_metadata`
- `freshness_metadata`
- `symbol_identity`
- `warnings`
- `degraded_state`

**Validation**:
- Exactly one kind is assigned.
- Raw HTML, raw PDF bytes, hidden page text, scripts, untrusted page instructions, and raw provider payloads are not valid content.

## ToolContextPack

**Purpose**: Request-scoped prompt input bundle assembled from normalized outputs.

**Fields**:
- `request_id`
- `route`
- `normalized_outputs`
- `citations`
- `source_metadata`
- `freshness_metadata`
- `warnings`
- `degraded_states`
- `artifact_references`

**Validation**:
- Request-scoped only; must not be persisted wholesale as conversation memory or durable market truth.
- May include references to retained derivatives but not raw payloads.

## SourceMetadata

**Purpose**: Preserve source lineage needed by normalized outputs and retained derivatives.

**Fields**:
- `provider_id`
- `provider_class`
- `source_url_or_reference`
- `retrieved_at`
- `source_timestamp`
- `published_at`
- `effective_at`
- `symbol_identity`
- `exchange`
- `currency`
- `license_posture`
- `freshness_status`
- `warnings`

**Validation**:
- Missing source values are represented explicitly as absent or degraded; they must not be fabricated.
- Full answer-level market-data attribution remains downstream M2B.3 work.

## DegradedState

**Purpose**: Machine-detectable representation of blocked, stale, missing, invalid, or otherwise unsafe outcomes.

**Fields**:
- `code`
- `safe_message`
- `reason`
- `route`
- `tool_name`
- `provider_id`
- `retryable`
- `user_visible`
- `trace_reference`

**Validation**:
- Stale, missing, parser-limited, provider-down, license-unclear, validation-failed, or freshness-unknown outcomes use `DegradedState` instead of silent fallback.

## MutationReceipt

**Purpose**: Future-proof audit shape for admitted in-system mutations while keeping production writes disabled by default in M2B.2.

**Fields**:
- `mutation_id`
- `target_record`
- `action`
- `before_summary`
- `after_summary`
- `actor_or_route`
- `approval_status`
- `audit_metadata`
- `timestamp`
- `result`

**Validation**:
- Symbol-store write actions are classified as `workflow_mutation` with `internal_state_mutation` subtype.
- Production mutation paths remain disabled or degraded by default unless a future policy explicitly admits them.

## RetainedDerivative

**Purpose**: Represent information that may be retained after a request without persisting the full `ToolContextPack`.

**Allowed Derivatives**:
- Reports
- Generated artifacts
- Mutation receipts
- Audit metadata
- Trace metadata
- Approved snapshots
- Domain records

**Validation**:
- Must preserve source lineage or explicit no-source degraded-state reason.
- Must not retain raw provider/web/tool payloads unless a later feature defines a governed storage and sanitization policy.

## Relationships

```text
InternalSymbolRecord -> CanonicalSymbolIdentity
ProviderSelectionPolicy -> ProviderAdapterDescriptor
ProviderSelectionPolicy -> ProviderSelectionDecision
ToolExecutionEnvelope -> NormalizedOutput
NormalizedOutput -> SourceMetadata
ToolContextPack -> NormalizedOutput[]
ToolContextPack -> DegradedState[]
RetainedDerivative -> SourceMetadata | DegradedState
MutationReceipt -> RetainedDerivative
```

## State Transitions

```text
raw candidate input
  -> validation
  -> normalized output or degraded state
  -> request-scoped ToolContextPack
  -> prompt boundary
  -> retained derivative only if allowed
```
