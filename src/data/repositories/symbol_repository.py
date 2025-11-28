"""Symbol repository for managing stock/instrument symbols."""

from typing import List, Optional, Dict, Any

from .mongodb_repository import MongoGenericRepository


class SymbolRepository(MongoGenericRepository):
    """Repository for symbols collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize symbol repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="symbols",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol by ticker."""
        try:
            return self.collection.find_one({"symbol": symbol})
        except Exception as e:
            self.logger.error(f"Error getting symbol {symbol}: {e}")
            return None
    
    def get_by_isin(self, isin: str) -> Optional[Dict[str, Any]]:
        """Get symbol by ISIN identifier."""
        try:
            return self.collection.find_one({"identifiers.isin": isin})
        except Exception as e:
            self.logger.error(f"Error getting symbol by ISIN {isin}: {e}")
            return None
    
    def get_by_exchange(self, exchange: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all symbols for a specific exchange."""
        try:
            return self.get_all({"listing.exchange": exchange}, limit=limit, sort=[("symbol", 1)])
        except Exception as e:
            self.logger.error(f"Error getting symbols by exchange {exchange}: {e}")
            return []
    
    def get_by_sector(self, sector: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get symbols by sector."""
        try:
            return self.get_all({"classification.sector": sector}, limit=limit, sort=[("symbol", 1)])
        except Exception as e:
            self.logger.error(f"Error getting symbols by sector {sector}: {e}")
            return []
    
    def get_by_asset_type(self, asset_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get symbols by asset type (equity, etf, etc.)."""
        try:
            return self.get_all({"asset_type": asset_type}, limit=limit, sort=[("symbol", 1)])
        except Exception as e:
            self.logger.error(f"Error getting symbols by asset_type {asset_type}: {e}")
            return []
    
    def get_tracked_symbols(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all actively tracked symbols."""
        try:
            query = {"coverage.is_tracked": True}
            return self.get_all(query, limit=limit, sort=[("symbol", 1)])
        except Exception as e:
            self.logger.error(f"Error getting tracked symbols: {e}")
            return []
    
    def search_by_name(self, name_pattern: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search symbols by name pattern (case-insensitive)."""
        try:
            query = {"name": {"$regex": name_pattern, "$options": "i"}}
            return self.get_all(query, limit=limit, sort=[("symbol", 1)])
        except Exception as e:
            self.logger.error(f"Error searching symbols by name: {e}")
            return []
    
    def get_by_tags(self, tags: List[str], match_all: bool = False, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get symbols by tags.
        
        Args:
            tags: List of tags to search for
            match_all: If True, symbol must have all tags; if False, any tag matches
            limit: Maximum number of results
        """
        try:
            if match_all:
                query = {"tags": {"$all": tags}}
            else:
                query = {"tags": {"$in": tags}}
            return self.get_all(query, limit=limit, sort=[("symbol", 1)])
        except Exception as e:
            self.logger.error(f"Error getting symbols by tags: {e}")
            return []
