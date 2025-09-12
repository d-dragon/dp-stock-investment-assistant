# src/data/repositories/mongodb_repository.py
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import pymongo
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from .base_repository import (
    BaseRepository,
    StockDataRepository,
    AnalysisRepository,
    ReportRepository
)

class MongoDBRepository(BaseRepository):
    """MongoDB implementation of the base repository"""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant", 
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize MongoDB connection"""
        self.connection_string = connection_string
        self.database_name = database_name
        self.username = username
        self.password = password
        self.auth_source = auth_source
        self.client = None
        self.db = None
        self.logger = logging.getLogger(__name__)
        
    def initialize(self):
        """Initialize MongoDB connection and set up collections/indexes"""
        try:
            # If separate credentials are provided, use them with a clean URI
            if self.username and self.password:
                # Parse connection string to extract host/port
                from urllib.parse import urlparse
                parsed = urlparse(self.connection_string)
                host_port = f"{parsed.hostname}:{parsed.port or 27017}"
                base_uri = f"mongodb://{host_port}"
                self.client = MongoClient(
                    base_uri,
                    username=self.username,
                    password=self.password,
                    authSource=self.auth_source or self.database_name
                )
            else:
                # Use connection string as-is (may have embedded credentials)
                self.client = MongoClient(self.connection_string)
                
            self.db = self.client[self.database_name]
            self.logger.info(f"Connected to MongoDB database: {self.database_name}")
            return True
        except PyMongoError as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
            
    def health_check(self) -> bool:
        """Check if MongoDB connection is healthy"""
        try:
            # Simple ping to check connection
            self.client.admin.command('ping')
            return True
        except PyMongoError:
            return False

class MongoDBStockDataRepository(MongoDBRepository, StockDataRepository):
    """MongoDB implementation for stock data operations"""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize with MongoDB connection"""
        super().__init__(connection_string, database_name, username, password, auth_source)
        
    def initialize(self):
        """Set up MongoDB connection and create time series collection if needed"""
        if not super().initialize():
            return False
            
        # Set up time series collection for market data if not exists
        try:
            # Try to list collections using command
            result = self.db.command("listCollections")
            collection_names = [doc["name"] for doc in result["cursor"]["firstBatch"]]
        except Exception as e:
            self.logger.warning(f"Could not list collections: {e}. Assuming market_data exists.")
            collection_names = ["market_data"]  # Assume it exists if we can't check
        
        if "market_data" not in collection_names:
            try:
                self.db.create_collection(
                    "market_data", 
                    timeseries={
                        "timeField": "timestamp",
                        "metaField": "symbol",
                        "granularity": "minutes"
                    }
                )
                self.db.market_data.create_index([("symbol", pymongo.ASCENDING), ("timestamp", pymongo.ASCENDING)])
                self.logger.info("Created market_data time series collection")
            except PyMongoError as e:
                self.logger.error(f"Failed to create time series collection: {str(e)}")
                return False
        return True
    
    def store_price_data(self, symbol: str, data: Dict[str, Any]) -> bool:
        """Store a single price data point in time series collection"""
        try:
            # Ensure data has timestamp
            if "timestamp" not in data:
                data["timestamp"] = datetime.utcnow()
                
            # Add symbol if not present
            if "symbol" not in data:
                data["symbol"] = symbol
                
            self.db.market_data.insert_one(data)
            return True
        except PyMongoError as e:
            self.logger.error(f"Failed to store price data: {str(e)}")
            return False
    
    def store_price_data_batch(self, symbol: str, data_points: List[Dict[str, Any]]) -> bool:
        """Store multiple price data points in batch"""
        if not data_points:
            return False
            
        try:
            # Ensure each data point has symbol and timestamp
            for data in data_points:
                if "symbol" not in data:
                    data["symbol"] = symbol
                if "timestamp" not in data:
                    data["timestamp"] = datetime.utcnow()
                    
            self.db.market_data.insert_many(data_points)
            return True
        except PyMongoError as e:
            self.logger.error(f"Failed to store batch price data: {str(e)}")
            return False
    
    def get_price_history(
        self, 
        symbol: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        interval: str = "1d",
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get historical price data for a symbol with optional date range"""
        query = {"symbol": symbol}
        
        # Add date range if provided
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        try:
            cursor = self.db.market_data.find(
                query,
                sort=[("timestamp", pymongo.ASCENDING)]
            )
            
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except PyMongoError as e:
            self.logger.error(f"Failed to retrieve price history: {str(e)}")
            return []
    
    def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the latest price for a symbol"""
        try:
            return self.db.market_data.find_one(
                {"symbol": symbol},
                sort=[("timestamp", pymongo.DESCENDING)]
            )
        except PyMongoError as e:
            self.logger.error(f"Failed to get latest price: {str(e)}")
            return None

# Additional implementation for AnalysisRepository and ReportRepository would follow similar patterns