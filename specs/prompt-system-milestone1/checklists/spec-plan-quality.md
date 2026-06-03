# Checklist: Spec-to-Plan Quality Gate & Cross-Reference Consistency

**Feature**: prompt-system-milestone1 (M1 — Prompt Runtime Parity)
**Created**: 2026-06-03
**Domain**: Spec-to-plan traceability, requirement quality, and cross-document consistency

## Requirement Completeness

- [X] CHK001 — Are all 6 PS backlog items (PS-01 through PS-06) explicitly addressed by at least one functional requirement (M1-FR-001 through M1-FR-012)? [Completeness, Spec §Requirements]
- [X] CHK002 — Is the scope boundary between M1 and M2-M5 clearly specified with explicit exclusions for PS-07 (route-context skills), PS-08 (route skills), PS-09/PS-10 (evaluation harness), PS-11 (experiment modes), and PS-12 (multi-agent taxonomy)? [Completeness, Spec §Governance Context → Out-of-Scope]
- [X] CHK003 — Are all 8 governing SRS items (FR-1.4.5, FR-1.4.6, FR-1.4.8, FR-1.4.16, NFR-5.2.5–5.2.9, NFR-6.2.3, AC-8.1, AC-8.2) mapped to at least one M1 functional requirement? [Completeness, Spec §Requirements]
- [X] CHK004 — Is the `PromptSelection` output contract fully specified with all required fields (selected_assets, prompt_version, prompt_variant, selection_mode, fallback_used, degraded_reason, trace_metadata) in both the spec and the plan? [Completeness, Spec M1-FR-005, Plan §Technical Context]
- [X] CHK005 — Does the plan include test tasks for all four test files listed (`test_prompt_asset_loader.py`, `test_prompt_metadata.py`, `test_prompt_config.py`, `test_agent_regression.py`)? [Completeness, Plan §Project Structure]
- [X] CHK006 — Are the recovery flows defined for all three fallback trigger scenarios (missing asset, malformed frontmatter, version not found)? [Completeness, Spec §User Story 2, §Edge Cases]

## Requirement Clarity

- [X] CHK007 — Is the two-layer validation model (structural error → blocks startup vs content-resolution error → falls back with WARN) clearly distinguished in every place it is referenced across spec and plan? [Clarity, Spec M1-FR-009a/M1-FR-009b, Plan §Constraints]
- [X] CHK008 — Are the performance targets quantified with specific thresholds: <50ms startup loading, <10ms metadata emission, no regression in NFR-1.1.1–1.1.6? [Clarity, Plan §Performance Goals, Spec M1-NFR-002/M1-NFR-003]
- [X] CHK009 — Is the term "most recent known-good baseline lineage" defined with enough precision to determine what constitutes the baseline and when it changes? [Clarity, Spec M1-FR-006, M1-FR-007]
- [X] CHK010 — Is the difference between "config reload" and "service restart" for NFR-6.2.3 compliance explicitly resolved (M1 uses startup-only initialization; live reload deferred)? [Clarity, Spec §Edge Cases → PS-03 config reload vs restart]
- [X] CHK011 — Are the 5 seed queries enumerated with their expected route classifications and the acceptance criteria for "semantically equivalent behavior"? [Clarity, Spec §User Story 1 → Independent Test]
- [X] CHK012 — Is the LangSmith independence requirement stated positively: response metadata MUST always be populated; LangSmith traces MAY be degraded silently? [Clarity, Spec M1-NFR-004, Spec §User Story 4 → AC-4]

## Requirement Consistency

- [X] CHK013 — Does the spec's Governance Context include AC-8.7 (Automatic Rollback Triggering) as a source authority, while the Assumptions section states auto-rollback triggers are deferred to M4 (PS-11)? This is a potential inconsistency. [Consistency, Spec §Governance Context vs §Assumptions]
- [X] CHK014 — Do spec.md and plan.md agree on the four test file names and their locations? [Consistency, Spec §User Stories → Independent Tests, Plan §Project Structure]
- [X] CHK015 — Does the plan's Constitution Check list the same governing artifacts as the spec's Governance Context? [Consistency, Spec §Governance Context, Plan §Constitution Check]
- [X] CHK016 — Do the `mapped_srs_items` in `specs/spec-traceability.yaml` match the SRS mapping annotations in each spec User Story? [Consistency, Spec §User Stories → SRS mapping, specs/spec-traceability.yaml]
- [X] CHK017 — Does the plan identify `tests/test_agent_regression.py` as a test file, but the spec's User Story 1 Independent Test describes test protocols (5-query seed set) without naming a specific test file? [Consistency, Spec §User Story 1, Plan §Project Structure]

## Cross-Reference Anchor Accuracy

- [X] CHK018 — Does the spec's anchor `ARCHITECTURE_DESIGN.md §4.5.1.1` resolve to valid content describing the ADR taxonomy (version in frontmatter, not directory path)? [Cross-Reference, Spec §Governance Context, ARCHITECTURE_DESIGN.md §4.5.1.1]
- [X] CHK019 — Does the spec's anchor `ARCHITECTURE_DESIGN.md §4.8.2` describe the planned `PromptAssetLoader → PromptAssembler → ResponseGuardrailMiddleware` pipeline? [Cross-Reference, Spec §Governance Context, ARCHITECTURE_DESIGN.md §4.8.2]
- [X] CHK020 — Does the spec's anchor `TECHNICAL_DESIGN.md §3.5 Prompt Realization and Guardrails` describe selection tuple fields that match the spec's M1 scope? Note: TECHNICAL_DESIGN.md §3.5.2.2 specifies an 8-field selection tuple including `route`, `locale`, `workspace_mode`, and `env`, but M1 scope is single-agent ReAct with one baseline. [Cross-Reference, Spec §Governance Context → Expected Sync Targets, TECHNICAL_DESIGN.md §3.5.2.2]
- [X] CHK021 — Do all `docs/` references in spec.md and plan.md use section-level anchors per Constitution v2.1.0 §Cross-Reference Precision Rule 1? [Cross-Reference, Constitution §Document Referencing]
- [X] CHK022 — Does the plan reference `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md §Proposed Prompt Asset Model` and does that section actually describe the `react_analyst.md` path with version in frontmatter? [Cross-Reference, Plan §Constitution Check, Spec §Governance Context]

