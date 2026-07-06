# Process View - DP Stock Investment Assistant

**Input**: `.specify/memory/architecture-scenario-view.md`, `.specify/memory/architecture-logical-view.md`

**Purpose**: Derive runtime collaboration, handoffs, approvals, receipts, state advancement, and failure closure from scenario paths and logical boundaries.

## Architecture Intent

This view preserves the runtime collaboration model for an admitted user turn: service lifecycle validation precedes reasoning; route classification drives prompt and tool policy; the model sees only admitted capabilities; selected tool calls pass through a thin gateway; provider policy, normalization, and request-scoped context happen below the model-visible tool layer; responses close with safe output, warning, block, cancellation, or degraded state.

## Core Tensions

| Tension | Current Tradeoff Direction | Process Consequence |
|---------|----------------------------|---------------------|
| Fast agent invocation vs lifecycle receipt | Service-owned lifecycle must complete before agent work where parity exists | Agent work item includes lifecycle admission, not raw transport input |
| Direct ReAct tool call vs governed admission | Tool selection remains inside one reasoning runtime, but execution is mediated by gateway policy | Tool execution has a pre-execution admission handoff and denied-call closure |
| Provider fallback vs provider authority | Provider policy can choose fallback only within admitted source posture | Fallback and degraded states are deterministic, not prompt-selected |
| Streaming progress vs response safety | Streaming can emit progressively, but terminal outcomes must remain explicit | Cancellation, block, degradation, and completion are separate closure states |
| Current prompt baseline vs route-aware prompt behavior | Prompt route skills are gated and guardrails remain planned | Process links must label which prompt controls are current, gated, or planned |
| Request-scoped evidence vs durable retention | Normalized context exists for the turn; only approved derivatives are retained | Retention requires explicit artifact, trace, or audit handoff |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Does Not Control |
|----------|----------------------------|-----------------------------|
| Transport to Service Handoff | User requests need consistent admission into lifecycle governance | Tool exposure, provider selection, lifecycle policy itself |
| Service Lifecycle Gate | Archived or unauthorized work must stop before reasoning or checkpoint updates | Model choice, tool execution, prompt asset resolution |
| Route Classification Link | Prompt and tool policies need a common route signal | Provider parsing, data retrieval, lifecycle state |
| Prompt Policy Link | Behavior policy must be applied before model invocation and future guardrail commitment | Market fact authority, provider licensing, persistent memory |
| Tool Surface Link | Model-visible capabilities must be filtered before ReAct tool selection | Execution, provider order, parser limits, credentials |
| Gateway Admission Link | Unsafe selected calls must fail closed before registry-backed execution | Provider parsing, report composition, lifecycle transitions |
| Provider and Normalization Link | Source authority, freshness, license posture, and output class must be resolved before prompt context | Model-visible tool names or prompt policy |
| Response Commitment Link | User-visible output must close with explicit success, warning, block, cancellation, or degradation | Lifecycle mutation or source acquisition |
| Spec Kit Sync Link | Architecture memory and traceability should update only from verified evidence or explicit target-state authority | Runtime execution and code changes |

## Change Axes

| Expected Change | Isolated By | Process Impact |
|-----------------|-------------|----------------|
| Route-skill activation | Prompt policy link | Adds route-specific prompt context without changing tool admission or provider policy |
| Tool gateway maturity | Gateway admission link | Adds stronger denial and trace closure while preserving registry-backed execution |
| Provider ecosystem expansion | Provider and normalization link | Adds fallback and source classes below tools without changing model-visible surface |
| Reporting persistence | Retention handoff | Adds artifact/lineage retention after normalized context, not direct provider fetch |
| Mutation-capable tools | Approval and mutation receipt handoff | Adds explicit authorization, confirmation, and audit closure before any durable change |
| Transport parity | Transport to service handoff | Aligns Socket.IO-style flow with service lifecycle gate |
| Observability hardening | Trace and receipt handoffs | Adds metrics/alerts/correlation without changing scenario order |

