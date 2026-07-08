"""Safe market-data payload fixtures."""

from __future__ import annotations


QUOTE_PAYLOAD = {"symbol": "FPT", "price": 100000, "unit": "VND"}
HISTORY_PAYLOAD = {"symbol": "FPT", "rows": [{"close": 100000, "volume": 1000}], "unit": "VND"}
INDICATOR_PAYLOAD = {"symbol": "FPT", "indicator": "sma_20", "value": 100000, "lineage": "price_history"}
FUNDAMENTAL_PAYLOAD = {"symbol": "FPT", "period": "2026Q1", "metric": "roe", "value": 0.18}
BREADTH_PAYLOAD = {"market": "VN", "time_window": "session", "advancers": 100, "decliners": 80}
FLOW_PAYLOAD = {"market": "VN", "time_window": "session", "foreign_net_buy": 1000000}
DISCLOSURE_PAYLOAD = {"symbol": "FPT", "event_type": "disclosure", "published_at": "2026-07-07T00:00:00Z"}
CORPORATE_ACTION_PAYLOAD = {"symbol": "FPT", "event_type": "dividend", "effective_at": "2026-07-31T00:00:00Z"}
