# Prompt System Architecture and Design

> **Document Version**: 1.3  
> **Last Updated**: May 6, 2026  
> **Phase**: 2A.2 - System Prompt Refinement and A/B Testing  
> **Status**: Research refined; practical scope narrowed to project-scoped implementation targets  
> **Primary Source Requirement**: Official vendor and regulator documentation only  
> **Governing ADR**: [ADR-001 — Layered LLM Architecture](./decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Scope and Project Boundaries](#scope-and-project-boundaries)
3. [Current State Assessment](#current-state-assessment)
4. [Research Synthesis and Design Drivers](#research-synthesis-and-design-drivers)
5. [Alignment with ADR-001](#alignment-with-adr-001)
6. [Target Prompt System Architecture](#target-prompt-system-architecture)
7. [LangChain Integration Scope](#langchain-integration-scope)
8. [LangSmith Integration Scope](#langsmith-integration-scope)
9. [Agentic Prompting Standards for Investment Analysis](#agentic-prompting-standards-for-investment-analysis)
10. [Prompt Versioning and Experiment Design](#prompt-versioning-and-experiment-design)
11. [Configuration Requirements](#configuration-requirements)
12. [Implementation Roadmap](#implementation-roadmap)
13. [Verification Strategy](#verification-strategy)
14. [Research Log and Decision Log](#research-log-and-decision-log)
15. [Document Update Log](#document-update-log)
16. [Reference Index](#reference-index)

---

## Executive Summary

### Objective

Define an industrial-standard prompt management architecture for the Stock Investment Assistant that:

- externalizes prompt assets for the current ReAct runtime and future specialist agents into version-controlled files;
- supports prompt versioning and controlled A/B testing;
- attaches prompt identity and experiment metadata to LangSmith traces and evaluations;
- supports a future multi-agent topology with distinct prompt contracts for orchestration, ReAct tool use, and RAG retrieval-grounded synthesis;
- stays within the project’s layered architecture boundaries for facts, memory, and tools;
- applies finance-domain safeguards appropriate for stock and investment workflows.

### Design Position

The prompt system should remain **project-scoped, repo-owned, and provider-neutral**.
This project already uses LangChain agents, LangGraph execution, MongoDB-backed short-term memory, and LangSmith-oriented tracing guidance. The prompt system must therefore be implemented as an internal runtime capability of the existing agent stack, not as a provider-specific dashboard feature or a separate orchestration service. The design target is now a controlled **multi-agent system**, but it should evolve from the current single-agent baseline rather than bypass it.

### Core Conclusion

The correct architectural move is to adopt a **local prompt registry and versioned prompt asset model** under `src/prompts/`, wire it into `StockAssistantAgent` as the source of truth for the current ReAct path, and extend that registry to support agent-specific prompt contracts for future specialist agents. The existing `StockQueryRouter` (`src/core/stock_query_router.py`) with its 8-route semantic classification already provides a routing foundation that the prompt system should build on rather than replace. LangSmith remains the **observability and evaluation layer** rather than the runtime prompt source.

### Multi-Agent Design Conclusion

The recommended **near-term target** is a **Skills pattern** — a single agent that loads specialized prompt context on demand based on the request category, without requiring a full multi-agent runtime. This is the lowest-cost path from the current single-agent baseline and directly leverages the existing `StockQueryRouter` with its 8 route categories (`PRICE_CHECK`, `NEWS_ANALYSIS`, `PORTFOLIO`, `TECHNICAL_ANALYSIS`, `FUNDAMENTALS`, `IDEAS`, `MARKET_WATCH`, `GENERAL_CHAT`).

The **medium-term target** is a **router-orchestrated specialist architecture**:

- a top-level orchestrator or routing layer decides whether the request stays on the current ReAct analyst path or is delegated to a retrieval-grounded specialist;
- each specialist receives a smaller, role-specific prompt contract instead of one oversized shared prompt;
- shared investment-policy and safety rules stay centralized in global prompt partials; and
- direct user-facing handoffs between agents are avoided initially in favor of centralized orchestration and synthesis.

LangChain’s multi-agent documentation provides a clear performance trade-off: the Skills pattern uses ~3 model calls for one-shot queries (same as Router pattern), while Subagents and Handoffs require 4+ calls. The Skills pattern is recommended when tasks are “simple and focused” — which matches most stock-analysis queries. Full multi-agent is justified only when context management, specialization, or parallelization become limiting factors.

> **Cost note**: Moving from single-agent to multi-agent doubles or quadruples LLM calls per query (orchestrator call + specialist call + optional validation + synthesis). This cost must be justified by measurable quality gains before adoption.

Source: [LangChain Multi-Agent](https://docs.langchain.com/oss/python/langchain/multi-agent)

### Implementation Status at Time of Research

| Capability | Status | Evidence |
|---|---|---|
| ReAct agent uses external prompt files | ❌ Not implemented | `src/core/stock_assistant_agent.py` still uses `REACT_SYSTEM_PROMPT` |
| Prompt file loader exists | ⚠️ Partial | `src/core/langchain_adapter.py` has `PromptBuilder`, but only for fallback-style prompt building |
| Prompt version config exists | ❌ Not implemented | `config/config.yaml` has no `prompts.*` section |
| Prompt variants and weighted selection | ❌ Not implemented | Roadmap only |
| LangSmith tracing baseline exists | ⚠️ Partial | `config/config.yaml`, `LANGSMITH_STUDIO_GUIDE.md`, `langsmith` dependency present |
| Prompt-version metadata in traces | ❌ Not implemented | No prompt-version tagging or experiment metadata path exists |
| Dataset-backed prompt comparison | ❌ Not implemented | No evaluation harness for prompt variants exists |
| Multi-agent prompt families | ❌ Not implemented | No orchestrator, RAG specialist, or agent-family registry exists |
| Retrieval-grounded specialist prompt | ❌ Not implemented | No RAG-specific prompt contract or retrieval prompt path is wired |

---

## Scope and Project Boundaries

### In Scope

- The primary ReAct system prompt for `StockAssistantAgent`
- Shared global prompt policy for multiple future agent roles
- Specialist prompt contracts for orchestrator, ReAct, and RAG-style agents
- Version-controlled prompt assets under the repository
- Prompt selection rules and experiment assignment
- LangChain middleware and agent integration points relevant to prompting
- LangSmith tags, metadata, datasets, and experiments for prompt evaluation
- Multi-agent routing and handoff prompt contracts at the architectural level
- Investment-domain prompt rules for evidence, disclaimers, uncertainty, and anti-hype behavior

### Out of Scope

- Frontend prompt editing UI
- Prompt storage in provider dashboards as the canonical production source
- Replacing tool logic, repository logic, or memory design with prompt logic
- Automated trading, market-making, or execution workflows
- Legal or compliance approval automation

### Multi-Agent Scope Clarification

This refinement adds **multi-agent prompt-system design** to scope, but not a full runtime implementation of multi-agent orchestration in this document. The design here defines how prompt assets, contracts, routing rules, and evaluation strategy should evolve so that a future multi-agent implementation remains aligned with ADR-001 and the repo’s current architecture.

### Project Boundary Rules

| Boundary | Required Rule |
|---|---|
| Prompt vs facts | Prompts govern behavior and output format; prompts do not become a hidden fact store |
| Prompt vs memory | Prompt system may reference STM/LTM boundaries, but must not duplicate memory persistence logic |
| Prompt vs tools | Prompts should direct the model to use tools for live or verifiable data rather than answer from prior model knowledge |
| Prompt vs provider | Prompt assets must remain repo-owned and provider-neutral; provider-specific prompt features are optional accelerators, not the system of record |
| Prompt vs experimentation | LangSmith evaluates and compares prompt behavior; it should not become a hard runtime dependency for the agent to answer queries |
| Shared policy vs local role prompts | Global investment-policy rules are inherited by all agents; specialist prompts may narrow scope but must not weaken core safety or grounding rules |
| Routing vs specialist behavior | The orchestrator decides where work goes; specialist prompts execute their domain-specific contract and must not silently broaden their authority |

---

## Current State Assessment

### Runtime Reality

The roadmap target in [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) is materially ahead of the live implementation.

The live runtime is still a **single-agent ReAct design**. The multi-agent target described in this refinement is therefore architectural guidance for the next design step, not a claim that orchestrator or RAG specialist paths already exist.

#### Current Prompt Path

The primary ReAct path is still hardcoded in `StockAssistantAgent`:

- `src/core/stock_assistant_agent.py`
  - `REACT_SYSTEM_PROMPT` is declared inline.
  - `_build_agent_executor()` passes that string directly into `create_agent(..., system_prompt=...)`.

#### Existing Prompt Utilities

The repository already contains:

- `src/core/langchain_adapter.py`
  - `_load_prompt_file()` with basic file caching
  - `PromptBuilder` that composes a fallback prompt around a system file
- `src/prompts/system_stock_assistant.txt`
- `src/prompts/system_stock_assistant-vn.txt`

These assets are useful source material, but they are **not** the primary system prompt source for the ReAct runtime.

#### Missing Multi-Agent Building Blocks

The current repo does not yet expose any of the following as first-class runtime components:

- orchestrator or router prompt contracts;
- specialist prompt families keyed by role;
- a RAG-specific prompt contract that treats retrieved content as data-only context;
- a handoff or synthesis schema between agents; or
- thread-level evaluation criteria for multi-agent trajectories.

#### Current Configuration Surface

`config/config.yaml` includes:

- `langchain.tools.*`
- `langchain.memory.*`
- `langchain.tracing.*`

It does **not** include:

- `prompts.active_version`
- `prompts.directory`
- `prompts.variants`
- `prompts.selection_mode`
- experiment weights or evaluation settings scoped to prompt variants

#### Current LangSmith Surface

The project already has a LangSmith dependency and local Studio guide:

- `requirements.txt` includes `langsmith`
- `docs/langchain-agent/LANGSMITH_STUDIO_GUIDE.md` documents local tracing usage
- `src/core/langgraph_bootstrap.py` establishes the LangGraph entry path

However, prompt-version traceability is not currently modeled as a first-class concern.

### Current State vs Target State

| Area | Current State | Target State |
|---|---|---|
| Prompt source of truth | Hardcoded string in agent class | Versioned file assets in repo |
| Prompt structure | Single static prompt blob | Shared global policy + role-specific prompt contracts + controlled dynamic sections |
| Prompt selection | Fixed at import/runtime construction | Config-driven fixed, weighted, or evaluation mode |
| Prompt observability | No prompt identity on traces | `prompt_version`, `prompt_variant`, `experiment_id` tagged in LangSmith |
| Experimentation | Manual prompt edits only | Dataset-backed offline evaluation plus guarded online observation |
| Finance safeguards | Mixed across prompt text and docs | Explicit, documented rules grounded in project ADR and regulator guidance |
| Agent topology | Single ReAct agent | Router-orchestrated ReAct and RAG specialists with centralized synthesis |

---

## Research Synthesis and Design Drivers

### LangChain Agent Runtime

Official LangChain guidance confirms that:

- `create_agent` (from `langchain.agents`) is the production-ready graph-based runtime for agents;
- agents accept a `system_prompt` parameter directly;
- runtime prompt changes should use **middleware** rather than hard-forking the agent implementation:
  - `@dynamic_prompt` — generates prompts from agent state and context at runtime;
  - `@wrap_model_call` — intercepts model invocation for dynamic model selection, retries, or fallback;
  - `@wrap_tool_call` — intercepts tool execution for error handling, logging, or permissions;
  - `@before_model` / `@after_model` — hooks for pre/post model-step logic;
  - `AgentMiddleware` class with `state_schema` for structured custom state;
  - Built-in middleware: `SummarizationMiddleware`, `HumanInTheLoopMiddleware`;
- middleware is passed via `middleware=[...]` parameter to `create_agent`;
- too many tools can overload the model and increase errors; dynamic tool filtering is a first-class pattern;
- `AgentState` (TypedDict) supports custom state propagation across agent steps; and
- structured output is available via `response_format` with `ProviderStrategy` or `ToolStrategy`.

Source: [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents), [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware)

### LangChain Multi-Agent Guidance

Official LangChain multi-agent guidance confirms that multi-agent architectures are most justified when:

- a single agent is overloaded with too many tools and too much context;
- specialist domains need their own focused instructions and context windows;
- multiple teams need clean ownership boundaries; or
- work should run in parallel or through controlled routing.

LangChain documents five multi-agent patterns with performance characteristics:

| Pattern | Model Calls (One-Shot) | Best For |
|---|---|---|
| **Skills** | ~3 | Simple focused tasks; single agent loads context on demand |
| **Router** | ~3 | Parallel execution; explicit classification step |
| **Subagents** | ~4 | Large-context domains; parallel specialist invocation |
| **Handoffs** | ~3 (one-shot), 5+ (repeat) | Dynamic state-based routing; single/repeat requests |
| **Custom workflow** | Varies | Bespoke LangGraph flows mixing deterministic and agentic |

For this repo, the **Skills pattern** is the recommended near-term stepping stone because:

- the existing `StockQueryRouter` already classifies requests into 8 categories;
- a single agent loading route-specific prompt context avoids multi-agent overhead;
- migration to a full Router or Subagents pattern is straightforward once specialization gaps are measured.

LangChain explicitly warns: "Not every complex task requires [multi-agent] — a single agent with the right (sometimes dynamic) tools and prompt can often achieve similar results."

Source: [LangChain Multi-Agent](https://docs.langchain.com/oss/python/langchain/multi-agent)

### LangGraph Workflow Guidance

Official LangGraph workflow guidance is also directly relevant because it distinguishes deterministic workflows from dynamic agents and shows routing, orchestrator-worker, evaluator-optimizer, and parallelization as first-class patterns.

For this repo, the main implication is that a future multi-agent design should not be implemented as free-form agent chatter. It should instead be expressed as a bounded workflow where:

- a router or orchestrator classifies the request;
- a specialist node executes a focused contract;
- an optional evaluator or validator can reject weak outputs; and
- a synthesizer produces the final user-facing answer.

Source: [LangGraph Workflows and Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

### LangSmith Observability and Evaluation

Official LangSmith guidance confirms that:

- traces are collections of runs for one operation;
- tags and metadata are intended for filtering, grouping, and analysis;
- threads are linked by `session_id`, `thread_id`, or `conversation_id` metadata;
- offline evaluation should run on curated datasets before shipping;
- online evaluation can monitor live quality after release; and
- datasets can preserve relevant inputs and outputs beyond trace retention windows.

Sources:

- [LangSmith Observability Concepts](https://docs.langchain.com/langsmith/observability-concepts)
- [Add Metadata and Tags to Traces](https://docs.langchain.com/langsmith/add-metadata-tags)
- [Configure Threads](https://docs.langchain.com/langsmith/threads)
- [LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation)
- [Custom Instrumentation](https://docs.langchain.com/langsmith/annotate-code)

LangSmith’s multi-turn evaluation guidance adds one more requirement for the multi-agent target: if conversation-level quality is to be assessed, traces must preserve thread-compatible top-level `messages` data and stable thread identifiers. This matters because future multi-agent quality checks should score not only single answers, but also routing quality, trajectory quality, and cross-turn coherence.

Source: [Set Up Multi-Turn Online Evaluators](https://docs.langchain.com/langsmith/online-evaluations-multi-turn)

### OpenAI Prompt and Tool Design Guidance

Official OpenAI guidance reinforces several design rules that are directly relevant here:

- use higher-authority developer or instruction layers for business rules;
- structure prompts into clear sections such as identity, instructions, examples, and context;
- pin production systems to explicit model snapshots and maintain evals alongside prompt changes;
- keep reusable prompt content external to integration code when operationally useful;
- define tools with clear names, schemas, descriptions, and strict validation; and
- keep the initial tool surface small, because tool definitions consume prompt tokens and accuracy drops when the tool surface is too large.

Sources:

- [OpenAI Prompt Engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)

OpenAI’s agent and file-search guidance reinforces the same separation of concerns at a platform level: knowledge access, tools, and control-flow logic are independent primitives. For this repo that supports a design where retrieval-oriented agents should receive bounded retrieval tools and knowledge context rather than inherit the entire ReAct analyst contract.

Sources:

- [OpenAI Agents](https://developers.openai.com/api/docs/guides/agents)
- [OpenAI File Search](https://developers.openai.com/api/docs/guides/tools-file-search)

### Retrieval and RAG Guidance

Official LangChain retrieval guidance is important because it separates:

- **2-step RAG**, where retrieval always precedes generation;
- **agentic RAG**, where an agent decides when and how to retrieve; and
- **hybrid RAG**, where query refinement, retrieval validation, and answer validation can be added.

For this project, that means a future RAG specialist should not simply reuse the current ReAct prompt. Its prompt contract must be retrieval-first, source-aware, and defensive against indirect prompt injection in retrieved content.

LangChain’s RAG tutorial is explicit that retrieved content must be treated as data only and that prompts should tell the model to ignore any instructions inside retrieved documents. That is especially important in an investment-analysis system where filings, news, and third-party documents may contain language that should inform the answer but never override system policy.

Sources:

- [LangChain Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [Build a RAG Agent with LangChain](https://docs.langchain.com/oss/python/langchain/rag)

### Agentic System Design Guidance

Anthropic’s engineering guidance is useful here because it frames the design trade-offs clearly:

- start with the simplest composable solution that works;
- prefer workflows over fully autonomous agents when tasks are predictable;
- add complexity only when it measurably improves outcomes;
- invest heavily in tool documentation and the agent-computer interface; and
- evaluate and iterate systematically rather than optimizing only by intuition.

Source: [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

### Investment-Domain Safeguards

SEC and Investor.gov guidance is directly relevant to this application class:

- investors should not make decisions solely on social or hype-based signals;
- guarantees of high returns with little or no risk are classic fraud red flags;
- social sentiment and social recommendation tools can be inaccurate, incomplete, misleading, stale, or manipulative;
- investors should verify sources and use publicly disclosed company information and fundamental analysis rather than rely on one signal source.

Sources:

- [Social Media and Stock Tip Scams — Investor Alert](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/social-media-stock-scams)
- [Social Sentiment Investing Tools — Think Twice Before Trading Based on Social Media](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-18)
- [Types of Fraud — Investor.gov](https://www.investor.gov/protect-your-investments/fraud/types-fraud)

### Practical Design Drivers for This Repo

The external research and the repo’s internal architecture both support the same conclusion:

1. Prompt assets should be externalized and versioned in the repository.
2. Prompt behavior should be observable through tags and metadata, not inferred from code revisions alone.
3. Evaluation should begin offline on curated datasets before any online split exposure.
4. Finance-domain prompts should aggressively prefer verifiable data and must avoid hype, certainty theater, and social-signal overreach.
5. Dynamic prompting should be narrow and deterministic, not an unbounded string-assembly system.
6. Multi-agent prompting should centralize global safety rules while shrinking each specialist’s local context and authority.
7. The initial multi-agent shape should favor centralized routing and synthesis over user-visible agent handoffs.

---

## Alignment with ADR-001

This prompt-system design must comply with the layered LLM rules in [AGENT_ARCHITECTURE_DECISION_RECORDS.md](./decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md).

| ADR Principle | Prompt-System Implication |
|---|---|
| Memory never stores facts | Prompt templates must never embed mutable market facts or cached analysis as if they were static policy |
| RAG never stores opinions | Prompt should instruct the model to ground factual claims in retrieved or tool-provided evidence, not inject analyst-style conclusions into base policy text |
| Fine-tuning never stores knowledge | Prompt iteration may improve structure and tone, but should not be used as a substitute for market data access |
| Prompting controls behavior, not data | The prompt defines rules, boundaries, output expectations, and tool-use policy; the data still comes from tools, repositories, or retrieval |
| Tools compute numbers, LLM reasons about them | The prompt must explicitly direct the agent to fetch live or verifiable figures rather than infer prices, ratios, or recommendations |
| Investment data sources are external | Prompt text should require source-aware reasoning and disclosure of missing or stale data |
| Market manipulation safeguards are enforced | Prompt text must forbid manipulative framing, certainty, or disguised recommendations intended to influence trading behavior |

---

## Target Prompt System Architecture

### Design Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                     Prompt System Architecture                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Shared Prompt Assets (repo-owned)                                 │
│  src/prompts/agent_system/                                         │
│   ├─ global/                                                       │
│   │   ├─ investment_safety.md                                      │
│   │   ├─ response_contract.md                                      │
│   │   └─ tool_use_policy.md                                        │
│   ├─ orchestrator/                                                 │
│   ├─ react_analyst/                                                │
│   ├─ rag_research/                                                 │
│   └─ registry_manifest.yaml (optional)                             │
│                                                                    │
│  Prompt Runtime                                                    │
│   ├─ PromptRegistry (load, resolve, cache prompt assets)           │
│   ├─ PromptComposer (global partials + role contract + selection)  │
│   └─ @dynamic_prompt middleware (narrow deterministic sections)     │
│                                                                    │
│  Agent Integration                                                 │
│   ├─ Orchestrator / router prompt                                  │
│   ├─ ReAct specialist prompt                                       │
│   ├─ RAG specialist prompt                                         │
│   └─ RunnableConfig / LangSmith metadata injection                 │
│                                                                    │
│  Evaluation Layer                                                  │
│   ├─ LangSmith datasets                                             │
│   ├─ Offline experiments                                            │
│   ├─ Pairwise and rubric scorers                                    │
│   ├─ Thread-level trajectory evaluators                             │
│   └─ Guarded online observation                                     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Recommended Evolution Path

**Phase A — Skills pattern (near-term)**:

1. `StockQueryRouter` classifies the request into one of 8 route categories;
2. the prompt system loads a route-specific prompt context (e.g., `TECHNICAL_ANALYSIS` loads chart interpretation rules, `FUNDAMENTALS` loads financial statement analysis rules);
3. the single ReAct agent executes with the composed prompt (global policy + route-specific context);
4. no additional model calls are needed for routing — classification uses semantic-router, not an LLM call.

**Phase B — Router-orchestrated specialists (medium-term)**:

1. an orchestrator or router classifies the request (may reuse StockQueryRouter or introduce LLM-based routing);
2. the router delegates to a ReAct analyst or a RAG research specialist;
3. the selected specialist executes a role-specific prompt contract;
4. an optional validation step can reject unsupported or weak evidence; and
5. a final synthesis step produces the user-facing response in the shared response contract.

Phase A is preferred as the starting point because it reuses existing infrastructure, adds zero additional LLM calls, and provides measurable baseline data before committing to multi-agent complexity.

### Proposed Prompt Asset Model

Recommended directory shape:

```text
src/prompts/
└── agent_system/
    ├── global/
    │   ├── investment_safety.md
    │   ├── response_contract.md
    │   └── tool_use_policy.md
    ├── react_analyst/
    │   ├── v1.md
    │   ├── v1_vi.md
    │   ├── candidates/
    │   └── routes/                    # Route-specific context for Skills pattern
    │       ├── price_check.md
    │       ├── news_analysis.md
    │       ├── portfolio.md
    │       ├── technical_analysis.md
    │       ├── fundamentals.md
    │       ├── ideas.md
    │       ├── market_watch.md
    │       └── general_chat.md
    ├── partials/
    │   ├── citation_rules.md
    │   ├── uncertainty_contract.md
    │   └── evidence_labeling.md
    ├── orchestrator/                  # Future: multi-agent orchestration
    ├── rag_research/                  # Future: RAG specialist
    └── CHANGELOG.md
```

Each prompt file should support lightweight metadata frontmatter:

```yaml
---
name: react_analyst_v1
version: 1.0.0
locale: en
status: active
owner: core-agent
change_type: behavioral
agent_role: react_analyst
inherits:
  - global/investment_safety
  - global/response_contract
  - global/tool_use_policy
last_reviewed: 2026-04-01
---
```

### Prompt Composition Rules

The prompt system should keep a strict separation between:

- **shared static policy**: finance-domain rules, answer contract, tool-use discipline, evidence and uncertainty standards inherited by all agents;
- **role contract**: the agent-specific mission, authority limits, input assumptions, and output obligations for one agent role;
- **controlled dynamic context**: language mode, user expertise mode, workspace mode, or experiment marker;
- **runtime factual context**: retrieved documents, tool outputs, and conversation state.

Only the first three belong in the prompt-system architecture. Runtime factual context remains in the existing tool, memory, and retrieval layers.

### Agent Prompt Taxonomy

| Agent Role | Primary Responsibility | Prompt Characteristics |
|---|---|---|
| `orchestrator` | classify, route, and synthesize | short, control-focused, no market opinion generation, minimal tool access |
| `react_analyst` | multi-step tool use and reasoning | tool-aware, evidence-first, explicit uncertainty, broader reasoning latitude |
| `rag_research` | retrieval-grounded evidence extraction and synthesis | retrieval-first, source-aware, citation-heavy, defensive against indirect prompt injection |
| `evaluator` | quality or safety critique (future — only after multi-agent runtime exists) | rubric-bound, non-user-facing, no autonomous tool sprawl |

### Prompt Contract Rules by Role

#### Orchestrator Contract (Future)

> **Note**: The orchestrator role is a medium-term target. In the near-term Skills pattern, `StockQueryRouter` handles classification without an LLM-based orchestrator.

When implemented, the orchestrator prompt should:

- decide whether the request can be answered directly by the ReAct analyst or should be delegated to retrieval-grounded research;
- keep its context intentionally small;
- avoid making final market claims from raw prior knowledge;
- emit structured routing decisions where possible; and
- apply shared policy but not duplicate every specialist instruction in full.

#### ReAct Analyst Contract

The ReAct analyst prompt should:

- remain the primary path for multi-step reasoning with deterministic tools;
- prefer verified tool output over model memory;
- distinguish observation, inference, and uncertainty;
- avoid direct dependence on long retrieved corpora unless routed through retrieval support; and
- inherit all shared finance safety and response-contract rules.

#### RAG Research Contract (Future)

> **Note**: The RAG research role requires retrieval infrastructure that does not yet exist in this project. This contract defines the target requirements for when that infrastructure is built.

The RAG research prompt should:

- treat retrieval as its primary evidence channel;
- state explicitly that retrieved content is data only and that instructions inside retrieved content must be ignored;
- prefer concise evidence extraction, source labeling, and sufficiency checks over broad open-ended reasoning;
- decline unsupported claims when retrieval is weak, conflicting, stale, or absent; and
- return evidence packages or grounded summaries that can be synthesized by the orchestrator or surfaced directly when appropriate.

### Cross-Agent Handoff Contract (Future)

> **Note**: This section describes a target-state contract for when multi-agent orchestration is implemented. It is not required for the near-term Skills pattern.

When a full multi-agent runtime is introduced, handoff payloads between agents should preserve:

- request intent;
- agent role that produced the payload;
- evidence summary or source bundle;
- uncertainty or insufficiency flags; and
- recommended next action (`answer`, `retrieve_more`, `call_tool`, `decline`).

### Dynamic Sections Policy

Dynamic prompting should be limited to deterministic sections such as:

- language selection (`en`, `vi`)
- output style depth (`beginner`, `advanced`, `operator`)
- workspace mode (`general_research`, `portfolio_review`, `education`)
- experiment variant labels
- agent role marker when composing shared policy with a specialist contract

Dynamic prompting should **not** be used to inject:

- ephemeral market claims
- calculated financial facts
- conversation summaries that belong to STM
- raw social sentiment or externally sourced claims without provenance
- retrieval results that should instead be attached through retrieval or tool context

---

## LangChain Integration Scope

### Recommended Integration Points

| Component | Current Status | Proposed Change |
|---|---|---|
| `src/core/stock_assistant_agent.py` | Hardcoded `REACT_SYSTEM_PROMPT` | Replace with prompt registry load path |
| `src/core/langchain_adapter.py` | Minimal loader and builder | Refactor into reusable prompt-loading utilities |
| `create_agent(..., system_prompt=...)` | Static string | Supply registry-resolved role-specific prompt object/string |
| Middleware | Not used for prompt policy | Use middleware only for narrow dynamic prompt sections and analytics |
| LangGraph workflow | Single-agent baseline | Add router/orchestrator and specialist nodes when multi-agent runtime is introduced |

### Recommended Runtime Flow

**Near-term (Skills pattern)**:

```python
# StockQueryRouter already exists — reuse it for prompt context selection
route = stock_query_router.classify(user_request)
selection = prompt_registry.resolve(
  agent_role="react_analyst",
  route_category=route.category,  # e.g. TECHNICAL_ANALYSIS
  version=config["prompts"]["agents"]["react_analyst"]["active_version"],
)

# Use @dynamic_prompt middleware for narrow runtime sections
@dynamic_prompt
def inject_route_context(state, config):
    """Load route-specific prompt context based on classification."""
    route_ctx = prompt_registry.get_route_context(state["route_category"])
    return f"{selection.system_prompt}\n\n{route_ctx}"

agent = create_agent(
  model=llm,
  tools=route.enabled_tools,
  system_prompt=selection.system_prompt,
  checkpointer=self._checkpointer,
  name="react_analyst",
  middleware=[inject_route_context],
)
```

**Medium-term (multi-agent)**:

```python
route = orchestrator.invoke(user_request)
selection = prompt_registry.resolve(
  agent_role=route.agent_role,
  version=config["prompts"]["agents"][route.agent_role]["active_version"],
)

specialist = create_agent(
  model=llm,
  tools=route.enabled_tools,
  system_prompt=selection.system_prompt,
  checkpointer=self._checkpointer,
  name=route.agent_role,
  middleware=[inject_route_context, analytics_middleware],
)
```

**Common metadata injection (both phases)**:

```python
invoke_config = {
  "configurable": {"thread_id": conversation_id},
  "metadata": {
    "agent_role": route.agent_role,
    "prompt_version": selection.version,
    "prompt_variant": selection.variant,
    "prompt_experiment_id": selection.experiment_id,
    "route_category": route.category,
  },
}
```

### Why Middleware Instead of Ad Hoc Prompt String Assembly

LangChain explicitly treats middleware as the extension point for context injection, tool filtering, analytics, and model behavior changes. The specific middleware hooks relevant to this project are:

| Hook | Use Case in This Project |
|---|---|
| `@dynamic_prompt` | Load route-specific prompt context based on `StockQueryRouter` classification |
| `@wrap_model_call` | Dynamic model selection aligned with `ModelClientFactory` fallback logic |
| `@wrap_tool_call` | Tool error handling, logging, permissions enforcement |
| `@before_model` / `@after_model` | Analytics, trace metadata injection, guardrail checks |

This approach is preferred over scattering conditional prompt logic across `StockAssistantAgent`, route handlers, and service code.

Sources: [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents), [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware)

### LangChain-Specific Recommendations

1. Keep a stable base system prompt asset and use middleware only for narrow deltas.
2. Do not expose an oversized tool surface by default; use the prompt to reinforce when tools should be used, but control actual exposure in code.
3. Avoid coupling prompt versions to model-provider-specific syntax unless the feature is intentionally provider-scoped.
4. Prefer a small, typed prompt context contract over arbitrary Jinja variable injection.
5. For the multi-agent target, route into role-specific prompts rather than merging every specialist rule into one system prompt.
6. Keep the orchestrator prompt smaller than specialist prompts so routing cost stays predictable.

---

## LangSmith Integration Scope

### LangSmith Role in This Design

LangSmith should serve five functions in the prompt system:

1. trace prompt identity and experiment assignment;
2. compare prompt variants offline on curated datasets;
3. monitor live quality after controlled rollout;
4. preserve experiment evidence independently from raw trace retention windows where necessary.
5. evaluate multi-turn routing and specialist trajectories once the multi-agent runtime exists.

### Required Trace Metadata

At minimum, every top-level run should attach:

| Field | Type | Purpose |
|---|---|---|
| `prompt_version` | metadata | Exact prompt file or semver |
| `prompt_variant` | metadata | Named variant label used for cohorting |
| `prompt_selection_mode` | metadata | `fixed`, `weighted`, `offline_eval`, `shadow`, `forced` |
| `prompt_experiment_id` | metadata | Stable experiment identifier |
| `agent_role` | metadata | Distinguish orchestrator, ReAct, RAG, or future evaluator runs |
| `routing_decision` | metadata | Capture orchestrator or router output for trajectory analysis |
| `conversation_id` | metadata | Thread grouping and existing STM alignment |
| `model_provider` | metadata | Prompt behavior comparison by provider |
| `model_name` | metadata | Prompt behavior comparison by snapshot |
| `env` | tag or metadata | `local`, `staging`, `production` |

Recommended trace tags:

- `prompt:v1`
- `variant:baseline`
- `agent:react_analyst`
- `experiment:exp_2026_04_prompt_v2`
- `env:staging`

This is directly aligned with LangSmith’s intended use of tags and metadata for grouping, filtering, and analysis. Source: [Add Metadata and Tags to Traces](https://docs.langchain.com/langsmith/add-metadata-tags)

### Threading Rule

LangSmith requires thread metadata to be present on all relevant runs if thread-level filtering and aggregation are expected to work reliably. Because this repo already uses conversation-scoped STM, the prompt-system design should standardize on the existing conversation identifier model and propagate it consistently. Source: [Configure Threads](https://docs.langchain.com/langsmith/threads)

### Evaluation Scope

#### Offline Evaluation

Use before promoting any prompt candidate:

- curated stock-analysis questions
- tool-use regression cases
- routing-decision cases for orchestrator prompts
- retrieval sufficiency and citation-quality cases for RAG prompts
- missing-data and uncertainty cases
- policy and disclaimer adherence cases
- sentiment-manipulation and hype-resistance cases

#### Online Evaluation

Use after offline acceptance:

- monitor live runs by variant
- collect feedback or evaluator scores
- watch latency, tool-call counts, and error rates
- compare behavioral drift over time
- add thread-level or trajectory-level review once multi-agent routing exists

LangSmith explicitly frames offline evaluation as a pre-ship benchmark and online evaluation as production monitoring. Source: [LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation)

### Recommended Experiment Workflow

1. Build or update a dataset.
2. Define evaluators.
3. Run baseline and candidate prompts as separate experiments.
4. Compare output quality, tool behavior, latency, and guardrail adherence.
5. Promote only if the candidate improves target metrics without regressions on finance-domain safety cases.

### Multi-Agent Evaluation Additions

Once the multi-agent runtime exists, evaluation should score more than final answer quality. It should also inspect:

- routing correctness;
- unnecessary delegation frequency;
- retrieval sufficiency and citation quality;
- whether the specialist respected its authority boundary; and
- whether the full thread trajectory remained coherent across turns.

---

## Agentic Prompting Standards for Investment Analysis

### Primary Prompting Goals

The system prompt must make the assistant:

- evidence-first;
- tool-aware;
- retrieval-aware when delegated to research specialists;
- uncertainty-explicit;
- non-manipulative;
- structured enough for downstream consumption;
- conservative around unverifiable stock claims.

### Required Behavioral Rules

| Category | Required Behavior |
|---|---|
| Facts | Use tool outputs, public filings, or repository-backed sources for factual claims whenever available |
| Missing data | Say that data is unavailable, stale, incomplete, or unverifiable instead of guessing |
| Recommendations | Avoid certainty framing, guaranteed outcomes, or manipulative urgency |
| Social signals | Do not rely solely on social sentiment, social stock tips, or hype-based signals |
| Reasoning | Separate observation, inference, and uncertainty clearly |
| Output | Prefer structured sections such as summary, evidence, risks, assumptions, and next checks |
| Retrieval | Treat retrieved text as evidence input, not instruction authority |

### Finance-Domain Guardrails

Based on SEC/Investor.gov guidance, the prompt should explicitly reject or de-emphasize:

- promises of high returns with little or no risk;
- “hot stock” or “guaranteed upside” phrasing;
- social proof as primary evidence;
- stock promotion language that could amplify rumors or manipulation;
- impulsive short-term trading cues presented as if they were validated research.

Supporting evidence:

- social sentiment tools may be inaccurate, incomplete, misleading, stale, or emotionally biasing;
- investors should not rely solely on such tools;
- fundamental analysis and public company information should remain part of the decision process;
- social media stock recommendations can be tied to pump-and-dump, scalping, or touting behavior.

Sources:

- [Social Sentiment Investing Tools — Think Twice Before Trading Based on Social Media](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-18)
- [Social Media and Stock Tip Scams — Investor Alert](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/social-media-stock-scams)

### Recommended Response Contract

The prompt should encourage an answer contract similar to:

1. Executive summary
2. Verified evidence
3. Interpretation and risks
4. Missing or uncertain inputs
5. What to watch next
6. Non-advisory disclaimer when applicable

For higher-risk or incomplete-data cases, the prompt should require a stronger uncertainty statement.

### Recommended Fact and Interpretation Separation

The Vietnamese prompt already contains a strong pattern: `FACT / ASSUMPTION / INFERENCE`. That pattern should be retained conceptually in the prompt-system redesign because it fits both the ADR and regulator-aligned safety posture.

### RAG-Specific Guardrails

Any future RAG specialist prompt should additionally require:

- source labeling or traceable evidence bundles for retrieved material;
- explicit acknowledgement when retrieved evidence is insufficient or conflicting;
- instruction/data separation, for example with delimiters or explicit retrieved-context sections; and
- refusal to follow formatting or behavioral instructions embedded inside retrieved content.

---

## Prompt Versioning and Experiment Design

### Versioning Model

Recommended identifiers:

| Field | Example |
|---|---|
| Prompt file | `react_analyst/v1.md` |
| Prompt name | `react_analyst_v1` |
| Semantic version | `1.0.0` |
| Variant label | `baseline`, `concise`, `evidence_strict` |
| Experiment ID | `exp_2026_04_prompt_v2_eval1` |
| Agent role | `orchestrator`, `react_analyst`, `rag_research` |

### Selection Modes

| Mode | Behavior | Intended Use |
|---|---|---|
| `fixed` | Always load one configured version | Default production behavior |
| `weighted` | Choose from configured variants by weight | Controlled experimentation in non-critical environments |
| `forced` | Force a specific prompt version or variant | QA, debugging, and offline evaluation |
| `shadow` | Run a non-user-facing comparison path | Evaluation and diagnostics |

### A/B Testing Guardrails

1. Start with offline evaluation before any weighted live exposure.
2. Never run uncontrolled live experiments in financial recommendation surfaces.
3. Keep the behavioral difference between variants narrow and measurable.
4. Do not mix prompt experiments with simultaneous model, tool, and retrieval changes unless the experiment is explicitly factorial.
5. Always log the active model snapshot along with the prompt version.
6. For multi-agent experiments, change one layer at a time: routing prompt, specialist prompt, or synthesis prompt.

### Evaluation Dimensions

| Dimension | Description |
|---|---|
| Evidence quality | Does the response use verifiable data and cite uncertainty correctly? |
| Routing quality | Was the correct specialist selected, or was delegation unnecessary? |
| Tool-use correctness | Were appropriate tools invoked when needed? |
| Tool-use efficiency | Were tools overused or called redundantly? |
| Retrieval grounding | Did the answer stay within retrieved evidence where required? |
| Finance-domain safety | Does the response avoid hype, guarantees, and manipulative framing? |
| Structured reasoning | Are facts, assumptions, and interpretation clearly separated? |
| Latency | Does the prompt change materially degrade response time? |
| Fallback behavior | Does the prompt hold up across provider fallback paths? |

### Recommended Dataset Families

**Core datasets (implement first)**:

- `tool_selection_regression` — verify correct tool invocation for known query types
- `missing_data_and_staleness` — verify uncertainty disclosure when data is unavailable or stale
- `finance_safety_and_hype_resistance` — verify rejection of manipulative framing and social hype signals
- `route_classification_accuracy` — verify `StockQueryRouter` route assignments match expected categories

**Extended datasets (implement when relevant features exist)**:

- `fundamental_analysis` — evaluation of financial statement analysis quality
- `technical_analysis_with_caveats` — evaluation of chart analysis with appropriate uncertainty
- `retrieval_grounding_and_citation_quality` — RAG-specific, implement when RAG specialist exists
- `routing_and_specialist_delegation` — multi-agent routing, implement when orchestrator exists
- `vietnam_market_context` — locale-specific evaluation

---

## Configuration Requirements

### Proposed Config Schema

```yaml
prompts:
  directory: "src/prompts/agent_system"
  selection_mode: "fixed"  # fixed | weighted | forced | shadow
  default_locale: "vi"
  global_partials:
    - "global/investment_safety.md"
    - "global/response_contract.md"
    - "global/tool_use_policy.md"
  agents:
    react_analyst:
      active_version: "v1"
      variants:
        - name: "baseline"
          version: "v1"
          file: "react_analyst/v1.md"
          weight: 1.0
          status: "active"
        - name: "evidence_strict"
          version: "v2_candidate"
          file: "react_analyst/candidates/v2_candidate.md"
          weight: 0.0
          status: "candidate"
    # orchestrator:        # Uncomment when multi-agent runtime is introduced
    #   active_version: "v1"
    #   variants:
    #     - name: "baseline"
    #       version: "v1"
    #       file: "orchestrator/v1.md"
    #       weight: 1.0
    #       status: "active"
    # rag_research:        # Uncomment when RAG specialist is implemented
    #   active_version: "v1"
    #   variants:
    #     - name: "baseline"
    #       version: "v1"
    #       file: "rag_research/v1.md"
    #       weight: 1.0
    #       status: "active"
  route_contexts:
    enabled: true
    directory: "react_analyst/routes"
    supported_routes:
      - PRICE_CHECK
      - NEWS_ANALYSIS
      - PORTFOLIO
      - TECHNICAL_ANALYSIS
      - FUNDAMENTALS
      - IDEAS
      - MARKET_WATCH
      - GENERAL_CHAT
  routing:
    mode: "skills"  # skills | single_specialist | multi_specialist
    default_agent: "react_analyst"
    allow_parallel_specialists: false

  experiments:
    enabled: false
    active_id: ""
    allow_live_weighted_selection: false

langsmith:
  prompt_tracking:
    enabled: true
    metadata_keys:
      - prompt_version
      - prompt_variant
      - prompt_experiment_id
      - prompt_selection_mode
```

### Config Validation Rules

- `active_version` must resolve to a real prompt asset.
- exactly one active baseline variant must exist for production fallback.
- each configured `agent_role` must resolve to one active baseline variant.
- weighted selection must not be enabled unless all weighted variants are valid and evaluation-approved.
- locale variants must fail closed to the default locale, not to an empty prompt.
- malformed metadata frontmatter must block prompt activation.
- orchestrator routing targets must resolve only to registered agent roles.
- candidate RAG prompts must not be promoted until retrieval-grounding tests pass.

---

## Implementation Roadmap

### Phase 1 - ReAct Baseline Extraction

- move the current ReAct system prompt into `src/prompts/agent_system/react_analyst/v1.md`;
- preserve the current behavior as the baseline variant;
- document provenance from the existing hardcoded string and Vietnamese source prompt.

### Phase 2 - Shared Prompt Runtime Refactor

- add prompt-loading utilities with metadata parsing;
- introduce `PromptRegistry` or equivalent;
- replace `REACT_SYSTEM_PROMPT` as the source of truth;
- keep legacy fallback prompt builder isolated until intentionally refactored.

### Phase 2.5 - Skills Pattern Integration

- create route-specific prompt context files under `react_analyst/routes/` for each `StockQueryRouter` category;
- wire `@dynamic_prompt` middleware to compose global policy + route-specific context based on `StockQueryRouter` classification;
- add `route_category` to LangSmith trace metadata;
- measure route-classification accuracy and prompt-context relevance as baseline for future multi-agent decision.

### Phase 3 - Multi-Agent Prompt Taxonomy (Future)

- introduce shared global partials for investment safety, response contract, and tool-use policy;
- define agent-role prompt folders for `orchestrator` and `rag_research`;
- formalize a handoff schema between specialist outputs and any synthesis layer;
- prerequisite: measurable evidence that the Skills pattern is insufficient for the project's needs.

### Phase 4 - Trace and Metadata Wiring

- activate prompt-version metadata injection for top-level runs;
- ensure `conversation_id` is present consistently in LangSmith thread metadata;
- add prompt, agent-role, and experiment tags for filtering and comparison.

### Phase 5 - Offline Evaluation Harness

- create the 4 core prompt-eval datasets (tool_selection_regression, missing_data_and_staleness, finance_safety_and_hype_resistance, route_classification_accuracy);
- add code and rubric evaluators;
- baseline current prompt performance;
- compare candidate prompts pairwise and against regression thresholds.

### Phase 6 - Controlled Rollout

- keep production on `fixed` mode initially;
- promote only after offline evaluation approval;
- use `shadow` or small-scope weighted observation before broader rollout if needed.

### Phase 7 - Multi-Agent Runtime Introduction (Future)

> **Prerequisite**: Phases 1–6 must be stable and producing measurable quality data before multi-agent work begins.

- add a router or orchestrator workflow in LangGraph;
- keep `react_analyst` as the default fallback path;
- introduce `rag_research` only after retrieval quality, grounding, and citation behavior are verified;
- add extended evaluation datasets (retrieval_grounding, routing_and_specialist_delegation);
- defer direct user-visible handoffs until centralized routing and synthesis are proven stable.

### Formal Implementation Backlog

The phase outline above expresses architectural intent. The backlog below converts that intent into a dependency-ordered delivery plan that can be executed, estimated, and gated. The milestone-level execution mirror for this backlog is maintained in [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md).

#### Prioritization Model

- **P0**: Required to remove the current hardcoded-prompt risk and establish a safe prompt runtime baseline.
- **P1**: Required to deliver route-aware behavior, observability completeness, and evaluation-readiness.
- **P2**: Required for controlled experimentation and broader rollout flexibility, but only after P0/P1 exit gates pass.
- **P3**: Future-state work for multi-agent prompt families and specialist-runtime evolution.

#### Dependency-Ordered Backlog

| Order | Backlog ID | Priority | Depends On | Scope | Primary Deliverables | Exit Gate |
|---|---|---|---|---|---|---|
| 1 | PS-01 | P0 | None | Establish prompt asset baseline | `src/prompts/agent_system/react_analyst/v1.md`; provenance note from `REACT_SYSTEM_PROMPT`; baseline locale decision for current runtime | Baseline prompt file reproduces current ReAct behavior and is reviewed as the canonical initial asset |
| 2 | PS-02 | P0 | PS-01 | Implement prompt asset loading and validation | `PromptRegistry` or equivalent loader; metadata frontmatter parsing; file cache; schema validation; `_baseline` fallback asset convention | Loader can resolve a valid prompt asset and rejects malformed metadata before activation |
| 3 | PS-03 | P0 | PS-01, PS-02 | Add prompt config surface and fail-closed validation | `prompts.*` config section in `config/config.yaml`; active version resolution; baseline variant rule; locale fallback rule | Config validation blocks invalid prompt references and guarantees one production-safe baseline |
| 4 | PS-04 | P0 | PS-02, PS-03 | Replace hardcoded ReAct prompt path | `StockAssistantAgent` loads prompt from registry instead of `REACT_SYSTEM_PROMPT`; legacy `PromptBuilder` isolated as non-authoritative fallback utility | ReAct path loads from versioned asset, not inline constant |
| 5 | PS-05 | P0 | PS-04 | Wire prompt identity into response and trace metadata | `prompt_version`, `prompt_variant`, `conversation_id`, provider/model metadata on top-level runs and structured response metadata | Relevant runs expose prompt identity consistently for filtering and audit |
| 6 | PS-06 | P0 | PS-02, PS-04, PS-05 | Add rollback and failure-path hardening | WARN logging for invalid prompt activation; baseline fallback path; fault-injection tests for missing/malformed prompt assets | Invalid prompt config falls back safely and emits diagnosable signals |
| 7 | PS-07 | P1 | PS-04 | Create route-context prompt assets for Skills pattern | `react_analyst/routes/*.md` for all 8 `StockQueryRouter` categories; route-to-context mapping contract | Every current semantic route has an explicit prompt-context asset or documented no-op mapping |
| 8 | PS-08 | P1 | PS-05, PS-07 | Compose route-aware prompt behavior in runtime | `PromptComposer`; `@dynamic_prompt` middleware; route-category propagation from `StockQueryRouter`; prompt assembly dump/debug path | Runtime composes base prompt plus route context deterministically and exposes `route_category` in metadata |
| 9 | PS-09 | P1 | PS-05, PS-08 | Build offline evaluation harness | Core datasets: `tool_selection_regression`, `missing_data_and_staleness`, `finance_safety_and_hype_resistance`, `route_classification_accuracy`; rubric/code evaluators; baseline run storage | Baseline and candidate prompts can be compared offline against regression thresholds |
| 10 | PS-10 | P1 | PS-06, PS-09 | Enforce finance-domain guardrail verification | Regression gates for hype, unsupported claims, uncertainty disclosure, source attribution, and fact-assumption-inference separation | Prompt candidate cannot advance if finance-safety regressions are detected |
| 11 | PS-11 | P2 | PS-09, PS-10 | Add controlled experiment and rollout controls | `fixed`, `forced`, `shadow`, optional `weighted` selection modes; candidate variant registry; rollout runbook; enablement guardrails | Production remains fixed by default; non-fixed modes are explicitly gated and observable |
| 12 | PS-12 | P3 | PS-08, PS-09, PS-11 | Introduce multi-agent prompt taxonomy | Shared global partials; `orchestrator/` and `rag_research/` prompt families; handoff schema; extended eval datasets | Skills-pattern baseline shows measurable limits and specialist prompt contracts are testable offline before runtime adoption |

#### Milestone Plan

| Milestone | Backlog Items | Outcome | Go / No-Go Rule |
|---|---|---|---|
| M1 - Prompt Runtime Parity | PS-01 to PS-06 | Current ReAct runtime is externalized, versioned, observable, and rollback-safe | Do not begin route-context work until the hardcoded prompt is fully removed from the primary ReAct path |
| M2 - Route-Aware Skills | PS-07 to PS-08 | Existing `StockQueryRouter` drives deterministic route-specific prompt context with no extra LLM routing cost | Do not introduce experiment modes until route-aware composition is stable and traceable |
| M3 - Evaluation and Safety Gates | PS-09 to PS-10 | Offline comparison and finance-safety regression checks are available for every prompt change | No live prompt experimentation before offline gates pass |
| M4 - Controlled Rollout | PS-11 | Candidate variants can be compared safely in `forced` or `shadow` mode, with weighted live exposure still optional and explicit | Keep production on `fixed` unless an approved rollout decision says otherwise |
| M5 - Multi-Agent Prompt Foundation | PS-12 | Specialist prompt families and handoff contracts are ready for future orchestration work | Do not start multi-agent runtime work until Skills-pattern evidence shows a real limitation |

#### Critical Path

The critical path is:

`PS-01 -> PS-02 -> PS-03 -> PS-04 -> PS-05 -> PS-06 -> PS-07 -> PS-08 -> PS-09 -> PS-10 -> PS-11`

`PS-12` is intentionally outside the near-term critical path. It remains blocked on measurable evidence that the Skills pattern is insufficient.

#### Recommended Ownership Split

| Workstream | Lead Surface | Backlog Items |
|---|---|---|
| Prompt runtime | `src/core/stock_assistant_agent.py`, `src/core/langchain_adapter.py` or successor loader module | PS-01 to PS-06 |
| Route-aware composition | `src/core/stock_query_router.py`, middleware integration, prompt asset tree | PS-07 to PS-08 |
| Evaluation and rollout | LangSmith metadata wiring, datasets, evaluators, rollout config | PS-09 to PS-11 |
| Future multi-agent taxonomy | Prompt asset hierarchy and specialist contracts | PS-12 |

#### Planning Notes

- Treat `PS-01` to `PS-06` as one implementation slice if a single PR can keep reviewable scope; otherwise split after `PS-03`.
- `PS-09` and `PS-10` should be prepared in parallel where possible, but `PS-10` cannot close until baseline evaluation artifacts from `PS-09` exist.
- Weighted live selection remains optional even after `PS-11`; `shadow` mode is the safer default for a financial-analysis surface.
- Prompt-level session-context injection remains follow-up work and should not be implied as complete until it is actually wired into runtime prompt composition.

---

## Verification Strategy

### Documentation Verification

This design is correct only if all of the following remain true:

1. The prompt system stays repo-owned and provider-neutral.
2. Prompting remains behavior-oriented, not fact-storage-oriented.
3. Prompt-version identity is visible in LangSmith metadata and tags.
4. Finance-domain safety cases are part of prompt evaluation, not treated as optional docs.
5. Live experimentation is blocked unless offline evaluation passes first.
6. Shared safety policy remains stronger than any specialist-local prompt customization.
7. Multi-agent routing quality is evaluated before specialist delegation is exposed broadly.

### Implementation Acceptance Criteria

| Requirement | Acceptance Test |
|---|---|
| Externalized prompt | ReAct path loads prompt from versioned asset, not hardcoded string |
| Prompt traceability | Every relevant run includes `prompt_version` and `prompt_variant` |
| Agent traceability | Multi-agent runs include `agent_role` and routing metadata |
| Experiment safety | Candidate variants cannot become weighted-production variants without explicit enablement |
| Finance safety | Regression dataset catches hype, guarantee, and unverifiable-claim failures |
| Rollback | Invalid prompt or experiment config falls back to approved baseline prompt |
| Retrieval safety | RAG specialist rejects or flags unsupported claims when retrieved evidence is insufficient |

---

## Research Log and Decision Log

### Research Log

| Date | Topic | Outcome |
|---|---|---|
| 2026-04-01 | Repo inspection | Confirmed the ReAct runtime still uses a hardcoded system prompt in `StockAssistantAgent` |
| 2026-04-01 | LangChain agents research | Confirmed `create_agent`, middleware, dynamic prompts, and tool filtering are the right extension points |
| 2026-04-01 | LangChain multi-agent research | Confirmed subagents, router, and custom workflow patterns are the relevant design space for a controlled multi-agent target |
| 2026-04-01 | LangGraph workflow research | Confirmed orchestrator-worker, routing, and evaluator patterns are better fits than unconstrained agent handoffs for this repo |
| 2026-04-01 | LangChain retrieval and RAG research | Confirmed 2-step, agentic, and hybrid RAG trade-offs and the need for retrieval-specific prompt contracts |
| 2026-04-01 | LangSmith research | Confirmed metadata, tags, threads, datasets, and experiments support prompt-variant traceability |
| 2026-04-01 | LangSmith multi-turn eval research | Confirmed thread-level evaluation prerequisites for future routing and trajectory scoring |
| 2026-04-01 | OpenAI prompt and tool guidance | Confirmed prompt structure, snapshot pinning, eval discipline, strict tool schemas, and constrained tool surfaces |
| 2026-04-01 | OpenAI agent and retrieval guidance | Confirmed knowledge access, tools, and control flow should remain separate primitives |
| 2026-04-01 | Agentic design research | Confirmed the repo should prefer a simple composable prompt runtime over a highly abstract prompt framework |
| 2026-04-01 | Finance-domain research | Confirmed the prompt must explicitly resist hype, guaranteed-return framing, and sole reliance on social-sentiment signals |
| 2026-04-13 | LangChain 1.0 API verification | Confirmed `create_agent`, `@dynamic_prompt`, `@wrap_model_call`, `@wrap_tool_call`, `AgentMiddleware`, and `SummarizationMiddleware` are official LangChain 1.0 APIs |
| 2026-04-13 | LangChain multi-agent patterns review | Documented 5 patterns (Subagents, Handoffs, Skills, Router, Custom workflow) with performance comparison; Skills pattern identified as recommended near-term stepping stone |
| 2026-04-13 | StockQueryRouter alignment | Identified existing 8-route semantic router as foundation for Skills pattern prompt-context loading |
| 2026-04-13 | Practical scope refinement | Reduced runtime abstractions from 5 to 3, dataset families from 9 to 4 core + 5 extended, config schema narrowed to react_analyst only |

### Decision Log

| Decision | Rationale | Status |
|---|---|---|
| Use local prompt files as system of record | Matches repo ownership, code review, deployment model, and provider-neutral architecture | Accepted |
| Use LangSmith for observability and evaluation, not prompt storage | Aligns with existing tracing direction and avoids runtime vendor lock-in | Accepted |
| Keep dynamic prompting narrow and deterministic | Prevents prompt logic from absorbing factual or session-state responsibilities | Accepted |
| Include finance safety rules in the base prompt | Required by ADR boundaries and regulator evidence | Accepted |
| Start with offline evaluation before live prompt experiments | Reduces regression risk in an investment-analysis product surface | Accepted |
| Prefer centralized routing over direct user-visible handoffs | Better matches the repo’s need for control, auditability, and bounded context | Accepted |
| Give RAG specialists their own prompt contract | Retrieval grounding and prompt-injection resistance require different rules than ReAct tool use | Accepted |
| Adopt Skills pattern as near-term target | Leverages existing StockQueryRouter, avoids multi-agent LLM cost overhead, provides measurable baseline before full multi-agent | Accepted |
| Build on StockQueryRouter rather than replace it | 8-route semantic classification already exists and works; prompt system should compose route-specific context using this foundation | Accepted |
| Reduce runtime to 3 components (PromptRegistry, PromptComposer, @dynamic_prompt) | 5 abstractions are over-engineered for a single hardcoded prompt; 3 components cover all near-term needs | Accepted |
| Start with 4 core evaluation datasets | 9 dataset families are unrealistic before any prompt infrastructure exists; 4 cover the critical path | Accepted |

### Open Follow-Up Questions

1. Should prompt locale selection be controlled at config level, workspace level, or per request?
2. Should candidate prompts live alongside active prompts in the same folder or in a `candidates/` subfolder?
3. Should online prompt experiments be allowed at all for user-facing financial analysis, or restricted to shadow mode only?
4. Should the FACT / ASSUMPTION / INFERENCE contract be mandatory for all analytical answers, or only for high-risk stock thesis queries?
5. Should the initial orchestrator be a lightweight router-only layer, or a fuller synthesizer that can merge ReAct and RAG outputs in one reply?
6. Should the first RAG specialist use 2-step retrieval for predictability, or agentic RAG for more flexible multi-hop research?

---

## Document Update Log

This section tracks changes made to other project documents as a result of research findings in this proposal.

### Update Session: 2026-05-06 (v1.3 → Formal Implementation Backlog)

**Trigger:** Convert the high-level roadmap into a dependency-ordered implementation backlog and milestone plan for execution tracking.

| # | Target Document | Change Summary | SRS/ADR References |
|---|----------------|----------------|-------------------|
| 1 | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | Added a formal implementation backlog with backlog IDs (`PS-01` to `PS-12`), dependency ordering, milestone gates, critical path, ownership split, and prioritization model. Updated document control to v1.3 / 2026-05-06. | FR-1.4.5–1.4.9, FR-1.5, NFR-5.2.5–5.2.7, NFR-6.2.3, ADR-002, ADR-003 |

**Total changes:** 1 document, implementation planning formalized for execution sequencing.

### Update Session: 2026-04-13 (v1.2 → Standard Documents Sync)

**Trigger:** Reflect PROMPT_SYSTEM_RESEARCH_PROPOSAL.md v1.2 findings into project-standard SDD documents.

| # | Target Document | Change Summary | SRS/ADR References |
|---|----------------|----------------|-------------------|
| 1 | [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md) | Version 2.2 → 2.3. Added FR-1.4.6–1.4.9 (prompt version identity, route-specific context, rollback safety, experiment assignment). Added FR-1.5 (Finance-Domain Behavioral Guardrails — 5 items: evidence-first, uncertainty disclosure, anti-hype, fact-assumption separation, source attribution). Added NFR-5.2.5–5.2.7 (prompt version, agent role, and experiment ID in traces). Strengthened NFR-6.2.3 (versioned file assets, no-code-deployment). Added AC-8 (4 prompt system acceptance criteria). Added OI-9 (prompt asset directory structure). Added related document reference. | FR-1.4.6–1.4.9, FR-1.5.1–1.5.5, NFR-5.2.5–5.2.7, NFR-6.2.3, AC-8.1–8.4 |
| 2 | [AGENT_ARCHITECTURE_DECISION_RECORDS.md](./decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md) | Added ADR-002 (Skills Pattern — composable prompt fragments with activation criteria). Added ADR-003 (Externalized Prompt Assets — versioned YAML files, baseline fallback, directory convention). Annotated the ADR-001 Prompt Compiler decision with implementation reference to this research proposal. | ADR-002, ADR-003 |
| 3 | [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md) | Added new “Prompt System Architecture” section (three-layer architecture, component responsibilities, prompt taxonomy, skills composition flow, observability integration). Updated System Prompt block with migration note. Added prompt file structure (`src/prompts/`) to File Structure. Added 3 design pattern rows (Asset Loader, Composer, Middleware). Added §4.4 Prompt System Externalization to Space for Improvements. Updated Table of Contents. | FR-1.4.5–1.4.9, FR-1.5, NFR-5.2.5–5.2.7 |
| 4 | [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) | Updated 2A.2 status to “Research complete — design refined.” Replaced 4 generic work items with refined 7-phase implementation roadmap. Updated dependencies with cross-references to this proposal, SRS v2.3, and ADR-002/ADR-003. | FR-1.4.5–1.4.9, FR-1.5, ADR-002, ADR-003 |
| 5 | [SRS_SPEC_TRACEABILITY.md](./SRS_SPEC_TRACEABILITY.md) | Version 1.4 → 1.5. Updated SRS baseline to v2.3. Added 16 unmapped trace entries: FR-1.4.6–1.4.9 (4), FR-1.5.1–1.5.5 (5), NFR-5.2.5–5.2.7 (3), AC-8.1–8.4 (4). Updated summary counts (302 → 318 total, 179 → 195 unmapped). Added AC-8 to family index. | All new SRS v2.3 items |

**Total changes:** 5 documents, ~80 new or modified content blocks.

---
## Reference Index

### Internal Project References

- [ADR-001 — Layered LLM Architecture](./decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md)
- [Phase 2 Agent Enhancement Roadmap](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md)
- [Agent Memory Technical Design](./AGENT_MEMORY_TECHNICAL_DESIGN.md)
- [LangChain Agent Architecture and Design](./ARCHITECTURE_DESIGN.md)
- [LangSmith Studio Guide](../LANGSMITH_STUDIO_GUIDE.md)

### Code Anchors

- `src/core/stock_assistant_agent.py` — ReAct agent with hardcoded `REACT_SYSTEM_PROMPT`
- `src/core/stock_query_router.py` — Semantic router with 8 route categories (StockQueryRouter)
- `src/core/routes.py` — StockQueryRoute enum definition
- `src/core/langchain_adapter.py` — PromptBuilder and prompt file loading utilities
- `src/core/langgraph_bootstrap.py` — LangGraph entry path
- `config/config.yaml` — Configuration (no `prompts.*` section yet)
- `src/prompts/system_stock_assistant.txt` — English system prompt (not used by ReAct runtime)
- `src/prompts/system_stock_assistant-vn.txt` — Vietnamese system prompt (not used by ReAct runtime)

### External Sources

- [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware)
- [LangChain Multi-Agent](https://docs.langchain.com/oss/python/langchain/multi-agent)
- [LangGraph Workflows and Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [LangChain Agents Reference](https://reference.langchain.com/python/langchain/agents/)
- [LangChain Core Runnables Reference](https://reference.langchain.com/python/langchain_core/runnables/)
- [LangChain Core Prompts Reference](https://reference.langchain.com/python/langchain_core/prompts/)
- [LangChain Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [Build a RAG Agent with LangChain](https://docs.langchain.com/oss/python/langchain/rag)
- [LangSmith Observability Concepts](https://docs.langchain.com/langsmith/observability-concepts)
- [Add Metadata and Tags to Traces](https://docs.langchain.com/langsmith/add-metadata-tags)
- [Configure Threads](https://docs.langchain.com/langsmith/threads)
- [LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation)
- [Set Up Multi-Turn Online Evaluators](https://docs.langchain.com/langsmith/online-evaluations-multi-turn)
- [Custom Instrumentation](https://docs.langchain.com/langsmith/annotate-code)
- [OpenAI Prompt Engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [OpenAI Agents](https://developers.openai.com/api/docs/guides/agents)
- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI File Search](https://developers.openai.com/api/docs/guides/tools-file-search)
- [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Social Media and Stock Tip Scams — Investor Alert](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/social-media-stock-scams)
- [Social Sentiment Investing Tools — Think Twice Before Trading Based on Social Media](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-18)
- [Types of Fraud — Investor.gov](https://www.investor.gov/protect-your-investments/fraud/types-fraud)
