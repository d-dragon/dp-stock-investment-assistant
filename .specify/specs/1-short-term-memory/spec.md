# Spec: Short-Term Memory (Conversation Buffer)

> **Feature ID**: FR-3.1  
> **Status**: Draft  
> **Created**: 2026-01-27  
> **Author**: AI Agent (Spec Kit)  
> **Source**: [Requirements.md](../../../docs/langchain-agent/Requirements.md) § FR-3.1  
> **Constitution Compliance**: Article III (Memory Architecture Boundaries)

---

## Overview

The Short-Term Memory (STM) system provides conversation context management within a single session. It enables the agent to maintain awareness of prior exchanges, persist session state across reconnections, and support stateless operation when no session tracking is requested.

**Key Constraint (Article III)**: Memory stores **conversational content only**—user messages and agent responses. Financial data, computed metrics, and raw tool outputs are explicitly prohibited in memory storage.

## Clarifications

### Session 2026-01-27

- Q: For E2 “expired session” behavior, should sessions expire (TTL) or use lifecycle states? → A: No expiration; sessions use lifecycle states with manual archive.
### Session 2026-01-28

- Q: Should operational parameters (token thresholds, message limits, TTLs) be hardcoded or configurable? → A: All operational parameters MUST be configurable via configuration file or database.
---

## User Scenarios

### P1: Session-Aware Conversation (Primary Path)

**Actor**: Authenticated user with active session  
**Goal**: Have a multi-turn conversation where the agent remembers context

**Steps**:
1. User initiates conversation with `session_id`
2. User asks: "Provide HAG (HAGL) stock basic information?"
3. Agent do data/information retrieves via tool and responds
4. User asks: "Analyse the latest P&L"
5. Agent recalls stored HAG stock information context and proceed analysis.

**Acceptance Criteria**:
- [ ] Agent references prior exchange accurately (FR-3.1.1)
- [ ] Session context binding demonstrated (FR-3.1.4)
- [ ] Memory contains "HAG basic information" but NOT the fundamentials data (FR-3.1.8)

---

### P2: Session Persistence Across Restart

**Actor**: User with active session  
**Goal**: Resume conversation after system restart without data loss

**Steps**:
1. User has active session with ≥3 message exchanges
2. System restarts (planned or unplanned)
3. User reconnects with same `session_id`
4. Agent demonstrates awareness of prior conversation

**Acceptance Criteria**:
- [ ] Message history matches 100% after restart (FR-3.1.2)
- [ ] Session identifier correctly binds to stored state (FR-3.1.3)
- [ ] First response after reconnect acknowledges prior context (FR-3.1.5)

---

### P3: Stateless Query Mode

**Actor**: Anonymous user or integration without session tracking  
**Goal**: Get agent response without conversation persistence

**Steps**:
1. Client sends query WITHOUT `session_id`
2. Agent processes query normally
3. Agent returns response
4. No conversation record is created or persisted

**Acceptance Criteria**:
- [ ] Agent responds normally without session_id (FR-3.1.6)
- [ ] No conversation data persisted to database
- [ ] Subsequent queries have no memory of prior exchange

---

### P4: Memory Content Compliance Verification

**Actor**: System auditor / compliance check  
**Goal**: Verify memory stores only allowed content types

**Steps**:
1. User has session with multiple tool invocations
2. Tools return: stock prices, ratios, news content
3. System auditor inspects stored memory data
4. Verification confirms compliant storage

**Acceptance Criteria**:
- [ ] Zero price values in stored data (FR-3.1.7)
- [ ] Zero financial ratios or calculated metrics (FR-3.1.7)
- [ ] Tool outputs stored as references only, not raw data (FR-3.1.8)
- [ ] Complies with Constitution Article III §3 (Explicitly Prohibited)

---

### P5: Session Recall on Disconnection

**Actor**: User experiencing network interruption  
**Goal**: Resume conversation after temporary disconnection

**Steps**:
1. User has active conversation with ≥2 messages
2. Network connection drops
3. User reconnects with same `session_id`
4. Agent resumes with awareness of prior context

**Acceptance Criteria**:
- [ ] Valid session_id restores conversation state when `status=active` (FR-3.1.5)
- [ ] First response after reconnect references prior context
- [ ] Message count and history are accurate

---

## Edge Cases

### E1: Session ID Collision Prevention

**Scenario**: Two requests arrive with same session_id simultaneously  
**Expected**: System handles race condition gracefully  
**Handling**: First-write-wins with conflict detection; no data corruption

