# ADR-SYS-002: Decision gate (Pass, Fail, Revise)

| Field | Value |
|---|---|
| Status | Proposed (stub) |
| Date | 2026-10-12 |
| Owner | Software Architect Assistant; decision by Phan Duy |
| Blocks | P0 gate and Position deliverables; runtime flows v0.2 sequences |
| Depends on | ADR-SYS-001 identity (the gate assumes an identified user) |

## Context

The gate moves a Working Thesis to a Position. It has two outcomes: Pass and Fail. Revise is the path after Fail. Both outcomes write a Decision record; only Pass creates a Position ([Spec §4.6](../../system/PRODUCT_SPECIFICATION.md#46-decision-gate-and-object-ontology-normative)). Spec §4.6 #2 does not yet say Fail keeps a Decision record. MongoDB runs standalone in compose and is not deployed by Helm, so multi-document transactions are unavailable today. The compose image `mongo:5.0` reached end-of-life on 31 Oct 2024 ([endoflife.date](https://endoflife.date/mongodb)), so moving to a supported version belongs in the same change as any replica-set option.

## Decision to make

How Pass writes the Decision record and the Position so that both exist or neither does, and how Decision records stay immutable.

## Options to evaluate

- A. Run MongoDB as a replica set (new infrastructure in compose and Helm) and write both records in one transaction.
- B. Write the Decision record first with an idempotency key, then create the Position from it in a repeatable step, with a repair path for a failed second write.
- For both: an idempotency key per gate submission; Decision records are append-only.

## Decision

Not yet decided.

## Follow-ups

- A build-failing import test: Agent code must not import Core storage or database code.
- A contract test that only the gate path writes Positions.
- Note to amend Spec §4.6 #2 so Fail keeps a Decision record.
