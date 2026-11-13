# ADR-Frontend-007: Design-Token Architecture; Colour Values Live in the Design System

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-007 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Accepted |
| **Date** | 2026-11-10 |
| **Last Updated** | 2026-11-13 |
| **Decision Owners** | Engineering · Architecture · UX / UI Designer |
| **Replaces in part** | [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) Decision bullet on token colours |

## Context

[ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) (Accepted) adopts Tailwind CSS + Radix UI "with financial dark-mode design tokens (emerald green for gains, rose red for losses, cyan for copilot, slate-950 dark background)". On 2026-11-10 the Product Owner locked the design-system direction: dark-first with light working on the same tokens, the Vietnamese exchange colour convention on prices (green up, red down, yellow reference, purple ceiling, cyan floor), AI provenance shown by shape and label rather than colour, and an accent clearly apart from floor and ceiling (Bone). ADR-002's colour line now conflicts in three places:

- **Cyan for the copilot** collides with `market.floor`.
- **Emerald / rose** are fixed hues; prices should follow the exchange convention through `market.up` / `market.down`.
- **A copilot colour** contradicts the rule that AI content is marked by a dashed outline and label (`ai.*` provenance), never by colour alone ([WCAG 2.2 SC 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)).

Colour values also change faster than architecture; keeping them in an ADR forces a supersession for every palette tweak.

## Decision

- Tokens are organised in **three tiers from one source**: primitive → semantic → component, compiled to CSS variables that feed the Tailwind theme and shadcn. Feature code never uses raw colour values.
- **Separate semantic groups**, each with its own usage rule:
  - `market.*` (up, down, reference, ceiling, floor): prices and deltas only; reference, ceiling and floor values come from the Backend.
  - `state.*`: system status, always with icon and label.
  - `ai.*`: provenance (AI-suggested vs investor-confirmed), expressed by a dashed outline and a label; no brand hue for the AI.
  - `track.*`: Sandbox / Portfolio accents only, never on prices.
- The **accent** stays clearly apart from `market.floor` and `market.ceiling`; non-text contrast ≥ 3:1 ([WCAG 2.2 SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)).
- **Values** (hex, themes, accent) live in [DESIGN_SYSTEM.md](../DESIGN_SYSTEM.md), owned by the UX / UI Designer. ADRs no longer carry colour values.
- This ADR replaces only ADR-002's token-colour bullet; the rest of ADR-002 stands.

## Considered Options

| Option | Outcome |
|--------|---------|
| Token architecture in ADR, values in DESIGN_SYSTEM.md (chosen) | Stable decision; palette can evolve without new ADRs |
| Keep ADR-002's colour values | Rejected: cyan conflicts with floor; colour-only AI cue fails 1.4.1 |
| Supersede all of ADR-002 | Rejected: the rest of the stack decision is unaffected |

## Consequences

- Positive: one colour truth; price, status and AI provenance cannot be confused.
- Positive: themes and chart skins change values, not components.
- Negative: ADR-002 needs a "replaced in part by ADR-007" note in its revision history once this ADR is accepted.
- Pipeline, file layout and the lint backstop that keeps `market.*` and `state.*` apart belong to [TECHNICAL_DESIGN.md](../TECHNICAL_DESIGN.md).

## Requirement Alignment

| Requirement | Relevance |
|-------------|-----------|
| **SNR-7** Usability, Accessibility, and Responsive Behavior | WCAG 1.4.1 / 1.4.11; consistent tokens |
| **SR-1.3.5** Docked price chart (proof of concept) | Chart uses `market.*` for reference, ceiling and floor |

## Related Documents

- [Frontend Domain Architecture](../ARCHITECTURE.md) §7.1
- [DESIGN_LOCK.md](../DESIGN_LOCK.md), [DESIGN_SYSTEM.md](../DESIGN_SYSTEM.md)
- [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md)

## References

- [WCAG 2.2 — Understanding SC 1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
- [WCAG 2.2 — Understanding SC 1.4.11 Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)
- [W3C Design Tokens Format (DTCG)](https://tr.designtokens.org/format/)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-11-10 | Software Architect Assistant | Proposed after Product Owner approval of the design-system direction and Bone accent |
| 0.2 | 2026-11-13 | Software Architect Assistant | Accepted by the Product Owner; ADR-002 carries the replaced-in-part note |
