# Contract: shell zones

**Slice**: B3 (T4 shell split, plus the geometry T5 wires)

**Source**: `docs/domains/frontend/ARCHITECTURE.md` — "4.1 Shell zones" and "7.2 Quality floor"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts"; `docs/domains/frontend/DESIGN_LOCK.md` — "1. Shell geometry" and "1.1 Viewport and zone width budget"; `spec.md` — FR-006, FR-007, FR-008, FR-010. Decisions: `research.md` R9, R11, R12.

## Landmarks (B3-D1)

At `/`, the router redirects to `/sandbox`. At 1920 px the shell renders four zones.

| Zone | Role | `data-zone` | `aria-label` |
|---|---|---|---|
| Z2 | `banner` | `z2` | from `t()` |
| Z1 | `navigation` | `z1` | from `t()` |
| Z3 | `main` | `z3` | from `t()` |
| Z4 | `complementary` | `z4` | from `t()` |

Tests select by role and `data-zone`, never by CSS class. The accessible name comes from `t()`. The five strings (skip link plus four labels) do not have a fixed sentence in the sources. New catalogue keys hold them. Tests do not lock a particular Vietnamese sentence beyond "the name comes from `t()`".

Z1 shows both tracks (Sandbox and Portfolio) and an empty lifecycle frame. The frame's accessible name is `t('shell.z1.lifecycle')`. It contains no stage rows. Tests lock the key, not a fixed sentence. Z2 does not contain Z1 content. Z2 is not resizable. The model selector renders in the Z4 header, not in Z2. `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.5 Shell and zone component contracts" still lists a `features/models` selector on the Z2 slot. That line is stale (`spec.md` — "Source conflicts"). This contract follows DESIGN_LOCK and the Z4 slot row.

## Focus order (B3-D2)

One Playwright test at 1920 px. Tab order is the skip link, then Z2, then Z1, then Z3, then Z4. The focused element's closest `data-zone` is the check, after the skip link. Every focused element has a `:focus-visible` outline of at least 2 px. The skip link text comes from `t()`. The technical design calls it skip-to-workspace. The catalogue holds the vi-VN string.

Z1, Z3, and Z4 resize handles are keyboard operable (`react-resizable-panels`). Z2 has no handle. `F6` zone cycling is not built.

## Widths (B3-D3)

Playwright at 1920, 1440, 1024, and 768. The Proposed 240 px and 440 px defaults are not asserted.

| Width | Z1 | Z3 | Z4 | Z2 utilities corner |
|---|---|---|---|---|
| 1440 and above | docked beside the others | beside the others | docked beside the others | no account menu; the drawer toggle is not the opener |
| below 1440, at least 1024 | docked | does not sit under a stacked zone | overlay drawer | toggle with `aria-expanded` |
| below 1024, down to 768 | 56 px rail | at 768, width ≥ 712 px | overlay drawer | same toggle |

On the rail, both track icons have an `aria-label` and a tooltip. Text labels show on hover or focus only. The active track has a visible mark besides the icon. Zone bounding boxes do not overlap. `scrollWidth <= clientWidth`. Zones do not stack. Widths below 768 px are out of scope.

## Isolation (B3-D5)

`ZoneHost` wraps each zone. A thrown child sets that zone to `data-state="error"` and calls `reportError` with the zone id. The other three zones still render their content. `reportError` is a console sink in `platform/observability`. No vendor reporter is selected.

## Dependency direction

`app` composes `features` and may use `platform` and `design-system`. A feature imports another feature only through `index.ts`. `platform` does not import `features` or `app`. A feature does not call `fetch`. Lint enforces this with core `no-restricted-imports` (`research.md` R8). `eslint-plugin-boundaries` is not added.
