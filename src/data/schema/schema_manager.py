"""
MongoDB schema management utilities for creating and updating collections.
"""

import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from .market_data_schema import (
    MARKET_DATA_SCHEMA, MARKET_DATA_INDEXES, 
    MARKET_DATA_TIMESERIES_OPTIONS, get_market_data_validation
)
from .symbols_schema import (
    SYMBOLS_SCHEMA, SYMBOLS_INDEXES, get_symbols_validation
)
from .fundamental_analysis_schema import (
    FUNDAMENTAL_ANALYSIS_SCHEMA, FUNDAMENTAL_ANALYSIS_INDEXES,
    get_fundamental_analysis_validation
)
from .investment_reports_schema import (
    INVESTMENT_REPORTS_SCHEMA, INVESTMENT_REPORTS_INDEXES,
    get_investment_reports_validation
)
from .news_events_schema import (
    NEWS_EVENTS_SCHEMA, NEWS_EVENTS_INDEXES,
    get_news_events_validation
)
from .user_preferences_schema import (
    USER_PREFERENCES_SCHEMA, USER_PREFERENCES_INDEXES,
    get_user_preferences_validation
)

logger = logging.getLogger(__name__)

class SchemaManager:
    """MongoDB schema manager for creating and updating collection schemas."""
    
    def __init__(self, connection_string, database_name="stock_assistant"):
        """Initialize with MongoDB connection details"""
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            return True
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def _get_collection_names(self):
        """Get list of collection names using direct command to avoid authentication issues"""
        try:
            result = self.db.command("listCollections")
            return [doc["name"] for doc in result["cursor"]["firstBatch"]]
        except Exception as e:
            logger.warning(f"Could not list collections: {e}. Assuming collections exist.")
            return []  # Return empty list if we can't check
            
    def setup_all_collections(self):
        """Setup all collections with schemas and indexes"""
        if not self.connect():
            return False
            
        success = True
        success &= self.setup_market_data_collection()
        success &= self.setup_symbols_collection()
        success &= self.setup_fundamental_analysis_collection()
        success &= self.setup_investment_reports_collection()
        success &= self.setup_news_events_collection()
        success &= self.setup_user_preferences_collection()
        
        return success
        
    def setup_market_data_collection(self):
        """Create and configure the market_data time-series collection"""
        try:
            # Check if collection exists
            collection_names = self._get_collection_names()
            
            # Create time-series collection if it doesn't exist
            if "market_data" not in collection_names:
                self.db.create_collection(
                    "market_data",
                    timeseries=MARKET_DATA_TIMESERIES_OPTIONS
                )
                logger.info("Created market_data time-series collection")
                
                # Note: Time-series collections don't support schema validation
                # We'll apply validation after data insertion if needed
                logger.info("Note: Schema validation not applied to time-series collection")
            else:
                logger.info("market_data collection already exists")
                
            # Create indexes for time-series collection
            # Time-series collections support indexes on meta field and time field
            try:
                self.db.market_data.create_index([("symbol", 1), ("timestamp", 1)])
                logger.info("Created index on market_data collection")
            except PyMongoError as e:
                logger.warning(f"Failed to create index on market_data: {str(e)}")
                
            return True
        except PyMongoError as e:
            logger.error(f"Failed to setup market_data collection: {str(e)}")
            return False
            
    def setup_symbols_collection(self):
        """Create and configure the symbols collection"""
        try:
            # Create collection if it doesn't exist
            if "symbols" not in self._get_collection_names():
                self.db.create_collection("symbols")
                logger.info("Created symbols collection")
                
            # Apply validation schema
            try:
                self.db.command(
                    "collMod", 
                    "symbols",
                    **get_symbols_validation()
                )
                logger.info("Applied schema validation to symbols collection")
            except PyMongoError as e:
                logger.warning(f"Failed to apply validation to symbols: {str(e)}")
                
            # Create indexes with correct syntax
            try:
                # Unique index on symbol
                self.db.symbols.create_index([("symbol", 1)], unique=True, name="idx_symbol_unique")
                
                # Regular indexes
                self.db.symbols.create_index([("sector", 1)], name="idx_sector")
                self.db.symbols.create_index([("industry", 1)], name="idx_industry")
                self.db.symbols.create_index([("market_cap_category", 1)], name="idx_market_cap")
                
                logger.info("Created indexes on symbols collection")
            except PyMongoError as e:
                logger.warning(f"Failed to create indexes on symbols: {str(e)}")
                
            return True
        except PyMongoError as e:
            logger.error(f"Failed to setup symbols collection: {str(e)}")
            return False
            
    def setup_fundamental_analysis_collection(self):
        """Create and configure the fundamental_analysis collection"""
        try:
            # Create collection if it doesn't exist
            if "fundamental_analysis" not in self._get_collection_names():
                self.db.create_collection("fundamental_analysis")
                logger.info("Created fundamental_analysis collection")
                
            # Apply validation schema
            try:
                self.db.command(
                    "collMod", 
                    "fundamental_analysis",
                    **get_fundamental_analysis_validation()
                )
                logger.info("Applied schema validation to fundamental_analysis collection")
            except PyMongoError as e:
                logger.warning(f"Failed to apply validation to fundamental_analysis: {str(e)}")
                
            # Create indexes with correct syntax
            try:
                self.db.fundamental_analysis.create_index([("symbol", 1)], name="idx_symbol")
                self.db.fundamental_analysis.create_index([("symbol", 1), ("timestamp", -1)], name="idx_symbol_timestamp")
                self.db.fundamental_analysis.create_index([("financial_ratios.pe_ratio", 1)], name="idx_pe_ratio", sparse=True)
                
                logger.info("Created indexes on fundamental_analysis collection")
            except PyMongoError as e:
                logger.warning(f"Failed to create indexes on fundamental_analysis: {str(e)}")
                
            return True
        except PyMongoError as e:
            logger.error(f"Failed to setup fundamental_analysis collection: {str(e)}")
            return False
            
    def setup_investment_reports_collection(self):
        """Create and configure the investment_reports collection"""
        try:
            # Create collection if it doesn't exist
            if "investment_reports" not in self._get_collection_names():
                self.db.create_collection("investment_reports")
                logger.info("Created investment_reports collection")
                
            # Apply validation schema
            try:
                self.db.command(
                    "collMod", 
                    "investment_reports",
                    **get_investment_reports_validation()
                )
                logger.info("Applied schema validation to investment_reports collection")
            except PyMongoError as e:
                logger.warning(f"Failed to apply validation to investment_reports: {str(e)}")
                
            # Create indexes with correct syntax
            try:
                self.db.investment_reports.create_index([("symbol", 1)], name="idx_symbol")
                self.db.investment_reports.create_index([("symbol", 1), ("timestamp", -1)], name="idx_symbol_timestamp")
                self.db.investment_reports.create_index([("recommendation.action", 1)], name="idx_recommendation_action", sparse=True)
                self.db.investment_reports.create_index([("report_type", 1)], name="idx_report_type")
                
                logger.info("Created indexes on investment_reports collection")
            except PyMongoError as e:
                logger.warning(f"Failed to create indexes on investment_reports: {str(e)}")
                
            return True
        except PyMongoError as e:
            logger.error(f"Failed to setup investment_reports collection: {str(e)}")
            return False
            
    def setup_news_events_collection(self):
        """Create and configure the news_events collection"""
        try:
            # Create collection if it doesn't exist
            if "news_events" not in self._get_collection_names():
                self.db.create_collection("news_events")
                logger.info("Created news_events collection")
                
            # Apply validation schema
            try:
                self.db.command(
                    "collMod", 
                    "news_events",
                    **get_news_events_validation()
                )
                logger.info("Applied schema validation to news_events collection")
            except PyMongoError as e:
                logger.warning(f"Failed to apply validation to news_events: {str(e)}")
                
            # Create indexes with correct syntax
            try:
                self.db.news_events.create_index([("symbols", 1)], name="idx_symbols")
                self.db.news_events.create_index([("timestamp", -1)], name="idx_timestamp_desc")
                self.db.news_events.create_index([("event_type", 1)], name="idx_event_type")
                self.db.news_events.create_index([("symbols", 1), ("timestamp", -1)], name="idx_symbols_timestamp")
                
                logger.info("Created indexes on news_events collection")
            except PyMongoError as e:
                logger.warning(f"Failed to create indexes on news_events: {str(e)}")
                
            return True
        except PyMongoError as e:
            logger.error(f"Failed to setup news_events collection: {str(e)}")
            return False
            
    def setup_user_preferences_collection(self):
        """Create and configure the user_preferences collection"""
        try:
            # Create collection if it doesn't exist
            if "user_preferences" not in self._get_collection_names():
                self.db.create_collection("user_preferences")
                logger.info("Created user_preferences collection")
                
            # Apply validation schema
            try:
                self.db.command(
                    "collMod", 
                    "user_preferences",
                    **get_user_preferences_validation()
                )
                logger.info("Applied schema validation to user_preferences collection")
            except PyMongoError as e:
                logger.warning(f"Failed to apply validation to user_preferences: {str(e)}")
                
            # Create indexes with correct syntax
            try:
                self.db.user_preferences.create_index([("user_id", 1)], unique=True, name="idx_user_id_unique")
                
                logger.info("Created indexes on user_preferences collection")
            except PyMongoError as e:
                logger.warning(f"Failed to create indexes on user_preferences: {str(e)}")
                
            return True
        except PyMongoError as e:
            logger.error(f"Failed to setup user_preferences collection: {str(e)}")
            return False