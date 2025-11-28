"""Analysis repository for managing stock analyses and research."""

from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError

from .mongodb_repository import MongoGenericRepository


class AnalysisRepository(MongoGenericRepository):
    """Repository for analyses collection."""
    
    def __init__(self, connection_string: str, database_name: str = "stock_assistant",
                 username: str = None, password: str = None, auth_source: str = None):
        """Initialize analysis repository."""
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            collection_name="analyses",
            username=username,
            password=password,
            auth_source=auth_source
        )
    
    def get_by_symbol(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get analyses for a specific symbol."""
        try:
            return self.get_all(
                {"symbol": symbol},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting analyses for symbol {symbol}: {e}")
            return []
    
    def get_by_analyst(self, analyst_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get analyses created by a specific analyst."""
        try:
            return self.get_all(
                {"analyst_id": analyst_id},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting analyses by analyst {analyst_id}: {e}")
            return []
    
    def get_by_type(self, analysis_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get analyses by type (fundamental, technical, quantitative, etc.)."""
        try:
            return self.get_all(
                {"analysis_type": analysis_type},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting analyses by type {analysis_type}: {e}")
            return []
    
    def get_by_workspace(self, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get analyses in a specific workspace."""
        try:
            return self.get_all(
                {"workspace_id": workspace_id},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting analyses for workspace {workspace_id}: {e}")
            return []
    
    def get_by_recommendation(self, recommendation: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get analyses by recommendation (buy, sell, hold)."""
        try:
            return self.get_all(
                {"recommendation": recommendation},
                limit=limit,
                sort=[("created_at", -1)]
            )
        except PyMongoError as e:
            self.logger.error(f"Error getting analyses by recommendation {recommendation}: {e}")
            return []
    
    def get_latest_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the most recent analysis for a symbol."""
        try:
            result = self.get_all(
                {"symbol": symbol},
                limit=1,
                sort=[("created_at", -1)]
            )
            return result[0] if result else None
        except PyMongoError as e:
            self.logger.error(f"Error getting latest analysis for symbol {symbol}: {e}")
            return None
