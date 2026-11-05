# Pitch: M-001 Adaptive Visual Canvas

| Field | Value |
|---|---|
| Milestone | [M-001 Adaptive Visual Canvas (multi-pane, context preserved)](../../docs/system/PRODUCT_SPECIFICATION.md#m-001) |
| Priority | P0 (from M-001) |
| Requirements covered | FR: [SR-1.3.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-1), [SR-1.3.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-2) · NFR: none in this pitch |
| Status | shaped |
| Appetite | 2 weeks *(proposed, Product Owner to confirm; chart-gate moved to M-006)* |
| Cost | Team time within the appetite; no paid service, data feed or model spend expected *(estimate, Product Owner to confirm)* |
| Slices | S1 canvas-zones-and-tracks — SR-1.3.1; S2 canvas-context-on-switch — SR-1.3.2 *(proposed, may change in delivery; not created yet)* |
| Last re-ranked | 2026-10-17 |
| References | Architecture: [overview §4.2.1 Logical building blocks](../../docs/architecture/SYSTEM_OVERVIEW_AND_BOUNDARIES.md#421-logical-building-blocks), [overview §4.2.3 Layered boundaries](../../docs/architecture/SYSTEM_OVERVIEW_AND_BOUNDARIES.md#423-layered-boundaries), [ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md) (partly accepted; only if per-user layout state is needed), [ADR-SYS-002](../../docs/architecture/DECISIONS/ADR-SYS-002-DECISION-GATE.md) (proposed; gate and chart-yield owned by M-006) · Design: [IA map §2.1](../../docs/system/CONCEPTUAL_IA_MAP.md#21-zone-map), [IA map §2.6](../../docs/system/CONCEPTUAL_IA_MAP.md#26-layout-lock-normative), [Journeys W1](../../docs/system/USER_JOURNEYS_WITH_WIREFRAMES.md#32-w1--empty-adaptive-workspace-shell), [Journeys W2b](../../docs/system/USER_JOURNEYS_WITH_WIREFRAMES.md#34-w2b--insights--chart) |

## Problem
Investing is a continuous, long-lived workload, but the work is scattered. [SR-1.3](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3) requires one zoned workspace where both tracks, Research Sandbox and Execution Portfolio, are visible at once ([SR-1.3.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-1)), and where the open work keeps its context when the user switches symbol, work object or track ([SR-1.3.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-2)). This is Milestone [M-001](../../docs/system/PRODUCT_SPECIFICATION.md#m-001). The chart-gate rule ([SR-1.3.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-4)) is owned by Milestone [M-006](../../docs/system/PRODUCT_SPECIFICATION.md#m-006). Without that shell, every later Core feature (Insights, Working Thesis, gate) has no stable place to live.

## Appetite
2 weeks *(proposed, Product Owner to confirm)*: about one week each for S1 and S2. The chart-gate rule (SR-1.3.4) belongs to Milestone M-006, not this pitch.

## Solution sketch (IA zones, no tech)
- **S1 — zones and tracks.** The workspace shows the four zones Z1–Z4 as locked in the IA map; Z1 shows both tracks (Track A · Research Sandbox, Track B · Execution Portfolio) at the same time, active track marked, and the Lifecycle cue present as an empty frame of stages, with no sidebar design ([SR-1.3.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-1); [IA map §2.2](../../docs/system/CONCEPTUAL_IA_MAP.md#22-z1--left-sidebar)). Empty-shell frame: Journeys W1.
- **S2 — context on switch.** Switching symbol, work object or track keeps the context of the open work within the current browser session: the open Core object, the chart state and the Z4 thread, including its scroll position and any draft ([SR-1.3.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-2)). The Z4 thread is reopened from the Backend session by reference, never copied into Frontend state. Keeping context across reloads, devices or sessions comes with the identity follow-up; Z2 always answers "what am I working on right now?" ([IA map §2.3](../../docs/system/CONCEPTUAL_IA_MAP.md#23-z2--top-chrome)).

## Rabbit holes
- **[ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md) (partly accepted).** Context that must survive reloads, devices or sessions needs owner-scoped state and therefore identity; a user ID header on its own is not enough. S2 stays within the current browser session until the identity follow-up lands.
- **[ADR-SYS-002](../../docs/architecture/DECISIONS/ADR-SYS-002-DECISION-GATE.md) (proposed).** The Decision gate belongs to the gate and Position pitch, and Core rules belong to the Backend. This pitch must not look like a working gate.
- **Sidebar detail.** IA map §2.2 defers detailed Z1 design; S1 must not grow into sidebar design.

## No-gos
- [SR-1.3.3](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-3) generated UI (P2 / Future): no AI-generated panels in this pitch.
- Saved layout presets (Milestone [M-009](../../docs/system/PRODUCT_SPECIFICATION.md#m-009), P1).
- Chart rule on the Execution Portfolio (IA map §2.4: optional later).
- Chart library, frontend stack or pixel choices (IA map §2.4 "Not this lock").
- A working Decision gate, Decision record or Pass/Fail logic (gate and Position pitch).
- A second copy of the Z4 thread in Frontend state.

## Done means
- The workspace shows both tracks and the four zones, and the open work survives a switch within the session: [SR-1.3.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-1) and [SR-1.3.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-3-2) are `verified`.
- Given/When/Then acceptance, including the UX Designer's criteria, lives in each slice's `spec.md`.

## Open questions
- [NEEDS CLARIFICATION] Is the 2-week appetite right for S1 → S2?
- [NEEDS CLARIFICATION] Is the cost estimate right: team time only, with no paid service or model spend?
- [NEEDS CLARIFICATION] When does the identity follow-up land, so S2 context can extend beyond one browser session?
- *Decided 2026-10-17:* SR-1.3.2 context covers the open Core object, chart state and Z4 thread, within the session. Z1 in S1 shows both tracks plus an empty Lifecycle frame. SR-1.3.4 / chart-gate moved fully to M-006 (2026-11-05).
