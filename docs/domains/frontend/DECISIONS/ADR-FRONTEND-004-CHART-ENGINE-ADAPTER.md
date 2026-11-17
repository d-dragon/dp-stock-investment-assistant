# ADR-Frontend-004: Chart Engine Behind an Adapter: M-001 Proof of Concept, M-006 Enhancement

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-004 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Accepted |
| **Date** | 2026-11-10 |
| **Last Updated** | 2026-11-13 |
| **Replaces in part** | [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) primary-canvas bullet, as to indicators: the library ships none; indicators are our own build in M-006 |
| **Decision Owners** | Engineering · Architecture · Frontend maintainers |

## Context

[ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) names TradingView Lightweight Charts as the primary canvas engine and Chart.js for auxiliary charts, and carves the chart out of the M-000 foundation. On 2026-11-10 the Product Owner set the chart sequence: a **simple chart proof of concept in M-001**, then **enhanced charting in M-006**, where the chart also yields to the Decision gate (**SR-1.3.4**).

Two facts shape this:

- Lightweight Charts is open source under Apache-2.0 and requires TradingView attribution ([repository](https://github.com/tradingview/lightweight-charts); [TradingView free charting libraries](https://www.tradingview.com/free-charting-libraries/)). It provides candlestick, line and volume series and markers, but **no built-in technical indicators or drawing tools**; those must be built on its plugin API. ADR-002's mention of indicators (RSI, MACD) therefore means indicators we build, not ones the library ships.
- TradingView's Advanced Charts is licensed only to companies for public web projects, not for personal, study or testing use ([TradingView FAQ](https://www.tradingview.com/free-charting-libraries/)). Its other conditions should be checked in the agreement itself before any adoption.

## Decision

- Feature code uses a platform **chart adapter** only; no feature imports a chart library directly.
- The adapter's first engine is **Lightweight Charts**, with TradingView attribution kept on the chart.
- **M-001 (proof of concept):** symbol, time range, price series, volume, markers for evidence and thesis points, `market.*` theme. Research Sandbox only. It runs on prepared mock data and is not production quality; a Backend price contract and a licensed source come later (ADR-SYS-004). Product Owner decision 2026-11-13.
- **M-006 (enhanced):** richer series and annotations, and the chart yields to the gate checklist in the Research Sandbox (SR-1.3.4). Named levels are Backend-owned Core data (Thesis / Decision); the chart only displays them, and they carry to the Position on Pass.
- Thesis and evidence annotations live in our own layer above the engine, so they survive an engine swap.
- The chart engine is lazy-loaded.

## Considered Options

| Option | Outcome |
|--------|---------|
| Lightweight Charts behind an adapter (chosen) | Permissive licence, small, swappable |
| Lightweight Charts imported directly by features | Rejected: engine lock-in across modules |
| TradingView Advanced Charts | Not chosen now; licence limited to company public projects. Kept as a Future swap option behind the adapter |
| Chart.js for price charts | Rejected for price: not built for financial series. Stays auxiliary per ADR-002, confirmed by the Product Owner 2026-11-13: non-price charts only, behind its own adapter like this one, and kept out of the bundle until a slice uses it |

## Consequences

- Positive: M-001 ships a chart quickly; an engine swap stays inside one block.
- Negative: indicators and drawing tools in M-006 are our own build cost on the plugin API.
- Negative: the adapter must be designed before M-001 and kept engine-neutral.
- Market data rights are separate from the chart licence; TradingView supplies no data. Data licensing stays with [ADR-SYS-004](../../../architecture/DECISIONS/ADR-SYS-004-DATA-PIPELINE-AND-RECORDS.md).
- The M-001 proof of concept is required by **SR-1.3.5** (approved 2026-11-10): reference, ceiling and floor prices are drawn as supplied by the Backend, never computed in the Frontend, and the TradingView credit ships from day one.

## Requirement Alignment

| Requirement | Relevance |
|-------------|-----------|
| **SR-1.3.1** Zoned workspace | Chart docked in Z3 |
| **SR-1.3.5** Docked price chart (proof of concept) | M-001 scope of this ADR |
| **SR-1.3.4** Chart yields at the Decision gate | M-006 enhancement |

## Related Documents

- [Frontend Domain Architecture](../ARCHITECTURE.md) §4.3, §4.4, §8.3
- [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) (this ADR refines its chart bullets; it does not supersede ADR-002)

## References

- [TradingView Lightweight Charts repository](https://github.com/tradingview/lightweight-charts)
- [TradingView — Free charting libraries and FAQ](https://www.tradingview.com/free-charting-libraries/)
- [Lightweight Charts documentation](https://tradingview.github.io/lightweight-charts/)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-11-10 | Software Architect Assistant | Proposed; horizon M-000 to M-009 agreed with the Product Owner |
| 0.2 | 2026-11-10 | Software Architect Assistant | Cites SR-1.3.5 for the M-001 proof of concept; still Proposed |
| 0.3 | 2026-11-13 | Software Architect Assistant | Accepted by the Product Owner; M-001 Sandbox only on prepared mock data; named levels Backend-owned; replaces ADR-002's indicator claim |
| 0.4 | 2026-11-13 | Software Architect Assistant | Chart.js confirmed for non-price charts behind its own adapter (Product Owner, 2026-11-13); this ADR still covers price charts only |
