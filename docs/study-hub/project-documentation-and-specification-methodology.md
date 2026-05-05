# Project Documentation Architecture and Spec-Driven Development Strategy

## Document Control

| Field | Value |
|-------|-------|
| Project | DP Stock Investment Assistant |
| Domain | Documentation architecture, requirements engineering, and specification governance |
| Focus | Spec-driven development strategy integrating system SRS, SDD lifecycle, constitution governance, and automated traceability for a multi-layer, multi-domain system |
| Date | 2026-04-01 |
| Status | Draft for planning and documentation-generation follow-up |
| Audience | Engineering, architecture, product, platform, and technical documentation maintainers |

## 1. Executive Summary

This document proposes a target-state documentation architecture for the DP Stock Investment Assistant repository, integrated with the project's **Spec-Driven Development (SDD)** methodology as the primary delivery and documentation governance engine.

The project is already a multi-layer, multi-domain system with distinct frontend, API, agent, service, data, and infrastructure concerns. The current repository contains strong documentation assets and an established SDD practice with constitution governance, automated traceability, and a quality gate chain through spec-kit extensions.

The current recommendation is:

- adopt **Spec-Driven Development as the central methodology** for how requirements flow from stable system-level definitions through feature delivery to verified implementation
- adopt a **hybrid, domain-oriented documentation model** with one master system SRS as the upstream requirement pool, whole-system architecture documents, and domain-owned realization documents under `docs/domains/`
- retain the **Constitution** (`.specify/memory/constitution.md`) as the non-negotiable governance layer that all feature specs, plans, and implementations must satisfy
- keep **ADRs** as decision records rather than requirement documents
- keep **OpenAPI** and other contract artifacts as executable interface sources of truth rather than duplicating them in prose
- keep **feature specs** under `specs/` as delivery-scoped realization artifacts linked back to approved requirement IDs, following the 18-step SDD lifecycle
- maintain **automated traceability** through `spec-traceability.yaml`, `sync_spec_status.py`, and spec-kit sync extensions to detect and resolve drift

This proposal is intentionally designed to be the next-step input for generating the future project documentation set. It does not attempt to rewrite the current document corpus. Instead, it defines the target structure, the SDD lifecycle integration, the governance model, and the document boundaries needed to guide the next documentation-generation phase.

## 2. Problem Statement

The current project has meaningful documentation depth and a proven SDD practice, but both are unevenly distributed:

- the agent domain already has a detailed SRS (v2.2, 302 items), architectural decision record set, and technical design documents
- the frontend domain already has ADRs and research reports for modernization and modularization
- the repository already maintains a machine-readable traceability model (`spec-traceability.yaml`) and automated sync (`sync_spec_status.py`) for feature-level specs
- the API surface already has a maintained OpenAPI specification (v1.4, 26+ endpoints)
- the operational domain already has practical artifacts such as reconciliation and migration tooling
- the SDD practice has been validated through three delivered features with full lifecycle completion (specify → plan → tasks → implement → verify)

However, the project still lacks a fully defined **system-level documentation architecture integrated with the SDD lifecycle** that answers these questions consistently:

- what document types exist in this repository and what each one is responsible for
- which document is authoritative for requirements, architecture decisions, contracts, technical realization, UX/UI intent, test evidence, and operations
- how the SRS, constitution, and SDD phases interact to govern how requirements are authored, delivered, verified, and maintained
- how requirements for frontend, API, agent, services, data, and maintenance should be distributed across documents
- how the project should evolve documentation over time without creating duplication, drift, or ambiguity
- how the existing automated traceability and quality gate chain extend to cover system-level and cross-domain documentation

Without an explicit documentation architecture that integrates with the proven SDD methodology, the next phase of project documentation generation risks producing overlapping artifacts that blur the boundary between requirements, decisions, design, and delivery, and that lack the automated governance mechanisms the project already relies on for feature-level work.

## 3. Objectives

This proposal has six objectives:

1. define a practical, repo-native target documentation structure for a multi-layer system
2. define the purpose and standards stance for each major document type
3. define how the SDD lifecycle governs the flow from stable requirements through feature delivery to verified documentation
4. define the constitution and quality gate integration model for system-level documentation
5. define the outline of the future master system SRS as the upstream requirement pool for SDD
6. define the subordinate document boundaries so future documentation generation stays coherent

## 4. Related Documents

This proposal is based on and aligned with the current project documents below.

| Document | Purpose in Current Repository | Role in This Proposal |
|----------|-------------------------------|-----------------------|
| [Architecture Review](../architecture-review.md) | Cross-domain and cross-layer architecture assessment of frontend, backend, agent, data, and infrastructure | Provides the system-wide framing and writing style for cross-domain and cross-layer documentation |
| [Stock Investment Assistant Agent — Software Requirements Specification](../langchain-agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md) | Detailed domain SRS for the agent system | Reference model for requirement structure, numbering, and wording |
| [SRS Spec Traceability](../langchain-agent/SRS_SPEC_TRACEABILITY.md) | Reverse trace from SRS items to feature specs | Reference model for requirement-to-delivery traceability |
| [Frontend Architecture Evolution Report](../frontend/frontend-architecture-evolution-report.md) | Research report for frontend architectural evolution | Reference model for analysis-oriented study documents |
| [ADR-Frontend-001](../frontend/adr-frontend-001-modular-application.md) | Frontend architectural direction | Reference model for ADR boundary and decision phrasing |
| [ADR-Frontend-002](../frontend/adr-frontend-002-modernize-frontend-foundation.md) | Frontend modernization stack and delivery direction | Reference model for implementation-oriented architecture decisions |
| [Spec-Kit HOW-TO](../spec-driven%20development%20(SDD)/spec-kit%20HOW-TO.md) | Repository-specific SDD workflow guidance with the 18-step SDD lifecycle | Defines the canonical SDD phase chain that this proposal integrates with system-level documentation |
| [Project Constitution](../../.specify/memory/constitution.md) | Non-negotiable governance layer: 7 core principles, 9 golden rules, memory boundaries, SOLID constraints, quality gates | Defines the governance authority that all system-level and feature-level documentation must satisfy |
| [Spec Traceability Registry](../../specs/spec-traceability.yaml) | Machine-readable traceability manifest linking SRS items to feature specs with status gates | Defines the automated traceability model that system-level documentation must integrate with |
| [OpenAPI Specification](../openapi.yaml) | Executable API contract for the backend | Canonical contract artifact in the proposed documentation model |

## 5. Proposed Documentation Model

### 5.1 Recommended Model

The recommended target state is a **hybrid, domain-oriented documentation model governed by Spec-Driven Development**.

This means:

