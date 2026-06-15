# Process View — DP Stock Investment Assistant

**Input**: `.specify/memory/architecture-scenario-view.md`, `.specify/memory/architecture-logical-view.md`

**Purpose**: Derive runtime collaboration, handoffs, approvals, receipts, state advancement, and failure closure from scenario paths and logical boundaries.

## Architecture Intent

This view preserves the runtime collaboration model where service-layer lifecycle governance, agent-runtime reasoning, tool-invocation evidence acquisition, provider fallback, and guardrail enforcement are executed as separate runtime links with defined handoffs, receipts, and failure-closure paths.

## Core Tensions

| Tension | Current Tradeoff Direction | Process Consequence |
|---------|----------------------------|---------------------|
| Service layer before agent runtime vs agent-first invocation | REST path enforces lifecycle checks via ChatService before agent invocation; Socket.IO path invokes the agent directly | Two runtime paths exist with different handoff sequences; Socket.IO lacks the service-layer lifecycle receipt |
| Streaming vs non-streaming response commitment | Non-streaming: full response evaluated at once. Streaming: partial chunks admitted through windows, final guardrail commits the stream | Streaming requires a checkpoint-emission loop that non-streaming does not; failure closure differs between modes |
| Provider fallback at request granularity vs potential mid-stream handoff | Fallback loop completes before streaming begins; mid-stream provider switching is not defined | A provider failure during a request triggers a full restart with the fallback provider, not a seamless handoff |
| Prompt compiler path as additive process step vs inline replacement | Current process uses inline prompt; compiler path would insert asset loading, composition, and guardrail middleware as explicit process steps | Adding compiler steps changes the runtime link order but does not alter the handoff semantics of existing steps |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Does Not Control |
|----------|----------------------------|-----------------------------|
| Service-layer lifecycle precedes agent invocation | REST path enforces archive checks and conversation existence before any agent call; this prevents archived conversations from entering the reasoning loop | Agent-runtime checkpoint recovery, tool execution, LLM provider selection |
| Provider selection precedes model invocation | ModelClientFactory resolves provider and model before any LLM call; fallback is resolved before the first provider attempt | Tool execution order, prompt composition, checkpoint saving |
| Guardrail evaluation precedes response commitment | Guardrail middleware executes after model generation but before any output reaches the response surface | Prompt assembly, tool execution, checkpoint management |
| Spec-kit sync phase follows implementation verification | Step 14 (verify.run) runs before step 17 (docs and contract sync); synchronization does not begin before verification evidence exists | Implementation tasks, test execution, deployment |

## Change Axes

| Expected Change | Isolated By | Process Impact |
|-----------------|-------------|----------------|
| Prompt compiler path introduction | Compiler steps (load→assemble→guard) are additive between route classification and agent invocation | Runtime link order gains asset resolution and guardrail middleware steps but existing links remain unchanged |
| Socket.IO lifecycle parity | Adding ChatService-equivalent checks in the Socket.IO path would mirror the REST handoff sequence | The Socket.IO runtime link gains a service-layer lifecycle receipt; agent invocation precondition now includes archive validation |
| LTM personalization activation (planned) | LTM context would be injected as an additional input to the agent reasoning loop, not as a replacement for checkpoint state | Agent invocation receives an additional data input (LTM preferences) but the handoff sequence from service layer to agent does not change |
| Streaming admission-window parameterization | Window size and checkpoint interval are config parameters, not process-structure changes | The checkpoint→emit→buffer loop structure stays stable; only timing and admission thresholds vary |

## Invariants

| Invariant | Source Scenario / Runtime Link | Risk If Violated |
|-----------|--------------------------------|------------------|
| Lifecycle validation completes before agent reasoning begins | S1, S3: ChatService's archive check and conversation-existence validation precede any agent invocation | Archived conversations could accept new turns and modify checkpoint state |
| Tool results are data-only context, not instruction-bearing content | S1: Tool outputs flow into the LLM as evidence, not as behavioral instructions | Model could treat tool outputs as overriding policy directives |
| Provider fallback completes before response streaming begins | S5: Fallback loop runs entirely during the LLM call, not mid-stream | Incomplete or switching responses could reach the user mid-stream |
| Guardrail result determines response commitment, not generation | S1, S2: The guardrail outcome ("pass", "warn", "block", "degraded") is read after generation is complete, not before | Blocked output could be leaked or partially emitted before guardrail evaluation finishes |
| Sync phase follows verification, not precedes it | S6: Step 16 (maintenance) and step 17 (docs sync) execute after step 14 (verify.run) | Stale or incorrect documentation could be synchronized before the implementation is proven |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Mid-stream provider switching | Would require streaming-aware provider handoff that no current scenario requires and that the current fallback infrastructure does not support |
| Agent-initiated lifecycle state changes | Agent runtime must not set conversation status or ownership; lifecycle is a service-layer concern |
| Transport-layer lifecycle enforcement | Transport boundaries must not short-circuit service-layer lifecycle checks by calling the agent directly |
| Synchronous commit before streaming admission | Streaming admission windows are designed for progressive release; waiting for full model completion before any emission negates the streaming benefit |

