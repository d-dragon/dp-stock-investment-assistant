"""
Stock Query Semantic Router

Routes stock-related queries to appropriate handlers using semantic similarity.
Uses semantic-router library with OpenAI embeddings (HuggingFace fallback).

Reference: backend-python.instructions.md § Model Factory and AI Clients
"""

import logging
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

try:
    from semantic_router import Route, SemanticRouter
    from semantic_router.encoders import DenseEncoder, HuggingFaceEncoder, OpenAIEncoder
except ModuleNotFoundError:
    class DenseEncoder:  # type: ignore[no-redef]
        """Fallback type used when semantic-router is not installed."""

        pass

    class Route:  # type: ignore[no-redef]
        """Fallback route object for import-safe tests and degraded startup."""

        def __init__(self, name: str, utterances: list[str]) -> None:
            self.name = name
            self.utterances = utterances

    class SemanticRouter:  # type: ignore[no-redef]
        """Fallback router that reports no match until dependency is installed."""

        def __init__(self, *args, **kwargs) -> None:
            self._available = False

        def __call__(self, query: str):
            return type("RouteMatch", (), {"name": None, "similarity_score": 0.0})()

    class HuggingFaceEncoder(DenseEncoder):  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            raise ModuleNotFoundError("semantic_router")

    class OpenAIEncoder(DenseEncoder):  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            raise ModuleNotFoundError("semantic_router")

from .routes import (
    ROUTE_UTTERANCES,
    RouteResult,
    StockQueryRoute,
    get_all_routes,
)

logger = logging.getLogger(__name__)


MARKET_TOOL_FAMILY_BY_ROUTE: Dict[StockQueryRoute, Tuple[str, ...]] = {
    StockQueryRoute.PRICE_CHECK: ("market_data", "stock_symbol"),
    StockQueryRoute.FUNDAMENTALS: ("market_data",),
    StockQueryRoute.TECHNICAL_ANALYSIS: ("market_data", "tradingview"),
    StockQueryRoute.MARKET_WATCH: ("market_data",),
    StockQueryRoute.NEWS_ANALYSIS: ("market_data",),
    StockQueryRoute.PORTFOLIO: (),
    StockQueryRoute.IDEAS: (),
    StockQueryRoute.GENERAL_CHAT: (),
}


_MARKET_ROUTE_KEYWORDS: Sequence[Tuple[StockQueryRoute, str, Tuple[str, ...]]] = (
    (
        StockQueryRoute.TECHNICAL_ANALYSIS,
        "tradingview",
        (
            "chart",
            "bieu do",
            "biểu đồ",
            "candlestick",
            "widget",
            "heatmap",
            "screener",
            "ticker tape",
            "rsi",
            "macd",
            "duong gia",
            "đường giá",
        ),
    ),
    (
        StockQueryRoute.FUNDAMENTALS,
        "market_data",
        (
            "fundamental",
            "fundamentals",
            "p/e",
            "pe",
            "roe",
            "roa",
            "eps",
            "bctc",
            "bao cao tai chinh",
            "báo cáo tài chính",
            "statement",
            "financial statement",
            "doanh thu",
            "loi nhuan",
            "lợi nhuận",
        ),
    ),
    (
        StockQueryRoute.NEWS_ANALYSIS,
        "market_data",
        (
            "disclosure",
            "cong bo thong tin",
            "công bố thông tin",
            "official notice",
            "dividend",
            "co tuc",
            "cổ tức",
            "quyen mua",
            "quyền mua",
            "corporate action",
            "listing change",
            "niem yet",
            "niêm yết",
        ),
    ),
    (
        StockQueryRoute.MARKET_WATCH,
        "market_data",
        (
            "breadth",
            "market breadth",
            "do rong thi truong",
            "độ rộng thị trường",
            "foreign flow",
            "dong tien",
            "dòng tiền",
            "nuoc ngoai",
            "nước ngoài",
            "vn-index",
            "vnindex",
            "sector",
        ),
    ),
    (
        StockQueryRoute.PRICE_CHECK,
        "market_data",
        (
            "price",
            "quote",
            "gia",
            "giá",
            "ohlcv",
            "history",
            "lich su gia",
            "lịch sử giá",
            "gia hien tai",
            "giá hiện tại",
            "close",
            "volume",
        ),
    ),
)


