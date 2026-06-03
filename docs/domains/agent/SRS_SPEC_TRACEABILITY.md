# SRS To Spec Traceability

> **Document Version**: 1.7  
> **Generated**: 2026-05-22 (manual reconciliation)  
> **Status**: Active  
> **Traceability Manifest Version**: 1  

## Baseline

- SRS: [docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md](SOFTWARE_REQUIREMENTS_SPECIFICATION.md)
- SRS version: `2.6`

## Summary

- Total traced SRS items discovered: `337`
- Items with linked specs: `151`
- Items without linked specs: `186`

For prompt-system entries that do not yet have a dedicated `specs/*` artifact, the `Linked Spec` column may point to an equivalent design-governance artifact in `docs/domains/agent/` or `docs/domains/agent/DECISIONS/`.

## Revision History

| Version | Date | Summary |
|---------|------|---------|
| `1.0` | `2026-03-19` | Initial bidirectional reverse trace generation between SRS items and spec-kit artifacts. |
| `1.1` | `2026-03-19` | Added line-specific SRS links, embedded document version tracking, and promoted exact pilot overlap to gate-enforced coverage. |
| `1.2` | `2026-03-19` | Added a requirement-family index and per-family mapping summaries to improve reverse-trace navigation. |
| `1.3` | `2026-03-19` | Reformatted the family index into a grouped markdown table for easier navigation by requirement type. |
| `1.4` | `2026-03-31` | Updated stm-phase-cde reverse-trace statuses from clarified to verified after implementation and verification completion. |
| `1.5` | `2026-04-13` | Added prompt-system trace entries and updated the governing SRS baseline to v2.3. |
| `1.6` | `2026-05-21` | Updated the governing SRS baseline to v2.6 and added prompt-governance trace entries for FR-1.4.10–1.4.16, FR-1.5.6, NFR-5.2.8–5.2.11, and AC-8.5–8.11. |
| `1.7` | `2026-05-22` | Repointed prompt-system reverse-trace entries from the missing prompt-governance spec reference to existing design-governance artifacts in the proposal, roadmap, benchmark review, and ADR set. |
| `1.8` | `2026-06-03` | Updated M1-mapped prompt-system entries (FR-1.4.5, FR-1.4.6, FR-1.4.8, FR-1.4.16, NFR-5.2.5–5.2.9, NFR-6.2.3, AC-8.1, AC-8.2) from `clarified`/`unmapped` to `implemented` with SRS v2.7 baseline. Pointed linked spec references to `specs/prompt-system-milestone1/spec.md`.

## Family Index

| Type | Families |
|------|----------|
| `FR` | [FR-1](#fr-1), [FR-2](#fr-2), [FR-3](#fr-3), [FR-4](#fr-4), [FR-5](#fr-5), [FR-6](#fr-6), [FR-7](#fr-7) |
| `NFR` | [NFR-1](#nfr-1), [NFR-2](#nfr-2), [NFR-3](#nfr-3), [NFR-4](#nfr-4), [NFR-5](#nfr-5), [NFR-6](#nfr-6) |
| `AC` | [AC-1](#ac-1), [AC-2](#ac-2), [AC-3](#ac-3), [AC-4](#ac-4), [AC-5](#ac-5), [AC-6](#ac-6), [AC-7](#ac-7), [AC-8](#ac-8) |
| `IR` | [IR-1](#ir-1), [IR-2](#ir-2) |
| `CON` | [CON](#con) |
| `ERR` | [ERR](#err) |
| `PRIV` | [PRIV](#priv) |

## Reverse Trace

### FR-1

Mapped: `17/37`. Unmapped: `20`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-1.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L140) | `-` | `unmapped` | `unmapped` |
| [FR-1.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L141) | `-` | `unmapped` | `unmapped` |
| [FR-1.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L142) | `-` | `unmapped` | `unmapped` |
| [FR-1.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L143) | `-` | `unmapped` | `unmapped` |
| [FR-1.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L144) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L150) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L151) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L152) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L153) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L154) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L160) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L161) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L162) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L163) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L164) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L170) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L171) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L172) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L173) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L174) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [FR-1.4.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L175) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [FR-1.4.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L176) | [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](DECISIONS/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md) | `clarified` | `current` |
| [FR-1.4.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L177) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [FR-1.4.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L178) | [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) | `clarified` | `current` |
| [FR-1.4.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L179) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L180) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.12](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L181) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.13](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L182) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.14](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L183) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.15](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L184) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [FR-1.4.16](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L185) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [FR-1.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L196) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L197) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L198) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L199) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L200) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L201) | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](PROMPT_SYSTEM_BENCHMARK_REVIEW.md) | `clarified` | `current` |

