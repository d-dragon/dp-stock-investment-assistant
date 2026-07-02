# SRS To Spec Traceability

> **Document Version**: 2.1
> **Generated**: 2026-07-02 04:38:41Z
> **Status**: Active
> **Traceability Manifest Version**: 1

## Baseline

- SRS: [docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md](SOFTWARE_REQUIREMENTS_SPECIFICATION.md)
- SRS version: `2.8`

## Summary

- Total traced SRS items discovered: `425`
- Items with linked specs: `159`
- Items without linked specs: `266`

## Revision History

| Version | Date | Summary |
|---------|------|---------|
| `1.0` | `2026-03-19` | Initial bidirectional reverse trace generation between SRS items and spec-kit artifacts. |
| `1.1` | `2026-03-19` | Added line-specific SRS links, embedded document version tracking, and promoted exact pilot overlap to gate-enforced coverage. |
| `1.2` | `2026-03-19` | Added a requirement-family index and per-family mapping summaries to improve reverse-trace navigation. |
| `1.3` | `2026-03-19` | Reformatted the family index into a grouped markdown table for easier navigation by requirement type. |
| `1.4` | `2026-03-31` | Updated stm-phase-cde reverse-trace statuses from clarified to verified after implementation and verification completion. |
| `1.5` | `2026-04-13` | Added prompt-system trace entries and updated the governing SRS baseline to v2.3. |
| `1.6` | `2026-05-21` | Updated the governing SRS baseline to v2.6 and added prompt-governance trace entries for FR-1.4.10-FR-1.4.16, FR-1.5.6, NFR-5.2.8-NFR-5.2.11, and AC-8.5-AC-8.11. |
| `1.7` | `2026-05-22` | Repointed prompt-system reverse-trace entries from the missing prompt-governance spec reference to existing design-governance artifacts in the proposal, roadmap, benchmark review, and ADR set. |
| `1.8` | `2026-06-03` | Updated M1-mapped prompt-system entries from clarified/unmapped to implemented with SRS v2.7 baseline. |
| `1.9` | `2026-06-22` | Updated the governing SRS baseline to v2.8 and added manual Phase 2B tool-system trace entries. |
| `2.0` | `2026-07-01` | Added generated reverse trace coverage for tool-system-implementation-m2b.1 against SRS v2.8 tool gateway requirements. |
| `2.1` | `2026-07-01` | Regenerated reverse trace after tool-system-implementation-m2b.1 planning artifacts advanced the feature lifecycle to planned. |
| `2.2` | `2026-07-02` | Regenerated reverse trace after tool-system-implementation-m2b.1 task generation added implementation-task evidence. |
| `2.3` | `2026-07-02` | Added NFR-4.2.3 reverse trace coverage and regenerated after pre-implementation analysis remediation for tool-system-implementation-m2b.1. |

## Family Index

| Type | Families |
|------|----------|
| `FR` | [FR-1](#fr-1), [FR-2](#fr-2), [FR-3](#fr-3), [FR-4](#fr-4), [FR-5](#fr-5), [FR-6](#fr-6), [FR-7](#fr-7) |
| `NFR` | [NFR-1](#nfr-1), [NFR-2](#nfr-2), [NFR-3](#nfr-3), [NFR-4](#nfr-4), [NFR-5](#nfr-5), [NFR-6](#nfr-6) |
| `AC` | [AC-1](#ac-1), [AC-2](#ac-2), [AC-3](#ac-3), [AC-4](#ac-4), [AC-5](#ac-5), [AC-6](#ac-6), [AC-7](#ac-7), [AC-8](#ac-8), [AC-9](#ac-9) |
| `IR` | [IR-1](#ir-1), [IR-2](#ir-2), [IR-3](#ir-3) |
| `CON` | [CON](#con) |
| `ERR` | [ERR](#err) |
| `PRIV` | [PRIV](#priv) |

## Reverse Trace

### FR-1

Mapped: `6/37`. Unmapped: `31`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-1.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L153) | `-` | `unmapped` | `unmapped` |
| [FR-1.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L154) | `-` | `unmapped` | `unmapped` |
| [FR-1.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L155) | `-` | `unmapped` | `unmapped` |
| [FR-1.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L156) | `-` | `unmapped` | `unmapped` |
| [FR-1.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L157) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L163) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L164) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L165) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L166) | `-` | `unmapped` | `unmapped` |
| [FR-1.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L167) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L173) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L174) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L175) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L176) | `-` | `unmapped` | `unmapped` |
| [FR-1.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L177) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L183) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L184) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L185) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L186) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L187) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [FR-1.4.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L188) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [FR-1.4.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L189) | [prompt-system-milestone2](../../../specs/prompt-system-milestone2/spec.md#governance-context-mandatory) | `implemented` | `current` |
| [FR-1.4.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L190) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [FR-1.4.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L191) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L192) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L193) | [prompt-system-milestone2](../../../specs/prompt-system-milestone2/spec.md#governance-context-mandatory) | `implemented` | `current` |
| [FR-1.4.12](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L194) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.13](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L195) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.14](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L196) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.15](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L197) | `-` | `unmapped` | `unmapped` |
| [FR-1.4.16](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L198) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
|  | [prompt-system-milestone2](../../../specs/prompt-system-milestone2/spec.md#governance-context-mandatory) | `implemented` | `current` |
| [FR-1.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L209) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L210) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L211) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L212) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L213) | `-` | `unmapped` | `unmapped` |
| [FR-1.5.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L214) | `-` | `unmapped` | `unmapped` |

