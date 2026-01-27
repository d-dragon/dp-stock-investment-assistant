# Requirements Checklist: Short-Term Memory (Conversation Buffer)

> **Feature ID**: FR-3.1  
> **Spec Version**: 1.0.0  
> **Created**: 2026-01-27  
> **Status**: Ready for Implementation

---

## P0 Requirements (Must Have - MVP Blocking)

### FR-3.1.1: Session History Retention
- [ ] **Implementation**: Message storage with full history retrieval
- [ ] **Unit Test**: Store 5 messages, query retrieval, assert all returned
- [ ] **Integration Test**: Multi-turn conversation with context recall
- [ ] **Review**: Code review approved

### FR-3.1.2: Session State Persistence
- [ ] **Implementation**: Durable storage with restart survival
- [ ] **Unit Test**: Persist session, simulate restart, verify integrity
- [ ] **Integration Test**: Full restart cycle with data verification
- [ ] **Review**: Code review approved

### FR-3.1.3: Session Identification
- [ ] **Implementation**: UUID-based session identifier system
- [ ] **Unit Test**: Same session_id returns same context
- [ ] **Unit Test**: Different session_id returns different contexts
- [ ] **Review**: Code review approved

### FR-3.1.4: Session Context Binding
- [ ] **Implementation**: Context injection in agent prompt
- [ ] **Integration Test**: Conversation with follow-up questions
- [ ] **Verification**: Keyword matching for context references
- [ ] **Review**: Code review approved

### FR-3.1.6: Stateless Fallback Mode
- [ ] **Implementation**: No-session query handling
- [ ] **Unit Test**: Query without session_id returns valid response
- [ ] **Database Check**: No conversation record created
- [ ] **Unit Test**: Subsequent query has no memory
- [ ] **Review**: Code review approved

### FR-3.1.7: No Financial Data Persistence
- [ ] **Implementation**: Content filtering/validation layer
- [ ] **Unit Test**: Attempt to store price, verify rejection/filtering
- [ ] **Regex Test**: Scan for prohibited patterns
- [ ] **Constitution Compliance**: Article III §3 verified
- [ ] **Review**: Code review approved

### FR-3.1.8: Conversational Content Only
- [ ] **Implementation**: Tool output filtering
- [ ] **Integration Test**: Invoke tool, verify raw output not stored
- [ ] **Schema Validation**: Message schema excludes tool_output
- [ ] **Constitution Compliance**: Article III §3 verified
- [ ] **Review**: Code review approved

---

## P1 Requirements (Should Have - Production Readiness)

### FR-3.1.5: Session Recall on Reconnect
- [ ] **Implementation**: Reconnection context restoration
- [ ] **Integration Test**: Disconnect, reconnect, verify context awareness
- [ ] **Response Analysis**: First message references prior conversation
- [ ] **Review**: Code review approved

---

## Success Criteria Verification

| SC | Metric | Target | Status |
|----|--------|--------|--------|
| SC-1 | Context accuracy | ≥95% | ⬜ Not Started |
| SC-2 | Persistence reliability | 100% match | ⬜ Not Started |
| SC-3 | Stateless mode success | 100% | ⬜ Not Started |
| SC-4 | Memory compliance | 100% (zero violations) | ⬜ Not Started |
| SC-5 | Session ID uniqueness | P(collision) < 1e-18 | ⬜ Not Started |
| SC-6 | Reconnection context | ≥90% | ⬜ Not Started |
| SC-7 | Context load time | <500ms | ⬜ Not Started |

---

## Constitution Compliance Sign-Off

| Check | Requirement | Verified By | Date |
|-------|-------------|-------------|------|
| ⬜ | Article III §1: STM stores only allowed content | | |
| ⬜ | Article III §3: No prohibited financial data | | |
| ⬜ | Article I.1: Memory never stores facts | | |
| ⬜ | Article I.5: Tools compute, LLM reasons | | |

---

## Implementation Progress Summary

| Category | Total | Completed | Remaining |
|----------|-------|-----------|-----------|
| P0 Requirements | 7 | 0 | 7 |
| P1 Requirements | 1 | 0 | 1 |
| Success Criteria | 7 | 0 | 7 |
| Constitution Checks | 4 | 0 | 4 |

**Overall Status**: ⬜ Ready for Implementation

---

## Notes

- FR-3.1.7 and FR-3.1.8 directly enforce Constitution Article III
- Stateless mode (FR-3.1.6) is critical for backward compatibility
- Session persistence (FR-3.1.2) depends on MongoDB + LangGraph checkpointing