### E2: Expired Session Access Attempt

**Scenario**: User attempts to resume a session that was manually archived  
**Expected**: Session history can still be loaded; session remains archived  
**Handling**: Return archived status; suggest creating a new active session to continue

### E3: Invalid Session ID Format

**Scenario**: Client provides malformed session_id  
**Expected**: Graceful validation failure  
**Handling**: Return 400 error with clear message; treat as stateless request

### E4: Memory Compliance Violation Attempt

**Scenario**: Code attempts to store financial data in memory  
**Expected**: Storage rejected or data filtered  
**Handling**: Validation layer strips prohibited content; log warning

### E5: System Restart During Active Write

**Scenario**: System restarts while persisting message  
**Expected**: No data corruption  
**Handling**: Atomic writes with transaction; rollback on failure

---

## Requirements

### FR-3.1.1: Session History Retention

| Field | Value |
|-------|-------|
| **Priority** | P0 (Must Have) |
| **Description** | The agent remembers all messages exchanged within a single conversation session |
| **Precondition** | User has an active session |
| **Expected Output** | Given 5 prior exchanges, the agent references any of them accurately when asked "What did I ask earlier?" |

**Verification**:
- Unit test: Store 5 messages, query retrieval, assert all returned
- Integration test: Multi-turn conversation with context recall

---

### FR-3.1.2: Session State Persistence

| Field | Value |
|-------|-------|
| **Priority** | P0 (Must Have) |
| **Description** | Conversation state survives system restarts without data loss |
| **Precondition** | Session was created and has ≥1 message |
| **Expected Output** | After restart, resuming session returns identical message history (100% match) |

**Verification**:
- Integration test: Create session, add messages, restart service, verify history
- Data integrity check: Compare hash of pre/post restart data

---

### FR-3.1.3: Session Identification

| Field | Value |
|-------|-------|
| **Priority** | P0 (Must Have) |
| **Description** | Each conversation is uniquely identifiable by a session identifier |
| **Precondition** | API request includes session_id |
| **Expected Output** | Requests with same session_id return consistent conversation context |

**Verification**:
- Unit test: Two requests with same session_id return same context
- Unit test: Two requests with different session_id return different contexts

---

### FR-3.1.4: Session Context Binding

| Field | Value |
|-------|-------|
| **Priority** | P0 (Must Have) |
| **Description** | Agent responses incorporate prior context from the same session |
| **Precondition** | Session has ≥2 prior messages |
| **Expected Output** | Response demonstrates awareness of earlier conversation (verified by human review or keyword match) |

**Verification**:
- Integration test: Conversation with follow-up questions
- Keyword matching: Agent response contains references to prior topics

---

### FR-3.1.5: Session Recall on Reconnect

| Field | Value |
|-------|-------|
| **Priority** | P1 (Should Have) |
| **Description** | User can resume a conversation after disconnection |
| **Precondition** | Valid session_id provided |
| **Expected Output** | First response after reconnect includes acknowledgment of prior context |

**Verification**:
- Integration test: Disconnect, reconnect, verify context awareness
- Response analysis: First message references prior conversation

---

### FR-3.1.6: Stateless Fallback Mode

| Field | Value |
|-------|-------|
| **Priority** | P0 (Must Have) |
| **Description** | Agent functions without session tracking when no session_id is provided |
| **Precondition** | session_id is null or omitted |
| **Expected Output** | Agent responds normally; no conversation record is persisted |

**Verification**:
- Unit test: Query without session_id returns valid response
- Database check: No conversation record created
- Unit test: Subsequent query has no memory of prior exchange

---

### FR-3.1.7: No Financial Data Persistence

| Field | Value |
|-------|-------|
| **Priority** | P0 (Must Have) |
| **Description** | Memory stores conversation text only, never computed financial metrics |
| **Precondition** | — |
| **Expected Output** | Inspection of stored data shows zero price values, ratios, or calculated figures |
| **Constitution Link** | Article III §3 (Explicitly Prohibited in Memory) |

**Verification**:
- Data inspection test: Query stored messages, assert no numeric financial data
- Regex scan: No patterns matching `$[0-9]+`, `[0-9]+%`, financial ratios
- Audit log: Any attempt to store prohibited data is logged as warning

**Constitution Compliance Note**:
> Article III explicitly prohibits storing: real-time or historical prices, financial ratios and calculated metrics, valuation assessments or price targets, forecasts or forward-looking statements, news content or filing text, analytical conclusions or recommendations.