### FR-2

Mapped: `6/57`. Unmapped: `51`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-2.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L225) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L226) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L227) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L228) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L229) | `-` | `unmapped` | `unmapped` |
| [FR-2.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L230) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L236) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L237) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L238) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L239) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L240) | `-` | `unmapped` | `unmapped` |
| [FR-2.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L241) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L247) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L248) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L249) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L250) | `-` | `unmapped` | `unmapped` |
| [FR-2.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L251) | `-` | `unmapped` | `unmapped` |
| [FR-2.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L257) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [FR-2.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L258) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [FR-2.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L259) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [FR-2.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L260) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [FR-2.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L261) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [FR-2.4.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L262) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [FR-2.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L268) | `-` | `unmapped` | `unmapped` |
| [FR-2.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L269) | `-` | `unmapped` | `unmapped` |
| [FR-2.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L270) | `-` | `unmapped` | `unmapped` |
| [FR-2.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L271) | `-` | `unmapped` | `unmapped` |
| [FR-2.5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L272) | `-` | `unmapped` | `unmapped` |
| [FR-2.6.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L278) | `-` | `unmapped` | `unmapped` |
| [FR-2.6.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L279) | `-` | `unmapped` | `unmapped` |
| [FR-2.6.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L280) | `-` | `unmapped` | `unmapped` |
| [FR-2.6.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L281) | `-` | `unmapped` | `unmapped` |
| [FR-2.6.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L282) | `-` | `unmapped` | `unmapped` |
| [FR-2.6.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L283) | `-` | `unmapped` | `unmapped` |
| [FR-2.7.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L289) | `-` | `unmapped` | `unmapped` |
| [FR-2.7.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L290) | `-` | `unmapped` | `unmapped` |
| [FR-2.7.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L291) | `-` | `unmapped` | `unmapped` |
| [FR-2.7.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L292) | `-` | `unmapped` | `unmapped` |
| [FR-2.7.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L293) | `-` | `unmapped` | `unmapped` |
| [FR-2.8.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L299) | `-` | `unmapped` | `unmapped` |
| [FR-2.8.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L300) | `-` | `unmapped` | `unmapped` |
| [FR-2.8.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L301) | `-` | `unmapped` | `unmapped` |
| [FR-2.8.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L302) | `-` | `unmapped` | `unmapped` |
| [FR-2.9.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L308) | `-` | `unmapped` | `unmapped` |
| [FR-2.9.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L309) | `-` | `unmapped` | `unmapped` |
| [FR-2.9.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L310) | `-` | `unmapped` | `unmapped` |
| [FR-2.9.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L311) | `-` | `unmapped` | `unmapped` |
| [FR-2.10.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L317) | `-` | `unmapped` | `unmapped` |
| [FR-2.10.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L318) | `-` | `unmapped` | `unmapped` |
| [FR-2.10.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L319) | `-` | `unmapped` | `unmapped` |
| [FR-2.10.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L320) | `-` | `unmapped` | `unmapped` |
| [FR-2.11.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L326) | `-` | `unmapped` | `unmapped` |
| [FR-2.11.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L327) | `-` | `unmapped` | `unmapped` |
| [FR-2.11.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L328) | `-` | `unmapped` | `unmapped` |
| [FR-2.11.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L329) | `-` | `unmapped` | `unmapped` |
| [FR-2.11.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L330) | `-` | `unmapped` | `unmapped` |
| [FR-2.11.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L331) | `-` | `unmapped` | `unmapped` |

