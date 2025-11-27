"""
MongoDB schema management utilities for creating and updating collections.
"""

import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from .accounts_schema import ACCOUNTS_INDEXES, get_accounts_validation
from .analyses_schema import ANALYSES_INDEXES, get_analyses_validation
from .chats_schema import CHATS_INDEXES, get_chats_validation
from .groups_schema import GROUPS_INDEXES, get_groups_validation
from .investment_ideas_schema import (
    INVESTMENT_IDEAS_INDEXES,
    get_investment_ideas_validation
)
from .investment_reports_schema import (
    INVESTMENT_REPORTS_SCHEMA, INVESTMENT_REPORTS_INDEXES,
    get_investment_reports_validation
)
from .fundamental_analysis_schema import (
    FUNDAMENTAL_ANALYSIS_SCHEMA, FUNDAMENTAL_ANALYSIS_INDEXES,
    get_fundamental_analysis_validation
)
from .investment_styles_schema import (
    INVESTMENT_STYLES_INDEXES,
    get_investment_styles_validation
)
from .market_data_schema import (
    MARKET_DATA_SCHEMA, MARKET_DATA_INDEXES, 
    MARKET_DATA_TIMESERIES_OPTIONS, get_market_data_validation
)
from .market_snapshots_schema import (
    MARKET_SNAPSHOTS_INDEXES,
    get_market_snapshots_validation
)
from .news_events_schema import (
    NEWS_EVENTS_SCHEMA, NEWS_EVENTS_INDEXES,
    get_news_events_validation
)
from .notes_schema import NOTES_INDEXES, get_notes_validation
from .notifications_schema import (
    NOTIFICATIONS_INDEXES, get_notifications_validation
)
from .portfolios_schema import PORTFOLIOS_INDEXES, get_portfolios_validation
from .positions_schema import POSITIONS_INDEXES, get_positions_validation
from .reports_schema import REPORTS_INDEXES, get_reports_validation
from .rules_policies_schema import (
    RULES_POLICIES_INDEXES, get_rules_policies_validation
)
from .sessions_schema import SESSIONS_INDEXES, get_sessions_validation
from .strategies_schema import STRATEGIES_INDEXES, get_strategies_validation
from .symbols_schema import (
    SYMBOLS_INDEXES, get_symbols_validation
)
from .tasks_schema import TASKS_INDEXES, get_tasks_validation
from .technical_indicators_schema import (
    TECHNICAL_INDICATORS_INDEXES,
    get_technical_indicators_validation
)
from .trades_schema import TRADES_INDEXES, get_trades_validation
from .user_preferences_schema import (
    USER_PREFERENCES_SCHEMA, USER_PREFERENCES_INDEXES,
    get_user_preferences_validation
)
from .user_profiles_schema import (
    USER_PROFILES_INDEXES, get_user_profiles_validation
)
from .users_schema import USERS_INDEXES, get_users_validation
from .watchlists_schema import WATCHLISTS_INDEXES, get_watchlists_validation
from .workspaces_schema import WORKSPACES_INDEXES, get_workspaces_validation

logger = logging.getLogger(__name__)

