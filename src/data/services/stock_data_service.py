# src/data/services/stock_data_service.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from ..repositories.mongodb_repository import MongoDBStockDataRepository
from ..repositories.redis_cache_repository import RedisCacheRepository

class StockDataService:
    """Service for coordinating stock data operations across repositories"""
    
    def __init__(
        self, 
        mongo_repository: MongoDBStockDataRepository,
        cache_repository: Optional[RedisCacheRepository] = None
    ):
        """Initialize with repositories"""
        self.mongo_repo = mongo_repository
        self.cache_repo = cache_repository
        self.logger = logging.getLogger(__name__)
        
    def get_stock_price_history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Get stock price history with caching"""
        # Convert period string to date range
        start_date, end_date = self._period_to_date_range(period)
        
        # Try to get from cache first if enabled
        if use_cache and self.cache_repo:
            cached_data = self.cache_repo.get_cached_price_history(symbol, period)
            if cached_data:
                self.logger.debug(f"Cache hit for {symbol} price history ({period})")
                return cached_data
                
        # Get from database
        data = self.mongo_repo.get_price_history(symbol, start_date, end_date)
        
        # Cache the result if we have a cache repository
        if data and self.cache_repo:
            self.cache_repo.cache_price_history(symbol, period, data)
            
        return data
    
    def get_latest_price(self, symbol: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Get the latest price with caching"""
        # Try to get from cache first if enabled
        if use_cache and self.cache_repo:
            cached_data = self.cache_repo.get_cached_price(symbol)
            if cached_data:
                self.logger.debug(f"Cache hit for {symbol} latest price")
                return cached_data
                
        # Get from database
        data = self.mongo_repo.get_latest_price(symbol)
        
        # Cache the result if we have a cache repository
        if data and self.cache_repo:
            self.cache_repo.cache_latest_price(symbol, data)
            
        return data
    
    def store_price_data(self, symbol: str, data: Dict[str, Any]) -> bool:
        """Store a single price data point and invalidate cache"""
        result = self.mongo_repo.store_price_data(symbol, data)
        
        # Update cache with latest data
        if result and self.cache_repo:
            self.cache_repo.cache_latest_price(symbol, data)
            
        return result
    
    def store_price_data_batch(self, symbol: str, data_points: List[Dict[str, Any]]) -> bool:
        """Store multiple price data points in batch and invalidate cache"""
        result = self.mongo_repo.store_price_data_batch(symbol, data_points)
        
        # Invalidate cached history since it's now outdated
        if result and self.cache_repo and data_points:
            # Find all common period keys that might be affected
            periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
            for period in periods:
                # Create an expiring key to prevent cache stampede
                self.cache_repo.client.set(
                    f"stock:history:{symbol}:{period}:updating",
                    "1",
                    ex=30  # Short expiry to prevent cache stampede
                )
                # Delete the actual cache key
                self.cache_repo.client.delete(f"stock:history:{symbol}:{period}")
                
            # Update latest price cache if we have data points
            if data_points:
                latest = max(data_points, key=lambda x: x.get("timestamp", datetime.min))
                self.cache_repo.cache_latest_price(symbol, latest)
                
        return result
    
    def _period_to_date_range(self, period: str) -> tuple:
        """Convert a period string to start and end dates"""
        end_date = datetime.utcnow()
        
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "5d":
            start_date = end_date - timedelta(days=5)
        elif period == "1mo":
            start_date = end_date - timedelta(days=30)
        elif period == "3mo":
            start_date = end_date - timedelta(days=90)
        elif period == "6mo":
            start_date = end_date - timedelta(days=180)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        elif period == "max":
            start_date = datetime(1900, 1, 1)  # Effectively no limit
        else:
            # Default to 1 year
            start_date = end_date - timedelta(days=365)
            
        return start_date, end_date