- one master system SRS as the **upstream requirement pool** that feature specs draw from
- domain-owned documentation grouped under `docs/domains/` for frontend, backend, agent, and data realization
- subordinate requirement specifications only where a domain (bounded context) is sufficiently specialized or already mature
- the **Constitution** as the non-negotiable governance layer that all specs, plans, and implementations must satisfy
- the **SDD lifecycle** (specify → clarify → plan → tasks → implement → verify) as the primary mechanism through which requirements become delivered, tested, and documented code
- domain technical design documents that explain realization, not requirements
- ADRs that explain architecturally significant decisions, not functional scope
- contract artifacts owned by the relevant domain that define interfaces directly, without unnecessary prose duplication
- feature specs that remain delivery-scoped and traceable to stable requirement IDs
- **automated traceability** (spec-traceability.yaml, sync_spec_status.py, speckit.sync) as the mechanism that keeps documentation and code aligned

Throughout this proposal, the units grouped under `docs/domains/` are better understood as **bounded contexts or delivery domains**, not technology stacks. The repository path is retained for brevity, but terms such as frontend, backend, agent, and data should be read as ownership domains or layers rather than as references to React, Flask, LangGraph, or similar implementation stacks.

This model is the best fit for the current repository because it preserves existing documentation strengths and the proven SDD practice while avoiding two failure modes:

- a single oversized SRS that mixes business intent, API schema, architecture decisions, and technical design
- a fragmented document set where every subdomain invents its own structure and terminology without a system-level anchor

### 5.2 The SDD Role in System Documentation

In this model, Spec-Driven Development is not merely a delivery process — it is the **documentation governance engine**:

- **SRS documents** define WHAT the system must do (the stable requirement pool)
- **Constitution** defines the non-negotiable constraints that all work must satisfy
- **SDD feature specs** translate approved requirements into delivery-scoped specifications with acceptance scenarios
- **SDD plans and tasks** produce the detailed realization artifacts
- **SDD verify and sync** keep documentation aligned with implementation

The consequence is that system-level documentation is not generated once and maintained by hand. Instead, it is *authored as stable reference material and then kept current through the SDD lifecycle*: when a feature spec touches a requirement, the traceability registry records the mapping; when implementation diverges from the spec, the sync extension detects drift; when new behavior is added without a spec, backfill analysis surfaces the gap.

### 5.3 Long-Lived vs. Delivery-Scoped Artifacts

The documentation model distinguishes two artifact lifecycles:

| Lifecycle | Location | Characteristics | Examples |
|-----------|----------|-----------------|----------|
| **Long-lived** | `docs/` | Evolve slowly; own stable contracts and cross-domain obligations; updated through SDD traceability when feature delivery touches their domain | System SRS, architecture docs, domain technical design, ADRs, owned contracts, runbooks |
| **Delivery-scoped** | `specs/` | SDD spec-kit artifacts created when a feature is specified; complete when verified; may trigger updates to long-lived docs during sync phase | spec.md, plan.md, tasks.md, review.md, data-model.md, contracts/, quickstart.md |

Long-lived documents are **upstream** reference material. Delivery-scoped artifacts are **downstream** working documents. The SDD lifecycle connects them through requirement mapping, traceability registry entries, and post-delivery sync checks.

### 5.4 Documentation Design Principles

The target documentation architecture should follow these principles:

1. **One primary responsibility per document type**
2. **Authoritative source over duplicated prose**
3. **Cross-domain consistency for terminology and IDs**
4. **Traceability from requirement to design, implementation, verification, and maintenance evidence**
5. **Separation of WHAT, WHY, HOW, and HOW TO OPERATE**
6. **Incremental evolution rather than wholesale document replacement**
7. **Spec-first delivery**: every non-trivial change flows through the SDD lifecycle before modifying long-lived documentation
8. **Constitution compliance**: all documentation artifacts must satisfy the constraints defined in the project constitution
9. **Automated drift detection**: documentation currency is maintained through tooling, not manual discipline alone

## 6. Standards Stance

This proposal uses three standards stances so the project can be disciplined without pretending formal compliance where it does not need to.

| Stance | Meaning | Typical Use in This Repository |
|--------|---------|--------------------------------|
| **Conformant** | The document should comply directly with an external standard or machine-readable schema | OpenAPI, JSON schema-based contract artifacts |
| **Aligned** | The document should follow the structure, intent, and terminology of a standard without claiming certification | SRS, architecture descriptions, UX process framing |
| **Practice-Based** | The document should follow an explicit internal template derived from good engineering practice | ADRs, runbooks, feature specs, study documents |

### 6.1 Recommended External Standards and Practices

| Standard / Practice | Recommended Use |
|---------------------|-----------------|
| **ISO/IEC/IEEE 29148** | Use as the primary organizing model for requirements engineering, requirement quality, and document layering |
| **ISO/IEC/IEEE 42010** | Use as the framing model for architecture descriptions and viewpoint separation |
| **OpenAPI 3.1** | Use as the authoritative HTTP API contract standard |
| **WCAG 2.2 AA** | Use as the baseline accessibility standard for UI and UX design specifications |
| **ADR / Nygard-style decision records** | Use as the practice model for architecture-significant decision capture |
| **Spec-Kit / Spec-Driven Development** | Use as the **primary delivery and governance methodology** for feature planning, implementation, verification, and documentation maintenance |

### 6.2 Canonical Glossary (Normative Taxonomy)

The terms in this glossary are the canonical vocabulary for this repository. Contributors should use these terms consistently in SRS documents, technical design documents, ADRs, contracts, and feature specs.

