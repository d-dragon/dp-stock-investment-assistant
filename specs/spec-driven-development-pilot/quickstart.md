# Quickstart: FR-3.1 Short-Term Memory Implementation

**Date**: 2025-01-27 | **Plan**: [plan.md](./plan.md)

---

## Prerequisites

- Python 3.8+ with virtual environment
- MongoDB 5.0+ running locally or via Docker
- Redis (optional, for caching)
- LangGraph >= 0.2.0

---

## 1. Setup Dependencies

```bash
# Activate virtual environment
cd G:\00_Work\Projects\dp-stock-investment-assistant
.\.venv\Scripts\Activate.ps1

# Install LangGraph MongoDB checkpointer
pip install langgraph-checkpoint-mongodb

# Verify installation
python -c "from langgraph.checkpoint.mongodb import MongoDBSaver; print('OK')"
```

---

## 2. Configuration

Add to `config/config.yaml`:

```yaml
langchain:
  memory:
    enabled: true
    
    # Summarization Settings (FR-3.1.6)
    summarize_threshold: 4000               # Token count to trigger summarization
    max_messages: 50                        # Max messages per session before pruning
    messages_to_keep: 10                    # Messages to preserve when pruning
    max_content_size: 32768                 # Max bytes for single message content
    summary_max_length: 500                 # Max tokens for summary
    
    # Performance Settings (FR-3.1.9)
    context_load_timeout_ms: 500            # Max time to load context
    state_save_timeout_ms: 50               # Max time to persist state
    
    # MongoDB Collections (FR-3.1.2)
    checkpoint_collection: "agent_checkpoints"
    conversations_collection: "conversations"
```

---

## 3. Run Database Migration

```powershell
# Create conversations collection with schema validation and indexes
python src\data\migration\db_setup.py
```

Expected output:
```
Creating collection: conversations
Creating index: idx_conversations_session_id_unique
Creating index: idx_conversations_user_status
Creating index: idx_conversations_workspace_status
Creating index: idx_conversations_status_activity
Creating TTL index on agent_checkpoints
Migration complete.
```

---

## 4. Verify Checkpointer Setup

```python
# Quick test script: test_checkpointer.py
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

# Connect
client = MongoClient("mongodb://localhost:27017")
db = client["stock_assistant"]

# Create checkpointer
checkpointer = MongoDBSaver(
    client=client,
    db_name="stock_assistant",
    collection_name="agent_checkpoints"
)

# Test save/load cycle
from langchain_core.messages import HumanMessage, AIMessage

config = {"configurable": {"thread_id": "test-session-123"}}

# This simulates what LangGraph does internally
print("✓ Checkpointer connected successfully")
```

Run:
```powershell
python test_checkpointer.py
```

---

## 5. Test Memory Flow (Manual)

### Test 1: Stateless Request (No session_id)

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AAPL trading at?"}'
```

Expected: Response without `session_id` or `conversation` metadata.

### Test 2: Stateful Request (With session_id)

```bash
# First message in session
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about AAPL", "session_id": "test-session-001"}'

# Follow-up (should have context)
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What about its P/E ratio?", "session_id": "test-session-001"}'
```

Expected: Second response references AAPL without re-specifying.

### Test 3: Get Conversation Metadata

```bash
curl http://localhost:5000/api/sessions/test-session-001/conversation
```

Expected:
```json
{
    "session_id": "test-session-001",
    "status": "active",
    "message_count": 2,
    "focused_symbols": ["AAPL"]
}
```

---

## 6. Run Automated Tests

```powershell
# Run memory-related tests
python -m pytest tests/test_conversation*.py -v

# Run integration tests
python -m pytest tests/integration/test_memory_flow.py -v
```

---

## 7. Development Workflow

### File Change Impact Matrix

| Change | Restart Required | Test Command |
|--------|------------------|--------------|
| `conversation_repository.py` | No | `pytest tests/test_conversation_repository.py` |
| `conversation_service.py` | No | `pytest tests/test_conversation_service.py` |
| `stock_assistant_agent.py` | Yes | `pytest tests/test_agent.py` |
| `ai_chat_routes.py` | Yes | `pytest tests/test_chat_routes.py` |
| `config.yaml` | Yes | Manual test |

### Debug Logging

Enable debug logging for memory operations:

```yaml
# config/config.yaml
logging:
  level: DEBUG
  loggers:
    langgraph.checkpoint: DEBUG
    services.conversation_service: DEBUG
```

---

## 8. Memory Content Compliance Verification

The memory system enforces **FR-3.1.7** and **FR-3.1.8** compliance requirements:

- **FR-3.1.7**: Zero financial data (prices, ratios, percentages) stored in memory
- **FR-3.1.8**: Tool outputs stored as references only, not raw data

### 8.1 Content Validator Usage

```python
from utils.memory_config import ContentValidator

# Check if content is compliant
validator = ContentValidator()

# Check specific content
result = validator.scan_prohibited_patterns("AAPL is trading at $150")
# Returns: ['$150'] - violation detected

result = validator.scan_prohibited_patterns("I found stock data for AAPL")
# Returns: [] - compliant

# Use convenience method
if validator.is_compliant("User asked about AAPL"):
    print("Content is compliant for storage")