class SchemaManager:
    """MongoDB schema manager for creating and updating collection schemas."""
    
    def __init__(self, connection_string, database_name="stock_assistant"):
        """Initialize with MongoDB connection details"""
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self._collection_cache = None
        import threading
        self._collection_cache_lock = threading.Lock()
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            return True
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def _get_collection_names(self, refresh=False):
        """Get and cache list of collection names (thread-safe)."""
        with self._collection_cache_lock:
            if self._collection_cache is not None and not refresh:
                return self._collection_cache
            try:
                result = self.db.command("listCollections")
                self._collection_cache = [doc["name"] for doc in result["cursor"]["firstBatch"]]
                return self._collection_cache
            except Exception as e:
                logger.warning(f"Could not list collections: {e}. Assuming collections exist.")
                return self._collection_cache or []

    def _setup_standard_collection(self, collection_name, validation_config, indexes):
        """Create collection, apply validation, and build indexes."""
        try:
            collection_names = self._get_collection_names()
            if collection_name not in collection_names:
                self.db.create_collection(collection_name)
                logger.info(f"Created {collection_name} collection")
                if self._collection_cache is not None:
                    self._collection_cache.append(collection_name)

            if validation_config:
                try:
                    self.db.command("collMod", collection_name, **validation_config)
                    logger.info(f"Applied schema validation to {collection_name} collection")
                except PyMongoError as e:
                    logger.warning(f"Failed to apply validation to {collection_name}: {str(e)}")

            if indexes:
                for index in indexes:
                    try:
                        self.db[collection_name].create_index(index["keys"], **index.get("options", {}))
                    except PyMongoError as e:
                        logger.warning(f"Failed to create index {index.get('options', {}).get('name')} on {collection_name}: {str(e)}")
            return True
        except PyMongoError as e:
            logger.error(f"Failed to setup {collection_name} collection: {str(e)}")
            return False
            
    def setup_all_collections(self):
        """Setup all collections with schemas and indexes"""
        if not self.connect():
            return False
            
        success = True
        success &= self.setup_groups_collection()
        success &= self.setup_users_collection()
        success &= self.setup_user_profiles_collection()
        success &= self.setup_accounts_collection()
        success &= self.setup_investment_styles_collection()
        success &= self.setup_strategies_collection()
        success &= self.setup_rules_policies_collection()
        success &= self.setup_workspaces_collection()
        success &= self.setup_sessions_collection()
        success &= self.setup_watchlists_collection()
        success &= self.setup_investment_ideas_collection()
        success &= self.setup_notes_collection()
        success &= self.setup_tasks_collection()
        success &= self.setup_analyses_collection()
        success &= self.setup_reports_collection()
        success &= self.setup_chats_collection()
        success &= self.setup_notifications_collection()
        success &= self.setup_portfolios_collection()
        success &= self.setup_positions_collection()
        success &= self.setup_trades_collection()
        success &= self.setup_technical_indicators_collection()
        success &= self.setup_market_snapshots_collection()
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
        return self._setup_standard_collection(
            "symbols", get_symbols_validation(), SYMBOLS_INDEXES
        )
            
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

    def setup_groups_collection(self):
        return self._setup_standard_collection(
            "groups", get_groups_validation(), GROUPS_INDEXES
        )

    def setup_users_collection(self):
        return self._setup_standard_collection(
            "users", get_users_validation(), USERS_INDEXES
        )

    def setup_user_profiles_collection(self):
        return self._setup_standard_collection(
            "user_profiles", get_user_profiles_validation(), USER_PROFILES_INDEXES
        )

    def setup_accounts_collection(self):
        return self._setup_standard_collection(
            "accounts", get_accounts_validation(), ACCOUNTS_INDEXES
        )

    def setup_investment_styles_collection(self):
        return self._setup_standard_collection(
            "investment_styles", get_investment_styles_validation(), INVESTMENT_STYLES_INDEXES
        )

    def setup_strategies_collection(self):
        return self._setup_standard_collection(
            "strategies", get_strategies_validation(), STRATEGIES_INDEXES
        )

    def setup_rules_policies_collection(self):
        return self._setup_standard_collection(
            "rules_policies", get_rules_policies_validation(), RULES_POLICIES_INDEXES
        )

    def setup_workspaces_collection(self):
        return self._setup_standard_collection(
            "workspaces", get_workspaces_validation(), WORKSPACES_INDEXES
        )

    def setup_sessions_collection(self):
        return self._setup_standard_collection(
            "sessions", get_sessions_validation(), SESSIONS_INDEXES
        )

    def setup_watchlists_collection(self):
        return self._setup_standard_collection(
            "watchlists", get_watchlists_validation(), WATCHLISTS_INDEXES
        )

    def setup_investment_ideas_collection(self):
        return self._setup_standard_collection(
            "investment_ideas",
            get_investment_ideas_validation(),
            INVESTMENT_IDEAS_INDEXES
        )

    def setup_notes_collection(self):
        return self._setup_standard_collection(
            "notes", get_notes_validation(), NOTES_INDEXES
        )

    def setup_tasks_collection(self):
        return self._setup_standard_collection(
            "tasks", get_tasks_validation(), TASKS_INDEXES
        )

    def setup_analyses_collection(self):
        return self._setup_standard_collection(
            "analyses", get_analyses_validation(), ANALYSES_INDEXES
        )

    def setup_chats_collection(self):
        return self._setup_standard_collection(
            "chats", get_chats_validation(), CHATS_INDEXES
        )

    def setup_notifications_collection(self):
        return self._setup_standard_collection(
            "notifications", get_notifications_validation(), NOTIFICATIONS_INDEXES
        )

    def setup_reports_collection(self):
        return self._setup_standard_collection(
            "reports", get_reports_validation(), REPORTS_INDEXES
        )

    def setup_portfolios_collection(self):
        return self._setup_standard_collection(
            "portfolios", get_portfolios_validation(), PORTFOLIOS_INDEXES
        )

    def setup_positions_collection(self):
        return self._setup_standard_collection(
            "positions", get_positions_validation(), POSITIONS_INDEXES
        )

    def setup_trades_collection(self):
        return self._setup_standard_collection(
            "trades", get_trades_validation(), TRADES_INDEXES
        )

    def setup_technical_indicators_collection(self):
        return self._setup_standard_collection(
            "technical_indicators",
            get_technical_indicators_validation(),
            TECHNICAL_INDICATORS_INDEXES
        )

    def setup_market_snapshots_collection(self):
        return self._setup_standard_collection(
            "market_snapshots",
            get_market_snapshots_validation(),
            MARKET_SNAPSHOTS_INDEXES
        )