| Term | Canonical Meaning | Use This For | Avoid Using For |
|------|-------------------|--------------|-----------------|
| **Domain** | A delivery ownership unit that groups related responsibilities and artifacts | Requirement allocation, document ownership, technical design scope | Naming implementation tool choices |
| **Bounded Context** | A domain boundary with explicit semantics and responsibilities | Clarifying scope boundaries when terms overlap across domains | Generic synonym for every folder |
| **Layer** | A technical or architectural level within a domain or service | Route/service/repository separation, presentation/business/data layering | Cross-domain ownership mapping |
| **Technology Stack** | The concrete implementation technologies used to build a domain or service | React/TypeScript, Flask/Python, LangGraph/LangChain, MongoDB/Redis | Requirement ownership taxonomy |
| **API Boundary / API Contract** | The externally exposed interface of the backend domain, expressed normatively through executable contracts such as OpenAPI | Backend interface ownership, request/response obligations, compatibility and schema governance | A separate ownership domain independent from the backend domain |
| **Frontend Domain** | User interaction, UX flow, client-side state, and rendering responsibilities | UI requirements, frontend technical design, frontend ADR impacts | Backend API contract ownership |
| **Backend Domain** | API surface, orchestration, business workflows, and integration mediation | System API obligations, service-layer realization, contract publication | Agent reasoning policy |
| **Agent Domain** | AI reasoning workflow, tool orchestration, memory behavior, and response composition | Agent-specific subordinate SRS and behavior constraints | Full-system requirement ownership |
| **Data Domain** | Persistence, schema/index policy, retention, migration, and cache behavior | Data constraints, storage semantics, recoverability concerns | UI or API interaction behavior |
| **Operations Domain** | Release readiness, observability operations, reconciliation, migration safety, and runbooks | Operations policy and runbook responsibilities | Functional feature behavior definitions |
| **Master System SRS** | The authoritative cross-domain requirement baseline | SR/SNR requirements, system-level lifecycle obligations | Domain-local implementation detail |
| **Domain SRS** | A subordinate SRS for one domain when justified by complexity | Domain-local specialization that does not contradict master SRS | Replacing master SRS authority |
| **Executable Contract** | Machine-readable interface source of truth (e.g., OpenAPI schema) | Payload/schema definitions and compatibility checks | Narrative rationale and decision tradeoffs |

**Repository path note**: The folder name `docs/domains/` is retained for backward compatibility and continuity, but its contents are interpreted normatively as domains/bounded contexts in this documentation model.

## 7. SDD Lifecycle Integration

### 7.1 The 18-Step SDD Lifecycle with Spec-Kit

The project has established an 18-step SDD lifecycle that governs all feature delivery. This lifecycle is the mechanism through which stable requirements become verified implementations and through which long-lived documentation stays current.

| Step | Phase | SDD Command | Documentation Impact |
|------|-------|-------------|---------------------|
| 0 | Requirements | Manual | Author SR/SNR or domain FR/NFR in the appropriate SRS document |
| 1 | Design | Manual | Author architectural and technical specifications |
| 2 | Governance | `speckit.constitution` | Verify constitution compliance before feature work begins |
| 3 | Specification | `speckit.specify` | Create spec.md referencing SRS IDs; update traceability registry |
| 4 | Clarification | `speckit.clarify` | Refine ambiguous requirements; record clarifications in spec.md |
| 5 | Planning | `speckit.plan` | Create plan.md with constitution check and technical context |
| 6 | Health check | `speckit.doctor` | Validate project state and template integrity |
| 7 | Quality checklist | `speckit.checklist` | Generate feature-specific quality checklist |
| 8 | Task generation | `speckit.tasks` | Create tasks.md with user-story-organized implementation tasks |
| 9 | Validation | `speckit.validate` | Verify spec-to-task traceability and file integrity |
| 10 | Analysis | `speckit.analyze` | Cross-artifact consistency and quality analysis |
| 11 | Review | `speckit.review` | Cross-model evaluation of plan and tasks before implementation |
| 12 | Implementation | `speckit.implement` | Execute tasks; code changes aligned to spec and plan |
| 13 | Task verification | `speckit.verify-tasks` | Detect phantom completions; verify code exists for every checked task |
| 14 | Post-implementation verification | `speckit.verify` | Validate implementation against spec, plan, tasks, and constitution |
| 15 | Testing and traceability | Manual + sync | Run tests; update spec-traceability.yaml with gate status |
| 16 | Maintenance | `speckit.sync` | Detect and resolve spec-to-code drift; backfill unspecced code |
| 17 | Documentation sync | Manual | Synchronize long-lived docs affected by the delivered feature |

### 7.2 How SDD Connects to System Documentation

The SDD lifecycle connects delivery-scoped artifacts (`specs/`) to long-lived system documentation (`docs/`) through these mechanisms:

1. **Requirement sourcing**: Step 3 (`speckit.specify`) references specific SRS requirement IDs. This creates an explicit upstream dependency from the feature spec to the system SRS.

2. **Traceability recording**: Step 5 (`speckit.plan`) updates the `spec-traceability.yaml` registry with the SRS-to-spec mapping. The registry enforces status gates (analyzed → planned → implemented → verified).

3. **Constitution compliance verification**: Steps 2, 5, and 14 verify the feature against the project constitution. This ensures every feature respects the governance constraints without manual review of every rule.

4. **Post-delivery documentation sync**: Step 17 is where the SDD lifecycle feeds back into long-lived documentation. When a feature changes API behavior, the OpenAPI contract must be updated (Constitution Golden Rule 9). When a feature introduces new architectural patterns, ADRs are created. When a feature covers new SRS territory, the traceability summary is updated.

5. **Drift detection**: Step 16 (`speckit.sync`) identifies when code has diverged from specs, when specs have diverged from SRS, or when code exists without spec coverage. This is the automated maintenance mechanism for the documentation set.

### 7.3 SRS as Upstream Requirement Pool

In this SDD-integrated model, the master system SRS has a specific role:

- it is the **stable** requirement source, not the working artifact
- requirements start in the SRS with an ID, statement, priority, primary owning domain, and contributing domains
- feature specs **draw** from the SRS by referencing requirement IDs (e.g., SR-3.1.1, SNR-2.3.2, or subordinate IDs such as FR-3.1.1 where delivery scope is anchored in a domain SRS)
- the SRS is **primarily updated** when new capability domains are identified, not on every individual feature delivery — but controlled iterative refinements such as sharpened acceptance criteria, clarified edge cases, and scope adjustments discovered during delivery may be fed back through a lightweight change-control process
- feature delivery **proves** SRS requirements through the traceability registry, not by rewriting the SRS — though iterative refinements to individual requirement entries are expected when delivery reveals ambiguity or gaps
- the SRS requirement entry can remain lightweight because the rich detail (rationale, acceptance scenarios, verification evidence) lives in the feature spec that delivers it

This is the key distinction from a traditional SRS-centric approach: the SRS defines the requirement pool; the SDD lifecycle delivers from it and proves coverage through traceability.

### 7.4 Practical SDD Best Practices for This Repository

For this repository, SDD should organize documentation and specifications using a simple rule: **keep long-lived documents few, stable, and cross-feature; keep feature detail in `specs/`.**

That translates into these practical operating rules:

