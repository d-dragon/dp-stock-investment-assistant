# ADR-SYS-004: Data pipeline and kept versus new records

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-10-12; accepted 2026-10-13 |
| Owner | Software Architect Assistant; decision by Phan Duy |
| Blocks | Information model in the data technical design; market data neighbour in the overview |
| Depends on | ADR-SYS-001 identity (record ownership) |

## Context

The ELT research proposal says "selected", but no decision has adopted it, and its gold-layer naming conflicts with the Phase 1 identities. The live market read uses yfinance, whose README says it is not affiliated with Yahoo and that the Yahoo Finance API is for personal use only.

## Decision to make

Whether to adopt the ELT/medallion pipeline, which records are kept and which are new, and the rule for persisting licensed vendor data.

## Options to evaluate

- Adopt, adapt, or reject the ELT proposal.
- A licensed, Vietnam-first market data provider for the target, versus keeping yfinance for development only.
- A licence-for-persistence rule per source.

## Decision

Accepted, 2026-10-13 (Phan Duy). Adopt the [ELT data-pipeline proposal](../../research/DATA_PIPELINE_PROCESS_ELT_RESEARCH_AND_PROPOSAL.md): raw, conformed and curated layers (bronze, silver, gold) on one store, with a cached live path for market queries.

- **Excluded:** the proposal's gold-layer naming of session analyses, idea records and vector memory as marts. Those records are not a Working Thesis, Position or Insight.
- **Licensing constraint:** yfinance's terms are personal use only. It stays a development source, and its data is not persisted as evidence. Every source needs a licence that covers persistence before its data lands in the pipeline.

## Follow-ups

- Choose a licensed, Vietnam-first market data provider for the target.
- Record the licence-for-persistence rule per source.

- The information model for the Phase 1 identities goes in `docs/domains/data/TECHNICAL_DESIGN.md`.
