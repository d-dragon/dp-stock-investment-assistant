# Contract: Attribution, Cache Freshness, and Trace Metadata

## Scope

Feature-local internal contract for M2B.3 answer attribution, cache freshness records, and provider-backed trace metadata.

## Answer Attribution

Each market fact used in an answer, retained derivative, report input, snapshot, or artifact metadata must carry:

- provider/source
- source URL or reference
- retrieved timestamp
- source, published, or effective timestamp where available
- canonical symbol identity where applicable
- exchange and currency where applicable
- freshness category
- license posture
- warnings or degraded-state reason

## Cache Freshness Metadata

Cache-hit records must carry:

- cache key
- provider/source
- source timestamp where available
- retrieved timestamp
- freshness category
- TTL or expiry
- warnings
- degraded-state reason where applicable

Anonymous, expired, stale, or freshness-unknown cache hits must refresh through admitted policy or return degraded state.

## Provider Trace Metadata

Internal traces for provider-backed tool calls must include:

- selected route
- selected tool family
- selected adapter where applicable
- provider class
- license mode
- source URL or reference
- retrieved timestamp
- source, published, or effective timestamp where available
- fallback decision or degraded-state reason
- descriptor/envelope identity where applicable

## Sanitization

Internal traces must omit credentials, secrets, raw provider payloads, parser internals, and raw untrusted web/page content from public metadata.

## Coverage Counters

M2B.3 verification should track:

- complete attribution count
- degraded no-source count
- stale-cache count
- provider/license blocked count
- unsafe trace leak count