1. **Start with the requirement source, not a new document family.** If a change can be expressed by extending the master SRS, an existing domain SRS, or `openapi.yaml`, do that before proposing a new long-lived document.
2. **Keep delivery detail in feature specs.** Acceptance scenarios, rollout notes, implementation sequencing, and evidence belong in `specs/<feature-id>/`, not in long-lived system documents.
3. **Promote only stable knowledge.** A concept should move from a feature spec into `docs/` only when it has become reusable, cross-feature, or part of the operating model.
4. **Prefer updating an existing document over creating a sibling.** Too many narrowly scoped documents create navigation and maintenance cost faster than they create clarity.
5. **Use executable artifacts as the contract source of truth.** If `openapi.yaml`, code-level schemas, or test contracts already express the interface, prose should explain obligations and rationale, not restate the contract.
6. **Create subordinate SRS documents only when the domain has sustained change pressure.** In this repository that likely means agent, frontend, and operations first; API and data should only gain separate requirement documents when repeated cross-feature obligations justify them.
7. **Promote requirement-level content after verification, not before.** SRS documents and requirement baselines should be updated after a feature passes implementation and verification, so the requirement record reflects proven behavior rather than planned intent. However, technical design documents and ADRs may be updated earlier in the lifecycle to communicate architectural direction to concurrent work — these serve as coordination tools, not just records of what was built.

### 7.5 SRS Lifecycle During Development

The diagram below shows how the master system SRS, domain SRS documents, feature specs, implementation, verification, and documentation sync should interact during delivery.

```mermaid
flowchart LR
  A["Master System SRS"] --> C["Feature Spec\n(spec.md)"]
  B["Domain SRS\nwhen justified"] --> C
  C --> D["Plan + Tasks"]
  D --> E["Implementation + Tests"]
  E --> F{"Verified against spec?"}
  F -- "No" --> C
  F -- "Yes" --> G["Documentation Sync"]
  G --> H{"Requirement impact?"}
  H -- "None" --> I["Traceability sync only"]
  H -- "Clarification or additive change" --> J["Minor SRS update\n+ traceability sync"]
  H -- "Breaking change, retirement, or conflict" --> K["Change review / ADR / approval"]
  K --> L["Major SRS update\n+ affected domain SRS sync"]
  J --> M["Updated requirement baselines"]
  L --> M
```

In practice, feature delivery should consume the current approved baseline, and requirement updates should be synchronized back only after the impact has been classified and the necessary approval path has been followed.

## 8. Constitution and Quality Gate Model

### 8.1 Constitution Governance

The project constitution (`.specify/memory/constitution.md`, currently v1.3) is the non-negotiable governance layer. It includes:

- **7 Core Principles** (from ADR-001): Memory boundaries, RAG integrity, tool-vs-LLM separation, market manipulation safeguards
- **9 Golden Development Rules**: Security first, test before merge, logging over print, document intent, backward compatibility, fail fast, keep it simple, follow domain standards, public API contract sync
- **Memory Architecture Boundaries**: Explicit lists of allowed and prohibited content in LTM and STM
- **Architecture and Quality constraints**: Factory, Repository, Blueprint, and Protocol patterns; SOLID principles; layered architecture enforcement

Every feature spec should pass a constitution check before planning begins (Step 2) and after design is complete (Step 5). The constitution check is enforced through the SDD workflow convention and spec-kit tooling, not through a programmatic CI gate — its effectiveness depends on consistent use of the `speckit.constitution` and `speckit.plan` commands during the SDD lifecycle. It is a strong governance convention, not an automated pipeline blocker.

### 8.2 Quality Gate Chain

The SDD practice uses a chain of quality gates enforced through spec-kit extensions:

| Gate | Extension | When Applied | What It Catches |
|------|-----------|--------------|-----------------|
| Spec quality | `speckit.understanding.validate` | After specify | Ambiguity, untestability, structural weakness (31 metrics, ISO 29148 gates) |
| Project health | `speckit.doctor` | Before plan | Missing templates, broken config, stale artifacts |
| Constitution compliance | `speckit.plan` (constitution check) | Before and after planning | Violations of core principles or golden rules |
| Traceability completeness | `speckit.validate` | After tasks | Unmapped requirements, orphaned tasks, missing files |
| Cross-artifact consistency | `speckit.analyze` | After tasks | Contradictions between spec, plan, and tasks |
| Cross-model review | `speckit.review` | Before implement | Blind spots, feasibility gaps, risk assessment |
| Phantom completion detection | `speckit.verify-tasks` | After implement | Tasks marked done but code missing or dead |
| Post-implementation verification | `speckit.verify` | After implement | Gaps between implemented code and spec/plan/tasks/constitution |
| Drift detection | `speckit.sync.analyze` | During maintenance | Code-to-spec divergence, unspecced features, inter-spec contradictions |

These gates apply to feature-level work today. As system-level documentation is generated, the same governance model should extend to long-lived documents through periodic sync analysis and constitution-aware authoring.

### 8.3 Traceability Automation

The project maintains automated traceability through three interconnected artifacts:

1. **`specs/spec-traceability.yaml`** — Machine-readable manifest linking SRS items to feature specs with status gates (analyzed → planned → implemented → verified). Currently tracks 302 SRS items with 123 mapped and 179 unmapped.

2. **`specs/spec-sync-status.md`** — Human-readable summary report showing feature mapping status, coverage, linked SRS items, and evidence links.

3. **`scripts/sync_spec_status.py`** — CLI automation that generates forward and reverse traceability reports from the YAML manifest.

When the system-level SRS is created, the traceability registry should be extended to track:

- system-level requirement IDs (SR-x for functional, SNR-x for non-functional) in addition to the current domain-level IDs (FR-x, NFR-x)
- cross-document references (e.g., a feature spec that delivers both agent requirements and API requirements)
- long-lived document freshness (last sync date, last delivery that touched the document)

### 8.4 Common Pitfalls, Tradeoffs, and Backward Pressure

An SDD-centered documentation strategy is strong, but it has real failure modes. The most important ones for this repository are below.

| Risk | How It Shows Up | Practical Countermeasure |
|------|------------------|--------------------------|
| **Document proliferation** | Every concern gets its own long-lived `.md` file, and maintainers stop keeping them current | Treat new long-lived docs as exceptions; require promotion criteria before creating them |
| **SRS overload** | The master SRS becomes a feature backlog, design spec, and test plan all at once | Keep the SRS lightweight; push detail into feature specs and contracts |
| **Spec bureaucracy** | Small changes are slowed down by over-heavy process expectations | Use SDD fully for non-trivial changes; allow lightweight handling for small, low-risk fixes while still updating traceability where needed |
| **Duplicate authority** | A requirement appears in SRS, a design doc, and an ADR with conflicting wording | Assign one owner per concern: SRS for requirements, ADR for decisions, contract for interface, feature spec for delivery detail |
| **Unverified promotion** | Planned behavior is copied into long-lived docs before code is verified | Update long-lived docs late in the lifecycle, after implementation and verification |
| **Tooling drift** | The process depends on traceability and sync tooling, but the registry is not maintained | Make sync and traceability updates part of the definition of done for any requirement-linked feature |
| **Backward pressure from existing docs** | Older documents continue to act as de facto sources of truth even after the new structure is defined | Reclassify existing docs explicitly as keep, merge, repurpose, or retire, and avoid creating parallel replacements without migration intent |