### FR-2

Mapped: `0/17`. Unmapped: `17`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-2.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L212) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L213) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L214) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L215) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L216) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L217) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L223) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L224) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L225) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L226) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L227) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L228) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L234) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L235) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L236) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L237) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L238) | `-` | `unmapped` | `unmapped` |

### FR-3

Mapped: `25/38`. Unmapped: `13`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-3.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L263) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L264) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L265) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L266) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L267) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L268) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L269) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L270) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L278) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L279) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L280) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L281) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L282) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L283) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L284) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L285) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L286) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L287) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L297) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L298) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L299) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L300) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L301) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L302) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L303) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L304) | `-` | `unmapped` | `unmapped` |
| [FR-3.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L312) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L313) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L314) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L315) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L316) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L317) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L318) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L328) | `-` | `unmapped` | `unmapped` |
| [FR-3.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L329) | `-` | `unmapped` | `unmapped` |
| [FR-3.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L330) | `-` | `unmapped` | `unmapped` |
| [FR-3.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L331) | `-` | `unmapped` | `unmapped` |
| [FR-3.5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L332) | `-` | `unmapped` | `unmapped` |

### FR-4

Mapped: `0/8`. Unmapped: `8`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-4.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L344) | `-` | `unmapped` | `unmapped` |
| [FR-4.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L345) | `-` | `unmapped` | `unmapped` |
| [FR-4.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L346) | `-` | `unmapped` | `unmapped` |
| [FR-4.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L347) | `-` | `unmapped` | `unmapped` |
| [FR-4.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L348) | `-` | `unmapped` | `unmapped` |
| [FR-4.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L354) | `-` | `unmapped` | `unmapped` |
| [FR-4.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L355) | `-` | `unmapped` | `unmapped` |
| [FR-4.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L356) | `-` | `unmapped` | `unmapped` |

### FR-5

Mapped: `31/39`. Unmapped: `8`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-5.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L368) | `-` | `unmapped` | `unmapped` |
| [FR-5.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L369) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L370) | `-` | `unmapped` | `unmapped` |
| [FR-5.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L371) | `-` | `unmapped` | `unmapped` |
| [FR-5.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L372) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L373) | `-` | `unmapped` | `unmapped` |
| [FR-5.1.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L374) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.1.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L375) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L381) | `-` | `unmapped` | `unmapped` |
| [FR-5.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L382) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L383) | `-` | `unmapped` | `unmapped` |
| [FR-5.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L384) | `-` | `unmapped` | `unmapped` |
| [FR-5.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L385) | `-` | `unmapped` | `unmapped` |
| [FR-5.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L386) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L397) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L398) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L399) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L400) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L401) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L402) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L413) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L414) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L415) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L416) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L417) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L418) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L419) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L420) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L431) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L432) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L433) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L434) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L435) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L436) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L446) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L447) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L448) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L449) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L450) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### FR-6

Mapped: `0/6`. Unmapped: `6`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-6.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L462) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L463) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L464) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L465) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L466) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L467) | `-` | `unmapped` | `unmapped` |

### FR-7

Mapped: `16/16`. Unmapped: `0`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-7.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L480) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L481) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L482) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L483) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L484) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L492) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L493) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L494) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L495) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L496) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L504) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L505) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L506) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L507) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L508) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L509) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### NFR-1

Mapped: `4/16`. Unmapped: `12`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-1.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L522) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L523) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L524) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L525) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L526) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L527) | `-` | `unmapped` | `unmapped` |
| [NFR-1.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L534) | `-` | `unmapped` | `unmapped` |
| [NFR-1.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L535) | `-` | `unmapped` | `unmapped` |
| [NFR-1.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L536) | `-` | `unmapped` | `unmapped` |
| [NFR-1.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L543) | `-` | `unmapped` | `unmapped` |
| [NFR-1.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L544) | `-` | `unmapped` | `unmapped` |
| [NFR-1.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L545) | `-` | `unmapped` | `unmapped` |
| [NFR-1.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L552) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-1.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L553) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-1.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L554) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-1.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L555) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### NFR-2

Mapped: `11/20`. Unmapped: `9`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-2.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L566) | `-` | `unmapped` | `unmapped` |
| [NFR-2.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L567) | `-` | `unmapped` | `unmapped` |
| [NFR-2.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L568) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L575) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L576) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L577) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L578) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L579) | `-` | `unmapped` | `unmapped` |
| [NFR-2.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L586) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L587) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L588) | `-` | `unmapped` | `unmapped` |
| [NFR-2.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L595) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L596) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L597) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L598) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L599) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L606) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L607) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L608) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L609) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### NFR-3

