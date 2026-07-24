# Phase 0 Research: Agent Structured Outputs & Response Tools

**Feature**: `003-agent-structured-outputs`  
**Branch**: `feature/agent-structured-ouputs`  
**Status**: Complete  

---

## Technical Unknowns & Resolved Questions

### 1. Primary Strategy Choice: Route-Adapted Custom Response Tools vs. Native Provider Formatting

- **Decision**: Adopt **Route-Adapted Custom Response Tool Pattern** ([ADR-AGENT-005 §3 Decision](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)) as primary strategy.
- **Rationale**:
  - Native provider formatting (`response_format={"type": "json_object"}` or provider JSON modes) requires a secondary LLM pass over the full message history to construct the JSON payload. In single-turn ReAct reasoning, this incurs 100%+ extra prompt input token overhead ([ADR-AGENT-005 §2 Decision Drivers](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#2-decision-drivers)).
  - Standard tool calling is universally supported across LLM providers (OpenAI, Anthropic, Gemini, Grok, local models via Ollama/vLLM).
  - Registering response tools with `return_direct=True` terminates the ReAct execution loop immediately upon calling the response tool, returning structured JSON directly with **0% extra prompt token overhead** ([TECHNICAL_DESIGN.md §3.1 Agent Runtime and Orchestration](../../docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration)).
- **Alternatives Considered**:
  - *Native Provider Response Formatting*: Rejected as primary due to 100%+ prompt token cost penalty and provider lock-in ([ADR-AGENT-005 §4 Options Considered](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#4-options-considered-and-evaluation)).
  - *Custom StateGraph Compiler Node*: Deferred to future SO.M2 phase because premature graph re-architecture risks checkpointer state drift without immediate functional gain ([ADR-AGENT-005 §3 Decision](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)).

---

### 2. Control-Plane Tool Admission & Risk Classification

- **Decision**: Register control-plane response tools (`submit_stock_analysis`, `submit_recommendation`, `submit_general_chat`) under codebase enum `RiskClass.BOUNDED_NON_MUTATING`.
- **Rationale**:
  - `ToolGateway.execute()` evaluates tool risk classes during admission ([TECHNICAL_DESIGN.md §3.2 Tool System Realization](../../docs/domains/agent/TECHNICAL_DESIGN.md#32-tool-system-realization-and-implemented-gateway-flow)).
  - Response tools perform no system state mutation or external API calls; they serve purely as structured output contract boundaries ([ARCHITECTURE_DESIGN.md §4.1.1 System Context](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#411-system-context)).
  - Classifying them as `RiskClass.BOUNDED_NON_MUTATING` ensures immediate gateway admission without bypassing security policies or trace logging ([ADR-AGENT-005 §3 Decision](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)).
- **Alternatives Considered**:
  - *Bypassing ToolGateway*: Rejected because all tool calls must pass through `ToolGateway.execute()` for unified audit logging and execution tracing ([Constitution v2.6.0 §V Deterministic Tools](../../.specify/memory/constitution.md#v-deterministic-tools-and-contracted-interfaces)).

---

### 3. Service-Layer Out-of-Band Fallback Formatter & Execution Budget

- **Decision**: Implement a two-stage service-layer fallback in `ChatService._extract_structured_response()` using `model.with_structured_output(target_schema)` with a default 10.0s timeout budget (`agent.structured_output.fallback_timeout_seconds: 10.0`).
- **Rationale**:
  - Open-source or smaller local LLMs (DeepSeek, Llama-3) may bypass tool calling and output plain markdown text.
  - If the model omits calling the response tool, `StockAssistantAgent.process_query_structured()` invokes the fallback formatter out-of-band on the raw markdown text summary (~500 tokens) ([TECHNICAL_DESIGN.md §3.1 StockAssistantAgent](../../docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration)).
  - A 10.0s timeout budget prevents long-tail LLM hangs while preserving thread safety.
  - If extraction fails or times out, the system sets `status = ResponseStatus.PARTIAL` and `structured_content = None`, preserving raw markdown in `AgentResponse.content` without throwing unhandled exceptions ([SRS v2.9 ERR-1.4](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#err-14-structured-extraction-failure-degradation)).
- **Alternatives Considered**:
  - *In-loop re-prompting*: Rejected for Milestone 1 because retrying LLM calls inside the ReAct loop multiplies token costs and user-perceived latency.

---

### 4. Checkpointer State Hygiene & Payload Exclusion

- **Decision**: Exclude `AgentStructuredOutput` Pydantic objects from `MongoDBSaver` checkpointer state (`agent_checkpoints`).
- **Rationale**:
  - `agent_checkpoints` stores conversation short-term memory (STM) `BaseMessage` arrays for thread resumption ([ARCHITECTURE_DESIGN.md §4.1.1 System Context](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#411-system-context)).
  - Serializing large Pydantic structured output payloads into checkpointer state causes MongoDB document bloat, state schema drift across feature releases, and potential deserialization crashes.
  - `AgentStructuredOutput` is attached to `AgentResponse` at the transport contract boundary only.
  - Conversation metadata frame (`route_kind`, `structured_status`, `schema_version`) is written to the `turns` array in the `conversations` collection, maintaining crisp separation between checkpointer STM and application persistence ([Constitution v2.6.0 §II Layered Boundaries](../../.specify/memory/constitution.md#ii-layered-boundaries-and-explicit-ownership), [SRS v2.9 FR-1.2.8](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#128-stm-checkpointer-state-hygiene-and-payload-exclusion)).
- **Alternatives Considered**:
  - *Storing JSON in message additional_kwargs*: Rejected to prevent checkpointer memory bloat and schema drift.

---

### 5. Transport Edge Streaming & Token Suppression

- **Decision**: Filter raw JSON tool argument streaming tokens out of natural language chat bubbles on REST SSE and WebSocket streams, emitting a discrete `structured_completion` event frame upon turn completion.
- **Rationale**:
  - When the LLM generates arguments for `submit_stock_analysis` (e.g. `{"symbol": "HSG", ...}`), streaming tool argument tokens directly to the user chat bubble produces ugly JSON flicker.
  - Transport edge handlers (`src/api/routes/chat.py`, `src/api/routes/websocket.py`) suppress tool argument streaming tokens from the text delta channel, emitting a clean `structured_completion` event frame once the Pydantic payload is validated ([SRS v2.9 IR-1.14 & IR-3.11](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ir-114-structured-output-transport-edge-serialization)).
- **Alternatives Considered**:
  - *Streaming JSON text to frontend*: Rejected due to poor visual UX and chat bubble formatting corruption.

---

## Consolidated Architecture Matrix

| Requirement | Primary Strategy | Fallback Strategy | Governance Anchor |
|-------------|------------------|-------------------|-------------------|
| **FR-1.2.5 (Structured Output)** | Route-Adapted Response Tools (`return_direct=True`) | Two-Stage `model.with_structured_output()` | [ADR-AGENT-005 §3](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision), [SRS v2.9 §1.2.5](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#125-structured-output-generation) |
| **FR-1.2.6 (Control-Plane Tools)** | `RiskClass.BOUNDED_NON_MUTATING` in `ToolRegistry` | Gateway admission audit logging | [ADR-AGENT-005 §3](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision), [SRS v2.9 §1.2.6](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#126-control-plane-route-adapted-response-tools) |
| **FR-1.2.7 (Fallback Formatter)** | Service-layer out-of-band extraction (10s budget) | Graceful degradation to `ResponseStatus.PARTIAL` | [SRS v2.9 §1.2.7](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#127-two-stage-service-layer-post-processing-formatter), [ERR-1.4](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#err-14-structured-extraction-failure-degradation) |
| **FR-1.2.8 (STM Hygiene)** | Exclusion from `agent_checkpoints` | Turn metadata summary in `conversations` | [SRS v2.9 §1.2.8](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#128-stm-checkpointer-state-hygiene-and-payload-exclusion), [Constitution §II](../../.specify/memory/constitution.md#ii-layered-boundaries-and-explicit-ownership) |
| **FR-1.2.9 (Phased Baseline)** | Factory-wrapped `create_agent` ReAct baseline | Deferred custom `StateGraph` optimization | [ADR-AGENT-005 §3](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision), [SRS v2.9 §1.2.9](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#129-phased-architecture-strategy-and-stategraph-migration) |