The main tradeoff is straightforward: SDD improves traceability and governance, but it adds process overhead. For this project, that overhead is justified for architecture changes, cross-domain and cross-layer features, agent behavior changes, API surface changes, and operational workflows. It is not justified if every small refactor must spawn a new long-lived document.

## 9. Target Documentation Structure

### 9.1 Target File Tree

The target structure should remain intentionally lean. It should organize documents first by ownership scope, then by artifact type. In this model, the repository uses four documentation layers:

1. **System** — canonical cross-domain requirements and governance
2. **Architecture** — whole-system structure, runtime flows, and architectural decisions
3. **Domains (Bounded Contexts)** — domain-owned realization, domain-specific constraints, and owned contracts
4. **Specs (SDD spec-kit)** — delivery-scoped feature artifacts created and maintained through the SDD lifecycle

```text
docs/
  system/
    REQUIREMENTS_METHOD_AND_GOVERNANCE.md
    SYSTEM_REQUIREMENTS_SPECIFICATION.md

  architecture/
    SYSTEM_OVERVIEW_AND_BOUNDARIES.md
    RUNTIME_AND_INTEGRATION_FLOWS.md
    decisions/
      ADR-0001-...
      ADR-0002-...

  domains/
    frontend/
      TECHNICAL_DESIGN.md
      decisions/
        adr-frontend-001-modular-application.md
        adr-frontend-002-modernize-frontend-foundation.md

    backend/
      TECHNICAL_DESIGN.md
      api/
        openapi.yaml

    agent/
      SOFTWARE_REQUIREMENTS_SPECIFICATION.md
      TECHNICAL_DESIGN.md
      decisions/

    data/
      TECHNICAL_DESIGN.md
      POLICY_AND_CONSTRAINTS.md

  operations/
    OPERATIONS_AND_RELEASE_POLICY.md
    RUNBOOKS/

  testing/
    VERIFICATION_AND_TRACEABILITY_STRATEGY.md

  study-hub/
    <analysis, proposals, research>

specs/
  <feature-id>/
    spec.md
    plan.md
    tasks.md
    review.md
    data-model.md
    contracts/
  spec-traceability.yaml
  spec-sync-status.md
```

This is the recommended compact domain model for this repository. The important simplifications are:

- the repository keeps one parent folder, `docs/domains/`, and the contents should be treated as ownership domains (bounded contexts) rather than technology stacks
- backend remains one bounded context, with API contracts owned inside that domain rather than split into a separate top-level API tree
- domain folders do not need symmetric document sets; each domain only grows when repeated delivery pressure justifies it
- delivery detail stays in `specs/`, so these domain folders hold stable design and specialized obligations rather than feature-by-feature change history

### 9.2 Purpose and Standards Stance by Document Type

| Document Type | Target Files | Purpose | Standards Stance |
|---------------|--------------|---------|------------------|
| **Master System SRS** | `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` | Authoritative source for cross-domain functional, non-functional, interface, lifecycle, and maintenance requirements | **Aligned** to ISO/IEC/IEEE 29148 |
| **Requirements Governance Guide** | `docs/system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md` | Defines how requirements are authored, approved, changed, traced, and retired | **Aligned** to 29148 traceability and change-discipline principles |
| **System Architecture Documents** | `docs/architecture/*.md` | Describe the system as a whole: boundaries, major building blocks, runtime flows, and cross-domain interactions | **Aligned** to ISO/IEC/IEEE 42010 |
| **ADRs** | `docs/architecture/decisions/` and `docs/domains/*/decisions/` | Capture architecturally significant decisions and tradeoffs at system or domain scope | **Practice-Based** ADR discipline |
| **Domain Technical Design** | `docs/domains/*/TECHNICAL_DESIGN.md` | Explains how each domain realizes the requirements allocated to it and records domain-specific constraints that do not belong in the system-level architecture documents | **Aligned** design practice |
| **Domain-Specific Requirement Documents** | only where justified, for example `docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md` | Holds subordinate requirement sets only when a bounded context is independently complex, specialized, or already mature enough to need its own requirement baseline | **Aligned** subordinate SRS practice |
| **Executable Contracts** | domain-owned artifacts such as `docs/domains/backend/api/openapi.yaml` | Defines request/response schemas, event contracts, and integration payloads without duplicating them in prose | **Conformant** to schema or contract standards |
| **Operations Policy and Runbooks** | `docs/operations/OPERATIONS_AND_RELEASE_POLICY.md`, `docs/operations/RUNBOOKS/` | Defines supportability, release readiness, migration, reconciliation, rollback, and incident handling expectations | **Aligned** for policy; **Practice-Based** for runbooks |
| **Verification and Traceability Strategy** | `docs/testing/VERIFICATION_AND_TRACEABILITY_STRATEGY.md` | Defines test levels, evidence expectations, and how requirements are proven through specs and tests | **Aligned** internal verification standard |
| **Study and Analysis Documents** | `docs/study-hub/` | Holds research, comparison studies, and planning proposals that inform decisions but are not themselves long-lived authority documents | **Practice-Based** study format |
| **Feature Specs** | `specs/<feature-id>/...` | Delivery-scoped realization documents for approved requirements | **Practice-Based** Spec-Kit workflow |
| **Traceability Registry and Reports** | `specs/spec-traceability.yaml`, `specs/spec-sync-status.md` | Maintains bidirectional requirement-to-delivery traceability | **Practice-Based** RTM-style governance |

### 9.3 Functional and Non-Functional Requirements in the Domain Model

Under the domain model, **functional requirements and non-functional requirements remain canonical at the system level first**, then are allocated to domains as ownership metadata.

The recommended rules are:

1. **System functional requirements live in the master system SRS.** These describe end-to-end capabilities such as conversation lifecycle, AI-assisted response generation, streaming, workspace management, and model fallback.
2. **System non-functional requirements also live in the master system SRS.** Performance, resilience, security, observability, maintainability, accessibility, and compatibility are cross-domain by default and should not be split into separate domain-owned source documents unless there is a strong reason.
3. **Each requirement should carry domain allocation metadata.** At minimum, each requirement should identify a primary owning domain and any contributing domains.
4. **Domain documents explain realization, not duplicate the SRS.** Domain technical design documents should show how allocated SRs and SNRs are satisfied inside that bounded context.
5. **A domain gets its own requirement document only when needed.** This should be exceptional, not the default. In this repository, the agent domain is the clearest justified example.

