"""
Stock Query Route Definitions

Defines route taxonomy and training utterances for semantic routing.
Uses semantic-router library (aurelio-labs) for classification.

Reference: backend-python.instructions.md § Model Factory and AI Clients
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class StockQueryRoute(str, Enum):
    """
    Stock query classification routes.
    
    Each route represents a distinct intent category for stock-related queries.
    The router uses semantic similarity to classify incoming queries.
    """
    
    # Price and Quote Information
    PRICE_CHECK = "price_check"
    """Current price, quotes, bid/ask spreads, market cap."""
    
    # News and Events
    NEWS_ANALYSIS = "news_analysis"
    """Headlines, earnings announcements, market events, sentiment."""
    
    # Portfolio Management
    PORTFOLIO = "portfolio"
    """Holdings, positions, P&L, allocation, rebalancing."""
    
    # Technical Analysis
    TECHNICAL_ANALYSIS = "technical_analysis"
    """Charts, indicators (MACD, RSI, Bollinger), patterns, trends."""
    
    # Fundamental Analysis
    FUNDAMENTALS = "fundamentals"
    """P/E, P/B, DCF, earnings, revenue, financial ratios."""
    
    # Investment Ideas
    IDEAS = "ideas"
    """Stock picks, sector opportunities, investment strategies."""
    
    # Market Overview
    MARKET_WATCH = "market_watch"
    """Index updates, sector performance, market breadth."""
    
    # Fallback for unmatched queries
    GENERAL_CHAT = "general_chat"
    """General conversation or ambiguous queries."""


# Training utterances for each route
# These are used to build the semantic index for classification
ROUTE_UTTERANCES: Dict[StockQueryRoute, List[str]] = {
    StockQueryRoute.PRICE_CHECK: [
        "What is the current price of AAPL?",
        "Get me the stock quote for Tesla",
        "How much is Microsoft trading at?",
        "Show me the bid-ask spread for NVDA",
        "What's the market cap of Amazon?",
        "Check the current price of VNM",
        "Get real-time quote for VCB",
        "What is HPG trading at right now?",
        "Show me the latest price for VIC",
        "How much does one share of Google cost?",
    ],
    
    StockQueryRoute.NEWS_ANALYSIS: [
        "What's the latest news on Apple?",
        "Show me recent headlines for Tesla",
        "Any earnings announcements today?",
        "What happened with NVDA stock today?",
        "Get news about the tech sector",
        "Are there any events affecting VNM?",
        "What's driving the move in VCB?",
        "Show me news about bank stocks",
        "Latest developments for Vingroup",
        "What's causing the market volatility?",
    ],
    
    StockQueryRoute.PORTFOLIO: [
        "Show my current holdings",
        "What's my portfolio P&L today?",
        "How is my position in AAPL performing?",
        "Calculate my portfolio allocation",
        "Should I rebalance my holdings?",
        "What's my exposure to tech stocks?",
        "Show my realized gains this year",
        "How much am I down on Tesla?",
        "List all my stock positions",
        "What's my portfolio value?",
    ],
    
    StockQueryRoute.TECHNICAL_ANALYSIS: [
        "Show me the MACD for AAPL",
        "What's the RSI on Tesla?",
        "Draw Bollinger Bands for NVDA",
        "Is there a head and shoulders pattern?",
        "Check support and resistance levels for VNM",
        "Show the 50-day moving average",
        "What's the trend on VCB?",
        "Analyze the chart pattern for HPG",
        "Is MSFT overbought or oversold?",
        "Show me the candlestick chart",
    ],
    
    StockQueryRoute.FUNDAMENTALS: [
        "What's the P/E ratio of Apple?",
        "Show me Amazon's revenue growth",
        "Calculate the DCF value for Tesla",
        "What are Microsoft's earnings per share?",
        "Compare P/B ratios in the banking sector",
        "Show VNM's debt-to-equity ratio",
        "What's the ROE for VCB?",
        "Analyze HPG's profit margins",
        "Get the dividend yield for VIC",
        "Is this stock undervalued?",
    ],
    
    StockQueryRoute.IDEAS: [
        "What stocks should I buy now?",
        "Give me investment ideas for tech sector",
        "Which sectors are undervalued?",
        "Recommend some growth stocks",
        "What are the best dividend stocks?",
        "Find me momentum plays",
        "Which stocks have upside potential?",
        "Suggest some defensive stocks",
        "What's a good entry point for AAPL?",
        "Which Vietnamese stocks are promising?",
    ],
    
    StockQueryRoute.MARKET_WATCH: [
        "How is VN-Index doing today?",
        "Show me the market overview",
        "What's the sector performance?",
        "Which sectors are leading?",
        "How is the S&P 500 performing?",
        "Show market breadth",
        "Are most stocks up or down?",
        "What's the market sentiment?",
        "How are Asian markets doing?",
        "Give me a market summary",
    ],
    
    StockQueryRoute.GENERAL_CHAT: [
        "Hello, how are you?",
        "What can you help me with?",
        "Tell me about yourself",
        "Thanks for the help",
        "I don't understand",
        "Can you explain that again?",
        "What time is it?",
        "Who created you?",
        "What's the weather like?",
        "Random conversation topic",
    ],
}


@dataclass(frozen=True)
class RouteResult:
    """
    Result of query routing classification.
    
    Attributes:
        route: The classified route (or GENERAL_CHAT if below threshold)
        confidence: Similarity score (0.0 to 1.0)
        query: Original query text
    """
    route: StockQueryRoute
    confidence: float
    query: str
    
    @property
    def is_confident(self) -> bool:
        """Check if routing confidence is above typical threshold (0.7)."""
        return self.confidence >= 0.7
    
    @property
    def is_fallback(self) -> bool:
        """Check if routed to general chat (fallback)."""
        return self.route == StockQueryRoute.GENERAL_CHAT
    
    def __str__(self) -> str:
        return f"RouteResult(route={self.route.value}, confidence={self.confidence:.3f})"


# Route descriptions for documentation and UI
ROUTE_DESCRIPTIONS: Dict[StockQueryRoute, str] = {
    StockQueryRoute.PRICE_CHECK: "Get current stock prices, quotes, and market cap",
    StockQueryRoute.NEWS_ANALYSIS: "Latest news, headlines, and market events",
    StockQueryRoute.PORTFOLIO: "View and manage your portfolio holdings",
    StockQueryRoute.TECHNICAL_ANALYSIS: "Chart analysis, indicators, and patterns",
    StockQueryRoute.FUNDAMENTALS: "Financial ratios, earnings, and valuation",
    StockQueryRoute.IDEAS: "Investment ideas and stock recommendations",
    StockQueryRoute.MARKET_WATCH: "Market overview and sector performance",
    StockQueryRoute.GENERAL_CHAT: "General questions and conversation",
}


def get_all_routes() -> List[StockQueryRoute]:
    """Get all available routes (excluding GENERAL_CHAT)."""
    return [r for r in StockQueryRoute if r != StockQueryRoute.GENERAL_CHAT]


def get_route_utterances(route: StockQueryRoute) -> List[str]:
    """Get training utterances for a specific route."""
    return ROUTE_UTTERANCES.get(route, [])