---

### FR-3.1.8: Conversational Content Only

| Field | Value |
|-------|-------|
| **Priority** | P0 (Must Have) |
| **Description** | Memory contains user messages and agent responses, not raw tool outputs |
| **Precondition** | Tools were invoked during session |
| **Expected Output** | Stored content includes "I found the price" but not the actual price data |
| **Constitution Link** | Article III §3 (Explicitly Prohibited in Memory) |

**Verification**:
- Integration test: Invoke tool, store response, verify tool output not in memory
- Content analysis: Agent response references tool use, raw output is absent
- Schema validation: Message schema has no tool_output field

**Constitution Compliance Note**:
> Memory is for **personalization, not truth** (Article I). Factual data from tools must be retrieved fresh, not recalled from memory.

---

### FR-3.1.9: Configurable Operational Parameters

| Field | Value |
|-------|-------|
| **Priority** | P0 (Must Have) |
| **Description** | All operational parameters MUST be configurable via configuration file (YAML) or database, never hardcoded in source code |
| **Precondition** | — |
| **Expected Output** | System behavior adjusts when configuration values change without code deployment |
| **Constitution Link** | Article VII (Quality Gates - no magic numbers) |

**Required Configurable Parameters:**

| Parameter | Type | Default | Storage | Description |
|-----------|------|---------|---------|-------------|
| `memory.summarize_threshold` | integer | 4000 | Config | Token count triggering summarization |
| `memory.max_messages` | integer | 50 | Config | Maximum messages before window buffer activates |
| `memory.messages_to_keep` | integer | 10 | Config | Messages retained after summarization |
| `memory.max_content_size` | integer | 32768 | Config | Maximum message content size in bytes |
| `memory.summary_max_length` | integer | 500 | Config | Maximum summary length in characters |
| `memory.context_load_timeout_ms` | integer | 500 | Config | Maximum time to load session context |
| `memory.state_save_timeout_ms` | integer | 50 | Config | Maximum time to save agent state |
| `memory.checkpoint_collection` | string | agent_checkpoints | Config | MongoDB collection for LangGraph checkpoints |
| `memory.conversations_collection` | string | conversations | Config | MongoDB collection for conversation metadata |

**Verification**:
- Unit test: Change config value, verify system behavior changes
- Integration test: Override defaults via environment variables
- Validation test: Invalid config values produce clear error messages
- No hardcoded values: Code review confirms no magic numbers

**Design Rationale**:
> Operational parameters vary between environments (dev, staging, production) and may need tuning based on usage patterns. Hardcoding prevents safe experimentation and requires code deployment for adjustments.

---

### FR-3.1.10: Configuration Validation

| Field | Value |
|-------|-------|
| **Priority** | P1 (Should Have) |
| **Description** | Configuration values are validated at startup with clear error messages for invalid values |
| **Precondition** | Application startup |
| **Expected Output** | Invalid configuration prevents startup with actionable error message |

**Validation Rules:**

| Parameter | Validation |
|-----------|------------|
| `summarize_threshold` | Must be > 0 and ≤ 100000 |
| `max_messages` | Must be > 0 and ≤ 1000 |
| `messages_to_keep` | Must be > 0 and ≤ max_messages |
| `max_content_size` | Must be > 0 and ≤ 1048576 (1MB) |
| `summary_max_length` | Must be > 0 and ≤ 2000 |
| `context_load_timeout_ms` | Must be > 0 and ≤ 30000 |
| `state_save_timeout_ms` | Must be > 0 and ≤ 5000 |

**Verification**:
- Unit test: Invalid values raise ConfigurationError at startup
- Unit test: Error messages include parameter name and valid range
- Integration test: Application fails fast on invalid config

---

## Key Entities

### Session

The conversation container that groups related messages.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `session_id` | string | Unique identifier | UUID v4 format; immutable after creation |
| `created_at` | datetime | Creation timestamp | UTC; immutable |
| `updated_at` | datetime | Last activity timestamp | UTC; updated on each message |
| `status` | enum | Lifecycle state | `active`, `summarized`, `archived` |
| `workspace_id` | string | Parent workspace | Foreign key; required |
| `message_count` | integer | Total messages | Auto-incremented; ≥0 |
| `token_count` | integer | Cumulative tokens | Running total; ≥0 |

**Invariants**:
- Session cannot transition backward in lifecycle
- Session belongs to exactly one workspace
- Session does not expire by TTL; it may be manually archived

---

### Message