In short: the master SRS remains the source of truth for SR and SNR requirements, domain documents explain realization and specialization, and feature specs provide delivery detail and verification evidence.

### 9.4 Promotion Rules for New Long-Lived Documents

Before creating a new long-lived document under `docs/`, the project should answer yes to at least one of these questions:

1. Does this information apply across multiple features or releases?
2. Does it define a stable requirement, policy, or architectural decision that future work must follow?
3. Does more than one engineering area need to reference it?
4. Would keeping it only inside one feature spec make future maintenance harder?
5. Can the content be absorbed into an existing system, architecture, or domain document instead of creating a new sibling?

If the answer is no, the content should usually remain inside the feature spec or implementation artifact rather than being promoted into the long-lived documentation set.

## 10. Master System SRS Proposal

### 10.1 Purpose of the Master System SRS

The **master system SRS** should become the authoritative upstream requirement pool for the workload as a whole.

In the SDD-integrated model, it should define:

- the cross-domain behavior the system must provide, expressed as stable requirement IDs that feature specs can reference
- the non-functional qualities the overall system must satisfy
- the domain allocation for each requirement, identifying the primary owning domain and any contributing domains
- the lifecycle obligations that span development, release, support, maintenance, and evolution
- the boundaries between system-level requirements, domain-owned realization documents, and any justified subordinate requirement sets

It should not try to become a contract file, a domain technical design specification, a feature backlog, or a delivery artifact. Feature delivery detail belongs in `specs/` under the SDD lifecycle, while domain realization belongs in `docs/domains/*/TECHNICAL_DESIGN.md`.

### 10.2 Recommended Outline

The recommended outline for `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` is below. It is intentionally tighter than a traditional monolithic SRS so that domain-owned realization can live in the domain documents rather than bloating the master SRS.

1. **Document Control**
2. **Purpose, Scope, and Intended Use**
3. **Related Documents and Governance**
4. **System Context and Domain Model**
5. **System Functional Requirements**
6. **System Non-Functional Requirements**
7. **Requirement Allocation by Domain**
8. **Owned Contracts and Subordinate Requirement Sets**
9. **Verification, Traceability, and Change Control**
10. **Open Issues and Deferred Decisions**
11. **Revision History**

### 10.3 SRS Versioning and Change Control Mechanism

The master system SRS should use a simple three-level versioning scheme so requirement evolution is visible and downstream impact can be managed.

- **Major version** — breaking semantic changes to approved system requirements, retired or replaced requirement families, changed precedence rules between the master and domain SRS baselines, or major restructuring of the document baseline
- **Minor version** — additive requirements, approved clarifications that change expected behavior or verification, new domain allocations, or new subordinate SRS references
- **Patch version** — editorial corrections, wording cleanup, formatting, or traceability/reference updates that do not change requirement meaning

A lightweight change-control flow should govern SRS evolution:

1. **Trigger identification** — feature delivery, incident analysis, audit work, or roadmap planning identifies a needed requirement change.
2. **Change classification** — classify the update as clarification, additive change, breaking change, retirement, or editorial correction.
3. **Impact assessment** — identify affected requirement IDs, domain SRS documents, contracts, active feature specs, tests, and operational documents.
4. **Decision and approval** — approve routine clarifications and additions through normal SDD governance; escalate breaking changes, retirements, and precedence changes through an ADR or explicit governance decision.
5. **Baseline update** — update the master SRS, related domain SRS documents, revision history, and traceability manifest in one logical change set.
6. **Downstream synchronization** — sync affected feature specs, contracts, and verification assets so no stale requirement baseline remains in active delivery work.
7. **Verification closeout** — confirm the updated baseline is reflected in traceability reports and in any impacted in-flight feature specs.

The future `docs/system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md` should define the approver roles and change classes in more operational detail, but the process above should be treated as the minimum baseline.

### 10.4 Recommended Functional Requirement Families

The master system SRS should organize functional requirements at the system level using requirement families such as:

- **SR-1: User Interaction and Experience Continuity**
- **SR-2: Workspace, Session, and Conversation Lifecycle**
- **SR-3: AI-Assisted Response Generation and Analysis**
- **SR-4: Market, Portfolio, and Supporting Data Acquisition**
- **SR-5: Real-Time Delivery and Streaming Behavior**
- **SR-6: Model and Provider Selection with Fallback**
- **SR-7: Administration, Support, and Operational Tooling**
- **SR-8: Contract Exposure and Integration Compatibility**

### 10.5 Recommended Non-Functional Requirement Families

The master system SRS should organize non-functional requirements using families such as:

- **SNR-1: Performance and Latency**
- **SNR-2: Availability, Resilience, and Graceful Degradation**
- **SNR-3: Security, Privacy, and Tenant Isolation**
- **SNR-4: Data Integrity, Consistency, and Recoverability**
- **SNR-5: Observability and Diagnosability**
- **SNR-6: Maintainability and Testability**
- **SNR-7: Usability, Accessibility, and Responsive Behavior**
- **SNR-8: Compatibility, Versioning, and Change Safety**

> **Namespace note**: `SNR-` distinguishes system-level non-functional requirements from subordinate domain SRS documents that may already use `NFR-` numbering. This mirrors the `SR-` vs `FR-` separation used for functional requirements.

### 10.6 Requirement Entry Template (Domain-Allocated and SDD-Compatible)

To work effectively as a requirement pool for the SDD lifecycle, each requirement entry in the master SRS should be **lightweight, allocatable, and traceable**. The rich detail (rationale, acceptance scenarios, implementation sequencing, and verification evidence) lives in the feature spec that delivers the requirement.

Each requirement should include:

- **Requirement ID** — stable, never reused (e.g., SR-1.1.1 for functional, SNR-3.2.1 for non-functional)
- **Type** — Functional or Non-Functional
- **Title** — concise label
- **Requirement Statement** — what the system must do, expressed in SHALL/MUST language
- **Priority** — P0 (critical), P1 (important), P2 (desirable)
- **Primary Owning Domain** — the domain accountable for delivery coordination (frontend, backend, agent, data, operations)
- **Contributing Domains** — other domains that must participate in delivery or verification
- **Linked Domain Documents / Contracts** — which domain technical design or owned contract artifacts are relevant
- **Spec Coverage Status** — whether a feature spec has been created that delivers this requirement (populated by traceability automation)

This is intentionally lighter than a traditional heavy SRS template. The master SRS remains the canonical requirement source; domain documents explain realization; feature specs carry the detailed delivery and evidence model.

### 10.7 Example FR and NFR Allocation to Domains

The examples below show how domain allocation should work in practice.

**Example Functional Requirement**

