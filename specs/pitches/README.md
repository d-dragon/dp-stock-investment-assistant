# Pitches — ranking

This is the ordered list of pitches chosen at the betting table (rules: [Requirements Method and Governance §2.3](../../docs/system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md#23-pitch-template-l15)). It is an ordering decided by the Product Owner, not a weighted score. Each Milestone in the [product roadmap](../../docs/system/PRODUCT_SPECIFICATION.md#product-roadmap) links to its pitches; this file holds the betting order across them. The SRS does not link to pitches. Rows are ordered by Rank only (1 = next to bet on), not grouped by Milestone.

> **Review note.** Row 1 is a **draft (shaped-draft)** M-000 pitch; row 2 is the shaped M-000 Frontend foundation pitch, ready for implementation (Product Owner, 2026-11-17). Row 3 is the shaped M-001 pitch. Rows marked **EXAMPLE — no pitch file yet** remain placeholders for review, not decisions. Every RICE value in this table is an example estimate.

## Fields

| Field | Meaning |
|---|---|
| Rank | Position in the betting order (1 = next to bet on) |
| Pitch | Link to `specs/pitches/M-nnn-<slug>.md` |
| Milestone + priority | The Milestone the pitch serves (linked to the Product roadmap) and its P0–P3 |
| Status | draft (shaped-draft) / shaped / bet / in delivery / delivered / cut |
| Appetite | Weeks the bet is worth |
| Why now | One line |
| Readiness | Ready / Partly ready / Not ready, plus what blocks the rest: ADR status, identity slice, or open item (OI-n) |
| RICE *(optional)* | Reach × Impact × Confidence ÷ Effort |
| Last re-ranked | Date of the last betting table that touched the row |

**Ranking rule.** At each betting table, order by value to the Phase 1 lifecycle path first, then pull forward rows that are architecture-ready and unblocked; a blocked row cannot be ranked above the item that unblocks it. Re-rank only at a betting table and update "Last re-ranked".

## Ranking

| Rank | Pitch | Milestone + priority | Status | Appetite | Why now | Readiness | RICE *(optional)* | Last re-ranked |
|---|---|---|---|---|---|---|---|---|
| 1 | [M-000 Identity and session](M-000-A-identity-and-session.md) | [M-000](../../docs/system/PRODUCT_SPECIFICATION.md#m-000) Platform foundation — P0 | draft (shaped-draft) | 2 wk *(proposed, to confirm by Product Owner)* | Unblocks owner-scoped Core and Canvas cross-reload context | Partly ready: ADR-SYS-001 token storage Accepted (2026-11-13), role mapping still Proposed; SR-10.1.x drafted; OI-4 waits | *example TBD* | 2026-11-13 |
| 2 | [M-000 Frontend foundation](M-000-B-frontend-foundation.md) | [M-000](../../docs/system/PRODUCT_SPECIFICATION.md#m-000) Platform foundation — P0 | shaped | 1 wk (agentic, Product Owner 2026-11-17) | Modern FE shell + tokens + SSE client so Canvas can land | Ready for implementation (Product Owner, 2026-11-17; Node 26 pinned): fresh, clean Frontend rebuild in six thin slices B0–B5 under the 2026-11-17 cut line (chart interfaces, price mocks, light theme, contrast script, token Storybook pages, F6 tests and visual snapshots move to M-001); ADR-FRONTEND-001–005, 007 and 008 Accepted; Backend stream headers / heartbeat / HTTP/2 deferred to a later Backend pitch (client proven on an MSW fixture, 60 s configurable idle timeout); OI-3 closes when the Vitest baseline lands | *example TBD* | 2026-11-13 |
| 3 | [M-001 Adaptive Visual Canvas](M-001-adaptive-visual-canvas.md) | [M-001](../../docs/system/PRODUCT_SPECIFICATION.md#m-001) — P0 | shaped | 3 wk | Every Core feature needs a shell with both tracks visible | Ready for S1–S3 after M-000 pitches; SR-1.3.4 lives on M-006. Context beyond one session waits on M-000 Pitch A (ADR-SYS-001) | *example:* 10 × 3 × 0.8 ÷ 3 = 8.0 | 2026-11-13 |
| 4 | **EXAMPLE — no pitch file yet** | [M-002](../../docs/system/PRODUCT_SPECIFICATION.md#m-002) Vietnam-first Data Hub — P0 | *example:* shaped | *example:* 3 wk | Insights need trusted data with provenance | Ready for ingestion (ADR-SYS-004 accepted); Agent contribution waits on the write-path rule; OI-6 (meaning of "confidence") open; SR-4.4.x still draft | *example:* 10 × 3 × 0.5 ÷ 3 = 5.0 | — |
| 5 | **EXAMPLE — no pitch file yet** | [M-003](../../docs/system/PRODUCT_SPECIFICATION.md#m-003) Insights foundation — P0 | *example:* shaped | *example:* 2 wk | Start of the lifecycle path | Partly ready: ADR-SYS-003 proposed; blocked by the identity slice (ADR-SYS-001 / M-000 Pitch A, OI-4) | *example:* 10 × 3 × 0.5 ÷ 2 = 7.5 | — |
| 6 | **EXAMPLE — no pitch file yet** | [M-006](../../docs/system/PRODUCT_SPECIFICATION.md#m-006) Decision gate — P0 | *example:* shaped | *example:* 2 wk | Gate closes the Phase 1 commit path; covers SR-1.3.4 (chart yields at the gate) | Not ready: blocked by ADR-SYS-002 (proposed) and the identity slice | *example:* 10 × 3 × 0.3 ÷ 2 = 4.5 | — |
| 7 | **EXAMPLE — no pitch file yet** | [M-007](../../docs/system/PRODUCT_SPECIFICATION.md#m-007) Position after Pass — P0 | *example:* shaped | *example:* 2 wk | Position is the outcome of Pass; Case remains optional | Not ready: blocked by the gate (M-006) and ADR-SYS-002 | *example:* 10 × 3 × 0.3 ÷ 2 = 4.5 | — |
| 8 | **EXAMPLE — no pitch file yet** | [M-009](../../docs/system/PRODUCT_SPECIFICATION.md#m-009) Saved layout presets — P1 | *example:* shaped | *example:* 1 wk | Speed across work once the Canvas exists | Partly ready: blocked until Adaptive Visual Canvas is delivered; per-user state needs M-000 Pitch A (ADR-SYS-001) | *example:* 6 × 1 × 0.5 ÷ 1 = 3.0 | — |

*RICE is optional and advisory: with only a few pitches it gives false precision; the betting order above is what counts.* Example RICE scales: Reach 1–10, Impact 0.5–3, Confidence 0–1, Effort in weeks.

## Traceability IDs

Convention adopted by the Product Owner, 2026-11-18 (hybrid approach). The docs are the source of truth, and each child names its parent. A script generates the reverse links (pitch to slices, specs, rows, tasks and tests) into the generated section of [`specs/spec-traceability.yaml`](../spec-traceability.yaml). Nobody writes that section by hand, and CI fails on orphans. GitHub issues may mirror these IDs later, but they never own them.

| Level | Format | Example | Defined in | Names its parent by |
|---|---|---|---|---|
| Pitch | `M-nnn-X` (Milestone + pitch letter) | `M-000-B` | Pitch file name and title | Its Milestone link in the Ranking table |
| Slice | `Bn`, unique within its pitch | `B2` | Pitch "Solution sketch" | The pitch file it sits in |
| Acceptance row | Slice + kind + number. Kinds: `D` design and UX, `F` format, `P` format edge case, `T` tokens and type, `S` Storybook, MSW and CI | `B3-D4`, `B4-P2` | Pitch acceptance tables | Its slice prefix |
| Spec | Spec Kit folder number | `004` | `specs/nnn-<slug>/` | Front matter `pitch:` and `slices:` (a list, so one spec may cover several slices and one slice may span specs) |
| Requirement, success criterion, user story | `FR-nnn`, `SC-nnn`, `USn`, scoped to the spec | `004/FR-001` | `spec.md` | Front matter `rows:` plus row IDs written inline |
| Task | `Tnnn`, scoped to the spec | `004/T005` | `tasks.md` | The slice or row ID written in the task line |
| Test | The row ID appears in the file or test name | `it('B4-F1 ...')` | Test code | That row ID |

**Rules**

1. IDs are stable. An ID already used in a task or test is never renamed or reused; a cut row keeps its ID and is marked cut or moved.
2. Write canonical IDs outside their home table. Pitch B lists `P1`-`P4` without a prefix inside the B4 table; everywhere else write `B4-P1`-`B4-P4`.
3. Pitch steps are not rows. Pitch B's migration steps `T0`-`T8` are written as "step T3" in new text. Existing `Bn-Tn` uses of a step in `tasks.md` and test names (for example `B1-T0`) stay as they are, and the script resolves them through an alias list. In `rows:` and in new text, `Bn-Tn` means a tokens-and-type acceptance row only.
4. Orphan check, in both directions:
   - **Fail:** a must-have (M) row in the current Milestone with no spec, task or test, or a spec, task or test that names an ID that does not exist.
   - **Warn:** a row of a lower tier that has no link yet.
   - **Deferred, not checked:** rows marked "Moved to M-nnn" (in Pitch B: `B4-T5`, `B4-T6`, `B5-S4`). They are checked under the Milestone they moved to.
