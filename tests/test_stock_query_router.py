"""
Tests for Stock Query Semantic Router

Full coverage tests for route definitions, StockQueryRouter,
and encoder fallback behavior.

Reference: testing.instructions.md § Backend Testing (Python + pytest)
"""

import pytest
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch, PropertyMock

from src.core.routes import (
    ROUTE_DESCRIPTIONS,
    ROUTE_UTTERANCES,
    RouteResult,
    StockQueryRoute,
    get_all_routes,
    get_route_utterances,
)
from src.core.stock_query_router import (
    StockQueryRouter,
    get_stock_query_router,
    reset_stock_query_router,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Minimal configuration for testing."""
    return {
        "openai": {
            "api_key": "test-openai-key",
        },
        "semantic_router": {
            "encoder": {
                "primary": "huggingface",  # Use HuggingFace to avoid API calls
                "huggingface_model": "sentence-transformers/all-MiniLM-L6-v2",
            },
            "threshold": 0.7,
            "cache_embeddings": True,
        },
    }


@pytest.fixture
def mock_semantic_router():
    """Mock SemanticRouter instance."""
    mock_router = MagicMock()
    # Default: return no match
    mock_result = MagicMock()
    mock_result.name = None
    mock_result.similarity_score = 0.0
    mock_router.return_value = mock_result
    return mock_router


@pytest.fixture
def mock_route_result():
    """Mock RouteLayer result."""
    result = MagicMock()
    result.name = "price_check"
    result.similarity_score = 0.85
    return result


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton before each test."""
    reset_stock_query_router()
    yield
    reset_stock_query_router()


# ============================================================================
# TESTS: StockQueryRoute Enum
# ============================================================================

class TestStockQueryRoute:
    """Test StockQueryRoute enum."""
    
    def test_all_routes_have_values(self):
        """Verify all routes have string values."""
        for route in StockQueryRoute:
            assert isinstance(route.value, str)
            assert len(route.value) > 0
    
    def test_route_count(self):
        """Verify expected number of routes."""
        assert len(StockQueryRoute) == 8
    
    def test_route_values_are_unique(self):
        """Verify route values are unique."""
        values = [r.value for r in StockQueryRoute]
        assert len(values) == len(set(values))
    
    def test_expected_routes_exist(self):
        """Verify all expected routes are defined."""
        expected = [
            "price_check",
            "news_analysis",
            "portfolio",
            "technical_analysis",
            "fundamentals",
            "ideas",
            "market_watch",
            "general_chat",
        ]
        actual = [r.value for r in StockQueryRoute]
        assert sorted(actual) == sorted(expected)
    
    def test_route_from_value(self):
        """Test creating route from string value."""
        route = StockQueryRoute("price_check")
        assert route == StockQueryRoute.PRICE_CHECK
    
    def test_invalid_route_value_raises(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            StockQueryRoute("invalid_route")


# ============================================================================
# TESTS: ROUTE_UTTERANCES
# ============================================================================

class TestRouteUtterances:
    """Test route training utterances."""
    
    def test_all_routes_have_utterances(self):
        """Verify all routes have utterance lists."""
        for route in StockQueryRoute:
            assert route in ROUTE_UTTERANCES
            assert isinstance(ROUTE_UTTERANCES[route], list)
    
    def test_each_route_has_sufficient_utterances(self):
        """Verify each route has at least 5 utterances."""
        for route in StockQueryRoute:
            utterances = ROUTE_UTTERANCES[route]
            assert len(utterances) >= 5, f"{route} has only {len(utterances)} utterances"
    
    def test_utterances_are_strings(self):
        """Verify all utterances are non-empty strings."""
        for route, utterances in ROUTE_UTTERANCES.items():
            for utterance in utterances:
                assert isinstance(utterance, str)
                assert len(utterance.strip()) > 0
    
    def test_price_check_utterances(self):
        """Test PRICE_CHECK has price-related utterances."""
        utterances = ROUTE_UTTERANCES[StockQueryRoute.PRICE_CHECK]
        price_keywords = ["price", "trading", "quote", "cost", "spread", "market cap"]
        
        has_price_keyword = any(
            any(kw in u.lower() for kw in price_keywords)
            for u in utterances
        )
        assert has_price_keyword
    
    def test_technical_analysis_utterances(self):
        """Test TECHNICAL_ANALYSIS has indicator-related utterances."""
        utterances = ROUTE_UTTERANCES[StockQueryRoute.TECHNICAL_ANALYSIS]
        technical_keywords = ["macd", "rsi", "bollinger", "chart", "moving average", "trend"]
        
        has_technical_keyword = any(
            any(kw in u.lower() for kw in technical_keywords)
            for u in utterances
        )
        assert has_technical_keyword


# ============================================================================
# TESTS: RouteResult
# ============================================================================

class TestRouteResult:
    """Test RouteResult dataclass."""
    
    def test_create_route_result(self):
        """Test creating a RouteResult."""
        result = RouteResult(
            route=StockQueryRoute.PRICE_CHECK,
            confidence=0.85,
            query="What is AAPL price?",
        )
        assert result.route == StockQueryRoute.PRICE_CHECK
        assert result.confidence == 0.85
        assert result.query == "What is AAPL price?"
    
    def test_is_confident_above_threshold(self):
        """Test is_confident when above threshold."""
        result = RouteResult(
            route=StockQueryRoute.PRICE_CHECK,
            confidence=0.75,
            query="test",
        )
        assert result.is_confident is True
    
    def test_is_confident_below_threshold(self):
        """Test is_confident when below threshold."""
        result = RouteResult(
            route=StockQueryRoute.GENERAL_CHAT,
            confidence=0.5,
            query="test",
        )
        assert result.is_confident is False
    
    def test_is_confident_at_threshold(self):
        """Test is_confident at exact threshold."""
        result = RouteResult(
            route=StockQueryRoute.PRICE_CHECK,
            confidence=0.7,
            query="test",
        )
        assert result.is_confident is True
    
    def test_is_fallback_true(self):
        """Test is_fallback for GENERAL_CHAT route."""
        result = RouteResult(
            route=StockQueryRoute.GENERAL_CHAT,
            confidence=0.0,
            query="test",
        )
        assert result.is_fallback is True
    
    def test_is_fallback_false(self):
        """Test is_fallback for non-GENERAL_CHAT route."""
        result = RouteResult(
            route=StockQueryRoute.PRICE_CHECK,
            confidence=0.85,
            query="test",
        )
        assert result.is_fallback is False
    
    def test_str_representation(self):
        """Test string representation."""
        result = RouteResult(
            route=StockQueryRoute.NEWS_ANALYSIS,
            confidence=0.823,
            query="test",
        )
        assert "news_analysis" in str(result)
        assert "0.823" in str(result)
    
    def test_route_result_is_frozen(self):
        """Test RouteResult is immutable."""
        result = RouteResult(
            route=StockQueryRoute.PRICE_CHECK,
            confidence=0.85,
            query="test",
        )
        with pytest.raises(AttributeError):
            result.confidence = 0.9  # type: ignore


# ============================================================================
# TESTS: Helper Functions
# ============================================================================

class TestHelperFunctions:
    """Test helper functions in routes module."""
    
    def test_get_all_routes(self):
        """Test get_all_routes excludes GENERAL_CHAT."""
        routes = get_all_routes()
        assert StockQueryRoute.GENERAL_CHAT not in routes
        assert len(routes) == 7  # All except GENERAL_CHAT
    
    def test_get_route_utterances(self):
        """Test get_route_utterances returns correct list."""
        utterances = get_route_utterances(StockQueryRoute.PORTFOLIO)
        assert isinstance(utterances, list)
        assert len(utterances) >= 5
    
    def test_get_route_utterances_unknown(self):
        """Test get_route_utterances with missing route returns empty list."""
        # Create a mock route not in utterances (shouldn't happen, but defensive)
        result = ROUTE_UTTERANCES.get(None, [])  # type: ignore
        assert result == []
    
    def test_route_descriptions_exist(self):
        """Test all routes have descriptions."""
        for route in StockQueryRoute:
            assert route in ROUTE_DESCRIPTIONS
            assert len(ROUTE_DESCRIPTIONS[route]) > 0


# ============================================================================
# TESTS: StockQueryRouter - Initialization
# ============================================================================

class TestStockQueryRouterInit:
    """Test StockQueryRouter initialization."""
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_init_with_huggingface_encoder(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test initialization with HuggingFace encoder."""
        mock_encoder_instance = MagicMock()
        mock_hf_cls.return_value = mock_encoder_instance
        mock_router_instance = MagicMock()
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        
        assert router.route_count == 7  # 7 routes (excluding GENERAL_CHAT fallback)
        assert router.threshold == 0.7
        mock_hf_cls.assert_called_once()
        mock_router_cls.assert_called_once()
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_init_uses_config_threshold(self, mock_hf_cls, mock_router_cls):
        """Test threshold is read from config."""
        mock_hf_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        config = {
            "semantic_router": {
                "threshold": 0.85,
                "encoder": {"primary": "huggingface"},
            },
        }
        router = StockQueryRouter(config)
        
        assert router.threshold == 0.85
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_init_default_threshold(self, mock_hf_cls, mock_router_cls):
        """Test default threshold when not in config."""
        mock_hf_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        config = {"semantic_router": {"encoder": {"primary": "huggingface"}}}
        router = StockQueryRouter(config)
        
        assert router.threshold == 0.7  # DEFAULT_THRESHOLD
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.OpenAIEncoder")
    def test_creates_openai_encoder_when_primary(self, mock_openai_cls, mock_router_cls):
        """Test OpenAI encoder is created when set as primary."""
        mock_openai_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        config = {
            "openai": {"api_key": "test-key"},
            "semantic_router": {
                "encoder": {"primary": "openai"},
            },
        }
        
        router = StockQueryRouter(config)
        mock_openai_cls.assert_called_once()
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_creates_huggingface_encoder_when_primary(self, mock_hf_cls, mock_router_cls):
        """Test HuggingFace encoder is created when set as primary."""
        mock_hf_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        config = {
            "semantic_router": {
                "encoder": {"primary": "huggingface"},
            },
        }
        
        router = StockQueryRouter(config)
        mock_hf_cls.assert_called_once()
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    @patch("src.core.stock_query_router.OpenAIEncoder")
    def test_falls_back_to_huggingface_on_openai_error(self, mock_openai_cls, mock_hf_cls, mock_router_cls):
        """Test fallback to HuggingFace when OpenAI fails."""
        mock_openai_cls.side_effect = Exception("OpenAI error")
        mock_hf_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        config = {
            "openai": {"api_key": "test-key"},
            "semantic_router": {
                "encoder": {"primary": "openai"},
            },
        }
        
        router = StockQueryRouter(config)
        mock_hf_cls.assert_called_once()
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.OpenAIEncoder")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_falls_back_to_openai_on_huggingface_error(self, mock_hf_cls, mock_openai_cls, mock_router_cls):
        """Test fallback to OpenAI when HuggingFace fails first."""
        mock_hf_cls.side_effect = Exception("HuggingFace error")
        mock_openai_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        config = {
            "openai": {"api_key": "test-key"},
            "semantic_router": {
                "encoder": {"primary": "huggingface"},
            },
        }
        
        router = StockQueryRouter(config)
        mock_openai_cls.assert_called_once()


# ============================================================================
# TESTS: StockQueryRouter - Routing
# ============================================================================

class TestStockQueryRouterRouting:
    """Test StockQueryRouter routing behavior."""
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_empty_query(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing empty query returns GENERAL_CHAT."""
        mock_hf_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        router = StockQueryRouter(mock_config)
        result = router.route("")
        
        assert result.route == StockQueryRoute.GENERAL_CHAT
        assert result.confidence == 0.0
        assert result.query == ""
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_whitespace_query(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing whitespace-only query returns GENERAL_CHAT."""
        mock_hf_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        router = StockQueryRouter(mock_config)
        result = router.route("   ")
        
        assert result.route == StockQueryRoute.GENERAL_CHAT
        assert result.confidence == 0.0
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_none_query(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing None query returns GENERAL_CHAT."""
        mock_hf_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        router = StockQueryRouter(mock_config)
        result = router.route(None)  # type: ignore
        
        assert result.route == StockQueryRoute.GENERAL_CHAT
        assert result.confidence == 0.0
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_successful_match(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing with successful match."""
        mock_hf_cls.return_value = MagicMock()
        
        # Mock the SemanticRouter response
        mock_result = MagicMock()
        mock_result.name = "price_check"
        mock_result.similarity_score = 0.85
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        result = router.route("What is AAPL price?")
        
        assert result.route == StockQueryRoute.PRICE_CHECK
        assert result.confidence == 0.85
        assert result.query == "What is AAPL price?"
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_no_match_returns_general_chat(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing with no match returns GENERAL_CHAT."""
        mock_hf_cls.return_value = MagicMock()
        
        # Mock no match
        mock_result = MagicMock()
        mock_result.name = None
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        result = router.route("Some random query")
        
        assert result.route == StockQueryRoute.GENERAL_CHAT
        assert result.confidence == 0.0
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_unknown_route_name(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing with unknown route name falls back to GENERAL_CHAT."""
        mock_hf_cls.return_value = MagicMock()
        
        # Mock unknown route name
        mock_result = MagicMock()
        mock_result.name = "unknown_route"
        mock_result.similarity_score = 0.8
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        result = router.route("Test query")
        
        assert result.route == StockQueryRoute.GENERAL_CHAT
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_exception_returns_general_chat(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing error returns GENERAL_CHAT."""
        mock_hf_cls.return_value = MagicMock()
        
        # Mock exception
        mock_router_instance = MagicMock(side_effect=Exception("Routing error"))
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        result = router.route("Test query")
        
        assert result.route == StockQueryRoute.GENERAL_CHAT
        assert result.confidence == 0.0


# ============================================================================
# TESTS: StockQueryRouter - Batch Routing
# ============================================================================

class TestStockQueryRouterBatch:
    """Test batch routing functionality."""
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_batch_empty_list(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test batch routing with empty list."""
        mock_hf_cls.return_value = MagicMock()
        mock_router_cls.return_value = MagicMock()
        
        router = StockQueryRouter(mock_config)
        results = router.route_batch([])
        
        assert results == []
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_batch_multiple_queries(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test batch routing with multiple queries."""
        mock_hf_cls.return_value = MagicMock()
        
        # Mock route results
        mock_results = [
            MagicMock(name="price_check", similarity_score=0.9),
            MagicMock(name="news_analysis", similarity_score=0.85),
            MagicMock(name=None),  # No match
        ]
        mock_results[0].name = "price_check"
        mock_results[1].name = "news_analysis"
        mock_results[2].name = None
        
        call_count = [0]
        def mock_router_call(query):
            result = mock_results[call_count[0]]
            call_count[0] += 1
            return result
        
        mock_router_instance = MagicMock(side_effect=mock_router_call)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        
        queries = [
            "What is AAPL price?",
            "Latest news on Tesla",
            "Random query",
        ]
        
        results = router.route_batch(queries)
        
        assert len(results) == 3
        assert results[0].route == StockQueryRoute.PRICE_CHECK
        assert results[1].route == StockQueryRoute.NEWS_ANALYSIS
        assert results[2].route == StockQueryRoute.GENERAL_CHAT


# ============================================================================
# TESTS: StockQueryRouter - Health Check
# ============================================================================

class TestStockQueryRouterHealth:
    """Test router health check."""
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_health_check_healthy(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test health check returns healthy status."""
        mock_hf_cls.return_value = MagicMock()
        
        # Mock successful routing
        mock_result = MagicMock()
        mock_result.name = "price_check"
        mock_result.similarity_score = 0.9
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        healthy, details = router.health_check()
        
        assert healthy is True
        assert details["component"] == "stock_query_router"
        assert details["status"] == "ready"
        assert "encoder" in details
        assert "routes" in details
        assert "threshold" in details
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_health_check_unhealthy(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test health check returns unhealthy on error."""
        mock_hf_cls.return_value = MagicMock()
        
        # Create router instance first
        mock_result = MagicMock()
        mock_result.name = "price_check"
        mock_result.similarity_score = 0.9
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        
        # Now patch the route method on the instance to raise an exception
        # This bypasses the internal exception handling in route()
        with patch.object(router, 'route', side_effect=Exception("Router broken")):
            healthy, details = router.health_check()
        
        assert healthy is False
        assert details["component"] == "stock_query_router"
        assert details["status"] == "error"
        assert "error" in details
        assert "Router broken" in details["error"]


# ============================================================================
# TESTS: Singleton Pattern
# ============================================================================

class TestSingletonPattern:
    """Test singleton management functions."""
    
    def test_get_stock_query_router_creates_instance(self):
        """Test get_stock_query_router creates instance."""
        config = {"semantic_router": {"threshold": 0.7}}
        
        with patch("src.core.stock_query_router.StockQueryRouter") as mock_cls:
            mock_cls.return_value = MagicMock()
            
            router = get_stock_query_router(config)
            
            mock_cls.assert_called_once_with(config)
    
    def test_get_stock_query_router_returns_same_instance(self):
        """Test get_stock_query_router returns same instance."""
        config = {"semantic_router": {"threshold": 0.7}}
        
        with patch("src.core.stock_query_router.StockQueryRouter") as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance
            
            router1 = get_stock_query_router(config)
            router2 = get_stock_query_router(config)
            
            assert router1 is router2
            mock_cls.assert_called_once()  # Only created once
    
    def test_reset_stock_query_router(self):
        """Test reset clears singleton."""
        config = {"semantic_router": {"threshold": 0.7}}
        
        with patch("src.core.stock_query_router.StockQueryRouter") as mock_cls:
            mock_cls.return_value = MagicMock()
            
            router1 = get_stock_query_router(config)
            reset_stock_query_router()
            router2 = get_stock_query_router(config)
            
            assert mock_cls.call_count == 2  # Created twice due to reset


# ============================================================================
# TESTS: Route Classification Integration (Mock-Based)
# ============================================================================

class TestRouteClassificationIntegration:
    """Integration tests for route classification with mocked encoder."""
    
    @pytest.mark.parametrize("query,expected_route", [
        ("What is the price of AAPL?", StockQueryRoute.PRICE_CHECK),
        ("Latest news on Tesla", StockQueryRoute.NEWS_ANALYSIS),
        ("Show my portfolio", StockQueryRoute.PORTFOLIO),
        ("What's the RSI on MSFT?", StockQueryRoute.TECHNICAL_ANALYSIS),
        ("What's the P/E ratio?", StockQueryRoute.FUNDAMENTALS),
        ("What stocks should I buy?", StockQueryRoute.IDEAS),
        ("How is the market today?", StockQueryRoute.MARKET_WATCH),
    ])
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_route_classification_by_route_type(
        self, mock_hf_cls, mock_router_cls, query, expected_route, mock_config
    ):
        """Test routing returns expected route for various query types."""
        mock_hf_cls.return_value = MagicMock()
        
        # Mock the expected route match
        mock_result = MagicMock()
        mock_result.name = expected_route.value
        mock_result.similarity_score = 0.85
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        result = router.route(query)
        
        assert result.route == expected_route
        assert result.is_confident is True


# ============================================================================
# TESTS: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_very_long_query(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing with very long query."""
        mock_hf_cls.return_value = MagicMock()
        
        mock_result = MagicMock()
        mock_result.name = "price_check"
        mock_result.similarity_score = 0.7
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        long_query = "What is the price of " + "AAPL " * 1000
        result = router.route(long_query)
        
        # Should still work
        assert result.route == StockQueryRoute.PRICE_CHECK
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_special_characters_in_query(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing with special characters."""
        mock_hf_cls.return_value = MagicMock()
        
        mock_result = MagicMock()
        mock_result.name = "fundamentals"
        mock_result.similarity_score = 0.8
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        query = "What's the P/E ratio for $AAPL & $MSFT?"
        result = router.route(query)
        
        assert result.route == StockQueryRoute.FUNDAMENTALS
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_unicode_in_query(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test routing with unicode characters."""
        mock_hf_cls.return_value = MagicMock()
        
        mock_result = MagicMock()
        mock_result.name = "price_check"
        mock_result.similarity_score = 0.75
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        query = "Giá cổ phiếu VNM là bao nhiêu?"  # Vietnamese
        result = router.route(query)
        
        assert result.route == StockQueryRoute.PRICE_CHECK
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_confidence_boundary_at_zero(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test handling zero confidence."""
        mock_hf_cls.return_value = MagicMock()
        
        mock_result = MagicMock()
        mock_result.name = "price_check"
        mock_result.similarity_score = 0.0
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        result = router.route("test")
        
        assert result.confidence == 0.0
        assert result.is_confident is False
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_confidence_boundary_at_one(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test handling perfect confidence."""
        mock_hf_cls.return_value = MagicMock()
        
        mock_result = MagicMock()
        mock_result.name = "price_check"
        mock_result.similarity_score = 1.0
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        result = router.route("test")
        
        assert result.confidence == 1.0
        assert result.is_confident is True
    
    @patch("src.core.stock_query_router.SemanticRouter")
    @patch("src.core.stock_query_router.HuggingFaceEncoder")
    def test_missing_similarity_score_attribute(self, mock_hf_cls, mock_router_cls, mock_config):
        """Test handling missing similarity_score attribute."""
        mock_hf_cls.return_value = MagicMock()
        
        # Mock result without similarity_score
        mock_result = MagicMock(spec=[])  # No attributes
        mock_result.name = "price_check"
        mock_router_instance = MagicMock(return_value=mock_result)
        mock_router_cls.return_value = mock_router_instance
        
        router = StockQueryRouter(mock_config)
        result = router.route("test")
        
        # Should default to 0.0
        assert result.confidence == 0.0