| Field | Example |
|------|---------|
| Requirement ID | SR-5.1.1 |
| Type | Functional |
| Title | Streaming response delivery |
| Requirement Statement | The system SHALL deliver assistant responses incrementally to the user interface for streaming-capable chat requests. |
| Priority | P0 |
| Primary Owning Domain | backend |
| Contributing Domains | frontend, agent |
| Linked Domain Documents / Contracts | `docs/domains/backend/TECHNICAL_DESIGN.md`, `docs/domains/frontend/TECHNICAL_DESIGN.md`, `docs/domains/backend/api/openapi.yaml` |
| Spec Coverage Status | mapped via feature spec(s) in `specs/` |

**Example Non-Functional Requirement**

| Field | Example |
|------|---------|
| Requirement ID | SNR-5.2.1 |
| Type | Non-Functional |
| Title | Observability of conversation processing |
| Requirement Statement | The system SHALL emit sufficient logs, metrics, and traces to diagnose failures across conversation handling, agent invocation, and persistence boundaries. |
| Priority | P1 |
| Primary Owning Domain | backend |
| Contributing Domains | agent, data, operations |
| Linked Domain Documents / Contracts | `docs/domains/backend/TECHNICAL_DESIGN.md`, `docs/domains/data/POLICY_AND_CONSTRAINTS.md`, `docs/operations/OPERATIONS_AND_RELEASE_POLICY.md` |
| Spec Coverage Status | mapped via feature spec(s) in `specs/` |

## 11. Subordinate Document Boundaries

### 11.1 Boundary Rules

The future documentation set should follow the boundary rules below.

1. **Requirements live in SRS documents, not in ADRs.**
2. **Decisions live in ADRs, not in SRS documents.**
3. **Schemas live in contracts, not in prose-heavy requirements documents.**
4. **Realization lives in technical design, not in the master SRS.**
5. **Operational steps live in runbooks, not in policy or architecture documents.**
6. **Delivery scope lives in `specs/`, not in long-lived system documents.**

### 11.2 Boundary Matrix

| Document | Owns | Must Not Own |
|----------|------|--------------|
| **Master System SRS** | Cross-domain behavior, non-functional qualities, lifecycle obligations, and domain allocation metadata | Detailed API schemas, implementation algorithms, UI component behavior, domain-specific design detail |
| **System Architecture Documents** | Whole-system boundaries, building blocks, runtime flows, and cross-domain interaction views | Feature backlog detail, per-domain implementation specifics, operational runbook steps |
| **Domain Technical Design** | How one domain realizes allocated requirements, domain boundaries, internal design constraints, and domain-owned interfaces | New system requirements, organization-wide policy, detailed delivery task breakdown |
| **Domain-Specific Requirement Documents** | Specialized subordinate requirements for a single domain when justified by maturity or complexity | Full-system ownership, duplicated cross-domain SNRs, contract payload detail already owned elsewhere |
| **Executable Contracts** | Request/response schemas, event contracts, payload definitions, and examples | Business rationale, architectural tradeoff prose, feature planning detail |
| **Runbooks and Operations Policy** | Support procedures, release/rollback steps, reconciliation, migration, and incident response | Requirement rationale, architecture decision content, per-feature design detail |
| **Verification Documents** | Requirement-to-test policy, evidence expectations, release gates, and traceability rules | Feature behavior requirements, domain design internals, contract definitions |
| **Feature Specs** | Delivery-scoped scenario definition, implementation planning, tasks, and evidence collection | Long-lived system authority, stable domain design baseline, organization-wide policy |

### 11.3 Conflict Resolution Between Master and Domain SRS Documents

The documentation set should use explicit precedence rules so the master system SRS and subordinate domain SRS documents do not become competing sources of truth.

1. **The master system SRS prevails for system outcomes and cross-domain qualities.** End-to-end behavior, lifecycle obligations, shared interfaces, and system-level SNRs are owned by the master baseline.
2. **A domain SRS prevails for domain-local specialization.** Internal behavior, domain-local constraints, error semantics, or specialized workflows inside a single domain may be elaborated in the subordinate SRS, provided they do not weaken or contradict the master SRS.
3. **Executable contracts prevail for schema shape.** When prose and machine-readable contracts disagree on payload or schema details, the contract artifact should be treated as the immediate source of truth for structure, and the prose documents must be reconciled.
4. **Conflicts trigger reconciliation, not silent override.** If a domain SRS reveals a gap or contradiction in the master SRS, the fix should be to update the master SRS, add a cross-reference, or record the resolution in an ADR or governance decision.
5. **Feature work must not proceed against unresolved competing baselines.** Active specs should reference the approved baseline after reconciliation so traceability and verification remain coherent.

### 11.4 Domain-Specific Boundary Recommendations for the Current Repository

#### 11.4.1 Agent Domain

The current [Stock Investment Assistant Agent — Software Requirements Specification](../langchain-agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md) should remain the primary specialized requirement document for the agent domain, but it should be repositioned conceptually as the future `docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md` under the domain-oriented model.

It should stop carrying implied full-system responsibility and instead function as a subordinate domain SRS under the master system SRS.

#### 11.4.2 Frontend Domain

The current frontend ADRs should remain authoritative decision records for frontend architectural evolution and modernization and should map into the future `docs/domains/frontend/decisions/` folder.

The frontend domain should gain a `TECHNICAL_DESIGN.md` before it gains a subordinate requirements specification. A separate frontend requirements document is justified only when user-visible obligations become large and persistent enough that the master system SRS plus the frontend technical design are no longer sufficient.

#### 11.4.3 Backend Domain

The backend domain should own both its internal realization and its external API contracts. Under the target model, the current [OpenAPI Specification](../openapi.yaml) maps conceptually to `docs/domains/backend/api/openapi.yaml`.

The backend domain technical design should explain route, service, and integration layering. It should not duplicate API contract schemas that already live in OpenAPI.

#### 11.4.4 Data Domain

The data domain should own persistence-focused realization and policy constraints such as consistency, retention, lineage, migration, and checkpoint-related boundaries. It should gain a dedicated subordinate requirements or policy document only if those obligations become large enough that they can no longer be cleanly managed through the master SRS plus domain technical design.

#### 11.4.5 Operations and Maintenance

The repository already contains strong operational evidence artifacts such as reconciliation and migration tooling. What is missing is a stable, explicit policy layer above them.

That future layer should define expectations for release readiness, rollback and recovery, data reconciliation, migration safety, observability obligations, deprecation policy, and documentation freshness.

## 12. Recommended Generation Strategy

This document is intended to support the next phase of project documentation generation. The generation strategy below is structured around the SDD lifecycle, but it is intentionally optimized for **practical adoption**, not document completeness.

### 12.1 Principle: Start Small and Promote by Need

