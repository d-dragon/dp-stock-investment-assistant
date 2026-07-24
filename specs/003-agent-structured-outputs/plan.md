# Implementation Plan: Agent Structured Outputs & Route-Adapted Response Tools

**Branch**: `feature/agent-structured-ouputs` | **Date**: 2026-07-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-agent-structured-outputs/spec.md`

---

## Summary

Implement machine-readable structured JSON response payloads (`AgentStructuredOutput`) attached to `AgentResponse.structured_content` in `src/core/types.py` and `src/core/stock_assistant_agent.py`. The primary implementation strategy adopts the **Route-Adapted Custom Response Tool Pattern** ([ADR-AGENT-005 §3 Decision](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)) registering control-plane response tools (`submit_stock_analysis`, `submit_recommendation`, `submit_general_chat`) with `return_direct=True` under `RiskClass.BOUNDED_NON_MUTATING`. This delivers 0% prompt token cost overhead during single-turn ReAct reasoning. Secondary fallback uses a service-layer post-processing formatter (`model.with_structured_output()`) in `ChatService` with graceful degradation to `ResponseStatus.PARTIAL` on extraction errors.

---

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pydantic v2, LangChain 0.3+, LangGraph 0.2+, FastAPI  
**Storage**: MongoDB (`conversations` collection for turn metadata; `agent_checkpoints` for STM checkpointer state)  
**Testing**: pytest (`tests/unit/test_structured_output.py`, `tests/integration/test_chat_structured_flow.py`)  
**Target Platform**: Linux server / Windows dev environment (Docker microservice deployment)  
**Project Type**: Web service / Agentic AI backend  
**Performance Goals**: 0% extra prompt token overhead on primary ReAct response tool path; <10.0s execution timeout budget on secondary fallback formatter.  
**Constraints**: Zero checkpointer state corruption (`AgentStructuredOutput` excluded from `agent_checkpoints` serialization); zero raw JSON token leakage in SSE/WebSocket natural language text bubbles.  
**Scale/Scope**: Polymorphic structured JSON generation across 7 domain query routes (`FUNDAMENTALS`, `TECHNICAL_ANALYSIS`, `PRICE_CHECK`, `IDEAS`, `PORTFOLIO`, `GENERAL_CHAT`, `MARKET_WATCH`).  

---

## Governance and Traceability Context

**Source Requirements**:
- [SRS v2.9 FR-1.2.5 (Polymorphic Structured Output Generation)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#125-structured-output-generation)
- [SRS v2.9 FR-1.2.6 (Control-Plane Route-Adapted Response Tools)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#126-control-plane-route-adapted-response-tools)
- [SRS v2.9 FR-1.2.7 (Two-Stage Service-Layer Post-Processing Formatter)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#127-two-stage-service-layer-post-processing-formatter)
- [SRS v2.9 FR-1.2.8 (STM Checkpointer Payload Exclusion Hygiene)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#128-stm-checkpointer-state-hygiene-and-payload-exclusion)
- [SRS v2.9 FR-1.2.9 (Phased Architecture Strategy & StateGraph Migration)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#129-phased-architecture-strategy-and-stategraph-migration)
- [SRS v2.9 AC-10 (Structured Output Acceptance Criteria)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-10-structured-output-acceptance-criteria)
- [SRS v2.9 IR-1.14 & IR-3.11 (Transport Edge Streaming & Contract Serialization)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ir-114-structured-output-transport-edge-serialization)
- [SRS v2.9 ERR-1.4 (Graceful Extraction Degradation)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#err-14-structured-extraction-failure-degradation)

**Authority References**:
- [Constitution v2.6.0 §Structured Output Subsystem and Response Tool Governance](../../.specify/memory/constitution.md#structured-output-subsystem-and-response-tool-governance)
- [Constitution v2.6.0 §Document Referencing in Spec-Kit Workflows](../../.specify/memory/constitution.md#document-referencing-in-spec-kit-workflows)
- [ADR-AGENT-005 §1 (Context and Problem Statement)](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#1-context-and-problem-statement)
- [ADR-AGENT-005 §3 (Decision)](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)
- [ADR-AGENT-005 §4 (Options Considered and Evaluation)](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#4-options-considered-and-evaluation)
- [ARCHITECTURE_DESIGN.md §4.1.1 (System Context & Structured Output Subsystem)](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#411-system-context)
- [ARCHITECTURE_DESIGN.md §4.2.1 (Logical Building Blocks & Response Types)](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#421-logical-building-blocks)
- [ARCHITECTURE_DESIGN.md §4.2.2 (Responsibility and Dependency Boundaries)](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#422-responsibility-and-dependency-boundaries)
- [TECHNICAL_DESIGN.md §1.1 (Domain Scope & Structured Output Realization)](../../docs/domains/agent/TECHNICAL_DESIGN.md#11-scope)
- [TECHNICAL_DESIGN.md §2.1 (Key Characteristics & Response Types)](../../docs/domains/agent/TECHNICAL_DESIGN.md#21-key-characteristics)
- [TECHNICAL_DESIGN.md §3.1 (StockAssistantAgent & Structured Execution Behavior)](../../docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration)

**Traceability Updates**:
- `specs/spec-traceability.yaml`: Update `agent-structured-outputs` entry mapping `FR-1.2.5` through `FR-1.2.9`, `AC-10.1`–`AC-10.6`, `IR-1.14`, `IR-3.11`, `ERR-1.4`.
- Coverage status: `Planned` -> `Implemented` -> `Verified`.

**Sync Report Updates**:
- Run `python scripts/sync_spec_status.py --gate` post-implementation.
- Sync reports: `specs/spec-sync-status.md`, `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`.

**Public Contract Impact**:
- `docs/openapi.yaml`: Update `ChatResponse` component schema to include `structured_content` (polymorphic payload object) and `status` (`SUCCESS`, `PARTIAL`, `FAILED`).

**Long-Lived Documentation Impact**:
- Update `docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration` with concrete Pydantic schemas and factory wiring.
- Update `docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2a3-structured-outputs` with verified status.

**Lifecycle Status Target**:
- `Planned` -> `Implemented` -> `Verified`.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Spec-Driven, Traceable Delivery)**: Plan maps directly to SRS v2.9 FR-1.2.5–1.2.9 and ADR-AGENT-005. Traceability targets named explicitly.
- [x] **Principle II (Layered Boundaries and Explicit Ownership)**: `AgentStructuredOutput` payloads are attached at output contract boundary only and strictly excluded from `MongoDBSaver` `agent_checkpoints` serialization ([TECHNICAL_DESIGN.md §3.1 Agent Runtime and Orchestration](../../docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration)).
- [x] **Principle IV (Prompts & Memory Control Behavior, Not Truth)**: Schema parsing (`AgentResponse.structured_content`) remains strictly separated from `ResponseGuardrailMiddleware` policy enforcement ([ARCHITECTURE_DESIGN.md §4.2.2 Responsibility and Dependency Boundaries](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#422-responsibility-and-dependency-boundaries)).
- [x] **Principle V (Deterministic Tools and Contracted Interfaces)**: Response tools registered under `RiskClass.BOUNDED_NON_MUTATING` with `return_direct=True` (0% extra token overhead) through `ToolRegistry` and admitted via `ToolGateway.execute()` ([ADR-AGENT-005 §3 Decision](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)).
- [x] **Structured Output Subsystem Governance**: Primary route-adapted response tools + secondary out-of-band fallback formatter + `ResponseStatus.PARTIAL` degradation ([Constitution v2.6.0 §Structured Output Subsystem Governance](../../.specify/memory/constitution.md#structured-output-subsystem-and-response-tool-governance)).
- [x] **Document Referencing in Spec-Kit Workflows**: Repository-relative paths with section-level anchors verified for all `docs/` references ([Constitution v2.6.0 §Document Referencing](../../.specify/memory/constitution.md#document-referencing-in-spec-kit-workflows)).

*Gate Verdict: PASS*

---

## Project Structure

### Documentation (this feature)

```text
specs/003-agent-structured-outputs/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── openapi-chat-response.yaml
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── types.py                         # AgentStructuredOutput Pydantic v2 schemas & ResponseStatus enum
│   ├── stock_assistant_agent.py          # Route response tools registration & process_query_structured()
│   └── tools/
│       └── response_tools.py            # submit_stock_analysis, submit_recommendation, submit_general_chat
├── services/
│   └── chat_service.py                  # Two-stage fallback formatter & Mongo turn metadata updates
├── web/
│   ├── routes/
│   │   └── ai_chat_routes.py            # REST endpoint SSE streaming filter & discrete event frame emission
│   └── sockets/
│       └── chat_events.py               # WebSocket event handler payload serialization
docs/
└── openapi.yaml                         # Canonical REST ChatResponse component contract update

tests/
├── unit/
│   ├── test_structured_output.py        # Pydantic schema & response tool unit tests
│   └── test_fallback_formatter.py       # Two-stage post-processing fallback unit tests
└── integration/
    └── test_chat_structured_flow.py     # End-to-end agent structured response integration test
```

**Structure Decision**: Single Python project structure within standard repo `src/`, `docs/`, `specs/`, and `tests/` directories.

---

## Complexity Tracking

> **Constitution Check: No violations required. Standard layered pattern followed.**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | N/A | N/A |
