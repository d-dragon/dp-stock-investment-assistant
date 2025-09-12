# src/data/repositories/base_repository.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

class BaseRepository(ABC):
    """Abstract base repository defining the interface for data operations"""
    
    @abstractmethod
    def initialize(self):
        """Initialize the repository (create collections, indexes, etc.)"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the repository is healthy and connected"""
        pass

class StockDataRepository(BaseRepository):
    """Repository interface for stock price data"""
    
    @abstractmethod
    def store_price_data(self, symbol: str, data: Dict[str, Any]) -> bool:
        """Store a single price data point"""
        pass
    
    @abstractmethod
    def store_price_data_batch(self, symbol: str, data: List[Dict[str, Any]]) -> bool:
        """Store multiple price data points in batch"""
        pass
    
    @abstractmethod
    def get_price_history(
        self, 
        symbol: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        interval: str = "1d",
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get historical price data for a symbol"""
        pass
    
    @abstractmethod
    def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the latest price for a symbol"""
        pass

class AnalysisRepository(BaseRepository):
    """Repository interface for analysis data"""
    
    @abstractmethod
    def store_fundamental_analysis(self, symbol: str, data: Dict[str, Any]) -> bool:
        """Store fundamental analysis for a symbol"""
        pass
    
    @abstractmethod
    def get_fundamental_analysis(
        self, 
        symbol: str,
        as_of_date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Get fundamental analysis for a symbol"""
        pass
    
    @abstractmethod
    def store_technical_analysis(
        self, 
        symbol: str, 
        indicators: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Store technical analysis indicators"""
        pass
    
    @abstractmethod
    def get_technical_analysis(
        self, 
        symbol: str,
        as_of_date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Get technical analysis indicators"""
        pass

class ReportRepository(BaseRepository):
    """Repository interface for investment reports"""
    
    @abstractmethod
    def store_report(
        self,
        symbol: str,
        report_type: str,
        report_data: Dict[str, Any]
    ) -> str:
        """Store an investment report and return its ID"""
        pass
    
    @abstractmethod
    def get_report(
        self,
        report_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a report by its ID"""
        pass
    
    @abstractmethod
    def get_latest_report(
        self,
        symbol: str,
        report_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get the latest report for a symbol and type"""
        pass