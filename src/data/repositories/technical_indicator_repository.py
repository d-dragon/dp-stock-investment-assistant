"""Technical indicator repository for managing calculated technical indicators."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class TechnicalIndicatorRepository(MongoGenericRepository):
    """Repository for technical_indicators collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize technical indicator repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="technical_indicators",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_symbol(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get technical indicators for a specific symbol."""
        try:
            return self.get_all(
                {"symbol": symbol},
                limit=limit,
                sort=[("calculated_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting indicators for symbol {symbol}: {e}")
            return []
    
    def get_by_indicator_type(self, indicator_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get indicators by type (sma, ema, rsi, macd, bollinger_bands, etc.)."""
        try:
            return self.get_all(
                {"indicator_type": indicator_type},
                limit=limit,
                sort=[("calculated_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting indicators by type {indicator_type}: {e}")
            return []
    
    def get_by_timeframe(self, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get indicators by timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)."""
        try:
            return self.get_all(
                {"timeframe": timeframe},
                limit=limit,
                sort=[("calculated_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting indicators by timeframe {timeframe}: {e}")
            return []
    
    def get_latest_by_symbol(self, symbol: str, indicator_type: str = None) -> Optional[Dict[str, Any]]:
        """Get the most recent indicator(s) for a symbol, optionally filtered by type."""
        try:
            query = {"symbol": symbol}
            if indicator_type:
                query["indicator_type"] = indicator_type
            
            result = self.get_all(
                query,
                limit=1,
                sort=[("calculated_at", -1)]
            )
            return result[0] if result else None
        except PyMongoError as e:
            self.logger.error(f"Error getting latest indicator for symbol {symbol}: {e}")
            return None
    
    def get_by_symbol_and_type(
        self, 
        symbol: str, 
        indicator_type: str, 
        timeframe: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get indicators for a symbol filtered by type and optionally timeframe."""
        try:
            query = {"symbol": symbol, "indicator_type": indicator_type}
            if timeframe:
                query["timeframe"] = timeframe
            
            return self.get_all(query, limit=limit, sort=[("calculated_at", -1)])
        except PyMongoError as e:
            self.logger.error(f"Error getting indicators for {symbol} type {indicator_type}: {e}")
            return []