## Invariants

| Invariant | Source Scenario / Runtime Link | Risk If Violated |
|-----------|--------------------------------|------------------|
| Lifecycle gate runs before agent reasoning where parity exists | S1, S2, S5; RL-2 | Archived or unauthorized conversations modify runtime state |
| Tool surface is built before model tool selection | S1, S3; RL-5 | The model sees unrelated, disabled, internal, or high-risk tools |
| Gateway denies before execution | S3; RL-7 | Disallowed calls execute and only fail after side effects or provider calls |
| Provider policy is deterministic and below tools | S6; RL-9 | The model chooses providers or bypasses licensing/freshness posture |
| Normalization happens before prompt context | S1, S4; RL-10 | Raw payloads or untrusted instructions enter the model context |
| Degraded outcomes are explicit | S3, S6, S9; F1-F8 | Users receive unsupported facts without visible limitations |
| Sync follows verification or target-design authority | S7; RL-14 | Architecture memory reports unverified implementation as current |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Mid-stream provider handoff without protocol | Streaming cannot safely merge partial outputs from different providers without a defined process |
| Tool gateway as second agent runtime | Gateway admits, denies, traces, and wraps execution; it does not reason, plan, or own prompts |
| Provider fallback selected by prompt text | Fallback must be deterministic application policy, not model instruction |
| Silent fallback from blocked tool to unrelated tool | Degradation must be visible and machine-detectable |
| Report generation before normalization | Reports must not become an alternate route around provider policy and source lineage |
| Syncing memory architecture from code diffs alone | The authority for this refresh is the named architecture, technical design, and SRS documents |

## Main Runtime Links

| Runtime Link | Trigger | Source | Target | Transferred Content / Fact | Completion Condition |
|--------------|---------|--------|--------|----------------------------|----------------------|
| RL-1: Request Admission | User sends message or management action | Transport boundary | Service lifecycle boundary | Normalized request intent and response mode | Request is structurally accepted or safely rejected |
| RL-2: Lifecycle and Context Validation | Request is admitted by transport | Service lifecycle boundary | Agent reasoning boundary | Active conversation status, ownership result, session context receipt | Work is admitted or stopped with safe lifecycle error |
| RL-3: STM Recovery | Agent work item begins | Agent reasoning boundary | STM checkpoint boundary | Conversation-scoped thread identity | Prior state is loaded or fresh state is declared |
| RL-4: Route Classification | Agent receives admitted query | Agent reasoning boundary | Prompt and tool policy boundaries | Route category and confidence posture | Route is selected or conservative route is used |
| RL-5: Tool Surface Construction | Route is available before model invocation | Tool surface boundary | Agent reasoning boundary | Model-safe admitted tool capabilities and hidden reasons | ReAct loop receives compact surface or no tools |
| RL-6: Prompt Assembly | Route and request context are available | Prompt policy boundary | Agent reasoning boundary | Baseline prompt, implemented/gated route context, data segment posture | Prompt is ready or stable fallback is used |
| RL-7: Model Tool Selection | ReAct loop requests a tool call | Agent reasoning boundary | Tool gateway boundary | Selected tool name and arguments | Gateway admission begins |
| RL-8: Gateway Admission | Tool call reaches gateway | Tool gateway boundary | Tool inventory boundary | Admission decision, descriptor identity, risk/license/freshness posture | Call is denied/degraded or allowed to execute |
| RL-9: Provider Mediation | Tool needs external or internal source access | Provider policy boundary | Provider adapter boundary | Admitted provider class, source posture, freshness, attribution requirements | Provider returns result or degraded state |
| RL-10: Output Normalization | Tool/provider result returns | Normalization boundary | Prompt policy and response boundary | Normalized output, warnings, degraded state, source lineage | Tool Context Pack is assembled for the request |
| RL-11: Model Response Generation | Prompt and data-only context are ready | Agent reasoning boundary | External LLM provider | Governed prompt and request-scoped context | Draft response or provider failure returns |
| RL-12: Response Guardrail and Commitment | Draft response exists | Prompt policy boundary | Transport boundary | Pass, warning, block, rewrite, cancellation, or degradation outcome | User-visible response is committed safely |
| RL-13: Retention Handoff | Report, artifact, trace, or mutation retention is admitted | Retention boundary | Metadata and artifact boundary | Source lineage, warnings, receipt, artifact reference, retention posture | Approved derivative is retained; full request context is discarded |
| RL-14: Delivery Sync | Architecture or feature evidence is ready | Spec Kit governance boundary | Architecture/docs/traceability memory | Verified or target-labeled architecture facts | Sync passes or gap remains explicit |

