# Architecture Synthesis: DP Stock Investment Assistant

**Input Views**:
- Scenario: `.specify/memory/architecture-scenario-view.md`
- Logical: `.specify/memory/architecture-logical-view.md`
- Process: `.specify/memory/architecture-process-view.md`
- Development: `.specify/memory/architecture-development-view.md`
- Physical: `.specify/memory/architecture-physical-view.md`

**Note**: This synthesis is filled by the speckit.arch.generate agent after the five 4+1 view files are updated.

## View Index

| View | File | Purpose | Current Status |
|------|------|---------|----------------|
| Scenario | `.specify/memory/architecture-scenario-view.md` | UC-producing actor, use case, path, branch, and acceptance semantics | Updated 2026-06-02 |
| Logical | `.specify/memory/architecture-logical-view.md` | Capability boundaries, domain objects, states, and invariants | Updated 2026-06-02 |
| Process | `.specify/memory/architecture-process-view.md` | Runtime links, handoffs, approvals, receipts, failure closure | Updated 2026-06-02 |
| Development | `.specify/memory/architecture-development-view.md` | Architecture-level components, package boundaries, contracts, dependencies | Updated 2026-06-02 |
| Physical | `.specify/memory/architecture-physical-view.md` | Deployment, external systems, fact sources, observability, operations | Updated 2026-06-02 |

## Architecture Intent

The five views stabilize the architecture of the DP Stock Investment Assistant as a layered, spec-governed, multi-provider AI system where transport, orchestration, reasoning, tool execution, memory, prompt policy, and governance are separable boundaries with explicit dependency direction and independent evolution paths. The architecture preserves conversation-scoped memory isolation, evidence-grounded financial intelligence, archive-over-delete lifecycle semantics, and spec-driven traceability as cross-cutting invariants.

## Central Design Forces

Five design forces connect the views:

1. **Conversation-scoped memory as the identity unit** — conversation_id→thread_id binding constrains all five views: scenarios assume single-conversation context, the logical model separates checkpoint state from lifecycle metadata, the process model saves state after each agent turn, the development boundary separates the checkpoint package from the repository package, and the physical deployment uses MongoDB for both but maintains logical separation.

2. **Spec-driven, traceable delivery as the governance engine** — The SDD lifecycle constrains all delivery: scenarios require governed artifacts, the logical model separates delivery-scoped specs from long-lived docs, the process model places sync after verification, the development boundary isolates governance from runtime code, and the physical model stores governance artifacts in the repository file system independently from container images.

3. **Archive-over-delete lifecycle semantics** — The irreversible archive chain constrains all views: scenarios expect cascade behavior, the logical model enforces forbidden transitions (archived to active), the process model terminates requests at the service layer for archived resources, the development boundary assigns lifecycle to the service orchestration package, and the physical model relies on data retention rather than deletion.

4. **Provider fallback at request granularity** — The request-level fallback constrains runtime collaboration: scenarios assume graceful degradation, the logical model separates provider selection from agent reasoning, the process model defines fallback as a pre-streaming loop, the development boundary isolates provider clients behind ModelClientFactory, and the physical model treats LLM providers as independent external dependencies.

5. **Prompt policy as an additive planned evolution** — The prompt compiler path as additive constrains architecture evolution: scenarios gain variant and experiment options without changing current behavior, the logical model keeps prompt policy separate from state and tools, the process model adds compiler steps between routing and agent invocation, the development boundary grows three additive packages without modifying existing runtime packages, and the physical model stores prompt assets on the file system independent of container images.

## Primary Tradeoffs

| Tradeoff | Chosen Direction | Consequence | Revisit When |
|----------|------------------|-------------|--------------|
| Single-agent simplicity vs future multi-agent routing | One ReAct agent with route-aware skills; multi-agent orchestrator deferred | Limited specialist-agent parallelism | When prompt contracts for different routes materially diverge |
| Service-layer lifecycle authority vs agent-runtime checkpoint authority | Two separate authorities for the same conversation | Requires correspondence management; bounded divergence tolerated | When automated reconciliation becomes a reliability requirement |
| Streaming parity between REST and Socket.IO | REST includes full lifecycle guards; Socket.IO bypasses them | Two streaming surfaces with different safety characteristics | When Socket.IO becomes the primary streaming path |
| Inline prompt baseline vs compiler path adoption | Inline prompts current; compiler path additive | No prompt variant or experiment capability today | When prompt variant selection becomes a feature requirement |
| Archive-over-delete vs data lifecycle management | Archive is irreversible; data accumulates | Long-term storage costs grow | When storage costs or regulations require lifecycle management |
| Provider fallback at request vs mid-stream granularity | Fallback completes before streaming begins | Mid-stream provider failures unrecoverable per request | When streaming session durations make mid-stream fallback necessary |

