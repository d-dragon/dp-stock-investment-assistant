# Feature Specification: Agent Integration Verification & Structured Outputs Architectural Alignment

**Feature Branch**: `feature/agent-integration-verification`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "conduct a feature spec at current branch that cover and include this implementation_plan.md"

## Governance Context *(mandatory)*

This feature is governed by the following system architecture and technical design specifications:
- **Agent Integration Architecture**: [docs/domains/agent/ARCHITECTURE_DESIGN.md#41-context-and-boundary-view](file:///g:/00_Work/Projects/dp-stock-investment-assistant/docs/domains/agent/ARCHITECTURE_DESIGN.md#41-context-and-boundary-view)
- **Fallback Formatter Design**: [docs/domains/agent/TECHNICAL_DESIGN.md#384-two-stage-service-layer-post-processing-formatter](file:///g:/00_Work/Projects/dp-stock-investment-assistant/docs/domains/agent/TECHNICAL_DESIGN.md#384-two-stage-service-layer-post-processing-formatter)
- **Persistent Data Schema**: [docs/domains/agent/TECHNICAL_DESIGN.md#389-persistent-data-schema--mongodb-realization](file:///g:/00_Work/Projects/dp-stock-investment-assistant/docs/domains/agent/TECHNICAL_DESIGN.md#389-persistent-data-schema--mongodb-realization)
- **Durable Decision Index**: [docs/domains/agent/DECISIONS/AGENT_ARCHITECTURE_DECISION_RECORDS.md#index-of-decisions](file:///g:/00_Work/Projects/dp-stock-investment-assistant/docs/domains/agent/DECISIONS/AGENT_ARCHITECTURE_DECISION_RECORDS.md#index-of-decisions)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Structured Output Fallback Formatter Recovery (Priority: P1)

When the LLM model client fails to call the route-adapted custom response tool (e.g. `submit_stock_analysis`, `submit_recommendation`, or `submit_general_chat`) and outputs raw markdown text instead, the system must trigger an out-of-band post-processing fallback call. This fallback parses the raw text into the appropriate structured schema using the model's native `.with_structured_output()` mechanism, preventing the response from being returned as unstructured text.

**Why this priority**: Highly critical for system resilience and formatting reliability. Ensures that raw text responses from the model are normalized back into structured JSON to support downstream UI presentation without failing.

**Independent Test**: Can be fully tested by mocking the model's initial generation to return a raw markdown text message instead of a tool call, and verifying that the fallback extractor is invoked and successfully outputs a structured response matching the expected schema.

**Acceptance Scenarios**:

1. **Given** the agent is executing a structured query route, **When** the LLM generates a raw text response omitting the custom response tool call, **Then** the service layer calls the fallback formatter using the model's `.with_structured_output()` method and returns a successfully parsed structured output payload.
2. **Given** the fallback formatter is triggered, **When** the out-of-band LLM call fails or times out, **Then** the system returns a partial response envelope with `ResponseStatus.PARTIAL` containing the raw message contents to prevent thread crashes.

---

### User Story 2 - Complete Conversation Metadata Persistence (Priority: P2)

When a structured agent response is successfully generated or recovered, the full structured payload must be persisted in the MongoDB `conversations` collection as `last_turn_metadata.last_structured_output` inside the database record. This makes the structured output accessible to presentation layers.

**Why this priority**: Required for UI integration and full backend traceability. Without this persistence, the frontend cannot retrieve structured summaries from previous turns.

**Independent Test**: Can be tested by invoking the chat service, waiting for a structured response, and verifying that the database record updated in the `conversations` collection includes the populated `last_turn_metadata.last_structured_output` field.

**Acceptance Scenarios**:

1. **Given** a successful structured turn completion, **When** the conversation repository's update metadata path runs, **Then** the MongoDB write includes the fully serialized structured output payload under `last_turn_metadata.last_structured_output`.

---

### User Story 3 - ADR Verification and Promotion (Priority: P3)

The architectural decision records (ADRs) that document the agent prompt composition, prompt asset versioning, tool gateways, and structured output patterns must be promoted from `Proposed` to `Accepted` to align documentation with implementation evidence.

**Why this priority**: Establishes the authoritative architecture baseline for subsequent development phases, preventing documentation drift.

**Independent Test**: Check that `ADR-AGENT-002`, `ADR-AGENT-003`, `ADR-AGENT-004`, and `ADR-AGENT-005` list status as `Accepted` and the ADR index references them correctly.

**Acceptance Scenarios**:

1. **Given** ADR 002 through 005 are currently draft/proposed, **When** the feature specification is verified, **Then** these files are updated to status `Accepted` and the index file is synchronized.

---

### Edge Cases

- **Fallback Formatter Timeout**: When the fallback formatter call times out (e.g. due to model latency or network issues), the agent must gracefully degrade by returning `ResponseStatus.PARTIAL` with the raw text preserved rather than raising an exception.
- **Malformed Fallback Output**: When the out-of-band extraction call fails validation (e.g. invalid JSON or missing schema properties), the system must preserve the raw text content and return status `PARTIAL`.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `StockAssistantAgent` MUST expose the underlying LangChain LLM instance as `agent.model` to allow outer service layers to use native model functionality.
- **FR-002**: `ChatService._extract_structured_response` MUST invoke the fallback formatter by calling `.with_structured_output()` on the exposed `agent.model` property when a raw markdown response is received.
- **FR-003**: `ChatService` MUST store the fully serialized structured output payload under `last_turn_metadata.last_structured_output` when recording turn completion metadata in the database.
- **FR-004**: The project's ADR files in `docs/domains/agent/DECISIONS/` (`ADR-AGENT-002`, `ADR-AGENT-003`, `ADR-AGENT-004`, and `ADR-AGENT-005`) MUST be updated to `Accepted` status.
- **FR-005**: The ADR index `AGENT_ARCHITECTURE_DECISION_RECORDS.md` MUST reflect the `Accepted` status of all promoted ADRs.

### Key Entities

- **AgentStructuredOutput**: Polymorphic response payload union representing the verified output models.
- **TurnMetadata**: MongoDB document structure storing tracking information for each turn, including the structured output.
- **ADR**: Architecture Decision Record documenting durable design decisions.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of plain-text fallback scenarios successfully recover structured output payloads without throwing unhandled thread exceptions.
- **SC-002**: Every successful structured query writes the corresponding JSON serialization to the database with 0 omissions.
- **SC-003**: All 4 target ADRs match implementation status and resolve links correctly in the ADR index.

---

## Assumptions

- We assume the existing MongoDB checkpointer collection `agent_checkpoints` remains thin and free of heavy structured payloads.
- We assume LangChain `ChatOpenAI`'s `.with_structured_output` remains stable and compatible with the pydantic schemas.
- Personalization LTM rules in `constitution.md` remain valid.