Mapped: `0/7`. Unmapped: `7`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-3.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L620) | `-` | `unmapped` | `unmapped` |
| [NFR-3.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L621) | `-` | `unmapped` | `unmapped` |
| [NFR-3.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L622) | `-` | `unmapped` | `unmapped` |
| [NFR-3.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L623) | `-` | `unmapped` | `unmapped` |
| [NFR-3.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L630) | `-` | `unmapped` | `unmapped` |
| [NFR-3.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L631) | `-` | `unmapped` | `unmapped` |
| [NFR-3.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L632) | `-` | `unmapped` | `unmapped` |

### NFR-4

Mapped: `2/12`. Unmapped: `10`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-4.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L643) | `-` | `unmapped` | `unmapped` |
| [NFR-4.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L644) | `-` | `unmapped` | `unmapped` |
| [NFR-4.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L645) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-4.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L646) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-4.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L653) | `-` | `unmapped` | `unmapped` |
| [NFR-4.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L654) | `-` | `unmapped` | `unmapped` |
| [NFR-4.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L655) | `-` | `unmapped` | `unmapped` |
| [NFR-4.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L656) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L663) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L664) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L665) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L666) | `-` | `unmapped` | `unmapped` |

### NFR-5

Mapped: `4/22`. Unmapped: `18`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-5.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L677) | `-` | `unmapped` | `unmapped` |
| [NFR-5.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L678) | `-` | `unmapped` | `unmapped` |
| [NFR-5.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L679) | `-` | `unmapped` | `unmapped` |
| [NFR-5.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L680) | `-` | `unmapped` | `unmapped` |
| [NFR-5.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L681) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L688) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L689) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L690) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L691) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L692) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [NFR-5.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L693) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [NFR-5.2.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L694) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [NFR-5.2.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L695) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [NFR-5.2.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L696) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [NFR-5.2.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L697) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [NFR-5.2.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L698) | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | `clarified` | `current` |
| [NFR-5.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L705) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L706) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L707) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L708) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L709) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L710) | `-` | `unmapped` | `unmapped` |

### NFR-6

Mapped: `1/13`. Unmapped: `12`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-6.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L721) | `-` | `unmapped` | `unmapped` |
| [NFR-6.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L722) | `-` | `unmapped` | `unmapped` |
| [NFR-6.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L723) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-6.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L724) | `-` | `unmapped` | `unmapped` |
| [NFR-6.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L725) | `-` | `unmapped` | `unmapped` |
| [NFR-6.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L732) | `-` | `unmapped` | `unmapped` |
| [NFR-6.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L733) | `-` | `unmapped` | `unmapped` |
| [NFR-6.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L734) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [NFR-6.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L735) | `-` | `unmapped` | `unmapped` |
| [NFR-6.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L742) | `-` | `unmapped` | `unmapped` |
| [NFR-6.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L743) | `-` | `unmapped` | `unmapped` |
| [NFR-6.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L744) | `-` | `unmapped` | `unmapped` |
| [NFR-6.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L745) | `-` | `unmapped` | `unmapped` |

### CON

Mapped: `0/5`. Unmapped: `5`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [CON-1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L753) | `-` | `unmapped` | `unmapped` |
| [CON-2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L754) | `-` | `unmapped` | `unmapped` |
| [CON-3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L755) | `-` | `unmapped` | `unmapped` |
| [CON-4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L756) | `-` | `unmapped` | `unmapped` |
| [CON-5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L757) | `-` | `unmapped` | `unmapped` |

### AC-1

Mapped: `0/4`. Unmapped: `4`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L767) | `-` | `unmapped` | `unmapped` |
| [AC-1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L768) | `-` | `unmapped` | `unmapped` |
| [AC-1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L769) | `-` | `unmapped` | `unmapped` |
| [AC-1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L770) | `-` | `unmapped` | `unmapped` |

### AC-2

Mapped: `5/7`. Unmapped: `2`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L776) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L777) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L778) | `-` | `unmapped` | `unmapped` |
| [AC-2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L779) | `-` | `unmapped` | `unmapped` |
| [AC-2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L780) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L781) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-2.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L782) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |

### AC-3

Mapped: `0/3`. Unmapped: `3`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L788) | `-` | `unmapped` | `unmapped` |
| [AC-3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L789) | `-` | `unmapped` | `unmapped` |
| [AC-3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L790) | `-` | `unmapped` | `unmapped` |

### AC-4

Mapped: `1/3`. Unmapped: `2`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L796) | `-` | `unmapped` | `unmapped` |
| [AC-4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L797) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L798) | `-` | `unmapped` | `unmapped` |

