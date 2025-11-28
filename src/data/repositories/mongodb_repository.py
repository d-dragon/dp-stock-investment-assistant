# src/data/repositories/mongodb_repository.py
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, TypeVar, Generic
from copy import deepcopy

import pymongo
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection

from .base_repository import (
    BaseRepository,
    StockDataRepository,
    AnalysisRepository,
    ReportRepository
)

T = TypeVar('T')

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
        if not self.client:
            self.logger.warning("MongoDB client not initialized")
            return False
            
        try:
            # Simple ping to check connection
            self.client.admin.command('ping')
            return True
        except PyMongoError as e:
            self.logger.error(f"MongoDB health check failed: {str(e)}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            try:
                self.client.close()
                self.logger.info("MongoDB connection closed")
            except PyMongoError as e:
                self.logger.error(f"Error closing MongoDB connection: {str(e)}")
            finally:
                self.client = None
                self.db = None


class MongoGenericRepository(MongoDBRepository, Generic[T]):
    """
    Generic repository providing standard CRUD operations.
    Inherit from this for collection-specific repositories.
    """
    
    def __init__(self, connection_string: str, database_name: str, collection_name: str,
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize with collection name"""
        super().__init__(connection_string, database_name, username, password, auth_source)
        self.collection_name = collection_name
        self._collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        """
        Lazy load collection.
        
        Raises:
            RuntimeError: If database connection not initialized
        """
        if self._collection is None:
            if not self.client or not self.db:
                raise RuntimeError(
                    f"Database connection not initialized. Call initialize() first."
                )
            self._collection = self.db[self.collection_name]
        return self._collection
    
    @staticmethod
    def _validate_object_id(id: str) -> Optional[ObjectId]:
        """
        Validate and convert string to ObjectId.
        
        Args:
            id: String representation of ObjectId
            
        Returns:
            ObjectId if valid, None otherwise
        """
        try:
            return ObjectId(id)
        except (InvalidId, TypeError, ValueError):
            return None
    
    @staticmethod
    def _get_current_timestamp() -> datetime:
        """Get current UTC timestamp. Mockable for testing."""
        return datetime.utcnow()

    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.
        
        Args:
            id: String representation of document ObjectId
            
        Returns:
            Document dict if found, None otherwise
        """
        object_id = self._validate_object_id(id)
        if not object_id:
            self.logger.warning(f"Invalid ObjectId format: {id}")
            return None
            
        try:
            return self.collection.find_one({"_id": object_id})
        except PyMongoError as e:
            self.logger.error(f"Error getting {self.collection_name} by id {id}: {e}")
            return None

    def get_all(self, filter_query: Dict[str, Any] = None, 
                limit: int = 100, sort: List[tuple] = None) -> List[Dict[str, Any]]:
        """
        Get all documents matching filter.
        
        Args:
            filter_query: MongoDB query filter (default: {})
            limit: Maximum documents to return (default: 100)
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List of matching documents
        """
        try:
            query = filter_query or {}
            cursor = self.collection.find(query)
            
            if sort:
                cursor = cursor.sort(sort)
            
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except PyMongoError as e:
            self.logger.error(f"Error listing {self.collection_name}: {e}")
            return []

    def create(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new document.
        
        Args:
            data: Document data (will not be mutated)
            
        Returns:
            String ID of created document, None on failure
        """
        try:
            # Create a copy to avoid mutating input
            doc = deepcopy(data)
            
            # Add timestamps if not present
            now = self._get_current_timestamp()
            if "created_at" not in doc:
                doc["created_at"] = now
            if "updated_at" not in doc:
                doc["updated_at"] = now
            
            result = self.collection.insert_one(doc)
            return str(result.inserted_id)
        except PyMongoError as e:
            self.logger.error(f"Error creating {self.collection_name}: {e}")
            return None

    def update(self, id: str, data: Dict[str, Any]) -> bool:
        """
        Update document by ID.
        
        Args:
            id: String representation of document ObjectId
            data: Fields to update (will not be mutated)
            
        Returns:
            True if document was modified, False otherwise
        """
        object_id = self._validate_object_id(id)
        if not object_id:
            self.logger.warning(f"Invalid ObjectId format: {id}")
            return False
            
        try:
            # Create a copy to avoid mutating input
            update_data = deepcopy(data)
            
            # Always update the updated_at timestamp
            update_data["updated_at"] = self._get_current_timestamp()
            
            result = self.collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            self.logger.error(f"Error updating {self.collection_name} {id}: {e}")
            return False

    def delete(self, id: str) -> bool:
        """
        Delete document by ID.
        
        Args:
            id: String representation of document ObjectId
            
        Returns:
            True if document was deleted, False otherwise
        """
        object_id = self._validate_object_id(id)
        if not object_id:
            self.logger.warning(f"Invalid ObjectId format: {id}")
            return False
            
        try:
            result = self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            self.logger.error(f"Error deleting {self.collection_name} {id}: {e}")
            return False

    def count(self, filter_query: Dict[str, Any] = None) -> int:
        """
        Count documents matching filter.
        
        Args:
            filter_query: MongoDB query filter (default: {})
            
        Returns:
            Count of matching documents
        """
        try:
            query = filter_query or {}
            return self.collection.count_documents(query)
        except PyMongoError as e:
            self.logger.error(f"Error counting {self.collection_name}: {e}")
            return 0

    def exists(self, filter_query: Dict[str, Any]) -> bool:
        """
        Check if document exists matching filter.
        
        Args:
            filter_query: MongoDB query filter
            
        Returns:
            True if at least one matching document exists
        """
        try:
            return self.collection.find_one(filter_query, {"_id": 1}) is not None
        except PyMongoError as e:
            self.logger.error(f"Error checking existence in {self.collection_name}: {e}")
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
        """
        Store a single price data point in time series collection.
        
        Args:
            symbol: Stock symbol
            data: Price data (will not be mutated)
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Create a copy to avoid mutating input
            doc = deepcopy(data)
            
            # Ensure data has timestamp
            if "timestamp" not in doc:
                doc["timestamp"] = datetime.utcnow()
                
            # Add symbol if not present
            if "symbol" not in doc:
                doc["symbol"] = symbol
                
            self.db.market_data.insert_one(doc)
            return True
        except PyMongoError as e:
            self.logger.error(f"Failed to store price data for {symbol}: {str(e)}")
            return False
    
    def store_price_data_batch(self, symbol: str, data_points: List[Dict[str, Any]]) -> bool:
        """
        Store multiple price data points in batch.
        
        Args:
            symbol: Stock symbol
            data_points: List of price data dicts (will not be mutated)
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not data_points:
            self.logger.warning("Empty data_points list provided")
            return False
            
        try:
            # Create deep copies to avoid mutating input
            docs = []
            now = datetime.utcnow()
            
            for data in data_points:
                doc = deepcopy(data)
                if "symbol" not in doc:
                    doc["symbol"] = symbol
                if "timestamp" not in doc:
                    doc["timestamp"] = now
                docs.append(doc)
                    
            self.db.market_data.insert_many(docs)
            return True
        except PyMongoError as e:
            self.logger.error(f"Failed to store batch price data for {symbol}: {str(e)}")
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