"""Market snapshot repository for managing market-wide snapshots and indices."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class MarketSnapshotRepository(MongoGenericRepository):
    """Repository for market_snapshots collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize market snapshot repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="market_snapshots",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_market(self, market: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get snapshots for a specific market (US, EU, ASIA, etc.)."""
        try:
            return self.get_all(
                {"market": market},
                limit=limit,
                sort=[("snapshot_time", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting snapshots for market {market}: {e}")
            return []
    
    def get_by_index(self, index_symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get snapshots for a specific index (SPX, DJI, IXIC, etc.)."""
        try:
            return self.get_all(
                {"indices.symbol": index_symbol},
                limit=limit,
                sort=[("snapshot_time", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting snapshots for index {index_symbol}: {e}")
            return []
    
    def get_latest(self, market: str = None) -> Optional[Dict[str, Any]]:
        """Get the most recent market snapshot, optionally filtered by market."""
        try:
            query = {}
            if market:
                query["market"] = market
            
            result = self.get_all(query, limit=1, sort=[("snapshot_time", -1)])
            return result[0] if result else None
        except PyMongoError as e:
            self.logger.error(f"Error getting latest snapshot: {e}")
            return None
    
    def get_by_timeframe(self, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get snapshots by timeframe (1m, 5m, 15m, 1h, 1d)."""
        try:
            return self.get_all(
                {"timeframe": timeframe},
                limit=limit,
                sort=[("snapshot_time", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting snapshots by timeframe {timeframe}: {e}")
            return []
    
    def get_by_date_range(
        self, 
        start_time, 
        end_time, 
        market: str = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get snapshots within a date range, optionally filtered by market."""
        try:
            query = {
                "snapshot_time": {
                    "$gte": start_time,
                    "$lte": end_time
                }
            }
            if market:
                query["market"] = market
            
            return self.get_all(query, limit=limit, sort=[("snapshot_time", 1)])
        except PyMongoError as e:
            self.logger.error(f"Error getting snapshots by date range: {e}")
            return []