An individual exchange within a session.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `message_id` | string | Unique identifier | UUID v4 format |
| `session_id` | string | Parent session | Foreign key; required |
| `role` | enum | Message author | `user`, `assistant`, `system` |
| `content` | string | Message text | No financial data (FR-3.1.7); max size per `memory.max_content_size` config |
| `timestamp` | datetime | Creation time | UTC; immutable |
| `sequence` | integer | Order in session | Auto-incremented; ≥1 |

**Invariants**:
- Content must not contain raw tool outputs (FR-3.1.8)
- Content must not contain financial metrics (FR-3.1.7)
- Content size enforced by configurable limit (FR-3.1.9)

---

### ConversationState

Runtime state for active sessions (not persisted).

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `session_id` | string | Session reference | Links to Session entity |
| `pinned_intent` | string | User's stated goal | Optional; cleared on session end |
| `focused_symbols` | array | Actively researched symbols | Optional; updated dynamically |
| `assumptions` | array | User-stated constraints | Optional; applies to responses |
| `last_tool_refs` | array | Referenced (not stored) tool outputs | Transient; not persisted |

**Invariants**:
- State is ephemeral within session lifecycle
- Financial data in `last_tool_refs` is reference only, not persisted

---

## Success Criteria

### SC-1: Session Context Accuracy

**Metric**: Agent correctly references prior context  
**Target**: ≥95% accuracy on 5-message conversation recall  
**Measurement**: Automated test suite with human-verified golden set

---

### SC-2: Session Persistence Reliability

**Metric**: Message history intact after restart  
**Target**: 100% data match (hash comparison)  
**Measurement**: Pre/post restart hash comparison in CI/CD

---

### SC-3: Stateless Mode Functionality

**Metric**: No-session queries return valid responses  
**Target**: 100% success rate  
**Measurement**: API test without session_id returns 200 status

---

### SC-4: Memory Compliance Rate

**Metric**: Stored data contains zero prohibited content  
**Target**: 100% compliance (zero violations)  
**Measurement**: Automated scan of stored messages for prohibited patterns

---

### SC-5: Session Identification Uniqueness

**Metric**: No session_id collisions  
**Target**: P(collision) < 1e-18 (UUID v4 guarantee)  
**Measurement**: Collision detection in storage layer

---

### SC-6: Reconnection Context Restoration

**Metric**: First response after reconnect demonstrates context awareness  
**Target**: ≥90% of reconnections (P1 requirement)  
**Measurement**: Integration test with disconnect/reconnect scenario

---

### SC-7: Response Time for Context Loading

**Metric**: Session context loads within acceptable latency  
**Target**: Within `memory.context_load_timeout_ms` (default: 500ms) for sessions with ≤`memory.max_messages` (default: 50) messages  
**Measurement**: Performance test with instrumented timing

---

### SC-8: Configuration Compliance

**Metric**: System behavior matches configuration values  
**Target**: 100% of configurable parameters honored  
**Measurement**: Unit tests verify each parameter affects system behavior

---

## Constitution Compliance Checklist

| Article | Section | Requirement | Verification |
|---------|---------|-------------|--------------|
| III | §1 (STM Allowed) | Conversation state, active context | ✅ Session, Message entities |
| III | §3 (Prohibited) | No prices, ratios, forecasts | ✅ FR-3.1.7, FR-3.1.8 |
| I | Principle I | Memory never stores facts | ✅ Memory for personalization only |
| I | Principle V | Tools compute, LLM reasons | ✅ Tool outputs not in memory |

---

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| MongoDB | Infrastructure | Persistence for Session and Message entities |
| LangGraph Checkpointing | Library | State persistence mechanism |
| Constitution v1.1.0 | Governance | Memory boundary rules |

---

## Open Questions

1. **Archive Policy**: Who/what can archive a session, and is it manual-only (P0) or does it also support future automation?
2. ~~**Summary Trigger**: At what token count should summarization occur?~~ **RESOLVED**: Configurable via `memory.summarize_threshold` (default: 4000 tokens) per FR-3.1.9.
3. **Workspace Isolation**: Is cross-workspace session access ever permitted? (FR-3.2.6 suggests no)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1.0 | 2026-01-28 | AI Agent | Added FR-3.1.9 (Configurable Parameters), FR-3.1.10 (Config Validation), SC-8; Updated Message entity, SC-7; Resolved Open Question #2 |
| 1.0.0 | 2026-01-27 | AI Agent | Initial spec from FR-3.1.x transformation |