### AC-5

Mapped: `7/7`. Unmapped: `0`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L804) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L805) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L806) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L807) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L808) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L809) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L810) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### AC-6

Mapped: `6/6`. Unmapped: `0`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-6.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L816) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L817) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L818) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L819) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L820) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L821) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### AC-7

Mapped: `5/5`. Unmapped: `0`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-7.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L827) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-7.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L828) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-7.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L829) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-7.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L830) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-7.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L831) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### AC-8

Mapped: `7/11`. Unmapped: `4`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-8.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L836) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [AC-8.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L837) | [prompt-system-milestone1 spec.md](../../../specs/prompt-system-milestone1/spec.md) | `implemented` | `2.7` |
| [AC-8.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L838) | `-` | `unmapped` | `unmapped` |
| [AC-8.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L839) | `-` | `unmapped` | `unmapped` |
| [AC-8.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L840) | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](PROMPT_SYSTEM_BENCHMARK_REVIEW.md) | `clarified` | `current` |
| [AC-8.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L841) | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](PROMPT_SYSTEM_BENCHMARK_REVIEW.md) | `clarified` | `current` |
| [AC-8.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L842) | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](PROMPT_SYSTEM_BENCHMARK_REVIEW.md) | `clarified` | `current` |
| [AC-8.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L843) | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](PROMPT_SYSTEM_BENCHMARK_REVIEW.md) | `clarified` | `current` |
| [AC-8.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L844) | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](PROMPT_SYSTEM_BENCHMARK_REVIEW.md) | `clarified` | `current` |
| [AC-8.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L845) | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](PROMPT_SYSTEM_BENCHMARK_REVIEW.md) | `clarified` | `current` |
| [AC-8.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L846) | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](PROMPT_SYSTEM_BENCHMARK_REVIEW.md) | `clarified` | `current` |

### IR-1

Mapped: `9/13`. Unmapped: `4`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [IR-1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L911) | `-` | `unmapped` | `unmapped` |
| [IR-1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L912) | `-` | `unmapped` | `unmapped` |
| [IR-1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L913) | `-` | `unmapped` | `unmapped` |
| [IR-1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L914) | `-` | `unmapped` | `unmapped` |
| [IR-1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L915) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L916) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L917) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L918) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L919) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L920) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L921) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.12](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L922) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.13](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L923) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### IR-2

Mapped: `0/5`. Unmapped: `5`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [IR-2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L929) | `-` | `unmapped` | `unmapped` |
| [IR-2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L930) | `-` | `unmapped` | `unmapped` |
| [IR-2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L931) | `-` | `unmapped` | `unmapped` |
| [IR-2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L932) | `-` | `unmapped` | `unmapped` |
| [IR-2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L933) | `-` | `unmapped` | `unmapped` |

### ERR

Mapped: `0/8`. Unmapped: `8`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [ERR-1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L943) | `-` | `unmapped` | `unmapped` |
| [ERR-1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L944) | `-` | `unmapped` | `unmapped` |
| [ERR-1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L945) | `-` | `unmapped` | `unmapped` |
| [ERR-2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L951) | `-` | `unmapped` | `unmapped` |
| [ERR-2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L952) | `-` | `unmapped` | `unmapped` |
| [ERR-2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L953) | `-` | `unmapped` | `unmapped` |
| [ERR-3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L959) | `-` | `unmapped` | `unmapped` |
| [ERR-3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L960) | `-` | `unmapped` | `unmapped` |

### PRIV

Mapped: `0/9`. Unmapped: `9`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [PRIV-1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L970) | `-` | `unmapped` | `unmapped` |
| [PRIV-1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L971) | `-` | `unmapped` | `unmapped` |
| [PRIV-1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L972) | `-` | `unmapped` | `unmapped` |
| [PRIV-2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L978) | `-` | `unmapped` | `unmapped` |
| [PRIV-2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L979) | `-` | `unmapped` | `unmapped` |
| [PRIV-2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L980) | `-` | `unmapped` | `unmapped` |
| [PRIV-3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L986) | `-` | `unmapped` | `unmapped` |
| [PRIV-3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L987) | `-` | `unmapped` | `unmapped` |
| [PRIV-3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L988) | `-` | `unmapped` | `unmapped` |

## Gate Rule

- A mapped feature is in sync only when its derived status and its feature `spec.md` status agree, and its SRS baseline version matches the manifest baseline.
- Informational mappings remain visible in the reverse trace but are excluded from gate enforcement.
- Use `python scripts/sync_spec_status.py --gate` after each development iteration.

