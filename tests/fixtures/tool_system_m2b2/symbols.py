"""Vietnam symbol and index fixtures for M2B.2 tests."""

SYMBOL_RECORDS = [
    {
        "symbol": "FPT",
        "name": "FPT Corporation",
        "asset_type": "equity",
        "aliases": ["HOSE:FPT", "FPT Corp"],
        "identifiers": {"isin": "VN000000FPT1"},
        "listing": {"exchange": "HOSE", "currency": "VND"},
        "classification": {"sector": "Technology", "market": "VN"},
        "coverage": {"capabilities": ["identity", "aliases", "coverage", "tags"]},
        "tags": ["vn30", "technology"],
        "stored_snapshot_metadata": {"snapshot_id": "symbol:FPT"},
        "updated_at": "2026-07-06T00:00:00Z",
        "_id": "symbol:FPT:HOSE",
    },
    {
        "symbol": "SHS",
        "name": "Saigon Hanoi Securities",
        "asset_type": "equity",
        "aliases": ["HNX:SHS"],
        "identifiers": {"ticker": "SHS"},
        "listing": {"exchange": "HNX", "currency": "VND"},
        "classification": {"sector": "Financials", "market": "VN"},
        "coverage": {"capabilities": ["identity"]},
        "tags": ["brokerage"],
        "updated_at": "2026-07-06T00:00:00Z",
        "_id": "symbol:SHS:HNX",
    },
    {
        "symbol": "BSR",
        "name": "Binh Son Refining and Petrochemical",
        "asset_type": "equity",
        "aliases": ["UPCOM:BSR"],
        "identifiers": {"ticker": "BSR"},
        "listing": {"exchange": "UPCOM", "currency": "VND"},
        "classification": {"sector": "Energy", "market": "VN"},
        "coverage": {"capabilities": ["identity"]},
        "tags": ["energy"],
        "updated_at": "2026-07-06T00:00:00Z",
        "_id": "symbol:BSR:UPCOM",
    },
    {
        "symbol": "VNINDEX",
        "name": "VN Index",
        "asset_type": "index",
        "aliases": ["VN-INDEX"],
        "identifiers": {"index_code": "VNINDEX"},
        "listing": {"exchange": "HOSE", "currency": "VND"},
        "classification": {"market": "VN"},
        "coverage": {"capabilities": ["identity", "index"]},
        "tags": ["index"],
        "updated_at": "2026-07-06T00:00:00Z",
        "_id": "index:VNINDEX",
    },
    {
        "symbol": "VN30",
        "name": "VN30 Index",
        "asset_type": "index",
        "aliases": ["VN30INDEX"],
        "identifiers": {"index_code": "VN30"},
        "listing": {"exchange": "HOSE", "currency": "VND"},
        "classification": {"market": "VN"},
        "coverage": {"capabilities": ["identity", "index"]},
        "tags": ["index", "vn30"],
        "updated_at": "2026-07-06T00:00:00Z",
        "_id": "index:VN30",
    },
    {
        "symbol": "HNXINDEX",
        "name": "HNX Index",
        "asset_type": "index",
        "aliases": ["HNX-INDEX"],
        "identifiers": {"index_code": "HNXINDEX"},
        "listing": {"exchange": "HNX", "currency": "VND"},
        "classification": {"market": "VN"},
        "coverage": {"capabilities": ["identity", "index"]},
        "tags": ["index"],
        "updated_at": "2026-07-06T00:00:00Z",
        "_id": "index:HNXINDEX",
    },
    {
        "symbol": "UPINDEX",
        "name": "UPCoM Index",
        "asset_type": "index",
        "aliases": ["UPCOMINDEX"],
        "identifiers": {"index_code": "UPINDEX"},
        "listing": {"exchange": "UPCOM", "currency": "VND"},
        "classification": {"market": "VN"},
        "coverage": {"capabilities": ["identity", "index"]},
        "tags": ["index"],
        "updated_at": "2026-07-06T00:00:00Z",
        "_id": "index:UPINDEX",
    },
    {
        "symbol": "ABC",
        "name": "ABC on HOSE",
        "asset_type": "equity",
        "aliases": ["ABC"],
        "listing": {"exchange": "HOSE", "currency": "VND"},
        "coverage": {"capabilities": ["identity"]},
        "_id": "symbol:ABC:HOSE",
    },
    {
        "symbol": "ABC",
        "name": "ABC on HNX",
        "asset_type": "equity",
        "aliases": ["ABC"],
        "listing": {"exchange": "HNX", "currency": "VND"},
        "coverage": {"capabilities": ["identity"]},
        "_id": "symbol:ABC:HNX",
    },
    {
        "symbol": "STALE",
        "name": "Stale Fixture",
        "asset_type": "equity",
        "listing": {"exchange": "HOSE", "currency": "VND"},
        "stale": True,
        "_id": "symbol:STALE:HOSE",
    },
]


class InMemorySymbolRepository:
    """Repository-shaped fixture for symbol tests."""

    def __init__(self, records=None):
        self.records = list(records or SYMBOL_RECORDS)
        self.write_calls = []

    def get_by_symbol(self, symbol):
        matches = [record for record in self.records if record["symbol"] == symbol]
        return matches[0] if len(matches) == 1 else None

    def search_by_name(self, name_pattern, limit=50):
        needle = name_pattern.upper()
        results = []
        for record in self.records:
            values = [record.get("symbol", ""), record.get("name", ""), *record.get("aliases", [])]
            if any(needle in value.upper() for value in values):
                results.append(record)
        return results[:limit]

    def get_by_exchange(self, exchange, limit=100):
        return [
            record
            for record in self.records
            if record.get("listing", {}).get("exchange") == exchange
        ][:limit]

    def get_tracked_symbols(self, limit=100):
        return self.records[:limit]

    def get_by_tags(self, tags, match_all=False, limit=100):
        tags = set(tags)
        results = []
        for record in self.records:
            record_tags = set(record.get("tags", []))
            if (tags <= record_tags) if match_all else bool(tags & record_tags):
                results.append(record)
        return results[:limit]

    def upsert_symbol(self, *args, **kwargs):
        self.write_calls.append(("upsert_symbol", args, kwargs))
        return None