## Stable Boundaries

| Boundary | Affected Views | Must Remain Stable Because | Forbidden Crossing |
|----------|----------------|----------------------------|--------------------|
| Conversation as STM identity unit | Scenario, Logical, Process, Development, Physical | All agent runtime, checkpointer, lifecycle, and management API surfaces assume conversation_id→thread_id binding | Service layer must not set checkpoint state; agent must not set lifecycle status |
| Layered routes to services to repositories to database | Logical, Development | All blueprints, factories, and repository singletons assume this ordering | Routes must not issue DB queries; services must not import route types |
| Tools compute facts, LLM reasons about them | Scenario, Logical, Process, Development, Physical | ADR-001 enforces separation; prevents fabricated figures | Tool results must not be instruction-bearing prompt content |
| Spec-driven traceable delivery | Scenario, Logical, Process, Development, Physical | Constitution v2.1.0 enforces governed artifacts | Code must not import from specs/; sync must follow verification |
| Archive-over-delete lifecycle | Scenario, Logical, Process, Development | All scenarios assume archival is terminal | Agent must not change lifecycle status; checkpoints must not contain lifecycle metadata |

## Change Axes

| Expected Change | Isolated By | Affected Views | Architecture Consequence |
|-----------------|-------------|----------------|--------------------------|
| New LLM provider added | ModelClientFactory provider registration | Development, Physical | Provider boundary expands; no change to scenario, logical, or process views |
| Prompt compiler path activated | ADR-002/003 additive packages | All five views | New scenario capabilities; new process steps; new development packages; new storage on file system |
| Frontend framework migration | Stable transport contract (REST + Socket.IO) | Physical only | No change to scenario, logical, process, or development views |
| LTM/RAG tier implementation | ADR-001 reserved boundaries | All five views | New scenario capabilities; new memory surfaces; new process inputs; new development packages |
| Socket.IO lifecycle parity achieved | ChatService-like checks in Socket.IO handler | Process, Development | Runtime link RL-2 now applies to Socket.IO path |
| Kubernetes HPA/PDN configured | Infrastructure overlay | Physical only | Deployment topology changes only; no architectural boundary impact |
| Mid-stream provider fallback defined | New streaming-aware provider handoff protocol | Process, Development | New failure branch; new client logic in provider package |

## Anti-patterns

| Anti-pattern | Why It Violates Intent | Affected Views |
|--------------|------------------------|----------------|
| Agent runtime setting lifecycle status | Collapses two distinct authority boundaries into one | Logical, Process, Development |
| Checkpointer becoming source of truth for metadata | Makes checkpoint schema responsible for service-layer lifecycle data | Logical, Development |
| Routes issuing ad-hoc database queries | Bypasses repository layer health-check, logging, and indexing conventions | Logical, Development |
| Prompt assets used as fact store | Violates ADR-001 separation of policy from truth | Scenario, Logical |
| Mid-stream provider switching without defined protocol | Risks partial or duplicated content | Process |
| Spec-kit sync preceding verification | Updates long-lived docs before implementation is proven | Scenario, Process, Development |

## Cross-View Architecture Model

Normalizes the 4+1 design results into the architecture SSOT. Do not treat view-specific concepts as equivalent or interchangeable.