### FR-3

Mapped: `25/38`. Unmapped: `13`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-3.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L356) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L357) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L358) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L359) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L360) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L361) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L362) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.1.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L363) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [spec-driven-development-pilot](../../../specs/spec-driven-development-pilot/plan.md#summary) | `implemented` | `current` |
| [FR-3.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L371) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L372) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L373) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L374) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L375) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L376) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L377) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L378) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L379) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.2.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L380) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L390) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L391) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L392) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L393) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L394) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L395) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L396) | `-` | `unmapped` | `unmapped` |
| [FR-3.3.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L397) | `-` | `unmapped` | `unmapped` |
| [FR-3.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L405) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L406) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L407) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L408) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L409) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L410) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.4.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L411) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-3.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L421) | `-` | `unmapped` | `unmapped` |
| [FR-3.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L422) | `-` | `unmapped` | `unmapped` |
| [FR-3.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L423) | `-` | `unmapped` | `unmapped` |
| [FR-3.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L424) | `-` | `unmapped` | `unmapped` |
| [FR-3.5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L425) | `-` | `unmapped` | `unmapped` |

### FR-4

Mapped: `1/8`. Unmapped: `7`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-4.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L437) | `-` | `unmapped` | `unmapped` |
| [FR-4.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L438) | `-` | `unmapped` | `unmapped` |
| [FR-4.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L439) | `-` | `unmapped` | `unmapped` |
| [FR-4.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L440) | `-` | `unmapped` | `unmapped` |
| [FR-4.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L441) | `-` | `unmapped` | `unmapped` |
| [FR-4.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L447) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [FR-4.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L448) | `-` | `unmapped` | `unmapped` |
| [FR-4.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L449) | `-` | `unmapped` | `unmapped` |

### FR-5

Mapped: `31/39`. Unmapped: `8`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-5.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L461) | `-` | `unmapped` | `unmapped` |
| [FR-5.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L462) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L463) | `-` | `unmapped` | `unmapped` |
| [FR-5.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L464) | `-` | `unmapped` | `unmapped` |
| [FR-5.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L465) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L466) | `-` | `unmapped` | `unmapped` |
| [FR-5.1.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L467) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.1.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L468) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L474) | `-` | `unmapped` | `unmapped` |
| [FR-5.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L475) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L476) | `-` | `unmapped` | `unmapped` |
| [FR-5.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L477) | `-` | `unmapped` | `unmapped` |
| [FR-5.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L478) | `-` | `unmapped` | `unmapped` |
| [FR-5.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L479) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L490) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L491) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L492) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L493) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L494) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L495) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L506) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L507) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L508) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L509) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L510) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L511) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L512) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.4.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L513) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L524) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L525) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L526) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L527) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L528) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.5.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L529) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L539) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L540) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L541) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L542) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-5.6.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L543) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### FR-6

Mapped: `0/6`. Unmapped: `6`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-6.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L555) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L556) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L557) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L558) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L559) | `-` | `unmapped` | `unmapped` |
| [FR-6.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L560) | `-` | `unmapped` | `unmapped` |

### FR-7

Mapped: `16/16`. Unmapped: `0`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [FR-7.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L573) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L574) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L575) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L576) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L577) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L585) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L586) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L587) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L588) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L589) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L597) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L598) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L599) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L600) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L601) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [FR-7.3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L602) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### NFR-1

Mapped: `4/16`. Unmapped: `12`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-1.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L615) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L616) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L617) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L618) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L619) | `-` | `unmapped` | `unmapped` |
| [NFR-1.1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L620) | `-` | `unmapped` | `unmapped` |
| [NFR-1.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L627) | `-` | `unmapped` | `unmapped` |
| [NFR-1.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L628) | `-` | `unmapped` | `unmapped` |
| [NFR-1.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L629) | `-` | `unmapped` | `unmapped` |
| [NFR-1.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L636) | `-` | `unmapped` | `unmapped` |
| [NFR-1.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L637) | `-` | `unmapped` | `unmapped` |
| [NFR-1.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L638) | `-` | `unmapped` | `unmapped` |
| [NFR-1.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L645) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-1.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L646) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-1.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L647) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-1.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L648) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### NFR-2