The practical goal is not to generate a complete documentation universe up front. The practical goal is to establish a **small authoritative core**, then promote more documents only when repeated delivery pressure proves they are needed.

### 12.2 Phase 1 — Establish the Minimum Viable Core

Generate or stabilize only the documents that the rest of the SDD workflow depends on:

1. `docs/system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md` — Defines how requirements are authored, approved, changed, traced, and retired.
2. `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — The upstream requirement pool for cross-domain requirements.
3. `docs/architecture/SYSTEM_OVERVIEW_AND_BOUNDARIES.md` — Whole-system static view and domain boundaries.
4. `docs/architecture/RUNTIME_AND_INTEGRATION_FLOWS.md` — Whole-system runtime flows across frontend, backend, agent, data, and operations concerns.
5. `docs/domains/backend/api/openapi.yaml` — The executable backend API contract, initially sourced from the current `docs/openapi.yaml`.

**SDD integration**: Extend `spec-traceability.yaml` to support system-level requirement IDs (SR-x, SNR-x) alongside the existing domain-level IDs (FR-x, NFR-x).

### 12.3 Phase 2 — Reclassify and Reuse Existing Strong Documents

Do not generate parallel replacements for documents the repository already maintains well. Instead:

1. Reclassify the current `docs/langchain-agent/` material into the future `docs/domains/agent/` ownership model.
2. Reclassify the current frontend ADRs into the future `docs/domains/frontend/decisions/` ownership model.
3. Reclassify the current `docs/openapi.yaml` into the future `docs/domains/backend/api/openapi.yaml` ownership model.

This phase is mostly classification, not content generation.

### 12.4 Phase 3 — Add Subordinate Documents Only Where Pressure Persists

Only after the core exists and reuse pressure is visible should the project add more long-lived documents. The likely order for this repository is:

1. `docs/domains/backend/TECHNICAL_DESIGN.md` — to explain route, service, repository, and integration layering.
2. `docs/domains/frontend/TECHNICAL_DESIGN.md` — to explain platform, modules, routing, and UI-state realization.
3. `docs/domains/data/TECHNICAL_DESIGN.md` — to explain persistence, schema, and cache realization.
4. `docs/operations/OPERATIONS_AND_RELEASE_POLICY.md` and `docs/testing/VERIFICATION_AND_TRACEABILITY_STRATEGY.md` — when operational and evidence expectations need stable long-lived homes.
5. Domain-specific subordinate requirement documents only if the master SRS plus domain technical design no longer provide enough clarity on their own.

Each new long-lived document should be introduced through SDD-backed feature work, so it is justified by an actual delivery need rather than speculative completeness.

### 12.5 Phase 4 — Promote Stable Knowledge Out of Feature Work

As features are delivered, promote only stable, repeated knowledge from `specs/` into long-lived docs:

1. stable requirements into the master or subordinate SRS
2. stable decisions into ADRs
3. stable contracts into domain-owned executable artifacts such as `docs/domains/backend/api/openapi.yaml`
4. stable operating procedures into runbooks

This keeps `docs/` lean and keeps `specs/` as the place where most delivery complexity lives.

### 12.6 Ongoing Maintenance Rule

On an ongoing basis, every documentation change should answer two questions:

1. Does this belong in a stable source under `docs/`, or is it really delivery detail that should remain in `specs/`?
2. If it belongs in `docs/`, which existing document should absorb it so the structure stays small?

## 13. Summary Recommendation

The recommended target state for the DP Stock Investment Assistant repository is a **lean domain-oriented documentation architecture** where SDD governs how documentation is authored, delivered, and maintained, while a small long-lived document core serves as the stable reference set.

This strategy preserves what the current repository already does well:

- detailed domain documentation in the agent area
- strong architecture-decision capture in the frontend area
- executable contract ownership via OpenAPI
- traceable delivery artifacts under `specs/`
- constitution-governed quality gates across the full lifecycle
- automated traceability between requirements, specs, and implementation

At the same time, it resolves the current structural gaps by introducing:

- a clear top-level documentation architecture with defined purposes and boundaries
- a simplified domain-oriented file tree anchored by SDD governance
- a standards stance for each document category
- the SDD 18-step lifecycle as the primary delivery mechanism for new documentation
- a constitution and quality gate model that prevents documentation drift
- a lightweight SRS template designed to complement rather than compete with feature specs
- explicit promotion rules so new long-lived documents are created only when they are truly needed

The practical recommendation is to keep `docs/` small, keep `specs/` rich, and promote stable knowledge upward only after feature work proves it belongs there. That is the best fit for this repository's current size, maturity, and maintenance capacity.

## 14. Revision History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 0.1 | 2026-04-01 | GitHub Copilot | Initial draft proposal for target documentation architecture and master SRS boundaries |
| 0.2 | 2026-04-01 | GitHub Copilot | Refined to center SDD as core methodology: added SDD lifecycle integration (Section 7), constitution and quality gate model (Section 8), reframed SRS as upstream requirement pool, lighter requirement entry template, SDD-aligned generation strategy |
| 0.3 | 2026-04-02 | GitHub Copilot | Simplified the target documentation structure to a minimum viable long-lived set; added practical SDD operating rules, promotion criteria, and explicit pitfalls/tradeoffs for repo-scale adoption |
| 0.4 | 2026-04-03 | GitHub Copilot | Disambiguated system-level NFR namespace (SNR-x) from agent-level (NFR-x); softened SRS immutability to allow controlled iterative refinements during delivery; corrected constitution governance wording to reflect convention-based enforcement via spec-kit tooling; scoped promote-after-verification rule to SRS and requirement baselines only, relaxing for technical design docs and ADRs which serve as coordination tools for concurrent work |
| 0.5 | 2026-04-03 | GitHub Copilot | Added an explicit SRS versioning and change-control mechanism; defined precedence and conflict-resolution rules between the master system SRS and subordinate domain SRS documents; reduced conceptual overuse of “stack” in prose by reframing the model around domains and layers while retaining `docs/domains/` as the repository path; added a Mermaid visualization of the SRS lifecycle during delivery and documentation sync |
| 0.6 | 2026-04-03 | GitHub Copilot | Added a normative canonical glossary section to lock taxonomy usage across contributors, including explicit definitions for domain, bounded context, layer, technology stack, domain ownership terms, SRS hierarchy terms, and executable contracts |
| 0.7 | 2026-04-03 | GitHub Copilot | Resolved remaining glossary drift by aligning the target file tree back to `docs/domains/`, correcting lifecycle wording to the 18-step SDD lifecycle consistently, and adding an explicit API Boundary / API Contract glossary entry to clarify that API is a backend domain boundary rather than a separate ownership domain |