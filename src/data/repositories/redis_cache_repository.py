# src/data/repositories/cache_repository.py
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

import redis
from redis.exceptions import RedisError

class RedisCacheRepository:
    """Repository for Redis caching operations"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, 
                 password: Optional[str] = None, ssl: bool = False):
        """Initialize Redis connection"""
        self.connection_params = {
            "host": host,
            "port": port,
            "db": db,
            "decode_responses": True
        }
        
        if password:
            self.connection_params["password"] = password
            
        if ssl:
            self.connection_params["ssl"] = True
            self.connection_params["ssl_cert_reqs"] = None
            
        self.client = None
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """Initialize Redis connection"""
        try:
            self.client = redis.Redis(**self.connection_params)
            return self.health_check()
        except RedisError as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            return False
    
    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            return self.client.ping()
        except RedisError:
            return False
    
    # Stock price caching methods
    def cache_latest_price(self, symbol: str, price_data: Dict[str, Any], 
                           expire_seconds: int = 60) -> bool:
        """Cache the latest price data for a symbol"""
        try:
            key = f"stock:price:{symbol}"
            
            # Convert non-string values to strings
            string_data = {k: str(v) for k, v in price_data.items()}
            
            # Store as hash
            self.client.hset(key, mapping=string_data)
            
            # Set expiration
            if expire_seconds > 0:
                self.client.expire(key, expire_seconds)
                
            return True
        except RedisError as e:
            self.logger.error(f"Failed to cache latest price: {str(e)}")
            return False
    
    def get_cached_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached price data for a symbol"""
        try:
            key = f"stock:price:{symbol}"
            data = self.client.hgetall(key)
            
            if not data:
                return None
                
            # Convert numeric string values back to numbers
            for k, v in data.items():
                try:
                    if '.' in v:
                        data[k] = float(v)
                    else:
                        data[k] = int(v)
                except (ValueError, TypeError):
                    # Keep as string if not convertible
                    pass
                    
            return data
        except RedisError as e:
            self.logger.error(f"Failed to get cached price: {str(e)}")
            return None
    
    # Historical data caching
    def cache_price_history(self, symbol: str, period: str, 
                           price_history: List[Dict[str, Any]], 
                           expire_seconds: int = 3600) -> bool:
        """Cache historical price data as a serialized JSON string"""
        try:
            key = f"stock:history:{symbol}:{period}"
            
            # Serialize the data to JSON
            json_data = json.dumps(price_history)
            
            # Store as string
            self.client.set(key, json_data, ex=expire_seconds if expire_seconds > 0 else None)
            return True
        except (RedisError, TypeError) as e:
            self.logger.error(f"Failed to cache price history: {str(e)}")
            return False
    
    def get_cached_price_history(self, symbol: str, period: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached historical price data"""
        try:
            key = f"stock:history:{symbol}:{period}"
            data = self.client.get(key)
            
            if not data:
                return None
                
            # Deserialize JSON
            return json.loads(data)
        except (RedisError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get cached price history: {str(e)}")
            return None
    
    # Analysis data caching
    def cache_fundamental_analysis(self, symbol: str, analysis_data: Dict[str, Any],
                                  expire_seconds: int = 86400) -> bool:
        """Cache fundamental analysis data"""
        try:
            key = f"analysis:fundamental:{symbol}"
            
            # Serialize the data to JSON
            json_data = json.dumps(analysis_data)
            
            # Store as string
            self.client.set(key, json_data, ex=expire_seconds if expire_seconds > 0 else None)
            return True
        except (RedisError, TypeError) as e:
            self.logger.error(f"Failed to cache fundamental analysis: {str(e)}")
            return False
    
    def get_cached_fundamental_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached fundamental analysis data"""
        try:
            key = f"analysis:fundamental:{symbol}"
            data = self.client.get(key)
            
            if not data:
                return None
                
            # Deserialize JSON
            return json.loads(data)
        except (RedisError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get cached fundamental analysis: {str(e)}")
            return None

    # Report caching methods
    def cache_report(self, symbol: str, report_type: str, 
                    report_data: Dict[str, Any],
                    expire_seconds: int = 43200) -> bool:
        """Cache a report"""
        try:
            key = f"report:{symbol}:{report_type}"
            
            # Serialize the data to JSON
            json_data = json.dumps(report_data)
            
            # Store as string
            self.client.set(key, json_data, ex=expire_seconds if expire_seconds > 0 else None)
            return True
        except (RedisError, TypeError) as e:
            self.logger.error(f"Failed to cache report: {str(e)}")
            return False
    
    def get_cached_report(self, symbol: str, report_type: str) -> Optional[Dict[str, Any]]:
        """Get a cached report"""
        try:
            key = f"report:{symbol}:{report_type}"
            data = self.client.get(key)
            
            if not data:
                return None
                
            # Deserialize JSON
            return json.loads(data)
        except (RedisError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get cached report: {str(e)}")
            return None