## Handoffs and Approvals

| Handoff / Approval | From | To | Meaning | Accepted Path | Rejected / Returned Path |
|--------------------|------|----|---------|---------------|--------------------------|
| H1: Work admitted | Transport boundary | Service lifecycle boundary | Request may be checked against business lifecycle | Continue to lifecycle and context validation | Safe transport rejection |
| H2: Lifecycle approved | Service lifecycle boundary | Agent reasoning boundary | Conversation/session ownership and status permit reasoning | Agent receives admitted work item | No agent invocation; lifecycle error closes request |
| H3: Prompt context accepted | Prompt policy boundary | Agent reasoning boundary | Baseline/gated route prompt can be used without weakening policy | Prompt proceeds to model invocation | Baseline fallback or degraded prompt metadata |
| H4: Tool surface accepted | Tool surface boundary | Agent reasoning boundary | Model sees only admitted capabilities | ReAct tool selection can occur | Empty surface; agent proceeds without tools |
| H5: Tool call admitted | Tool gateway boundary | Tool inventory/provider boundary | Selected call is valid for route, risk, license, freshness, and descriptors | Registry-backed execution proceeds | Degraded state; no underlying execution |
| H6: Provider source admitted | Provider policy boundary | Provider adapter boundary | Source class is legal, fresh enough, attributed, and permitted | Provider result can be normalized | Provider degraded state or fallback path |
| H7: Output accepted for context | Normalization boundary | Prompt policy boundary | Output is data-only and classified | Tool Context Pack enters prompt assembly | Raw payload quarantined or degraded state returned |
| H8: Response committed | Prompt policy boundary | Transport boundary | Output is safe to expose | Complete/streaming response emitted | Safe refusal, warning, degradation, cancellation, or block |
| H9: Mutation approved | Approval boundary | Retention and mutation audit boundary | Future state-changing action has authorization and confirmation | Mutation receipt can be retained | Mutation is blocked or degraded |
| H10: Sync approved | Verification/governance boundary | Architecture memory and traceability | Delivery evidence supports the state label | Architecture memory and sync artifacts update | Gap remains documented |

## Receipts and User Participation

| Receipt / Participation Point | Sender | Receiver | Content | User Action | Architecture Consequence |
|-------------------------------|--------|----------|---------|-------------|--------------------------|
| R1: Request accepted or rejected | Transport/Service boundary | End User | Safe admission, lifecycle, or validation result | User sends or corrects request | Stops unsafe work before agent reasoning |
| R2: Tool limitation disclosed | Tool gateway or provider policy | End User through response boundary | Safe warning or degraded-state summary | User interprets caveat or changes request | Prevents silent unsupported facts |
| R3: Streaming terminal state | Transport boundary | End User | Completed, cancelled, blocked, or degraded terminal outcome | User observes final state | Makes partial response closure explicit |
| R4: Visualization provenance | Visualization boundary | End User/report boundary | Chart/widget/deep-link provenance and caveat | User inspects visualization | Keeps visualization separate from evidence facts |
| R5: Report/artifact receipt | Reporting/retention boundary | End User/operator | Generated artifact reference with lineage and warnings | User downloads or reviews report | Retained derivative is auditable |
| R6: Mutation receipt | Future mutation boundary | User/operator | Approval and state-change audit result | User confirms or reviews mutation | Durable changes become traceable |
| R7: Sync report | Spec Kit governance boundary | System Operator | Current/stale status and linked evidence | Operator reviews delivery readiness | Architecture and requirement drift is visible |