_DEFERRED_REPORT_KEYWORDS = (
    "report",
    "bao cao dau tu",
    "báo cáo đầu tư",
    "investment report",
    "write report",
    "generate report",
)


class StockQueryRouter:
    """
    Semantic router for stock-related queries.
    
    Uses semantic similarity to classify queries into one of 8 route categories.
    Supports OpenAI encoder with HuggingFace fallback for embedding generation.
    
    Attributes:
        config: Configuration mapping with semantic_router settings
        threshold: Minimum confidence score for route matching
        encoder: Active encoder instance (OpenAI or HuggingFace)
        router: RouteLayer instance for query classification
        
    Example:
        >>> router = StockQueryRouter(config)
        >>> result = router.route("What is AAPL trading at?")
        >>> result.route
        <StockQueryRoute.PRICE_CHECK: 'price_check'>
        >>> result.confidence
        0.85
    """
    
    # Default configuration values
    DEFAULT_THRESHOLD = 0.7
    DEFAULT_OPENAI_MODEL = "text-embedding-3-small"
    DEFAULT_HUGGINGFACE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    def __init__(
        self,
        config: Mapping[str, Any],
        *,
        encoder: Optional[DenseEncoder] = None,
    ) -> None:
        """
        Initialize the stock query router.
        
        Args:
            config: Application configuration with semantic_router section
            encoder: Optional pre-configured encoder (for testing)
        """
        self._config = config
        self._router_config = config.get("semantic_router", {})
        
        # Load settings from config
        self._threshold = self._router_config.get("threshold", self.DEFAULT_THRESHOLD)
        self._cache_embeddings = self._router_config.get("cache_embeddings", True)
        
        # Initialize encoder (or use provided one)
        self._encoder = encoder or self._create_encoder()
        
        # Build the route layer
        self._routes = self._build_routes()
        self._router = self._create_route_layer()
        
        logger.info(
            f"StockQueryRouter initialized with encoder={type(self._encoder).__name__}, "
            f"threshold={self._threshold}, routes={len(self._routes)}"
        )
    
    def _create_encoder(self) -> DenseEncoder:
        """
        Create encoder with OpenAI primary and HuggingFace fallback.
        
        Returns:
            DenseEncoder: Configured encoder instance
            
        Raises:
            RuntimeError: If both OpenAI and HuggingFace fail to initialize
        """
        encoder_config = self._router_config.get("encoder", {})
        primary = encoder_config.get("primary", "openai")
        
        # Try primary encoder first
        if primary == "openai":
            try:
                return self._create_openai_encoder(encoder_config)
            except Exception as e:
                logger.warning(f"OpenAI encoder failed, falling back to HuggingFace: {e}")
                return self._create_huggingface_encoder(encoder_config)
        else:
            # Primary is huggingface
            try:
                return self._create_huggingface_encoder(encoder_config)
            except Exception as e:
                logger.warning(f"HuggingFace encoder failed, trying OpenAI: {e}")
                return self._create_openai_encoder(encoder_config)
    
    def _create_openai_encoder(self, encoder_config: Dict[str, Any]) -> OpenAIEncoder:
        """Create OpenAI encoder with API key from config."""
        openai_model = encoder_config.get("openai_model", self.DEFAULT_OPENAI_MODEL)
        
        # Get API key from openai config section
        openai_config = self._config.get("openai", {})
        api_key = openai_config.get("api_key")
        
        if not api_key or api_key.startswith("your-"):
            raise ValueError("OpenAI API key not configured")
        
        logger.info(f"Creating OpenAI encoder with model: {openai_model}")
        return OpenAIEncoder(
            name=openai_model,
            openai_api_key=api_key,
        )
    
    def _create_huggingface_encoder(self, encoder_config: Dict[str, Any]) -> HuggingFaceEncoder:
        """Create HuggingFace encoder as fallback."""
        hf_model = encoder_config.get("huggingface_model", self.DEFAULT_HUGGINGFACE_MODEL)
        
        logger.info(f"Creating HuggingFace encoder with model: {hf_model}")
        return HuggingFaceEncoder(name=hf_model)
    
    def _build_routes(self) -> List[Route]:
        """
        Build Route objects from ROUTE_UTTERANCES.
        
        Returns:
            List of Route objects for the RouteLayer
        """
        routes = []
        
        for route_type in get_all_routes():
            utterances = ROUTE_UTTERANCES.get(route_type, [])
            if utterances:
                routes.append(
                    Route(
                        name=route_type.value,
                        utterances=utterances,
                    )
                )
                logger.debug(f"Route '{route_type.value}' loaded with {len(utterances)} utterances")
        
        return routes
    
    def _create_route_layer(self) -> SemanticRouter:
        """Create the SemanticRouter with configured encoder and routes."""
        return SemanticRouter(
            encoder=self._encoder,
            routes=self._routes,
        )
    
    def route(self, query: str) -> RouteResult:
        """
        Classify a query into a stock query route.
        
        Args:
            query: User query text to classify
            
        Returns:
            RouteResult with classified route and confidence score
        """
        if not query or not query.strip():
            logger.debug("Empty query received, returning GENERAL_CHAT")
            return RouteResult(
                route=StockQueryRoute.GENERAL_CHAT,
                confidence=0.0,
                query=query or "",
            )
        
        try:
            # Call semantic router
            result = self._router(query)
            
            # Handle no match (below threshold)
            if result.name is None:
                logger.debug(f"No route matched for query: {query[:50]}...")
                return RouteResult(
                    route=StockQueryRoute.GENERAL_CHAT,
                    confidence=0.0,
                    query=query,
                )
            
            # Map route name back to enum
            try:
                route = StockQueryRoute(result.name)
            except ValueError:
                logger.warning(f"Unknown route name: {result.name}, defaulting to GENERAL_CHAT")
                route = StockQueryRoute.GENERAL_CHAT
            
            # Extract confidence (similarity score)
            confidence = getattr(result, "similarity_score", 0.0) or 0.0
            
            logger.debug(
                f"Query routed: '{query[:30]}...' -> {route.value} (confidence={confidence:.3f})"
            )
            
            return RouteResult(
                route=route,
                confidence=confidence,
                query=query,
            )
            
        except Exception as e:
            logger.error(f"Routing error for query '{query[:50]}...': {e}", exc_info=True)
            return RouteResult(
                route=StockQueryRoute.GENERAL_CHAT,
                confidence=0.0,
                query=query,
            )
    
    def route_batch(self, queries: List[str]) -> List[RouteResult]:
        """
        Classify multiple queries in batch.
        
        Args:
            queries: List of query texts to classify
            
        Returns:
            List of RouteResult objects
        """
        return [self.route(query) for query in queries]
    
    @property
    def threshold(self) -> float:
        """Get the current confidence threshold."""
        return self._threshold
    
    @property
    def encoder_type(self) -> str:
        """Get the active encoder type name."""
        return type(self._encoder).__name__
    
    @property
    def route_count(self) -> int:
        """Get the number of configured routes."""
        return len(self._routes)
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check router health status.
        
        Returns:
            Tuple of (healthy, details) for health monitoring
        """
        try:
            # Test routing with a sample query
            test_result = self.route("What is AAPL price?")
            
            return True, {
                "component": "stock_query_router",
                "status": "ready",
                "encoder": self.encoder_type,
                "routes": self.route_count,
                "threshold": self._threshold,
                "test_query_route": test_result.route.value,
            }
        except Exception as e:
            return False, {
                "component": "stock_query_router",
                "status": "error",
                "error": str(e),
            }


# Singleton instance management
_router_instance: Optional[StockQueryRouter] = None


def get_stock_query_router(config: Mapping[str, Any]) -> StockQueryRouter:
    """
    Get or create the singleton StockQueryRouter instance.
    
    Args:
        config: Application configuration
        
    Returns:
        StockQueryRouter instance
    """
    global _router_instance
    
    if _router_instance is None:
        _router_instance = StockQueryRouter(config)
    
    return _router_instance


def reset_stock_query_router() -> None:
    """Reset the singleton instance (useful for testing)."""
    global _router_instance
    _router_instance = None


def classify_market_tool_family(query: str) -> Dict[str, Any]:
    """Classify market fixture queries without invoking embedding services."""

    normalized = " ".join((query or "").lower().split())
    if not normalized:
        return {
            "route": StockQueryRoute.GENERAL_CHAT,
            "tool_family": None,
            "confidence": 0.0,
            "degraded": True,
            "degraded_reason": "empty_query",
            "deferred_scope": False,
        }

    if any(keyword in normalized for keyword in _DEFERRED_REPORT_KEYWORDS):
        return {
            "route": StockQueryRoute.MARKET_WATCH,
            "tool_family": "report_fixture",
            "confidence": 0.82,
            "degraded": True,
            "degraded_reason": "report_generation_deferred",
            "deferred_scope": True,
        }

    best: Optional[Tuple[StockQueryRoute, str, int]] = None
    for route, tool_family, keywords in _MARKET_ROUTE_KEYWORDS:
        score = sum(1 for keyword in keywords if keyword in normalized)
        if score and (best is None or score > best[2]):
            best = (route, tool_family, score)

    if best is None:
        return {
            "route": StockQueryRoute.GENERAL_CHAT,
            "tool_family": None,
            "confidence": 0.0,
            "degraded": True,
            "degraded_reason": "ambiguous_or_unsupported",
            "deferred_scope": False,
        }

    route, tool_family, score = best
    confidence = min(0.99, 0.74 + (score * 0.08))
    return {
        "route": route,
        "tool_family": tool_family,
        "confidence": confidence,
        "degraded": False,
        "degraded_reason": None,
        "deferred_scope": False,
        "allowed_tool_families": MARKET_TOOL_FAMILY_BY_ROUTE.get(route, ()),
    }


def evaluate_market_route_cases(cases: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Evaluate route and tool-family fixture cases for market acceptance gates."""

    total = len(cases)
    if total == 0:
        return {
            "total": 0,
            "accuracy": 1.0,
            "precision": 1.0,
            "recall": 1.0,
            "correct": 0,
            "results": [],
        }

    results: List[Dict[str, Any]] = []
    route_correct = 0
    tool_correct = 0
    expected_tool_count = 0
    predicted_tool_count = 0
    for case in cases:
        outcome = classify_market_tool_family(str(case.get("query", "")))
        expected_route = case.get("expected_route")
        expected_tool = case.get("expected_tool_family")
        expected_deferred = bool(case.get("deferred_scope", False))
        route_value = outcome["route"].value if isinstance(outcome["route"], StockQueryRoute) else str(outcome["route"])
        route_ok = route_value == str(expected_route)
        tool_ok = outcome.get("tool_family") == expected_tool
        deferred_ok = bool(outcome.get("deferred_scope", False)) == expected_deferred
        if route_ok and deferred_ok:
            route_correct += 1
        if expected_tool is not None:
            expected_tool_count += 1
        if outcome.get("tool_family") is not None:
            predicted_tool_count += 1
        if tool_ok:
            tool_correct += 1
        results.append(
            {
                "query": case.get("query"),
                "expected_route": expected_route,
                "actual_route": route_value,
                "expected_tool_family": expected_tool,
                "actual_tool_family": outcome.get("tool_family"),
                "route_ok": route_ok,
                "tool_ok": tool_ok,
                "deferred_ok": deferred_ok,
            }
        )

    precision_denominator = predicted_tool_count or 1
    recall_denominator = expected_tool_count or 1
    return {
        "total": total,
        "accuracy": route_correct / total,
        "precision": tool_correct / precision_denominator,
        "recall": tool_correct / recall_denominator,
        "correct": route_correct,
        "tool_family_correct": tool_correct,
        "results": results,
    }
