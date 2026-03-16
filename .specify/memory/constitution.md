<!--
SYNC IMPACT REPORT
==================
Version Change: 1.1.0 → 1.2.0 (MINOR)
Bump Rationale: Restructured to align with latest constitution-template.md format.
  Removed "Article N:" numbering from all section headers; consolidated 9 Article
  sections into 4 template-aligned top-level sections (Core Principles, Development
  Standards, Architecture & Quality, Governance). No principles added or removed.

Modified Sections:
- "Article I: Core Architectural Principles" → now nested under "## Core Principles"
- "Article II: Golden Development Rules" → subsection of "## Development Standards"
- "Article III: Memory Architecture Boundaries" → subsection of "## Development Standards"
- "Article IV: Design Patterns & Architecture" → subsection of "## Architecture & Quality"
- "Article V: SOLID Principles" → subsection of "## Architecture & Quality"
- "Article VI: Testing Standards" → subsection of "## Architecture & Quality"
- "Article VII: Quality Gates" → subsection of "## Architecture & Quality"
- "Article VIII: Import & Code Style Standards" → subsection of "## Development Standards"
- "Article IX: Governance" → "## Governance" (top-level, as per template)

Added Sections: None
Removed Sections: None (all content preserved, restructured only)

Template Consistency Check:
- .specify/templates/plan-template.md: ✅ Constitution Check section is generic; no update needed
- .specify/templates/spec-template.md: ✅ Constitution compliance section compatible
- .specify/templates/tasks-template.md: ✅ Task types align with principle-driven standards
- .specify/templates/constitution-template.md: ✅ Structure now aligned

Follow-up TODOs: None
-->

# DP Stock Investment Assistant Constitution

> **Purpose**: This constitution defines the governing principles for the DP Stock Investment
> Assistant project. It establishes hard rules for AI memory architecture, development practices,
> design patterns, and quality standards that all contributors and AI agents MUST follow.

---

## Core Principles

These seven principles from ADR-001 form the foundation of the LangChain agent architecture.
They are **non-negotiable** and prevent hallucination, data leakage, and compounding errors.

### I. Memory Never Stores Facts
Long-Term Memory (LTM) and Short-Term Memory (STM) retain **user preferences, session context,
and routing hints only**. All financial facts MUST originate from external sources or verified
data stores. Memory is for personalization, not truth.

### II. RAG Never Stores Opinions
Retrieval-Augmented Generation (RAG) indices contain **sourced documents only**: SEC filings,
news articles, macro data, and retrieved snippets. Interpretations and opinions remain in LLM
output and MUST be tied to cited evidence.

### III. Fine-Tuning Never Stores Knowledge
Fine-tuning enforces **structure and tone**, not factual content. Training data MUST be
human-verified and explicitly exclude invented numbers, forecasts, or market predictions.

### IV. Prompting Controls Behavior, Not Data
Prompts encode **rules, safety constraints, and output schema**. Data used for answers is
injected at runtime from LTM/STM/RAG/tools. Prompts define "how to reason," not "what to say."

### V. Tools Compute Numbers, LLM Reasons About Them
Deterministic tools fetch and calculate metrics; the LLM explains implications. This separation
keeps **computations auditable** and prevents fabricated figures.

### VI. Investment Data Sources Are External
Stock-related data is fetched from **pre-listed external websites, approved data sources, and the
in-system database**. The agent may request tools to collect, normalize, and organize data—but
MUST never invent it.

### VII. Market Manipulation Safeguards Are Enforced
No intent to influence markets, prices, or trading behavior. All outputs are **informational
only** and MUST be grounded in verifiable sources.

---

## Development Standards

### Golden Development Rules

These eight rules govern all development practices. Violations MUST be corrected before merge.

#### 1. Security First
No secrets in code, logs, or version control. API keys, passwords, and credentials MUST never
appear in source files, error messages, or stack traces exposed to users.

#### 2. Test Before Merge
All changes MUST have passing tests. New behavior requires test coverage; changed behavior
requires updated tests. The test suite MUST pass locally before pushing.