## Main Runtime Links

| Runtime Link | Trigger | Source | Target | Transferred Content / Fact | Completion Condition |
|--------------|---------|--------|--------|----------------------------|----------------------|
| RL-1: Request Admission | Inbound HTTP/Socket.IO request | Transport boundary (Flask blueprint / Socket.IO handler) | Service layer (ChatService or equivalent) | Normalized request including conversation_id, message content, stream flag | Request is accepted and routed to the correct service handler; or rejected at transport (auth, rate limit) |
| RL-2: Lifecycle Validation and Context Resolution | Request arrives at service layer | ChatService | Service layer internal | Validated conversation state: exists, active, owned by correct user; session context resolved | Lifecycle check passes (not archived, ownership confirmed); or 409/403 returned |
| RL-3: Agent Invocation | Service layer has validated request and resolved context | ChatService | Agent runtime (StockAssistantAgent) | Validated conversation_id, message payload, resolved session context | Agent runtime begins reasoning; or invocation rejected if conversation found archived during race |
| RL-4: Route Classification | Agent runtime receives the validated work item | Agent runtime (semantic-router) | Agent runtime internal | Query classified into one of 8 route categories | Route category determined; or fallback to GENERAL_CHAT for ambiguous queries |
| RL-5: Prompt Assembly | Route classification is complete | Agent runtime; planned PromptAssembler | Agent runtime internal | Compiled prompt including shared policy, route skill, memory context, evidence | Prompt is ready for LLM submission; or falls back to shared-policy-only if route skill missing |
| RL-6: Provider Selection | Prompt is ready for LLM submission | ModelClientFactory | Selected LLM provider client | Cached provider client instance for the configured model | Provider client is available; or fallback sequence activated |
| RL-7: Model Invocation and Response Generation | Provider client is selected | LLM provider (OpenAI/Grok) | Agent runtime | Generated response content (streamed or complete) | Response generation completes; or provider returns error triggering fallback |
| RL-8: Tool Invocation and Evidence Return | LLM requests a tool call | Agent runtime (through ReAct loop) | Tool implementation (StockSymbol, Reporting, etc.) | Structured data result with provenance metadata | Tool returns data; or returns cache hit; or returns error (tool unavailable, network failure) |
| RL-9: Checkpoint Save | After each agent turn (user+assistant message pair) | LangGraph MongoDBSaver | MongoDB checkpoints collection | Serialized thread-local agent state: messages, tool call history | Checkpoint stored successfully; or degraded mode continues without persistence |
| RL-10: Guardrail Evaluation | Model generation completes | ResponseGuardrailMiddleware (planned) | Agent runtime | GuardrailResult: status, triggered_rules, rewrite_applied, trace_metadata | Guardrail status determined (pass/warn/block/degraded); blocked outputs trigger safe terminal |
| RL-11: Response Emission | Guardrail evaluation completes with pass or warn status | Transport layer (Flask SSE response or Socket.IO emit) | End User | Streaming SSE chunks or complete JSON response | Response reaches client; stream terminates with final event |
| RL-12: Sync and Traceability Refresh | Feature implementation is verified | Spec-kit verify.run (step 14) | Sync targets: docs/, specs/, traceability | Updated artifacts: spec-traceability.yaml, long-lived docs, reverse-trace docs | Sync gates pass; or sync gap is flagged for correction |

## Handoffs and Approvals

| Handoff / Approval | From | To | Meaning | Accepted Path | Rejected / Returned Path |
|--------------------|------|----|---------|---------------|--------------------------|
| H1: Request Admitted | Transport | Service Layer | Request is structurally valid and may proceed to lifecycle validation | Request flows to ChatService | Transport rejects: 401 (no auth), 429 (rate limit), 400 (bad request) |
| H2: Conversation Lifecycle Approved | Service Layer | Agent Runtime | Conversation exists, is active, and is owned by the requesting user | Validated request proceeds to agent invocation | 409 Conflict (archived), 403/404 (wrong user or missing conversation) |
| H3: Provider Selected | ModelClientFactory | Agent Runtime | LLM provider is available and configured for the request | Provider client is used for model invocation | Fallback sequence triggered; if all providers fail, error response returned |
| H4: Guardrail Outcome Determined | Guardrail Middleware | Transport Layer | Response content passes safety checks | Response emitted to user (pass/warn) | Blocked response replaced with safe refusal; degraded response returned with limited content |
| H5: Sync Approved | Verify.run | Docs/Specs Sync | Implementation matches spec and passes constitution checks | Long-lived docs and traceability are updated | Sync gap flagged; drift repair required before promotion |

## Receipts and User Participation

