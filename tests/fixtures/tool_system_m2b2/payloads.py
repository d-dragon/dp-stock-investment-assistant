"""Raw-payload and degraded-state fixtures for M2B.2 tests."""

RAW_PROVIDER_PAYLOAD = {
    "symbol": "FPT",
    "raw_provider_payload": {"price": 100000},
    "raw_html": "<html><script>alert(1)</script></html>",
}

SAFE_FACT = {
    "kind": "EvidenceFact",
    "content": {"metric": "price", "value": 100000, "currency": "VND"},
}

DEGRADED_FIXTURES = [
    "stale",
    "missing_field",
    "provider_down",
    "parser_limited",
    "blocked_license",
    "freshness_unknown",
    "validation_failed",
    "unsupported_provider",
]
