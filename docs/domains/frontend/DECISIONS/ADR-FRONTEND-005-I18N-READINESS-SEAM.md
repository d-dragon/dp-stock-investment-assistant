# ADR-Frontend-005: Reserve an i18n and Locale Seam Now; Adopt Translation Later

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-005 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Accepted |
| **Date** | 2026-11-10 |
| **Last Updated** | 2026-11-13 |
| **Decision Owners** | Engineering · Architecture · Frontend maintainers |

## Context

DP Stock AI is Vietnam-first. The Product Owner decided on 2026-11-10 that translation (Vietnamese and English) is **future work**, but the architecture must make it cheap to adopt. Retrofitting text keys and number formats after many feature modules exist is expensive. Vietnamese market display also needs consistent VND, price, percent and lot formatting and the `Asia/Ho_Chi_Minh` time zone. Exchange sessions and price bands (for example HOSE ±7%, HNX ±10%, UPCoM ±15%) change over time ([FPTS on HOSE](https://www.fpts.com.vn/customer-service/securities-trading/stock-trading-guide/trading-regulations/hose-trading-regulations/), [HSC on HNX](https://www.hsc.com.vn/en/12-hnx-trading-regulations)).

## Decision

- From M-000, every user-facing string goes through **one message layer** (`t()` keys), even with one language shipped.
- Every number, price, percent, currency and date goes through **one locale-format helper** built on the browser `Intl` APIs, with locale and time zone as settings.
- Exchange sessions, price bands and reference/ceiling/floor prices come from the Backend as data, never hard-coded in the Frontend.
- Layouts tolerate longer strings; fonts cover Vietnamese diacritics (design rules in DESIGN_LOCK / `DESIGN_SYSTEM.md`).
- **Launch language is Vietnamese (`vi-VN`)**, with `Asia/Ho_Chi_Minh`; the source message catalogue is Vietnamese (Product Owner decision 2026-11-13).
- **Prices use the Vietnamese price-board style:** thousands of VND, always two decimals, dot decimal (for example `25.30` for 25,300 ₫). Volume is a whole number and never goes through the price formatter. **The dot is only ever a decimal mark and the comma only ever groups thousands**: percent change is `+6.98%`, volume is `1,234,500`, and other whole numbers and ₫ totals group the same way; dates use `vi-VN`. One formatter owns these rules (Product Owner decisions 2026-11-13).
- **More languages are Future:** English and the library choice (react-i18next or FormatJS) are decided when translation is scheduled, by amending this ADR.

## Considered Options

| Option | Outcome |
|--------|---------|
| Seam now, adoption later (chosen) | Low cost now, no retrofit |
| Full i18n now | Rejected: cost before need |
| Nothing now | Rejected: costly retrofit across every module |

## Consequences

- Positive: translation drops in without touching feature code.
- Negative: small discipline cost; a lint check for raw strings belongs in TECHNICAL_DESIGN.

## Requirement Alignment

| Requirement | Relevance |
|-------------|-----------|
| **SNR-7** Usability, Accessibility, and Responsive Behavior | Consistent, locale-correct presentation |
| **SNR-6** Maintainability and Testability | Avoids cross-module retrofit |

## Related Documents

- [Frontend Domain Architecture](../ARCHITECTURE.md) §4.3, §7.1

## References

- [MDN — Intl](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)
- [FPTS — HOSE trading regulations](https://www.fpts.com.vn/customer-service/securities-trading/stock-trading-guide/trading-regulations/hose-trading-regulations/)
- [HSC — HNX trading regulations](https://www.hsc.com.vn/en/12-hnx-trading-regulations)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-11-10 | Software Architect Assistant | Proposed; horizon M-000 to M-009 agreed with the Product Owner |
| 0.2 | 2026-11-13 | Software Architect Assistant | Accepted by the Product Owner; launch UI `vi-VN` with a Vietnamese source catalogue; board-style price format |
| 0.3 | 2026-11-13 | Software Architect Assistant | Same-day correction before first commit: board style applies to prices only; volume is a grouped whole number |
| 0.4 | 2026-11-13 | Software Architect Assistant | Product Owner chose the dot decimal for every number, including percent change (`+6.98%`) |
| 0.5 | 2026-11-13 | Software Architect Assistant | Product Owner chose comma grouping for thousands (`1,234,500`), so the dot only ever marks a decimal |