| Receipt / Participation Point | Sender | Receiver | Content | User Action | Architecture Consequence |
|-------------------------------|--------|----------|---------|-------------|--------------------------|
| R1: Query Submitted | End User | Transport Layer | Natural language query | User types and submits a message | Triggers RL-1 through RL-11 sequence |
| R2: Streaming Chunk Received | Transport Layer | End User | Partial response token (SSE chunk) | User observes progressive output | Streaming admission window must pass before chunk is emitted |
| R3: Terminal Event Received | Transport Layer | End User | "done", "cancelled", or "blocked" event | User sees completion or error state | Terminal guardrail commitment determines which event fires |
| R4: Management API Response | Service Layer | End User | JSON response with resource state | User creates/lists/updates/archives resources | Lifecycle state transition is persisted; cascading effects enforced |
| R5: Sync Report Generated | Sync Script | System Operator | spec-sync-status.md report | Operator reviews sync status and drift | Sync gate pass/fail determines whether delivery is complete |
| R6: Error Response | Transport Layer | End User | JSON error with safe user-visible message | User sees explanation of failure | Error is logged with context; secrets must not appear in response |

## Failure, Degradation, and Closure

| Failure / Branch | Detection Boundary | Responsible Boundary | Degradation or Compensation | User-Visible Result | Closure Condition |
|------------------|--------------------|----------------------|-----------------------------|---------------------|-------------------|
| F1: Provider unavailable (primary) | ModelClientFactory provider health check or timeout | Provider Selection | Fallback to configured secondary provider in fallback_order | Response generated by fallback provider; user may see provider change indicated in metadata | Request completes with fallback content; or all providers fail → error response |
| F2: All providers unavailable | ModelClientFactory fallback loop exhausted | Provider Selection | Error response with safe messaging; no further model interaction | "Unable to process your request at this time." | Request terminates with error; no checkpoint is saved for a failed request |
| F3: Archive guard triggered (attempted write to archived conversation) | ChatService lifecycle check | Service Orchestration | Request rejected with 409 conflict; no agent invocation occurs | "This conversation is archived and cannot accept new messages." | Request terminates at service layer; checkpoint is not modified |
| F4: Guardrail blocks response | ResponseGuardrailMiddleware | Prompt Enforcement | Safe refusal message replaces generated content; triggered rules recorded in trace metadata | "I cannot provide that information." (or equivalent safe response) | Blocked response committed; guardrail outcome attributable via trace_metadata |
| F5: Guardrail degrades response | ResponseGuardrailMiddleware | Prompt Enforcement | Reduced response content emitted with degradation metadata | Partial or disclaimer-heavy response | Degraded response committed with degradation_reason |
| F6: Mid-stream blocker detected | Streaming admission checkpoint | Transport / Guardrail | Immediate emission stop; safe terminal frame emitted | Partial content visible, then safe terminal event | Stream marked as blocked at terminal |
| F7: Client cancellation | Transport layer receives cancellation signal | Transport | Generation stops; no completed-answer state recorded | Stream ends without terminal success event | Stream marked as cancelled |
| F8: Tool execution failure | Tool-invocation interface | Agent Runtime / Tool Layer | Cache miss returns tool error; agent may retry, use cached value, or explain unavailability | "I could not retrieve the latest data for that symbol." or cached data shown with staleness note | Agent continues with available data or explains the gap |
| F9: Sync gap detected (stale traceability or docs) | Sync script or manual review | Spec-Kit Governance | Gap is flagged in sync report; drift is not automatically repaired | Sync report shows "flag" or "fail" status for affected mappings | Sync phase not complete until gaps are corrected |
| F10: Checkpoint save failure | LangGraph MongoDBSaver | Agent Runtime | Request continues without persistence; next request starts with fresh state | No user-visible effect on the current response; subsequent responses lack prior context | Checkpoint failure logged; degraded mode continues |

## Process Gaps

| Gap | Affected Runtime Link / Scenario | Why It Matters |
|-----|----------------------------------|----------------|
| Socket.IO path lacks RL-2 (lifecycle validation) | RL-1 (Socket.IO request admission), RL-2 (lifecycle validation) | Socket.IO chat bypasses ChatService; a message to an archived conversation via Socket.IO would not be rejected |
| Mid-stream provider fallback undefined | RL-7 (model invocation), F1 (provider failure) | If the primary provider fails mid-stream during SSE emission, there is no defined handoff to a fallback provider without restarting the request |
| Prompt compiler path steps not yet inserted | RL-5 (prompt assembly), RL-10 (guardrail evaluation) | Prompt variant selection, experiment assignment, and explicit guardrail middleware are not present in the current runtime; all prompt-related process steps are planned |
| No checkpoint-before-provider-call pattern | RL-6/RL-7 (provider selection/invocation) | The current process does not save checkpoint state before an LLM call; a failure during generation after a successful tool call loses the tool-call result |

## Prohibited Content

Do not write call stacks, queue names, retry counts, thread/process details, endpoint sequences, workflow engine configuration, or orchestration code here.