Mapped: `11/23`. Unmapped: `12`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-2.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L659) | `-` | `unmapped` | `unmapped` |
| [NFR-2.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L660) | `-` | `unmapped` | `unmapped` |
| [NFR-2.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L661) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L668) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L669) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L670) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L671) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L672) | `-` | `unmapped` | `unmapped` |
| [NFR-2.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L673) | `-` | `unmapped` | `unmapped` |
| [NFR-2.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L680) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L681) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L682) | `-` | `unmapped` | `unmapped` |
| [NFR-2.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L683) | `-` | `unmapped` | `unmapped` |
| [NFR-2.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L684) | `-` | `unmapped` | `unmapped` |
| [NFR-2.4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L691) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L692) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L693) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.4.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L694) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.4.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L695) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L702) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L703) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L704) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-2.5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L705) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### NFR-3

Mapped: `0/7`. Unmapped: `7`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-3.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L716) | `-` | `unmapped` | `unmapped` |
| [NFR-3.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L717) | `-` | `unmapped` | `unmapped` |
| [NFR-3.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L718) | `-` | `unmapped` | `unmapped` |
| [NFR-3.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L719) | `-` | `unmapped` | `unmapped` |
| [NFR-3.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L726) | `-` | `unmapped` | `unmapped` |
| [NFR-3.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L727) | `-` | `unmapped` | `unmapped` |
| [NFR-3.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L728) | `-` | `unmapped` | `unmapped` |

### NFR-4

Mapped: `3/13`. Unmapped: `10`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-4.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L739) | `-` | `unmapped` | `unmapped` |
| [NFR-4.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L740) | `-` | `unmapped` | `unmapped` |
| [NFR-4.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L741) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-4.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L742) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-4.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L749) | `-` | `unmapped` | `unmapped` |
| [NFR-4.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L750) | `-` | `unmapped` | `unmapped` |
| [NFR-4.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L751) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [NFR-4.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L752) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L759) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L760) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L761) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L762) | `-` | `unmapped` | `unmapped` |
| [NFR-4.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L763) | `-` | `unmapped` | `unmapped` |

### NFR-5

Mapped: `6/28`. Unmapped: `22`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-5.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L774) | `-` | `unmapped` | `unmapped` |
| [NFR-5.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L775) | `-` | `unmapped` | `unmapped` |
| [NFR-5.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L776) | `-` | `unmapped` | `unmapped` |
| [NFR-5.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L777) | `-` | `unmapped` | `unmapped` |
| [NFR-5.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L778) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L785) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L786) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L787) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L788) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L789) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [NFR-5.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L790) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [NFR-5.2.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L791) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [NFR-5.2.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L792) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
|  | [prompt-system-milestone2](../../../specs/prompt-system-milestone2/spec.md#governance-context-mandatory) | `implemented` | `current` |
| [NFR-5.2.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L793) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [NFR-5.2.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L794) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L795) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.12](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L796) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [NFR-5.2.13](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L797) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.14](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L798) | `-` | `unmapped` | `unmapped` |
| [NFR-5.2.15](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L799) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L806) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L807) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L808) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L809) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L810) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L811) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L812) | `-` | `unmapped` | `unmapped` |
| [NFR-5.3.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L813) | `-` | `unmapped` | `unmapped` |

### NFR-6

Mapped: `3/15`. Unmapped: `12`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [NFR-6.1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L824) | `-` | `unmapped` | `unmapped` |
| [NFR-6.1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L825) | `-` | `unmapped` | `unmapped` |
| [NFR-6.1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L826) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [NFR-6.1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L827) | `-` | `unmapped` | `unmapped` |
| [NFR-6.1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L828) | `-` | `unmapped` | `unmapped` |
| [NFR-6.2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L835) | `-` | `unmapped` | `unmapped` |
| [NFR-6.2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L836) | `-` | `unmapped` | `unmapped` |
| [NFR-6.2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L837) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [NFR-6.2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L838) | `-` | `unmapped` | `unmapped` |
| [NFR-6.2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L839) | `-` | `unmapped` | `unmapped` |
| [NFR-6.2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L840) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [NFR-6.3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L847) | `-` | `unmapped` | `unmapped` |
| [NFR-6.3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L848) | `-` | `unmapped` | `unmapped` |
| [NFR-6.3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L849) | `-` | `unmapped` | `unmapped` |
| [NFR-6.3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L850) | `-` | `unmapped` | `unmapped` |

### CON

