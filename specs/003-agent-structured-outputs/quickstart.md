# Quickstart Validation Guide: Agent Structured Outputs & Response Tools

**Feature**: `003-agent-structured-outputs`  
**Branch**: `feature/agent-structured-ouputs`  
**Status**: Complete  

---

## Authority & Cross-References

- [Constitution v2.6.0 §Document Referencing in Spec-Kit Workflows](../../.specify/memory/constitution.md#document-referencing-in-spec-kit-workflows)
- [Constitution v2.6.0 §Structured Output Subsystem Governance](../../.specify/memory/constitution.md#structured-output-subsystem-and-response-tool-governance)
- [ADR-AGENT-005 §3 (Decision)](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)
- [ARCHITECTURE_DESIGN.md §4.1.1 (System Context & Structured Output Subsystem)](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#411-system-context)
- [TECHNICAL_DESIGN.md §3.1 (StockAssistantAgent & Structured Execution Behavior)](../../docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration)

---

## 1. Prerequisites & Setup

Ensure the virtual environment is activated and dependencies are up to date:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Run pytest on the new structured output unit test suite
pytest tests/unit/test_structured_output.py -v
```

---

## 2. Validation Scenarios

### Scenario 1: Unit Test Validation of Pydantic Schemas & Response Tools

**Command**:
```bash
pytest tests/unit/test_structured_output.py -k "test_schemas or test_response_tools" -v
```

**Expected Outcome**:
- `StockAnalysisResponse`, `RecommendationResponse`, `GeneralChatResponse` instantiate and validate required fields ([TECHNICAL_DESIGN.md §2.1 Key Characteristics](../../docs/domains/agent/TECHNICAL_DESIGN.md#21-key-characteristics)).
- `submit_stock_analysis`, `submit_recommendation`, `submit_general_chat` register in `ToolRegistry` with `return_direct=True` and `RiskClass.BOUNDED_NON_MUTATING` ([ADR-AGENT-005 §3 Decision](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)).

---

### Scenario 2: Two-Stage Fallback Formatter & Graceful Degradation Test

**Command**:
```bash
pytest tests/unit/test_fallback_formatter.py -v
```

**Expected Outcome**:
- Simulated raw markdown text outputs without tool calls trigger `ChatService._extract_structured_response()`.
- Valid extractions return `AgentResponse(structured_content=..., status=ResponseStatus.PARTIAL)`.
- Malformed extractions or timeouts degrade gracefully to `ResponseStatus.PARTIAL` with `structured_content=None` without throwing unhandled thread exceptions ([SRS v2.9 ERR-1.4](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#err-14-structured-extraction-failure-degradation)).

---

### Scenario 3: MongoDB STM Checkpointer Payload Exclusion Hygiene

**Command**:
```bash
pytest tests/integration/test_chat_structured_flow.py -k "test_checkpointer_exclusion" -v
```

**Expected Outcome**:
- Inspection of `MongoDBSaver` `agent_checkpoints` collection document verifies that `channel_values.messages` stores raw `BaseMessage` arrays and **excludes** `AgentStructuredOutput` Pydantic objects ([SRS v2.9 FR-1.2.8](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#128-stm-checkpointer-state-hygiene-and-payload-exclusion), [Constitution v2.6.0 §II](../../.specify/memory/constitution.md#ii-layered-boundaries-and-explicit-ownership)).

---

### Scenario 4: End-to-End Agent Query Execution (HAPPY PATH)

**Python Execution Script**:
```python
import asyncio
from src.core.stock_assistant_agent import StockAssistantAgent
from src.core.types import ResponseStatus, StockAnalysisResponse

async def main():
    agent = StockAssistantAgent()
    response = await agent.process_query_structured("Danh gia HSG trung han")
    
    print(f"Content length: {len(response.content)}")
    print(f"Status: {response.status}")
    print(f"Structured Content Type: {type(response.structured_content)}")
    
    assert response.status == ResponseStatus.SUCCESS
    assert isinstance(response.structured_content, StockAnalysisResponse)
    assert response.structured_content.symbol == "HSG"

if __name__ == "__main__":
    asyncio.run(main())
```

**Expected Outcome**:
- Output confirms `status == ResponseStatus.SUCCESS` and `structured_content` is a validated `StockAnalysisResponse` object populated with `symbol="HSG"`.

---

### Scenario 5: REST API OpenAPI Contract & SSE Event Stream Verification

**Command**:
```bash
pytest tests/integration/test_chat_structured_flow.py -k "test_api_chat_structured" -v
```

**Expected Outcome**:
- `POST /api/chat` response contains `structured_content` matching `docs/openapi.yaml` `ChatResponse` component schema ([SRS v2.9 IR-3.11](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ir-114-structured-output-transport-edge-serialization)).
- SSE stream filters out raw JSON tool argument tokens and emits a discrete `structured_completion` event frame upon completion ([SRS v2.9 IR-1.14](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ir-114-structured-output-transport-edge-serialization)).
