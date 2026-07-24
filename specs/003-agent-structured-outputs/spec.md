# Feature Specification: Agent Structured Outputs & Route-Adapted Response Tools

**Feature Identifier**: `003-agent-structured-outputs`  
**Status**: Implemented  
**Created**: `2026-07-23`  
**Author**: Assistant / Architecture Lead  
**SRS Reference**: [`SOFTWARE_REQUIREMENTS_SPECIFICATION.md v2.9`](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#12-functional-requirements) (`FR-1.2.5`–`FR-1.2.9`, `AC-10.1`–`AC-10.6`, `IR-1.14`, `IR-3.11`, `ERR-1.4`)  
**Architecture Reference**: [`ARCHITECTURE_DESIGN.md`](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#411-stockassistantagent) (§4.1.1, §4.2.1)  
**Technical Design Reference**: [`TECHNICAL_DESIGN.md`](../../docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration) (§3.1, §3.2)  
**ADR Reference**: [`ADR-AGENT-005`](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md)

## Governance Context *(mandatory)*

**Source Requirements**:
- [SRS v2.9 FR-1.2.5 (Polymorphic Structured Output Generation)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#125-structured-output-generation)
- [SRS v2.9 FR-1.2.6 (Control-Plane Route-Adapted Response Tools)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#126-control-plane-route-adapted-response-tools)
- [SRS v2.9 FR-1.2.7 (Two-Stage Service-Layer Post-Processing Formatter)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#127-two-stage-service-layer-post-processing-formatter)
- [SRS v2.9 FR-1.2.8 (STM Checkpointer Payload Exclusion Hygiene)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#128-stm-checkpointer-state-hygiene-and-payload-exclusion)
- [SRS v2.9 FR-1.2.9 (Phased Architecture Strategy & StateGraph Migration)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#129-phased-architecture-strategy-and-stategraph-migration)
- [SRS v2.9 AC-10 (Structured Output Acceptance Criteria)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-10-structured-output-acceptance-criteria)
- [SRS v2.9 IR-1.14 & IR-3.11 (Transport Edge Streaming & Contract Serialization)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ir-114-structured-output-transport-edge-serialization)
- [SRS v2.9 ERR-1.4 (Graceful Extraction Degradation)](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#err-14-structured-extraction-failure-degradation)

**Authoritative Inputs**:
- [Constitution v2.6.0 §Structured Output Subsystem and Response Tool Governance](../../.specify/memory/constitution.md#structured-output-subsystem-and-response-tool-governance)
- [ADR-AGENT-005 (Adopt Route-Adapted Custom Response Tool Pattern)](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)
- [ARCHITECTURE_DESIGN.md §4.3.1 (Primary Query Processing Flow)](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#431-primary-query-processing-flow)
- [ARCHITECTURE_DESIGN.md §4.8.4 (Output Contract Boundary)](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#484-output-contract-boundary)
- [TECHNICAL_DESIGN.md §3.8 (Structured Output Subsystem Realization)](../../docs/domains/agent/TECHNICAL_DESIGN.md#38-structured-output-subsystem-realization)
- [TECHNICAL_DESIGN.md §3.8.9 (Persistent Data Schema & MongoDB Realization)](../../docs/domains/agent/TECHNICAL_DESIGN.md#389-persistent-data-schema--mongodb-realization)

**Traceability Target**:
- `specs/spec-traceability.yaml` entry `agent-structured-outputs` covering `FR-1.2.5`, `FR-1.2.6`, `FR-1.2.7`, `FR-1.2.8`, `FR-1.2.9`, `AC-10.1`–`AC-10.6`, `IR-1.14`, `IR-3.11`, and `ERR-1.4`.

**Sync Targets**:
- `docs/openapi.yaml` (ChatResponse component schema)
- `specs/spec-traceability.yaml`
- `specs/spec-sync-status.md`
- `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`

**Contract Impact**:
- `docs/openapi.yaml` updating `ChatResponse` component schema to include `structured_content` (polymorphic payload object) and `status` (`SUCCESS`, `PARTIAL`, `FAILED`).

**Lifecycle Status Rule**:
- Draft -> Clarified -> Planned -> Implemented -> Verified.

## Clarifications

### Session 2026-07-22

- Q: What execution timeout budget should be enforced on the out-of-band fallback formatter before degrading to ResponseStatus.PARTIAL? → A: Option A: Configurable setting with default 10.0s timeout (`agent.structured_output.fallback_timeout_seconds: 10.0`).
- Q: Which response tool should ToolSurfaceBuilder inject by default for unclassified or general conversational routes? → A: Option A: Inject `submit_general_chat` with `GeneralChatResponse` schema.
- Q: How should structured metadata be updated on the conversations BSON document across multi-turn user chats? → A: Option A: Update `last_turn_metadata` and append light summary metadata frame (`route_kind`, `structured_status`, `schema_version`) to `turns` array in `conversations` collection.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Typed Structured Output Generation via Route-Adapted Response Tools (Priority: P1)

As a financial application user, I want agent responses to deliver typed, machine-readable JSON payloads (`AgentStructuredOutput`) matching domain Pydantic schemas (`StockAnalysisResponse`, `RecommendationResponse`, `GeneralChatResponse`) alongside rich markdown narratives, so that the frontend can render interactive UI components (charts, risk badges, target price cards) without secondary LLM formatting calls or added response latency.

**Why this priority**: Core value driver for modern UI rendering. Using route-adapted response tools with `return_direct=True` achieves 0% extra prompt token overhead on single-turn ReAct execution, delivering machine-readable data without increasing token cost.

**Independent Test**: Can be fully verified by sending a query (e.g. "Danh gia HSG trung han") to `StockAssistantAgent.process_query_structured()` and asserting that `AgentResponse.structured_content` returns a valid `StockAnalysisResponse` object populated with `symbol`, `sentiment`, and `key_metrics` with `status == ResponseStatus.SUCCESS`.

**Acceptance Scenarios**:

1. **Given** a user query routed to `FUNDAMENTALS`, `TECHNICAL_ANALYSIS`, or `PRICE_CHECK`, **When** the agent completes its ReAct evidence loop, **Then** the LLM invokes `submit_stock_analysis`, returning direct control to the agent runtime with `AgentResponse.structured_content` containing a validated `StockAnalysisResponse` object (`AC-10.1`, `AC-10.2`).
2. **Given** a user query routed to `IDEAS` or `PORTFOLIO`, **When** the agent completes reasoning, **Then** the LLM invokes `submit_recommendation`, returning direct control with `AgentResponse.structured_content` containing a validated `RecommendationResponse` object.
3. **Given** a user query routed to `GENERAL_CHAT`, `MARKET_WATCH`, or `NEWS_ANALYSIS`, **When** the agent completes reasoning, **Then** the LLM invokes `submit_general_chat`, returning direct control with `AgentResponse.structured_content` containing a validated `GeneralChatResponse` object.
4. **Given** single-turn ReAct reasoning execution, **When** the model calls a registered route response tool, **Then** `return_direct=True` terminates the execution loop immediately without executing secondary LLM formatter passes, consuming **0% extra input prompt tokens** (`AC-10.3`).

---

### User Story 2 - Out-of-Band Fallback Formatter & Graceful Degradation (Priority: P2)

As a system operator, I want plain markdown text outputs from open-source or local LLMs to be automatically formatted out-of-band via a service-layer fallback formatter (`model.with_structured_output()`) and degrade gracefully if extraction fails, so that user conversation threads never crash or lose readable text.

**Why this priority**: Ensures system robustness and model agnosticism. Smaller open-source or local models (e.g., DeepSeek, Llama-3) may bypass function calling and reply in plain markdown text; the fallback formatter guarantees machine-readable JSON extraction while graceful degradation protects thread continuity.

**Independent Test**: Can be verified by simulating an LLM response emitting raw markdown text without tool calls, confirming that `process_query_structured()` transparently invokes `ChatService._extract_structured_response()`, returning `AgentResponse` with `structured_content` populated and `status == ResponseStatus.PARTIAL` (`ERR-1.4`).

**Acceptance Scenarios**:

1. **Given** an LLM outputting plain markdown text without invoking a route response tool, **When** `StockAssistantAgent.process_query_structured()` detects tool omission, **Then** it transparently triggers `ChatService._extract_structured_response()` calling `model.with_structured_output(target_schema)` on the raw text summary (~500 tokens) (`AC-10.4`).
2. **Given** out-of-band extraction succeeds, **When** the Pydantic schema is validated, **Then** `AgentResponse` is assembled with raw text in `content`, extracted payload in `structured_content`, and `status = ResponseStatus.PARTIAL`.
3. **Given** out-of-band extraction fails or times out due to invalid JSON syntax, **When** fallback extraction fails, **Then** the runtime captures the error, sets `structured_content = None`, raw markdown in `content`, and `status = ResponseStatus.PARTIAL`, returning a clean user response without raising an unhandled exception (`ERR-1.4`).

---

### User Story 3 - Checkpointer State Hygiene & Transport Edge Serialization (Priority: P3)

As a system developer, I want heavy typed JSON payloads explicitly excluded from MongoDB short-term memory checkpointer state (`agent_checkpoints`) and raw JSON syntax tokens suppressed during real-time streaming, so that database checkpointer state remains uncorrupted and frontend text chat bubbles remain clean.

**Why this priority**: Protects database health and user experience. Checkpointer state must only store raw conversation message history to avoid schema drift, while streaming edges must prevent raw function argument JSON tokens from leaking into text chat bubbles.

**Independent Test**: Can be verified by executing a conversation turn, inspecting `MongoDBSaver` `agent_checkpoints` collection documents to confirm `channel_values.messages` contains raw `BaseMessage` objects without `AgentStructuredOutput` payloads (`FR-1.2.8`), and verifying that transport edge streaming filters out response tool argument tokens (`IR-1.14`).

**Acceptance Scenarios**:

1. **Given** an executed conversation turn returning structured output, **When** `MongoDBSaver` persists state to `agent_checkpoints`, **Then** raw `BaseMessage` objects are stored in `channel_values.messages` while `AgentStructuredOutput` typed payloads are **strictly excluded** from checkpointer serialization (`FR-1.2.8`, `AC-10.5`).
2. **Given** real-time response streaming (`astream_events` / SSE / WebSocket), **When** the LLM generates response tool call arguments (`submit_stock_analysis`), **Then** transport edge handlers suppress raw JSON syntax tokens from the natural language text stream (`IR-1.14`).
3. **Given** turn completion on REST or WebSocket transport edges, **When** the structured payload is validated, **Then** edge handlers emit a discrete `structured_completion` event frame (SSE) or `structured_content` payload (`chat_response` WebSocket event) matching `docs/openapi.yaml` `ChatResponse` schema (`IR-3.11`).

---

### Edge Cases

- What happens when a user query cannot be unambiguously classified into a specific domain route?
  - *System defaults to `GENERAL_CHAT` route, injecting `submit_general_chat` response tool into the tool surface.*
- How does the system handle model non-compliance when the model calls `submit_stock_analysis` with missing mandatory fields (e.g. missing `symbol`)?
  - *Pydantic validation raises a `ValidationError`, triggering the two-stage service-layer fallback formatter; if fallback also fails, `status` is set to `ResponseStatus.PARTIAL` with `structured_content = None`.*
- What happens when legacy conversation documents created before Milestone 1 are queried?
  - *The system enforces zero-downtime backward compatibility, returning `AgentResponse(content=text, structured_content=None, status=ResponseStatus.SUCCESS)`.*

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate typed, machine-readable JSON response payloads (`AgentStructuredOutput`) inheriting polymorphic domain schemas (`StockAnalysisResponse`, `RecommendationResponse`, `GeneralChatResponse`) attached to `AgentResponse.structured_content` (`FR-1.2.5`, `AC-10.1`).
- **FR-002**: System MUST register control-plane route-adapted response tools (`submit_stock_analysis`, `submit_recommendation`, `submit_general_chat`) in `ToolRegistry` under codebase enum `RiskClass.BOUNDED_NON_MUTATING` with `return_direct=True` (`FR-1.2.6`, `AC-10.2`).
- **FR-003**: System MUST dynamically expose only the matching route response tool per turn via `ToolSurfaceBuilder` (defaulting to `submit_general_chat` for unclassified or general chat routes), ensuring the model emits structured JSON arguments during single-turn ReAct reasoning with 0% extra prompt token overhead (`FR-1.2.6`, `AC-10.3`).
- **FR-004**: System MUST execute a two-stage service-layer post-processing fallback formatter (`model.with_structured_output()`) in `ChatService` enforcing a configurable execution timeout budget (`agent.structured_output.fallback_timeout_seconds: 10.0`) when the model completes reasoning without calling the response tool (`FR-1.2.7`, `AC-10.4`).
- **FR-005**: System MUST assign `ResponseStatus.PARTIAL` and preserve raw text in `AgentResponse.content` when fallback extraction fails or degrades, preventing unhandled thread exceptions (`ERR-1.4`).
- **FR-006**: System MUST explicitly exclude `AgentStructuredOutput` typed JSON payloads from `MongoDBSaver` short-term memory checkpointer serialization (`agent_checkpoints`), persisting only raw `BaseMessage` arrays while updating `last_turn_metadata` and appending light summary frames (`route_kind`, `structured_status`, `schema_version`) to the `turns` array in the `conversations` MongoDB collection (`FR-1.2.8`, `AC-10.5`).
- **FR-007**: System MUST fulfill all functional requirements on the single-turn ReAct baseline (`create_agent`) before custom compiled `StateGraph` nodes and in-graph self-repair loops are promoted to current runtime behavior (`FR-1.2.9`, `AC-10.6`).
- **FR-008**: Transport edges (REST `POST /api/chat` and WebSocket `chat_message`) MUST filter raw JSON tool argument tokens out of streaming text bubbles and emit a discrete `structured_completion` event frame upon turn completion (`IR-1.14`, `IR-3.11`).

### Key Entities *(include if feature involves data)*

- **`AgentStructuredOutput`**: Union type alias over domain Pydantic v2 schemas (`StockAnalysisResponse`, `RecommendationResponse`, `GeneralChatResponse`, `ErrorResponse`), each with `route_kind: StockQueryRoute` as the discriminator field.
- **`StockAnalysisResponse`**: Specialized structured output model for `FUNDAMENTALS`, `TECHNICAL_ANALYSIS`, and `PRICE_CHECK` routes containing `symbol`, `summary`, `sentiment`, `key_metrics` (Dict), and `citations` (List).
- **`RecommendationResponse`**: Specialized structured output model for `IDEAS` and `PORTFOLIO` routes containing `recommendation` (BUY/HOLD/SELL/WATCH), `time_horizon`, `thesis`, `risk_factors`, and `disclaimer`.
- **`GeneralChatResponse`**: Specialized structured output model for `GENERAL_CHAT`, `MARKET_WATCH`, and `NEWS_ANALYSIS` routes containing `message`, `topics_covered`, and `follow_up_suggestions`.
- **`AgentResponse`**: Core envelope containing `content: str`, `structured_content: Optional[AgentStructuredOutput]`, `status: ResponseStatus`, and `metadata: Dict`.
- **`ResponseStatus`**: Enum distinguishing output contract validation states (`SUCCESS`, `FALLBACK`, `ERROR`, `PARTIAL`, `FAILED`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of happy-path queries on supported LLM providers emit typed `AgentStructuredOutput` payloads via route response tools with **0% extra prompt token overhead** (`AC-10.3`).
- **SC-002**: 100% of plain text model outputs automatically format via the two-stage service-layer post-processing fallback formatter without dropping raw text (`AC-10.4`).
- **SC-003**: 0% of malformed or unparseable extractions cause unhandled thread exceptions or conversation crashes, failing gracefully into `ResponseStatus.PARTIAL` (`ERR-1.4`).
- **SC-004**: 0% of typed `AgentStructuredOutput` JSON payloads leak into `MongoDBSaver` `agent_checkpoints` documents, maintaining 100% checkpointer memory hygiene (`AC-10.5`).
- **SC-005**: 100% of real-time streaming sessions suppress raw JSON tool argument syntax from natural language text streams (`IR-1.14`).

---

## Assumptions

- **Target LLM Capabilities**: Primary LLM models (OpenAI, Anthropic, Gemini, Grok) support standard tool/function calling syntax.
- **Single-Turn ReAct Foundation**: `StockAssistantAgent` reuses the factory-wrapped `create_agent` ReAct runtime baseline without requiring custom compiled `StateGraph` modifications for Milestone 1.
- **Frontend TS Contract Generation**: Frontend applications consume contract types generated from `docs/openapi.yaml` via `openapi-typescript`.
- **Database Compatibility**: Existing MongoDB collections (`conversations`, `agent_checkpoints`) support additive turn metadata fields without requiring offline database downtime.