Mapped: `3/10`. Unmapped: `7`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [CON-1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L858) | `-` | `unmapped` | `unmapped` |
| [CON-2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L859) | `-` | `unmapped` | `unmapped` |
| [CON-3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L860) | `-` | `unmapped` | `unmapped` |
| [CON-4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L861) | `-` | `unmapped` | `unmapped` |
| [CON-5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L862) | `-` | `unmapped` | `unmapped` |
| [CON-6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L863) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [CON-7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L864) | `-` | `unmapped` | `unmapped` |
| [CON-8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L865) | `-` | `unmapped` | `unmapped` |
| [CON-9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L866) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [CON-10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L867) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |

### AC-1

Mapped: `0/4`. Unmapped: `4`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L877) | `-` | `unmapped` | `unmapped` |
| [AC-1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L878) | `-` | `unmapped` | `unmapped` |
| [AC-1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L879) | `-` | `unmapped` | `unmapped` |
| [AC-1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L880) | `-` | `unmapped` | `unmapped` |

### AC-2

Mapped: `5/7`. Unmapped: `2`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L886) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L887) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L888) | `-` | `unmapped` | `unmapped` |
| [AC-2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L889) | `-` | `unmapped` | `unmapped` |
| [AC-2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L890) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-2.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L891) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-2.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L892) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |

### AC-3

Mapped: `0/3`. Unmapped: `3`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L898) | `-` | `unmapped` | `unmapped` |
| [AC-3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L899) | `-` | `unmapped` | `unmapped` |
| [AC-3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L900) | `-` | `unmapped` | `unmapped` |

### AC-4

Mapped: `1/3`. Unmapped: `2`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-4.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L906) | `-` | `unmapped` | `unmapped` |
| [AC-4.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L907) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-4.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L908) | `-` | `unmapped` | `unmapped` |

### AC-5

Mapped: `7/7`. Unmapped: `0`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-5.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L914) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L915) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L916) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L917) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L918) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L919) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-5.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L920) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### AC-6

Mapped: `6/6`. Unmapped: `0`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-6.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L926) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L927) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L928) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L929) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L930) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-6.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L931) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### AC-7

Mapped: `5/5`. Unmapped: `0`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-7.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L937) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-7.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L938) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-7.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L939) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
|  | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-7.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L940) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [AC-7.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L941) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### AC-8

