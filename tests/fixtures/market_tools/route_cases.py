"""Vietnamese, English, and mixed-language route cases."""

from __future__ import annotations

from core.routes import StockQueryRoute


ROUTE_CASES = [
    {
        "query": "Gia hien tai cua FPT tren HOSE la bao nhieu?",
        "expected_route": StockQueryRoute.PRICE_CHECK.value,
        "expected_tool_family": "market_data",
    },
    {
        "query": "Show price history OHLCV for HNX:SHS",
        "expected_route": StockQueryRoute.PRICE_CHECK.value,
        "expected_tool_family": "market_data",
    },
    {
        "query": "Mo bieu do TradingView cho FPT",
        "expected_route": StockQueryRoute.TECHNICAL_ANALYSIS.value,
        "expected_tool_family": "tradingview",
    },
    {
        "query": "Show TradingView heatmap for HOSE",
        "expected_route": StockQueryRoute.TECHNICAL_ANALYSIS.value,
        "expected_tool_family": "tradingview",
    },
    {
        "query": "Lay BCTC va ROE cua VNM",
        "expected_route": StockQueryRoute.FUNDAMENTALS.value,
        "expected_tool_family": "market_data",
    },
    {
        "query": "Show financial statement and EPS for FPT",
        "expected_route": StockQueryRoute.FUNDAMENTALS.value,
        "expected_tool_family": "market_data",
    },
    {
        "query": "Cong bo thong tin va co tuc cua FPT",
        "expected_route": StockQueryRoute.NEWS_ANALYSIS.value,
        "expected_tool_family": "market_data",
    },
    {
        "query": "Corporate action rights issue for HOSE:FPT",
        "expected_route": StockQueryRoute.NEWS_ANALYSIS.value,
        "expected_tool_family": "market_data",
    },
    {
        "query": "Do rong thi truong va dong tien nuoc ngoai",
        "expected_route": StockQueryRoute.MARKET_WATCH.value,
        "expected_tool_family": "market_data",
    },
    {
        "query": "Foreign flow and market breadth on VN-Index",
        "expected_route": StockQueryRoute.MARKET_WATCH.value,
        "expected_tool_family": "market_data",
    },
    {
        "query": "Generate an investment report for FPT",
        "expected_route": StockQueryRoute.MARKET_WATCH.value,
        "expected_tool_family": "report_fixture",
        "deferred_scope": True,
    },
    {
        "query": "ABC",
        "expected_route": StockQueryRoute.GENERAL_CHAT.value,
        "expected_tool_family": None,
    },
]
