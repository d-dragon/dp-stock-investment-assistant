# Contract: Mutation Receipts and Retained Derivatives

## Purpose

Define the M2B.2 non-mutating retention and mutation receipt backbone without enabling production symbol-store writes.

## Mutation Classification

Symbol-store write actions are classified as:

- `workflow_mutation`
- subtype: `internal_state_mutation`

## Default Behavior

- Production write paths remain disabled or degraded.
- A mutation request without future authorization and confirmation policy returns `DegradedState`.
- Test-only or future approved mutation paths must emit `MutationReceipt`.

## MutationReceipt Shape

Required fields:

- `mutation_id`
- `target_record`
- `action`
- `before_summary`
- `after_summary`
- `actor_or_route`
- `approval_status`
- `audit_metadata`
- `timestamp`
- `result`

## Retained Derivative Rules

Allowed derivative classes:

- Reports
- Generated artifacts
- Mutation receipts
- Audit metadata
- Trace metadata
- Approved snapshots
- Domain records

Rules:

- Retained derivatives preserve source lineage or explicit no-source degraded-state reason.
- `ToolContextPack` is not persisted wholesale.
- Raw provider, web, parser, and tool payloads are not retained by this feature unless a later governed feature defines storage and sanitization policy.

## Verification Expectations

- Write-action fixtures remain blocked or degraded by default.
- Mutation receipt fixtures contain all required receipt fields.
- Retained derivative fixtures preserve source lineage or degraded no-source reason.
- Context pack persistence tests prove only approved derivatives are retained.
