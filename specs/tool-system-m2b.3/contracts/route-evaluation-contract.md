# Contract: Vietnamese and Mixed-Language Route Evaluation

## Scope

Feature-local contract for deterministic M2B.3 route-evaluation fixtures. It verifies route and tool-family selection before market-data and visualization tools are considered verified.

## Fixture Shape

Each fixture must define:

- fixture id
- utterance
- language mix: Vietnamese, English, or mixed
- expected route
- expected tool family
- symbol context or absence of symbol
- ambiguity label
- expected outcome: routed, disambiguation, degraded, or deferred-scope

## Required Coverage

Fixture sets must cover:

- price and quote prompts
- chart and visualization prompts
- fundamentals prompts
- disclosures and corporate-action prompts
- market breadth prompts
- flow prompts
- report-like prompts that remain route/evaluation fixtures only
- ambiguous ticker-only prompts
- unsupported or deferred-scope prompts

## Metrics

- Meaning-based classification accuracy must be at least 85%.
- Route-tool exposure precision and recall targets must be recorded before verification.
- Ambiguous fixtures must degrade or request disambiguation rather than exposing unrelated tool families.

## Scope Guards

Report-like fixtures must not enable report generation or persistence. Generic web evidence, remote/MCP admission, and production provider enablement remain outside this contract.