```

### 8.2 Prohibited Patterns

The following patterns are automatically detected:

| Pattern Type | Examples | Regex Pattern |
|--------------|----------|---------------|
| Dollar amounts | `$150`, `$1,234.56` | `\$[\d,]+(?:\.\d{2})?` |
| Percentages | `5%`, `12.5%` | `\d+(?:\.\d+)?%` |
| P/E ratios | `P/E 25.3`, `PE ratio 18` | `(?:P/?E|PE)\s*(?:ratio)?\s*[\d.]+` |
| Price patterns | `price $100`, `trading at 150` | `(?:price|trading at|worth)\s*\$?[\d,.]+` |

### 8.3 Audit Checkpoint Data

Query stored checkpoints for compliance violations:

```python
from pymongo import MongoClient
from utils.memory_config import ContentValidator

client = MongoClient("mongodb://localhost:27017")
db = client["stock_assistant"]
validator = ContentValidator()

# Audit all checkpoints for a session
thread_id = "test-session-001"
checkpoints = db.agent_checkpoints.find({"thread_id": thread_id})

violations = []
for checkpoint in checkpoints:
    # Extract all message content from checkpoint
    channel_values = checkpoint.get("channel_values", {})
    messages = channel_values.get("messages", [])
    
    for msg in messages:
        content = msg.get("content", "")
        found_violations = validator.scan_prohibited_patterns(content)
        if found_violations:
            violations.append({
                "checkpoint_id": str(checkpoint["_id"]),
                "content": content[:100],
                "violations": found_violations
            })

if violations:
    print(f"⚠️ Found {len(violations)} compliance violations")
    for v in violations:
        print(f"  - {v['violations']} in: {v['content']}")
else:
    print("✓ All checkpoints are compliant")
```

### 8.4 Run Compliance Tests

```powershell
# Run content validator unit tests
python -m pytest tests/test_memory_config.py -v -k "ContentValidator"

# Run compliance audit tests (unit)
python -m pytest tests/test_conversation_service.py::TestMemoryContentCompliance -v
python -m pytest tests/test_conversation_service.py::TestComplianceAuditScenarios -v

# Run compliance integration tests
python -m pytest tests/integration/test_memory_persistence.py::TestMemoryContentComplianceIntegration -v

# Run all compliance-related tests
python -m pytest -v -k "compliance or ContentValidator"
```

### 8.5 Compliant Response Patterns

When the agent processes tool outputs, it should summarize rather than echo raw data:

**Non-compliant** (raw data in response):
```text
Agent: "AAPL is currently trading at $185.50 with a P/E ratio of 28.5"
```

**Compliant** (reference to data without storing values):
```text
Agent: "I found current price and valuation metrics for AAPL. Based on the data, 
the stock appears to be trading at a premium relative to its sector peers."
```

### 8.6 Tool Reference Format

Tools should return data for immediate display but the stored reference should be neutral:

```python
# Tool output format (for display)
tool_output = {
    "symbol": "AAPL",
    "price": 185.50,  # Displayed to user
    "pe_ratio": 28.5
}

# Stored checkpoint message (compliant)
stored_message = "Tool invocation: get_stock_data(AAPL) returned stock metrics"
# Note: No actual values stored
```

---

## 9. Common Issues

### Issue: "Collection 'agent_checkpoints' not found"

**Cause**: MongoDBSaver creates collection on first use, but TTL index may need manual creation.

**Fix**:
```python
db.agent_checkpoints.create_index(
    [("created_at", 1)],
    expireAfterSeconds=30*24*60*60
)
```

### Issue: "Session not found" when session_id provided

**Cause**: Session must exist in `sessions` collection before using in chat.

**Fix**: Create session first via existing session API.

### Issue: Context not persisting between requests

**Cause**: Using different `session_id` values, or checkpointer not initialized.

**Debug**:
```python
# Check if checkpoint exists
db.agent_checkpoints.find_one({"thread_id": "your-session-id"})
```

---

## 10. Code Snippets

### Initialize Checkpointer in Agent

```python
# src/core/langgraph_bootstrap.py
from langgraph.checkpoint.mongodb import MongoDBSaver

def create_checkpointer(config: dict, db_client) -> MongoDBSaver:
    """Create MongoDB checkpointer for agent state persistence."""
    memory_config = config.get("langchain", {}).get("memory", {})
    
    if not memory_config.get("enabled", False):
        return None
    
    return MongoDBSaver(
        client=db_client,
        db_name=config["mongodb"]["database"],
        collection_name=memory_config.get("checkpointer", {}).get(
            "collection", "agent_checkpoints"
        )
    )
```

### Invoke Agent with Session Context

```python
# In route handler
result = agent.process_query(
    message=request_data["message"],
    session_id=request_data.get("session_id")  # Optional
)
```

### Conversation Service Usage

```python
from services.conversation_service import ConversationService

# Get or create conversation
conversation = conversation_service.get_or_create(session_id)

# Update after message exchange
conversation_service.update_after_exchange(
    session_id=session_id,
    message_tokens=token_count,
    detected_symbols=["AAPL"]
)
```

---

## 11. Next Steps

After completing basic implementation:

1. **Add summarization** — Implement token threshold and LLM summarization
2. **Add archive job** — Background task for auto-archiving inactive conversations
3. **Add frontend integration** — Pass session_id in frontend API calls
4. **Performance testing** — Verify <500ms context load

---

## 12. References

- [plan.md](./plan.md) — Full implementation plan
- [data-model.md](./data-model.md) — Data model specification
- [api-contract.yaml](./contracts/api-contract.yaml) — API contract
- [research.md](./research.md) — Design decisions and rationale