## Failure, Degradation, and Closure

| Failure / Branch | Detection Boundary | Responsible Boundary | Degradation or Compensation | User-Visible Result | Closure Condition |
|------------------|--------------------|----------------------|-----------------------------|---------------------|-------------------|
| F1: Archived or unauthorized conversation | Service lifecycle boundary | Service lifecycle authority | Reject before agent invocation | Safe lifecycle or ownership error | Request closes without checkpoint or tool changes |
| F2: Ambiguous route | Agent reasoning boundary | Agent reasoning and prompt policy | Conservative route and narrower tool surface | General or cautious answer | Response commits with limited scope |
| F3: No admitted tools | Tool surface boundary | Tool surface boundary | Empty model-visible surface | Agent answers without tool claim or explains limitation | No tool execution occurs |
| F4: Descriptor drift or missing descriptor | Tool surface/gateway boundary | Tool gateway boundary | Hide capability or deny selected call | Safe limitation/degraded-state summary | Trace records descriptor failure |
| F5: Invalid or disallowed tool call | Tool gateway boundary | Tool gateway boundary | Deny before execution | Limitation or corrected request guidance | Underlying tool not executed |
| F6: Provider license or freshness blocked | Provider policy boundary | Provider policy boundary | Try admitted fallback or return degraded state | Source/freshness caveat | No unsupported provider result is used |
| F7: Raw web or provider content unsafe | Normalization boundary | Normalization boundary | Quarantine raw content and emit snippets/documents or degraded state | Safe evidence caveat | Raw instructions excluded from prompt |
| F8: Visualization mistaken for evidence | Normalization or response boundary | Prompt policy and normalization | Classify as Visualization Provenance only | Chart caveat or sourced numeric facts from another source | Response avoids unsupported numeric claim |
| F9: Report lacks normalized context | Reporting boundary | Reporting/retention boundary | Degraded report or no report | User sees missing-data limitation | No direct provider scraping occurs |
| F10: LLM provider failure before response | Provider/model boundary | Provider selection boundary | Deterministic fallback or safe error | Fallback response or unavailable message | Request closes with provider outcome |
| F11: Mid-stream provider failure | Streaming boundary | Transport and provider boundary | Stop stream or safe terminal state; no seamless handoff | Partial stream ends safely | Gap remains until protocol exists |
| F12: Prompt asset missing or invalid | Prompt policy boundary | Prompt policy boundary | Stable baseline fallback with metadata | Response continues with baseline behavior | Prompt degradation is traceable |
| F13: Sync drift | Spec Kit governance boundary | Governance boundary | Mark stale/gap and block promotion | Sync report shows gap | Corrected by later governed update |

## Process Gaps

| Gap | Affected Runtime Link / Scenario | Why It Matters |
|-----|----------------------------------|----------------|
| Socket.IO lifecycle parity | RL-1, RL-2, S2 | WebSocket-style chat can lack the same service lifecycle receipt as REST/SSE |
| Mid-stream provider fallback | RL-11, F11, S2/S6 | Current fallback is request-granular; streaming handoff needs a defined protocol |
| Prompt guardrail middleware | RL-12, UC-8 | Prompt route assets exist/gate behavior, but final guardrail enforcement is not universal |
| Full provider licensing posture | RL-9, F6 | Production source admission needs terms, credential scope, redistribution, and caveat rules |
| Executable IR-3 contracts | RL-5 through RL-13 | Architecture names the flow, but implementation specs must define enforceable contract details |
| Observability correlation | RL-8 through RL-14 | Tool/provider/prompt degraded modes need stronger cross-boundary trace correlation |

## Prohibited Content

Do not write call stacks, retry counts, transport route sequences, queue identifiers, thread/process implementation details, workflow engine configuration, or orchestration code here.