Mapped: `5/11`. Unmapped: `6`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-8.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L946) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [AC-8.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L947) | [prompt-system-milestone1](../../../specs/prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `implemented` | `current` |
| [AC-8.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L948) | `-` | `unmapped` | `unmapped` |
| [AC-8.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L949) | `-` | `unmapped` | `unmapped` |
| [AC-8.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L950) | [prompt-system-milestone2](../../../specs/prompt-system-milestone2/spec.md#governance-context-mandatory) | `implemented` | `current` |
| [AC-8.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L951) | `-` | `unmapped` | `unmapped` |
| [AC-8.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L952) | `-` | `unmapped` | `unmapped` |
| [AC-8.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L953) | [prompt-system-milestone2](../../../specs/prompt-system-milestone2/spec.md#governance-context-mandatory) | `implemented` | `current` |
| [AC-8.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L954) | `-` | `unmapped` | `unmapped` |
| [AC-8.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L955) | `-` | `unmapped` | `unmapped` |
| [AC-8.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L956) | [prompt-system-milestone2](../../../specs/prompt-system-milestone2/spec.md#governance-context-mandatory) | `implemented` | `current` |

### AC-9

Mapped: `4/17`. Unmapped: `13`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [AC-9.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L962) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [AC-9.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L963) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [AC-9.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L964) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [AC-9.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L965) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [AC-9.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L966) | `-` | `unmapped` | `unmapped` |
| [AC-9.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L967) | `-` | `unmapped` | `unmapped` |
| [AC-9.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L968) | `-` | `unmapped` | `unmapped` |
| [AC-9.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L969) | `-` | `unmapped` | `unmapped` |
| [AC-9.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L970) | `-` | `unmapped` | `unmapped` |
| [AC-9.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L971) | `-` | `unmapped` | `unmapped` |
| [AC-9.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L972) | `-` | `unmapped` | `unmapped` |
| [AC-9.12](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L973) | `-` | `unmapped` | `unmapped` |
| [AC-9.13](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L974) | `-` | `unmapped` | `unmapped` |
| [AC-9.14](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L975) | `-` | `unmapped` | `unmapped` |
| [AC-9.15](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L976) | `-` | `unmapped` | `unmapped` |
| [AC-9.16](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L977) | `-` | `unmapped` | `unmapped` |
| [AC-9.17](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L978) | `-` | `unmapped` | `unmapped` |

### IR-1

Mapped: `9/13`. Unmapped: `4`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [IR-1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1060) | `-` | `unmapped` | `unmapped` |
| [IR-1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1061) | `-` | `unmapped` | `unmapped` |
| [IR-1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1062) | `-` | `unmapped` | `unmapped` |
| [IR-1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1063) | `-` | `unmapped` | `unmapped` |
| [IR-1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1064) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1065) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1066) | [agent-session-with-stm-wiring](../../../specs/agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1067) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1068) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1069) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.11](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1070) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.12](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1071) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |
| [IR-1.13](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1072) | [stm-phase-cde](../../../specs/stm-phase-cde/spec.md#requirements-mandatory) | `verified` | `current` |

### IR-2

Mapped: `0/5`. Unmapped: `5`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [IR-2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1078) | `-` | `unmapped` | `unmapped` |
| [IR-2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1079) | `-` | `unmapped` | `unmapped` |
| [IR-2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1080) | `-` | `unmapped` | `unmapped` |
| [IR-2.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1081) | `-` | `unmapped` | `unmapped` |
| [IR-2.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1082) | `-` | `unmapped` | `unmapped` |

### IR-3

Mapped: `2/10`. Unmapped: `8`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [IR-3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1088) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [IR-3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1089) | [tool-system-implementation-m2b.1](../../../specs/tool-system-implementation-m2b.1/spec.md#governance-context-mandatory) | `planned` | `current` |
| [IR-3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1090) | `-` | `unmapped` | `unmapped` |
| [IR-3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1091) | `-` | `unmapped` | `unmapped` |
| [IR-3.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1092) | `-` | `unmapped` | `unmapped` |
| [IR-3.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1093) | `-` | `unmapped` | `unmapped` |
| [IR-3.7](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1094) | `-` | `unmapped` | `unmapped` |
| [IR-3.8](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1095) | `-` | `unmapped` | `unmapped` |
| [IR-3.9](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1096) | `-` | `unmapped` | `unmapped` |
| [IR-3.10](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1097) | `-` | `unmapped` | `unmapped` |

### ERR

Mapped: `0/8`. Unmapped: `8`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [ERR-1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1107) | `-` | `unmapped` | `unmapped` |
| [ERR-1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1108) | `-` | `unmapped` | `unmapped` |
| [ERR-1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1109) | `-` | `unmapped` | `unmapped` |
| [ERR-2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1115) | `-` | `unmapped` | `unmapped` |
| [ERR-2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1116) | `-` | `unmapped` | `unmapped` |
| [ERR-2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1117) | `-` | `unmapped` | `unmapped` |
| [ERR-3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1123) | `-` | `unmapped` | `unmapped` |
| [ERR-3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1124) | `-` | `unmapped` | `unmapped` |

### PRIV

Mapped: `0/13`. Unmapped: `13`.

| SRS Item | Linked Spec | Current Status | Sync Status |
|----------|-------------|----------------|-------------|
| [PRIV-1.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1134) | `-` | `unmapped` | `unmapped` |
| [PRIV-1.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1135) | `-` | `unmapped` | `unmapped` |
| [PRIV-1.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1136) | `-` | `unmapped` | `unmapped` |
| [PRIV-1.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1137) | `-` | `unmapped` | `unmapped` |
| [PRIV-1.5](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1138) | `-` | `unmapped` | `unmapped` |
| [PRIV-1.6](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1139) | `-` | `unmapped` | `unmapped` |
| [PRIV-2.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1145) | `-` | `unmapped` | `unmapped` |
| [PRIV-2.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1146) | `-` | `unmapped` | `unmapped` |
| [PRIV-2.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1147) | `-` | `unmapped` | `unmapped` |
| [PRIV-3.1](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1153) | `-` | `unmapped` | `unmapped` |
| [PRIV-3.2](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1154) | `-` | `unmapped` | `unmapped` |
| [PRIV-3.3](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1155) | `-` | `unmapped` | `unmapped` |
| [PRIV-3.4](SOFTWARE_REQUIREMENTS_SPECIFICATION.md#L1156) | `-` | `unmapped` | `unmapped` |

## Gate Rule

- A mapped feature is in sync only when its derived status and its feature `spec.md` status agree, and its SRS baseline version matches the manifest baseline.
- Informational mappings remain visible in the reverse trace but are excluded from gate enforcement.
- Use `python scripts/sync_spec_status.py --gate` after each development iteration.