| Architecture Concept | Scenario Meaning | Logical Interpretation | Runtime Role | Development Boundary | Physical Constraint | Architecture Constraint |
|----------------------|------------------|------------------------|--------------|----------------------|---------------------|---------------------------|
| Conversation | UC-1, UC-2, UC-4: unit of user interaction with memory retrieval | Conversation object with lifecycle, ownership, and checkpoint identity | RL-2 to RL-5, RL-9: lifecycle-resolved work item through agent, saved as checkpoint | Service orchestration package (lifecycle); Checkpoint package (runtime state) | MongoDB conversations + checkpoints collections | conversation_id→thread_id must be 1:1; checkpoint must not contain lifecycle metadata |
| Route Classification | UC-1: query categorized for skill selection | Route Classification domain object; one of 8 route categories | RL-4: semantic-router classifies before prompt assembly | Agent reasoning package | No dedicated physical storage; in-memory classification | Must not execute tools; must not persist state |
| Prompt Compilation | UC-8: prompt variant/experiment selection (planned) | Prompt Asset lineage with version, locale, fallback, selection_mode | RL-5: assemble prompt from assets before agent invocation (planned) | Prompt asset and compiler package (planned) | File system under src/prompts/ | Must be additive to current baseline; must preserve section-level cross-references |
| Guardrail Enforcement | UC-1, UC-2: safe response boundary | GuardrailResult with status, triggered_rules, trace_metadata | RL-10: evaluate model draft before response commitment | Prompt asset and compiler package (planned) | No dedicated storage; outcomes as trace metadata | After generation and before commitment; attributable outcome required |
| Provider Selection | UC-5: model provider chosen with fallback | Provider Client cached by \{provider\:\{model_name\} key | RL-6: resolve client; RL-7: invoke model; F1/F2: fallback | Provider client package via ModelClientFactory | External OpenAI/Grok endpoints; in-memory client cache | Fallback before streaming; mid-stream fallback not defined |
| Spec-Driven Delivery | UC-6: governed feature lifecycle | Spec Feature Artifact + Long-Lived Doc | RL-12: sync after verification; H5: approved after review | Spec-kit governance package | GitHub file system: specs/, docs/, .specify/ | All non-trivial changes from governed artifacts; sync after verification |
| Lifecycle State Machine | UC-3, UC-7: create to close to archive | State: active to archived; forbidden archived to active | RL-2 validates lifecycle; F3 rejects archived writes | Service orchestration package | MongoDB collections | Archive is terminal; service layer owns lifecycle; agent must not set lifecycle status |

## Key Architecture Conclusions

| Conclusion | Affected Views | Boundary/Owner | Consequence |
|------------|----------------|----------------|-------------|
| Conversation is the single identity unit for STM across all views | Scenario, Logical, Process, Development, Physical | Checkpoint and Memory / Service Orchestration | Two-authority model requires correspondence management; bounded divergence tolerated but not reconciled automatically |
| Provider fallback is limited to request granularity | Scenario, Process, Development | Provider Selection / ModelClientFactory | Mid-stream provider failures during SSE cannot be recovered without restart; explicit gap |
| Prompt compiler path is additive, not replacive | Scenario, Logical, Process, Development | Prompt Policy and Guardrail | Adding compiler path activates variant/experiment/guardrail capabilities without changing current behavior |
| Socket.IO and REST have different lifecycle safety | Scenario, Process, Development | Transport / Service Orchestration | Socket.IO chat bypasses lifecycle validation; parity is a documented gap |
| Spec-driven delivery is the mandatory change path | Scenario, Process, Development, Physical | Spec-Kit Governance / Constitution | Every non-trivial change must start from governed artifacts and must sync long-lived docs after verification |

## Cross-Cutting Constraints

| Constraint | Source | Affected Views | Scope | Architecture Consequence |
|------------|--------|----------------|-------|--------------------------|
| Constitution v2.1.0 governs all delivery | Constitution Principle I, Golden Rules, Document Referencing, Lifecycle Obligations | Scenario, Logical, Process, Development, Physical | All non-trivial code, docs, and IaC changes | All architectural work must respect spec-driven delivery, archive-over-delete, section-level cross-references, and sync gates |
| ADR-001 layered LLM architecture | ADR-AGENT-001 | Scenario, Logical, Process, Development | Agent memory, tools, prompts, retrieval | Memory never stores prices/ratios/forecasts; tools compute facts, LLM reasons about them; prompts control behavior not truth |
| ADR-002/003 prompt evolution | ADR-AGENT-002, ADR-AGENT-003 | Scenario, Logical, Process, Development | Prompt asset taxonomy, composition, compiler path | Prompt evolution is additive to current baseline; compiler path does not replace existing behavior |
| Transport contract stability | Architecture review; frontend uses REST + Socket.IO only | Physical | Frontend-to-backend communication | Frontend modernization does not affect backend or agent architecture |

## Open Risks and Review Triggers

| Risk or Trigger | Missing Evidence / Change Condition | Affected Views | Required Architecture Review |
|-----------------|-------------------------------------|----------------|------------------------------|
| Socket.IO lifecycle parity gap | Socket.IO handler does not use ChatService lifecycle validation | Process, Development | Required before Socket.IO becomes primary streaming path or before lifecycle bypass incident |
| Mid-stream provider fallback undefined | No streaming-aware provider handoff protocol | Process, Development | Required before streaming session durations increase significantly |
| Prompt compiler path not yet implemented | Loader, Assembler, GuardrailMiddleware are planned but not built | Scenario, Logical, Process, Development | Required before prompt variant selection or experiment assignment becomes a feature |
| No Prometheus metrics, HPA, PDB, or NetworkPolicy | Infrastructure monitoring and resilience not configured | Physical | Required before production deployment with availability SLAs |
| Automated summarization trigger not wired | Summarized schema exists but no trigger | Logical, Process | Required before lifecycle gap becomes a user-facing concern |
| No OpenTelemetry tracing | Request correlation not instrumented | Physical | Required before cross-service latency debugging becomes necessary |