## Acceptance Criteria Quality

- [X] CHK023 — Can AC-8.1 (prompt version in response metadata and trace spans) be objectively verified by the described integration test? [Measurability, Spec §User Story 1 → AC-1, SRS AC-8.1]
- [X] CHK024 — Can AC-8.2 (missing/malformed asset → baseline fallback + WARN) be objectively verified by the described fault-injection test? [Measurability, Spec §User Story 2 → AC-2, SRS AC-8.2]
- [X] CHK025 — Are the success criteria (SC-M1-01 through SC-M1-07) each associated with a specific test or verification method, making them independently verifiable? [Measurability, Spec §Success Criteria]
- [X] CHK026 — Is "semantically equivalent agent behavior" in SC-M1-02 defined with concrete comparison criteria (same section structure, same tool-call pattern, no new safety failures)? [Measurability, Spec SC-M1-02, Spec §User Story 1 → Independent Test]
- [X] CHK027 — Is the 5-query seed set defined with enough specificity to be reproducible by a different engineer? [Measurability, Spec §User Story 1 → Independent Test]

## Scenario Coverage

- [X] CHK028 — Does the spec define the primary success scenario (all PS items implemented, single baseline asset, config loads correctly)? [Coverage, Spec §User Stories]
- [X] CHK029 — Does the spec define the recovery path for the "fallback chain exhaustion" case (no baseline lineage available)? The spec documents this as a startup error for M1, not a graceful fallback. Is this documented as a known limitation? [Coverage, Spec §Edge Cases → PS-02/PS-03 fallback chain exhaustion]
- [X] CHK030 — Are non-functional scenarios (startup with invalid config, startup with missing asset, startup with malformed frontmatter) defined with expected outcomes? [Coverage, Spec §User Story 3 → AC-2, AC-3]
- [X] CHK031 — Does the spec cover the stateless request scenario (no `conversation_id`) for metadata emission? [Coverage, Spec §Edge Cases → PS-05 metadata on stateless requests]
- [X] CHK032 — Does the spec cover the legacy `REACT_SYSTEM_PROMPT` deprecation scenario (alias retained, primary path switched)? [Coverage, Spec §Edge Cases → Legacy REACT_SYSTEM_PROMPT removal]

## Edge Case Coverage

- [X] CHK033 — Are requirements defined for the edge case where version is in the filename path instead of frontmatter metadata (roadmap vs ADR taxonomy conflict)? [Edge Case, Spec §Edge Cases → PS-01 extraction]
- [X] CHK034 — Is the edge case for missing frontmatter delimiters (`---` missing) defined and assigned to the correct fallback behavior? [Edge Case, Spec §Edge Cases → PS-01 extraction: missing frontmatter]
- [X] CHK035 — Is the edge case for LangSmith-unreachable behavior defined (response metadata always populated, trace tags degrade silently)? [Edge Case, Spec §Edge Cases → PS-05 LangSmith-unavailable fallback]
- [X] CHK036 — Is the edge case for concurrent config file changes during agent operation defined? Note: M1 uses startup-only config initialization. [Edge Case, Spec §Edge Cases → PS-03 config reload vs restart]

## Non-Functional Requirements Quality

- [X] CHK037 — Are the performance NFRs (M1-NFR-002: <50ms startup, M1-NFR-003: <10ms metadata) quantified with specific pass/fail thresholds? [NFR Quality, Spec M1-NFR-002, M1-NFR-003]
- [X] CHK038 — Is the LangSmith independence NFR (M1-NFR-004) stated with a measurable criterion ("always populated regardless of connectivity")? [NFR Quality, Spec M1-NFR-004]
- [X] CHK039 — Is the cache invalidation strategy for `PromptAssetLoader` defined with sufficient detail to implement (tied to manifest-version, review-state, or lineage changes)? [NFR Quality, Spec M1-NFR-001]
- [X] CHK040 — Are the trace metadata latency requirements verifiable without production load testing? [NFR Measurability, Spec M1-NFR-003]

## Dependencies & Assumptions

- [X] CHK041 — Is the assumption that `PyYAML` is available (via existing transitive dependency) documented and validated? [Assumption, Spec §Assumptions, Plan §Technical Context]
- [X] CHK042 — Is the assumption that the roadmap `v1.md` path is superseded by ADR taxonomy explicitly documented, with the supersession rationale given? [Assumption, Spec §Assumptions]
- [X] CHK043 — Is the assumption that LangSmith tracing integration already exists validated against the actual `requirements.txt` or `langsmith` SDK availability? [Assumption, Spec §Assumptions]
- [X] CHK044 — Is the dependency on `config/config.yaml` changes documented as requiring coordination with deployment teams (config changes affect all environments)? [Dependency, Plan §Project Structure, Plan §Sync Targets]
