"""
Stock Query Semantic Router

Routes stock-related queries to appropriate handlers using semantic similarity.
Uses semantic-router library with OpenAI embeddings (HuggingFace fallback).

Reference: backend-python.instructions.md § Model Factory and AI Clients
"""

import logging
from typing import Any, Dict, List, Mapping, Optional, Tuple

from semantic_router import Route, SemanticRouter
from semantic_router.encoders import DenseEncoder, HuggingFaceEncoder, OpenAIEncoder

from .routes import (
    ROUTE_UTTERANCES,
    RouteResult,
    StockQueryRoute,
    get_all_routes,
)

logger = logging.getLogger(__name__)


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