#### 3. Logging Over Print
Use structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR). No `print()`
statements in production code. Include context (request ID, user ID, resource name) in log
messages.

#### 4. Document Intent
Explain "why" in code comments, commit messages, and PRs. Self-documenting code is preferred;
comments explain rationale, not mechanics.

#### 5. Backward Compatibility
Consider migration paths when changing APIs or schemas. Use deprecation warnings and versioning;
do not break existing integrations without notice and migration guidance.

#### 6. Fail Fast
Validate early; provide clear, actionable error messages; log failures with context. Every error
path MUST be logged and surfaced appropriately. No silent failures.

#### 7. Keep It Simple
Prefer simple, maintainable solutions over complex abstractions. YAGNI—do not build features
until they are needed. Complexity MUST be justified against simplicity.

#### 8. Follow Domain Standards
Adhere to language-specific guidelines: PEP 8 for Python, Airbnb/Standard for TypeScript.
Reference domain instruction files in `.github/instructions/` for runtime development guidance.

### Memory Architecture Boundaries

These boundaries govern the FR-3.1 Memory System implementation, ensuring clean separation
between personalization and factual data.

#### Long-Term Memory (LTM) — Allowed
- User risk profile (conservative, moderate, aggressive)
- Investment style (value, growth, dividend, momentum)
- Investment goals (income, capital appreciation, wealth preservation)
- Time horizon preferences
- Experience level and sector preferences
- Output verbosity and language preferences

#### Short-Term Memory (STM) — Allowed
- Current session context and assumptions
- Active conversation state
- Temporary routing hints
- In-progress analysis context

#### Explicitly Prohibited in Memory
These items **MUST** live in RAG/Tools layer, never in LTM/STM:
- Real-time or historical prices
- Financial ratios and calculated metrics
- Valuation assessments or price targets
- Forecasts or forward-looking statements
- News content or filing text
- Analytical conclusions or recommendations

### Import & Code Style Standards

#### Import Conventions
- **Absolute imports only**: Always use `from <module>` for application code
- **No relative imports**: They break pytest discovery and packaging
- **Import order**: stdlib → third-party → local project modules (alphabetically sorted within groups)
- **Avoid circular dependencies**: Refactor using dependency injection or protocol abstraction

#### Python Standards
- **Version**: Python 3.8+ required
- **Style**: PEP 8 compliance mandatory
- **Type hints**: Required for function signatures and public APIs
- **Docstrings**: Google or NumPy style for modules, classes, and public functions

#### TypeScript Standards
- **Strict mode**: TypeScript strict mode enabled
- **Interfaces**: Define TypeScript interfaces for all component props and API contracts
- **No `any`**: Avoid `any` type; use proper typing or `unknown`

---

## Architecture & Quality

### Design Patterns

These patterns govern the codebase structure. New code MUST follow established patterns;
deviations require explicit justification.

#### Factory Pattern
- **ModelClientFactory**: Creates provider-specific AI model clients with caching
- **RepositoryFactory**: Centralizes repository creation with singleton instances
- **ServiceFactory**: Wires repositories into services with dependency injection

#### Repository Pattern
- All database access MUST go through `src/data/repositories/` extending `MongoGenericRepository`
- No ad-hoc database queries in routes, services, or presentation layers
- Repositories implement `health_check() -> Tuple[bool, Dict]` contract

#### Blueprint Architecture
- Flask routes organized by domain in `src/web/routes/<domain>.py`
- Each blueprint receives dependencies via immutable `APIRouteContext` (frozen dataclass)
- Registration through app factory in `api_server.py`

#### Protocol-Based Dependencies
- Cross-service dependencies use protocols (structural typing) from `src/services/protocols.py`
- Avoids circular imports; enables easy testing with duck-typed mocks
- Services depend on abstractions, not concrete implementations

#### Layered Architecture
The system follows strict layer separation:
```
Routes (API Layer) → Services (Business Logic) → Repositories (Data Access) → Database
```
- Routes handle HTTP/WebSocket concerns only
- Services contain business logic and orchestration
- Repositories handle data persistence
- Each layer depends only on the layer below

