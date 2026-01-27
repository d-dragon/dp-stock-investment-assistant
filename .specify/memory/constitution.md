# DP Stock Investment Assistant Constitution

> **Purpose**: This constitution defines the governing principles for the DP Stock Investment Assistant project. It establishes hard rules for AI memory architecture, development practices, and quality standards that all contributors and AI agents must follow.

---

## Article I: Core Architectural Principles

These seven principles from ADR-001 form the foundation of the LangChain agent architecture. They are **non-negotiable** and prevent hallucination, data leakage, and compounding errors.

### I. Memory Never Stores Facts
Long-Term Memory (LTM) and Short-Term Memory (STM) retain **user preferences, session context, and routing hints only**. All financial facts must originate from external sources or verified data stores. Memory is for personalization, not truth.

### II. RAG Never Stores Opinions
Retrieval-Augmented Generation (RAG) indices contain **sourced documents only**: SEC filings, news articles, macro data, and retrieved snippets. Interpretations and opinions remain in LLM output and must be tied to cited evidence.

### III. Fine-Tuning Never Stores Knowledge
Fine-tuning enforces **structure and tone**, not factual content. Training data must be human-verified and explicitly exclude invented numbers, forecasts, or market predictions.

### IV. Prompting Controls Behavior, Not Data
Prompts encode **rules, safety constraints, and output schema**. Data used for answers is injected at runtime from LTM/STM/RAG/tools. Prompts define "how to reason," not "what to say."

### V. Tools Compute Numbers, LLM Reasons About Them
Deterministic tools fetch and calculate metrics; the LLM explains implications. This separation keeps **computations auditable** and prevents fabricated figures.

### VI. Investment Data Sources Are External
Stock-related data is fetched from **pre-listed external websites, approved data sources, and the in-system database**. The agent may request tools to collect, normalize, and organize data—but never invent it.

### VII. Market Manipulation Safeguards Are Enforced
No intent to influence markets, prices, or trading behavior. All outputs are **informational only** and grounded in verifiable sources.

---

## Article II: Golden Development Rules

These eight rules from the project's Copilot Instructions govern all development practices.

### 1. Security First
No secrets in code, logs, or version control. API keys, passwords, and credentials must never appear in source files or error messages.

### 2. Test Before Merge
All changes must have passing tests. New behavior requires test coverage; changed behavior requires updated tests.

### 3. Logging Over Print
Use structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR). No `print()` statements in production code.

### 4. Document Intent
Explain "why" in code comments, commit messages, and PRs. Self-documenting code is preferred, but intent must be clear.

### 5. Backward Compatibility
Consider migration paths when changing APIs or schemas. Use deprecation warnings; don't break existing integrations without notice.

### 6. Fail Fast
Validate early; provide clear error messages; log failures with context. Every error path should be logged and surfaced appropriately.

### 7. Keep It Simple
Prefer simple, maintainable solutions over complex abstractions. YAGNI—don't build features until they're needed.

### 8. Follow Domain Standards
Adhere to language-specific guidelines: PEP 8 for Python, Airbnb/Standard for TypeScript, and domain instruction files in `.github/instructions/`.

---

## Article III: Memory Boundaries

These boundaries govern the FR-3.1 Memory System implementation, ensuring clean separation between personalization and factual data.

### Long-Term Memory (LTM) — Allowed
- User risk profile (conservative, moderate, aggressive)
- Investment style (value, growth, dividend, momentum)
- Investment goals (income, capital appreciation, wealth preservation)
- Time horizon preferences
- Experience level and sector preferences
- Output verbosity and language preferences

### Short-Term Memory (STM) — Allowed
- Current session context and assumptions
- Active conversation state
- Temporary routing hints
- In-progress analysis context

### Explicitly Prohibited in Memory
These items **MUST** live in RAG/Tools layer, never in LTM/STM:
- Real-time or historical prices
- Financial ratios and calculated metrics
- Valuation assessments or price targets
- Forecasts or forward-looking statements
- News content or filing text
- Analytical conclusions or recommendations

---

## Article IV: Governance

### Supremacy
This constitution supersedes all other practices. When conflicts arise, constitutional principles take precedence.

### Amendment Process
1. Propose amendment with rationale and impact analysis
2. Document affected components and migration plan
3. Require explicit approval before implementation
4. Update version number and amendment date

### Compliance Verification
- All PRs/reviews must verify constitutional compliance
- Complexity must be justified against simplicity principle
- Use `.github/instructions/` for runtime development guidance

### Version Control
- MAJOR: Breaking changes to core principles
- MINOR: New articles or clarifications
- PATCH: Typo fixes or minor rewording

---

**Version**: 1.0.0 | **Ratified**: 2026-01-27 | **Last Amended**: N/A
