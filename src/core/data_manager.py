"""
Data Manager for handling stock data and financial APIs.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import yfinance as yf


class DataManager:
    """Manages stock data retrieval and processing."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the data manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get financial API configuration
        self.financial_apis = config.get('financial_apis', {})
        self.yahoo_enabled = self.financial_apis.get('yahoo_finance', {}).get('enabled', True)
        
        self.logger.info("Data Manager initialized")
    
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get stock data for a given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Data period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            
        Returns:
            DataFrame with stock data or None if error
        """
        try:
            if not self.yahoo_enabled:
                self.logger.warning("Yahoo Finance API is disabled")
                return None
                
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                self.logger.warning(f"No data found for symbol: {symbol}")
                return None
                
            self.logger.info(f"Retrieved data for {symbol}: {len(data)} records")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get basic stock information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock info or None if error
        """
        try:
            if not self.yahoo_enabled:
                self.logger.warning("Yahoo Finance API is disabled")
                return None
                
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key information
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'current_price': info.get('currentPrice', 'N/A'),
                'previous_close': info.get('previousClose', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }
            
            self.logger.info(f"Retrieved info for {symbol}")
            return stock_info
            
        except Exception as e:
            self.logger.error(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Optional[pd.DataFrame]]:
        """Get data for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to their data
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_data(symbol)
        return results
