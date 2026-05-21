# Prompt System Benchmark Review

> **Status**: Active review; refreshed after P1 documentation sync  
> **Review Mode**: Design artifacts only; implementation excluded  
> **Benchmark Basis**: Official vendor and framework documentation only  
> **Companion Documents**: [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md), [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md), [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md)

## Document Control

| Field | Value |
|-------|-------|
| Project | DP Stock Investment Assistant |
| Domain | Agent |
| Focus | External benchmark review of the prompt-system design against current official guidance from OpenAI, Anthropic, Google Gemini, LangChain, LangGraph, and LangSmith |
| Date | 2026-05-21 |
| Status | Active; refreshed after P1 documentation sync |
| Audience | Engineering, architecture, maintainers, reviewers, prompt-system owners, and requirement custodians |
| Review Scope | Prompt-system design, architecture framing, governance model, evaluation model, documented evolution path, and resulting requirement codification |
| Explicit Exclusion | No runtime or code-implementation review is performed in this document |

---

## Table of Contents

1. [Review Scope and Method](#1-review-scope-and-method)
2. [Executive Summary](#2-executive-summary)
3. [Key Findings](#3-key-findings)
4. [External Benchmark Synthesis](#4-external-benchmark-synthesis)
5. [Benchmark Matrix](#5-benchmark-matrix)
6. [Strengths of the Current Design](#6-strengths-of-the-current-design)
7. [Design Gaps and Risks](#7-design-gaps-and-risks)
8. [Recommended Documentation Follow-Ups](#8-recommended-documentation-follow-ups)
9. [Overall Evaluation](#9-overall-evaluation)
10. [Reference Index](#10-reference-index)

---

## 1. Review Scope and Method

### Reviewed Project Artifacts

This review is based on the current prompt-system design statements in:

- [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md), especially the Source Layout View and Prompt and Behavior View.
- [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), especially Prompt Asset Mapping, the Planned Prompt Compiler Path, and Prompt Asset Model and Composition Rules.
- [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md), especially the Current State Assessment, Prompt-System Gap Matrix and Risk Analysis, Proposed Prompt Asset Model, Concrete Finance-Grade Prompt Asset Schema, Required Trace Metadata, Evaluation Scope, and Finance-Domain Guardrails.
- [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md), where the latest prompt-governance controls are now formalized as requirements and acceptance criteria.

### Benchmark Sources

This review compares the project design against current official guidance from:

- OpenAI on agent orchestration, guardrails, evaluation, and instruction authority.
- Anthropic on effective agents, prompt engineering, tool use, and extended thinking.
- Google Gemini on agents, prompt design strategies, tool combination, and context caching.
- LangChain and LangGraph on agents, middleware, multi-agent patterns, and workflow design.
- LangSmith on observability, metadata, thread grouping, and offline versus online evaluation.

### Review Question

The core review question is:

> Does the current project prompt-system design reflect modern agentic-AI best practice for a finance-oriented assistant, and where does it remain under-specified or governance-incomplete?

### Review Standard

The review uses the following benchmark expectations:

- simplicity-first topology before multi-agent expansion;
- explicit separation between policy, context, tools, and runtime state;
- boundary-aware guardrails rather than prompt-only safety;
- strong observability and evaluation before rollout expansion;
- explicit treatment of authority, trust, and untrusted content;
- provider-neutral architecture with provider-specific features treated as optimizations, not architectural dependencies;
- finance-domain response discipline grounded in evidence, uncertainty, and non-manipulative behavior.

---

## 2. Executive Summary

The current prompt-system design is directionally strong and broadly aligned with current agent-engineering guidance. In particular, the design correctly favors a repo-owned prompt system, a skills-first evolution path, route-aware prompt composition, metadata-driven observability, offline evaluation before broader rollout, and a delayed move to multi-agent specialization only when single-agent limits are measurable. Those positions continue to align well with current guidance from OpenAI on orchestration and guardrails, Anthropic on effective agents, Google Gemini on agentic prompting, and LangChain on skills, middleware, and multi-agent tradeoffs.

Since the earlier benchmark passes, the design package has incorporated the P0 and P1 governance follow-ups identified by this review. The proposal now defines instruction authority, release gates, tool-risk classes, locale-parity review, and prompt-segment policy; the architecture now expresses the guardrail, tool-risk, and segment-governance boundaries; the technical design now realizes those controls; and the agent-domain SRS now codifies them as testable requirements and acceptance criteria. This materially improves control-plane completeness across the design set.

The main remaining weaknesses are now future-state orchestration questions rather than missing control-plane or rollout-governance layers. Manager-versus-specialist answer ownership, cross-agent handoff trust, and deeper adversarial evaluation for future RAG or multi-agent flows remain intentionally open. For a finance-oriented assistant, those questions should remain deferred until broader orchestration scope is justified.

Overall assessment:

- **Strategic alignment**: High
- **Prompt-governance maturity**: High at design level
- **Finance-grade control completeness**: High at design level; only P2 future-state governance items remain open
- **Readiness for multi-agent expansion**: Correctly deferred until ownership and handoff rules are explicit

The strongest near-term design work is still not to add more agents. It is to preserve the newly documented governance controls during implementation and to formalize future orchestration ownership before multi-agent scope expands.

---

## 3. Key Findings

| Status / Severity | Finding | Why It Matters |
|-------------------|---------|----------------|
| Closed (was High) | The prior instruction-authority gap is now materially resolved at documentation level through the proposal's trust matrix and the SRS requirement set. | This closes the largest control-plane omission from the earlier review and makes the authority model reviewable and testable. |
| Closed (was High) | The prior guardrail-boundary gap is now materially resolved at architecture level through the explicit boundary model spanning input, prompt-assembly, tool, output, and approval controls. | This aligns the design with workflow-boundary guardrail guidance rather than leaving safety framed as response-only shaping. |
| Closed (was Medium) | The prior release-gate precision gap is now materially resolved at proposal and SRS level through explicit thresholds, metadata completeness rules, rollback triggers, and promotion conditions. | This makes prompt experimentation governable at design level rather than directionally correct but operationally soft. |
| Closed (was Medium) | Tool governance now includes an explicit risk-envelope model across proposal, architecture, technical design, and SRS. | This gives tool exposure, approval posture, and traceability one shared control vocabulary before the tool surface grows. |
| Closed (was Medium) | Locale governance now includes a parity-review protocol plus trace-metadata requirements for locale promotion decisions. | This turns multilingual safety equivalence into a reviewable and testable control instead of a declarative intent only. |
| Closed (was Medium) | Static-versus-dynamic prompt segment policy is now explicit, including provider-neutral caching and evidence-boundary rules. | This clarifies what may be reused, what remains request-scoped, and what never gains policy authority. |
| Medium | Future manager-versus-specialist answer ownership is still only partially documented. | This choice should be explicit before any multi-agent runtime is implemented. |
| Medium | Cross-agent handoff trust rules remain a future-state design item. | Multi-agent expansion should not proceed until handoff payloads preserve evidence-as-data and shared-policy precedence. |

No active High-severity documentation gap remains in the reviewed design package after the P0 and P1 follow-up sync.

No material benchmark problem was found with the following current design choices:

- repo-owned prompt assets rather than vendor-managed prompt state;
- skills-first evolution before multi-agent runtime expansion;
- explicit prompt metadata and LangSmith observability goals;
- shallow, metadata-driven prompt asset taxonomy;
- finance-domain emphasis on evidence, uncertainty, and anti-hype behavior.

---

## 4. External Benchmark Synthesis

### 4.1 Start Simple; Add Specialists Only When Contracts Change

Current guidance from [OpenAI Orchestration and Handoffs](https://developers.openai.com/api/docs/guides/agents/orchestration), [Anthropic's Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents), and [LangChain Multi-Agent](https://docs.langchain.com/oss/python/langchain/multi-agent) converges on the same point: start with one capable agent, and split only when instructions, tools, policy boundaries, or context windows materially diverge.

That is a direct strength of the current project design. The proposal's skills-pattern-first stance is more modern than prematurely committing to a specialist swarm. It is also more cost-aware and easier to govern.

### 4.2 Prompt Systems Are Runtime Control Planes, Not Just Prompt Files

[OpenAI's building-agents guidance](https://developers.openai.com/tracks/building-agents), [Google Gemini Agents Overview](https://ai.google.dev/gemini-api/docs/agents), and [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware) all treat the prompt system as one part of a larger control plane that includes tools, runtime state, guardrails, and orchestration hooks.

The project design mostly understands this already. The planned `PromptAssetLoader -> PromptAssembler -> ResponseGuardrailMiddleware` path recognizes that governed behavior requires more than prompt text. Since the earlier review pass, the architecture and proposal now define authority and boundary-control layers more explicitly, so the remaining gap is no longer the absence of a control-plane model but the lack of deeper tool-risk and segment-policy detail in the technical realization layer.

### 4.3 Guardrails Belong at Boundaries

[OpenAI Guardrails and Human Review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals) makes a sharp distinction between input guardrails, output guardrails, tool guardrails, and human approvals. [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware) similarly frames middleware as the place for pre-model processing, output validation, tool error handling, retries, fallbacks, and human-in-the-loop controls.

This was a key benchmark pressure on the earlier design baseline. It has now been materially addressed at architecture level: the reviewed documents distinguish input, prompt-assembly, tool, output, and approval boundaries. The remaining gap is finer-grained tool risk classification and approval policy, not the absence of a boundary-aware guardrail model.

### 4.4 Authority and Trust Classes Must Be Explicit

[OpenAI Model Spec](https://model-spec.openai.com/2025-02-12.html) explicitly distinguishes instruction authority levels and warns against treating tool output or quoted content as trusted instructions. [Google Gemini Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) likewise recommends separating role, constraints, context, and task so the model can distinguish data from instructions. Anthropic's prompt-engineering and tool-use guidance also assumes that schemas, context boundaries, and tool contracts should be explicit rather than inferred.

The earlier design partially addressed this through bounded dynamic context and future RAG rules that treat retrieved content as data only. The refreshed proposal now defines instruction precedence across:

- shared policy assets;
- role contracts;
- route skills;
- user requests;
- session context;
- tool outputs;
- retrieved documents; and
- experimental overlays.

Within the scope of a design-only review, that change materially closes the most important earlier documentation gap.

### 4.5 Tool Surfaces Should Be Narrow, Typed, and Deliberately Exposed

[Anthropic Tool Use](https://platform.claude.com/docs/en/docs/agents-and-tools/tool-use/overview) emphasizes strict schema conformance and high-quality tool definitions. [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents) emphasizes dynamic tool filtering because too many tools overload the model. [Google Gemini Tool Combination](https://ai.google.dev/gemini-api/docs/tool-combination) emphasizes preserving tool-call context correctly and treating tool context circulation as part of the agent protocol.

The project's `tool_policy` direction is now materially stronger. The design package defines tool risk classes, prompt-asset risk envelopes, runtime registry ownership, and approval expectations for future higher-risk actions. The remaining question is not how tool classes should be described, but when any class above bounded transformation should be admitted into runtime.

### 4.6 Evaluation and Traceability Are First-Class Design Concerns

[OpenAI Evaluate Agent Workflows](https://developers.openai.com/api/docs/guides/agent-evals) recommends starting with traces, then moving to datasets and repeatable evaluation runs. [LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation) and [LangSmith Observability Concepts](https://docs.langchain.com/langsmith/observability-concepts) make the same distinction between observability, offline benchmarking, and online monitoring. [LangSmith Threads](https://docs.langchain.com/langsmith/threads) further requires consistent thread metadata on all runs for multi-turn analysis.

This is one of the strongest areas in the current design. The proposal's required trace metadata, dataset-first evaluation stance, prompt version observability, and newly documented release gates are well aligned with current best practice. The remaining issue is now narrower: richer red-team families and broader rollout protocol depth, not missing release-gate precision itself.

### 4.7 Provider Features Should Optimize the Runtime, Not Redefine the Architecture

[Anthropic Extended Thinking](https://platform.claude.com/docs/en/docs/build-with-claude/extended-thinking), [Google Context Caching](https://ai.google.dev/gemini-api/docs/caching), and LangChain's note on provider-specific prompt caching through structured system messages in [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents) show that caching, thinking, and long-context features are useful but provider-specific.

The current project design is right to remain provider-neutral. That refinement is now present: the documents distinguish cacheable static policy, request-scoped dynamic control segments, and data-only runtime evidence, while treating provider-specific reasoning and long-context features as operational optimizations rather than architectural authorities.

---

## 5. Benchmark Matrix

| Dimension | External Benchmark | Current Design Assessment | Review Conclusion |
|-----------|--------------------|---------------------------|------------------|
| Topology strategy | Start with one agent; add specialists only when contracts materially diverge ([OpenAI](https://developers.openai.com/api/docs/guides/agents/orchestration), [Anthropic](https://www.anthropic.com/engineering/building-effective-agents), [LangChain](https://docs.langchain.com/oss/python/langchain/multi-agent)) | The design explicitly favors a skills-pattern baseline and defers multi-agent runtime until limits are measurable. | Strong alignment |
| Prompt asset governance | Externalize prompt assets, keep ownership explicit, and separate policy from code deployment ([Anthropic Prompt Engineering Overview](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/overview), [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)) | The design proposes governed prompt assets, metadata frontmatter, status fields, ownership, and fallback lineage. | Strong alignment |
| Prompt composition boundary | Treat composition as a deterministic runtime boundary, not arbitrary string concatenation ([LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware), [Google Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)) | The design documents a `PromptAssetLoader -> PromptAssembler -> ResponseGuardrailMiddleware` path and ordered composition rules. | Strong alignment |
| Instruction authority and trust model | Distinguish authoritative instructions from untrusted content and tool output ([OpenAI Model Spec](https://model-spec.openai.com/2025-02-12.html), [Google Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)) | The proposal now defines a full precedence and trust matrix for shared policy, role contracts, route skills, user input, session context, tool outputs, retrieved documents, and experiment overlays, with SRS-backed requirement authority. | Strong alignment after P0 sync |
| Guardrail model | Place controls at input, output, tool, and approval boundaries ([OpenAI Guardrails and Human Review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals), [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware)) | The architecture now defines an explicit cross-boundary guardrail model spanning input, prompt assembly, tool, output, and approval controls. | Strong alignment after P0 sync |
| Tool governance | Keep tools narrow, typed, and dynamically exposed when useful ([Anthropic Tool Use](https://platform.claude.com/docs/en/docs/agents-and-tools/tool-use/overview), [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents), [Google Tool Combination](https://ai.google.dev/gemini-api/docs/tool-combination)) | The design now defines tool risk classes, prompt risk envelopes, runtime ownership of tool classification, and approval expectations for higher-risk actions. | Strong alignment after P1 sync |
| Observability and metadata | Track traces, runs, tags, metadata, and thread identifiers as first-class evaluation context ([LangSmith Observability Concepts](https://docs.langchain.com/langsmith/observability-concepts), [LangSmith Threads](https://docs.langchain.com/langsmith/threads), [LangSmith Add Metadata and Tags](https://docs.langchain.com/langsmith/add-metadata-tags)) | The design strongly specifies prompt-version metadata, route metadata, experiment identifiers, and conversation identifiers. | Strong alignment |
| Evaluation lifecycle | Use offline datasets before live rollout; use online evaluation for production monitoring ([OpenAI Agent Evals](https://developers.openai.com/api/docs/guides/agent-evals), [LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation), [Anthropic Prompt Engineering Overview](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/overview)) | The design now combines offline-first rollout intent with explicit prompt release gates, metadata completeness rules, rollback triggers, and candidate-promotion conditions. | Strong alignment after P0 sync |
| Locale and variant governance | Keep variants structured and test for semantic parity rather than assuming wording parity ([Google Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)) | The design now requires locale fallback, shared parity lineage, paired evaluation, locale-competent review, and locale trace metadata before promotion. | Strong alignment after P1 sync |
| Provider neutrality versus provider optimization | Treat caching, thinking, and long-context features as runtime optimizations, not architecture ownership shifts ([Anthropic Extended Thinking](https://platform.claude.com/docs/en/docs/build-with-claude/extended-thinking), [Google Context Caching](https://ai.google.dev/gemini-api/docs/caching), [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)) | The design now spells out static-policy, dynamic-control, and runtime-evidence segment treatment while keeping provider-specific optimizations outside the policy authority model. | Strong alignment after P1 sync |
| Finance-domain discipline | High-stakes domains require evidence, uncertainty disclosure, and non-definitive regulated guidance ([OpenAI Model Spec regulated-advice guidance](https://model-spec.openai.com/2025-02-12.html)) | The design's finance policy, anti-hype stance, fact/inference separation, and response contract are notably strong. | Strong alignment |

---

## 6. Strengths of the Current Design

### 6.1 Correct Near-Term Architecture Choice

The choice to evolve through a skills-pattern prompt compiler path rather than immediately introducing multi-agent specialization is one of the design's best decisions. It matches current external guidance, reduces cost and complexity, and keeps behavior centralizable while the system is still proving its prompt governance model.

### 6.2 Strong Separation Between Policy and Facts

The design repeatedly states that prompts govern behavior, not financial facts. That is architecturally sound and especially important in a finance domain. The proposal's distinction between shared static policy, role contract, controlled dynamic context, and runtime factual context is a strong foundation.

### 6.3 Good Prompt Asset Governance Direction

The shallow `system` / `skills` / `experiments` taxonomy is pragmatic. It is easier to review and evolve than deep version-directory trees, while still preserving governance through metadata. This is a good balance between future richness and near-term maintainability.

### 6.4 Strong Observability and Evaluation Intent

The required trace metadata, prompt lineage fields, experiment identifiers, and offline-versus-online evaluation split are well designed. Many prompt-system proposals stop at file externalization; this design correctly treats measurement and traceability as core architecture.

### 6.5 Finance-Specific Behavioral Discipline Is Better Than Average

The finance-domain schema, evidence-first stance, explicit uncertainty rules, anti-hype guardrails, and route-specific output expectations are stronger than what is commonly seen in generic prompt-management proposals. The design shows domain understanding rather than merely adopting generic AI-agent terminology.

### 6.6 The Documents Mostly Preserve Current-versus-Planned Discipline

The architecture and technical design documents are careful about distinguishing current baseline behavior from proposed prompt-system evolution. That discipline is critical to avoiding architecture drift in a documentation-heavy design effort.

---

## 7. Design Gaps and Risks

The former P1 gaps on tool risk, locale parity, and segment policy are now addressed in the reviewed design package. The remaining documentation risks are future-state orchestration and adversarial-evaluation questions that become material only when scope expands beyond the governed single-agent or skills baseline.

### 7.1 Future Multi-Agent Expansion Needs an Explicit Ownership Rule

The current design sensibly favors centralized orchestration and synthesis. That should be made more explicit as a future-state rule: when specialists arrive, does the specialist own the user-facing answer, or does a manager/orchestrator own it? Current external guidance treats that choice as a primary orchestration decision, and the project should document it before implementation pressure arrives.

### 7.2 Cross-Agent Handoff Trust Model Still Needs Explicit Design

The refreshed authority matrix is a strong improvement for the current single-agent and skills-pattern path, but the same trust discipline is not yet extended to future specialist handoffs. Before any multi-agent runtime is finalized, the design should define how evidence remains data, how shared policy stays stronger than specialist-local prompts, and how handoff payloads are prevented from weakening finance-safety posture.

### 7.3 Adversarial Evaluation Depth Should Grow with Future RAG or Multi-Agent Scope

The current release-gate model is materially stronger than before, but it is still oriented to the present runtime shape. Before retrieval-grounded or multi-agent flows are implemented, the evaluation strategy should add explicit prompt-injection, context-pollution, and handoff-corruption test families so future orchestration work is measured against the same finance-safety posture as the governed single-agent path.

---

## 8. Recommended Documentation Follow-Ups

The recommendations below are documentation and design follow-ups only. The former P0 and P1 items are now complete in the reviewed documentation baseline, so the active follow-up set begins with the remaining P2 work.

### P0 - Completed in the Current Documentation Baseline

1. Added an **Instruction Authority and Trust Matrix** to the prompt-system proposal.
2. Added a **Guardrail Boundary Model** that distinguishes input, tool, output, and approval controls.
3. Added **Prompt Release Gates** covering dataset pass thresholds, mandatory metadata keys, rollback triggers, and candidate-promotion rules, then reflected them into the governing SRS and traceability artifacts.

### P1 - Completed in the Current Documentation Baseline

1. Added a **Tool Risk Classification Model** that maps tool classes to validation and approval expectations.
2. Added a **Locale Parity Review Protocol** that defines how equivalent finance-policy behavior is verified across `vi` and `en` variants.
3. Added a **Static versus Dynamic Prompt Segment Policy** that states what may be cached, what must remain request-scoped, and what must never be treated as policy.

### P2 - Recommended Before Any Multi-Agent Runtime Design Is Finalized

1. Add a **Manager versus Specialist Ownership Rule** for future orchestration.
2. Add a **Cross-Agent Handoff Trust Model** that preserves evidence as data and prevents specialist-local prompts from weakening shared policy.
3. Add **Prompt-Injection and Context-Pollution Test Families** to the evaluation strategy, especially for future RAG or document-grounded flows.

### Suggested Placement

The most natural document placements are:

- `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md` now owns authority, release-gate, tool-risk, locale-parity, and prompt-segment governance.
- `ARCHITECTURE_DESIGN.md` now owns the architecture-level guardrail, tool-risk, and segment-governance boundaries; future orchestration ownership rules belong there.
- `TECHNICAL_DESIGN.md` now owns the realization detail for segment treatment, tool risk classes, locale-parity selection, and trace completeness expectations.
- `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` now carries the formal requirement and acceptance-criteria authority for the completed P0 and P1 governance controls.

---

## 9. Overall Evaluation

The current project prompt-system design is substantively aligned with the current direction of agentic AI engineering. It is more mature than a simple prompt-externalization proposal and already reflects several ideas that matter: skills-first evolution, explicit prompt observability, repo-owned prompt policy, evaluation before live expansion, and domain-specific behavioral discipline.

The earlier P0 and P1 governance follow-ups identified by this review are now present in the proposal, architecture, technical design, and governing SRS. Within the scope of a design-only review, that moves the design from "strong direction with governance gaps" to "well-governed finance-grade prompt-system architecture" for the current single-agent, skills-first runtime.

The remaining work is now chiefly about future-state orchestration governance and deeper adversarial evaluation before the project expands into retrieval-grounded or multi-agent runtime designs. That means the next design step is still not broader capability. It is explicit ownership and handoff design for the later runtime shapes that are intentionally deferred today.

Runtime enforcement quality, implementation correctness, and regression behavior remain outside the scope of this document and still require separate validation.

---

## 10. Reference Index

### OpenAI

- [Building agents](https://developers.openai.com/tracks/building-agents)
- [Orchestration and handoffs](https://developers.openai.com/api/docs/guides/agents/orchestration)
- [Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
- [Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)
- [OpenAI Model Spec, 2025-02-12](https://model-spec.openai.com/2025-02-12.html)

### Anthropic

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Prompt engineering overview](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/overview)
- [Tool use with Claude](https://platform.claude.com/docs/en/docs/agents-and-tools/tool-use/overview)
- [Building with extended thinking](https://platform.claude.com/docs/en/docs/build-with-claude/extended-thinking)

### Google Gemini

- [Agents Overview](https://ai.google.dev/gemini-api/docs/agents)
- [Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [Combine built-in tools and function calling](https://ai.google.dev/gemini-api/docs/tool-combination)
- [Context caching](https://ai.google.dev/gemini-api/docs/caching)

### LangChain and LangGraph

- [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware)
- [LangChain Multi-Agent](https://docs.langchain.com/oss/python/langchain/multi-agent)
- [LangGraph Workflows and Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

### LangSmith

- [Observability concepts](https://docs.langchain.com/langsmith/observability-concepts)
- [Add metadata and tags to traces](https://docs.langchain.com/langsmith/add-metadata-tags)
- [Configure threads](https://docs.langchain.com/langsmith/threads)
- [LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation)