# ADR-AGENT-005: Adopt Route-Adapted Custom Response Tool Pattern and Phased Architecture Strategy for Agent Structured Outputs

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-AGENT-005 |
| **Title** | Adopt Route-Adapted Custom Response Tool Pattern and Phased Architecture Strategy for Agent Structured Outputs |
| **Status** | Proposed |
| **Date** | 2026-07-21 |
| **Authors** | System & Architecture Team |
| **Domain** | Agent Subsystem / Structured Output & Runtime Execution |
| **Governing SRS** | [SRS v2.9](../SOFTWARE_REQUIREMENTS_SPECIFICATION.md) (FR-1.2.5–1.2.9, AC-10, IR-1.14, IR-3.11, ERR-1.4) |
| **Related Documents** | [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) §2A.3, [structured_output_technical_analysis.md](../../research/structured_output_technical_analysis.md), [stategraph_migration_analysis.md](../../research/stategraph_migration_analysis.md), [structured_output_review_report.md](../../research/structured_output_review_report.md) |

---

## 1. Context and Problem Statement

The Stock Investment Assistant Agent requires predictable, machine-readable structured JSON responses matching domain Pydantic schemas (e.g., `StockAnalysisResponse`, `RecommendationResponse`, `GeneralChatResponse`) to drive rich UI rendering in the frontend.

However, the core agent execution layer must satisfy strict architectural constraints:
1. **Token Efficiency**: Must avoid secondary LLM formatting calls that double prompt token cost.
2. **Model Agnosticism**: Must operate reliably across OpenAI, Anthropic, Gemini, Grok, and local open-source models (DeepSeek, Llama-3).
3. **Gateway Security**: Must pass through `ToolGateway.execute()` admission without bypassing risk envelopes or trace logging.
4. **Boundary Discipline**: Must maintain a clean separation between **Output Contract Schema Validation** and **Behavioral Policy Enforcement** (`ResponseGuardrailMiddleware`).
5. **Runtime Stability**: Must deliver 100% of functional requirements without introducing high-risk, state-breaking graph re-architectures prematurely.

---

## 2. Decision Drivers

- **Prompt Token Overhead**: Native LLM Provider Response Formatting (Option A) appends a formatting step after ReAct execution over the full conversation history, incurring 100%+ extra prompt input token overhead.
- **Provider Parity**: Not all model providers natively support strict JSON mode or schema binding, whereas standard function/tool calling is universally supported.
- **Gateway Governance**: Control-plane response tools must execute through `ToolGateway.execute()` under an explicit risk class (`RiskClass.BOUNDED_NON_MUTATING`) rather than circumventing gateway checks.
- **State Preservation**: Prematurely re-architecting the agent runtime from factory-wrapped `create_agent` to custom `StateGraph` introduces checkpointer migration risks (MongoDB state schema drift) for zero immediate functional gain.

---

## 3. Decision

We decide to:

1. **Adopt the Route-Adapted Custom Response Tool Pattern as Primary Architecture Strategy**:
   - Register route-specific response tools (`submit_stock_analysis`, `submit_recommendation`, `submit_general_chat`) in `ToolRegistry` with `return_direct=True`.
   - Dynamic injection of the route-matched response tool into the model's tool surface during single-turn ReAct execution.
   - Response tools emit structured JSON directly as tool call arguments, incurring **0% extra prompt token overhead** on happy-path executions.

2. **Adopt the Two-Stage Service-Layer Post-Processing Formatter as Secondary Fallback**:
   - If a model omits calling the response tool and outputs plain markdown text, the service layer transparently invokes an out-of-band `model.with_structured_output()` call.
   - If both response tool argument parsing and fallback formatting fail, the system returns `ResponseStatus.PARTIAL` with raw text preserved, preventing thread crashes.

3. **Classify Response Tools under `RiskClass.BOUNDED_NON_MUTATING`**:
   - Control-plane response tools are classified as `RiskClass.BOUNDED_NON_MUTATING` (codebase enum) / `bounded_transformation` (architecture category).
   - This ensures immediate admission through `ToolSurfaceBuilder` and `ToolGateway.execute()` without violating gateway security controls.

4. **Adopt a Phased Architecture Strategy (Active Single-Turn ReAct Baseline → Deferred Graph Optimization)**:
   - **Active Single-Turn ReAct Baseline**: Deliver 100% of structured output value using the factory-wrapped `create_agent` ReAct runtime.
   - **Deferred Custom StateGraph Optimization**: Preserve custom compiled `StateGraph` (with `structured_response` state channel and in-graph self-repair loops) as a deferred architectural runway for future multi-agent specialist routing.

---

## 4. Options Considered and Evaluation

| Evaluation Dimension | Native LLM Provider Response Formatting | Route-Adapted Custom Response Tool Pattern (Accepted) | Two-Stage Post-Processing Formatter (Accepted Fallback) | Custom StateGraph Migration (Deferred Optimization) |
|----------------------|-----------------------------------------|-------------------------------------------------------|---------------------------------------------------------|----------------------------------------------------|
| **Token Cost Overhead** | ❌ High (100%+ extra prompt tokens on secondary pass) | ✅ **0% Overhead** (single-turn tool call) | ⚠️ Conditional (100% extra tokens only on fallback trigger) | ✅ 0% Overhead |
| **Model Agnosticism** | ❌ Vendor-locked (OpenAI JSON mode only) | ✅ **Universal** (supported by all tool-calling LLMs) | ✅ Universal | ✅ Universal |
| **Gateway Integration** | ❌ Bypasses Tool Gateway | ✅ **100% Gateway Admitted** (`RiskClass.BOUNDED_NON_MUTATING`) | N/A (Service-layer out-of-band) | ✅ Gateway Admitted |
| **Runtime Risk** | ⚠️ Low | ✅ **Zero Runtime Risk** (fits current `create_agent`) | ✅ Low | ❌ High (Checkpointer state schema drift) |

---

## 5. Consequences

### Positive Consequences

- **100% Requirement Coverage**: Fulfills SRS `FR-1.2.5`–`FR-1.2.9` and `AC-10` with zero extra prompt token overhead on happy paths.
- **Model Flexibility**: Enables switching between OpenAI, Grok, Anthropic, and local LLMs without rewriting response formatting code.
- **Fail-Safe Operation**: `ResponseStatus.PARTIAL` ensures malformed outputs never crash active conversation threads or lose user-visible text.
- **Risk-Managed Delivery**: Avoids premature `StateGraph` rewrites, protecting MongoDB checkpointer stability.

### Negative Consequences and Mitigations

- **Message History Tool Call Overhead**: ReAct message history retains response tool calls; mitigated by message history pruning prior to STM compaction.
- **Schema Maintenance**: Requires maintaining Pydantic v2 schemas; mitigated by unifying schemas under the `AgentStructuredOutput` polymorphic union.

---

## 6. Traceability

- **Governing SRS Requirements**: `FR-1.2.2`, `FR-1.2.5`, `FR-1.2.6`, `FR-1.2.7`, `FR-1.2.8`, `FR-1.2.9`, `AC-10.1`–`AC-10.6`, `IR-1.14`, `IR-3.11`, `ERR-1.4`.
- **Roadmap Alignment**: Section `2A.3` (Structured Outputs enhancement track).
- **Research Authority**: [structured_output_technical_analysis.md](../../research/structured_output_technical_analysis.md), [stategraph_migration_analysis.md](../../research/stategraph_migration_analysis.md), [structured_output_review_report.md](../../research/structured_output_review_report.md).
