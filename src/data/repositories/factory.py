# src/data/repositories/factory.py
from typing import Optional, Dict, Any
import os
from urllib.parse import urlparse

from .mongodb_repository import MongoDBStockDataRepository
from .redis_cache_repository import RedisCacheRepository
from ..services.stock_data_service import StockDataService
import logging

class RepositoryFactory:
    """Factory for creating repository instances"""
    
    @staticmethod
    def create_mongo_repository(
        config: Dict[str, Any]
    ) -> Optional[MongoDBStockDataRepository]:
        """Create a MongoDB repository from configuration.

        Looks under `database.mongodb` (primary) and falls back to legacy
        top-level `mongodb` keys if present.
        """
        logger = logging.getLogger(__name__)
        db_root = config.get('database', {}) if isinstance(config, dict) else {}
        mongo_config = db_root.get('mongodb', {}) or config.get('mongodb', {})

        connection_string = os.environ.get('MONGO_URI') or mongo_config.get('connection_string')
        if not connection_string:
            raise RuntimeError("MongoDB connection string not configured")
            

            # Add debugging logs
        logger.debug(f"MongoDB connection string: {connection_string}")


        parsed = urlparse(connection_string)
        if parsed.scheme not in ('mongodb', 'mongodb+srv'):
            raise ValueError("Invalid MongoDB URI scheme")

        database_name = mongo_config.get('database_name', 'stock_assistant')
        logger.debug(f"Database name: {database_name}")
        # Check if connection string has embedded credentials
        has_embedded_creds = parsed.username is not None and parsed.password is not None

        if has_embedded_creds:
            # Use connection string as-is
            repository = MongoDBStockDataRepository(connection_string, database_name)
        else:
            # Use separate credentials if provided
            username = mongo_config.get('username')
            password = mongo_config.get('password')
            auth_source = mongo_config.get('auth_source', database_name)
            repository = MongoDBStockDataRepository(
                connection_string,
                database_name,
                username,
                password,
                auth_source,
            )

        if repository.initialize():
            return repository
        return None
    
    @staticmethod
    def create_cache_repository(
        config: Dict[str, Any]
    ) -> Optional[RedisCacheRepository]:
        """Create a Redis cache repository from configuration.

        Looks under `database.redis` (primary) and falls back to legacy
        top-level `redis` keys if present.
        """
        db_root = config.get('database', {}) if isinstance(config, dict) else {}
        cache_config = db_root.get('redis', {}) or config.get('redis', {})

        if not cache_config.get('enabled', False):
            return None

        repository = RedisCacheRepository(
            host=cache_config.get('host', 'localhost'),
            port=cache_config.get('port', 6379),
            db=cache_config.get('db', 0),
            password=cache_config.get('password'),
            ssl=cache_config.get('ssl', False),
        )

        if repository.initialize():
            return repository
        return None
    
    @staticmethod
    def create_stock_data_service(
        config: Dict[str, Any]
    ) -> Optional[StockDataService]:
        """Create the stock data service with appropriate repositories"""
        mongo_repo = RepositoryFactory.create_mongo_repository(config)
        if not mongo_repo:
            return None
            
        cache_repo = RepositoryFactory.create_cache_repository(config)
        
        return StockDataService(mongo_repo, cache_repo)