### SOLID Principles

All code MUST adhere to SOLID principles. These are non-negotiable design constraints.

**Single Responsibility**: One concern per layer; routes handle HTTP, services handle business
logic, repositories handle data access. Each class/module has one reason to change.

**Open/Closed**: Extend via new modules (blueprints, services, providers) registered in
factories. Avoid editing unrelated modules to add functionality.

**Liskov Substitution**: Implementations MUST honor interface contracts (types, errors,
invariants). No consumer-specific branches or special cases that violate expected behavior.

**Interface Segregation**: Keep interfaces lean; split large surfaces. Give consumers only what
they need (read vs write, query vs command).

**Dependency Inversion**: Depend on protocols/interfaces (e.g., `WorkspaceProvider`,
`UserProvider`), not concrete implementations. Inject dependencies via factories/config.

**Additional**: Favor composition over inheritance except for established bases (`BaseService`,
`MongoGenericRepository`, `CacheBackend`). Add new components as modules registered in factories
rather than modifying existing code.

### Testing Standards

#### Test Philosophy
- **Test behavior, not implementation**: Focus on user-facing functionality and API contracts
- **Fast feedback**: Unit tests MUST complete in seconds; integration tests in minutes
- **Isolation**: Tests MUST NOT depend on external services, network, or shared state
- **Repeatability**: Tests MUST produce consistent results regardless of execution order

#### Test Pyramid
```
       /\
      /E2E\         ← 5-10% of tests
     /------\       User workflows, UI → API → DB
    /  INT   \      ← 20-30% of tests
   /----------\     API routes, service integration
  /   UNIT     \    ← 60-75% of tests
 /--------------\   Pure functions, business logic
```

#### Coverage Requirements
- **Overall**: 80%+ line coverage minimum
- **Critical paths**: 90%+ for financial data accuracy, model fallback logic, user authentication
- **Edge cases**: Error handling, boundary conditions, null/empty inputs MUST be tested

#### Mocking Requirements
- Mock ALL external dependencies (APIs, databases, network)
- Tests MUST run offline without real connections
- Use `MagicMock` for protocol-based dependencies
- Never use real API keys in tests

### Quality Gates

#### Pre-Commit Checklist
- [ ] Code compiles/imports without errors
- [ ] Test suite passes locally with 100% pass rate
- [ ] No secrets or credentials in code/logs
- [ ] No `print()` statements—use logging
- [ ] Type hints present on public APIs

#### Pull Request Requirements
- [ ] Descriptive title explaining what and why
- [ ] Tests added/updated for all changes
- [ ] Documentation updated (README, OpenAPI, inline docs)
- [ ] Breaking changes explicitly noted with migration path
- [ ] PR addresses one logical change (split large changes)

#### CI/CD Pipeline
- **Build**: Clean compilation with no errors or warnings
- **Lint**: PEP 8 for Python, ESLint for TypeScript—zero violations
- **Type Check**: mypy for Python, tsc for TypeScript—must pass
- **Tests**: All automated tests pass with >80% meaningful coverage
- **Security**: No high/critical vulnerabilities in dependencies

---

## Governance

### Supremacy
This constitution supersedes all other practices. When conflicts arise, constitutional
principles take precedence.

### Amendment Process
1. Propose amendment with rationale and impact analysis
2. Document affected components and migration plan
3. Require explicit approval before implementation
4. Update version number and amendment date

### Compliance Verification
- All PRs/reviews MUST verify constitutional compliance
- Complexity MUST be justified against simplicity principle
- Use `.github/instructions/` for runtime development guidance
- Automated checks enforce linting, testing, and type checking

### Version Control
- **MAJOR**: Breaking changes to core principles or backward-incompatible governance changes
- **MINOR**: New articles, principles, or materially expanded guidance
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

**Version**: 1.2.0 | **Ratified**: 2026-01-27 | **Last Amended**: 2026-03-12
