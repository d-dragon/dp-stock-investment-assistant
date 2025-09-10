"""
Data Manager for handling stock data and financial APIs.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import yfinance as yf

from src.data.repositories.factory import RepositoryFactory
from src.data.services.stock_data_service import StockDataService


class DataManager:
    """Enhanced DataManager with database integration"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize DataManager with configuration
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get financial API configuration
        self.financial_apis = config.get('financial_apis', {})
        self.yahoo_enabled = self.financial_apis.get('yahoo_finance', {}).get('enabled', True)
        
        # Initialize database services
        self.stock_data_service = RepositoryFactory.create_stock_data_service(config)
        if not self.stock_data_service:
            self.logger.warning("Failed to initialize stock data service. Running in API-only mode.")
            
        self.logger.info("Data Manager initialized")
    
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get stock data for a given symbol with database caching.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Data period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            
        Returns:
            DataFrame with stock data or None if error
        """
        # First try to get data from the database
        if self.stock_data_service:
            db_data = self.stock_data_service.get_stock_price_history(
                symbol, 
                period=period, 
                interval=interval
            )
            
            if db_data and len(db_data) > 0:
                # Convert to pandas DataFrame
                df = pd.DataFrame(db_data)
                if not df.empty:
                    # Format columns to match yfinance output
                    if 'timestamp' in df.columns:
                        df.set_index('timestamp', inplace=True)
                    
                    # Rename columns to match yfinance convention if needed
                    column_mapping = {
                        'open': 'Open',
                        'high': 'High',
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume',
                        'adjusted_close': 'Adj Close'
                    }
                    df.rename(columns={k: v for k, v in column_mapping.items() 
                                     if k in df.columns}, inplace=True)
                    
                    return df
        
        # If database retrieval failed or returned no data, fall back to API
        if self.yahoo_enabled:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval=interval)
                
                # Store in database for future use if we have a service
                if not data.empty and self.stock_data_service:
                    # Convert to format expected by repository
                    data_points = []
                    for date, row in data.iterrows():
                        data_point = {
                            'symbol': symbol,
                            'timestamp': date.to_pydatetime(),
                            'open': float(row['Open']),
                            'high': float(row['High']),
                            'low': float(row['Low']),
                            'close': float(row['Close']),
                            'volume': int(row['Volume']),
                            'adjusted_close': float(row['Adj Close']) if 'Adj Close' in row else float(row['Close'])
                        }
                        data_points.append(data_point)
                    
                    # Store in database
                    self.stock_data_service.store_price_data_batch(symbol, data_points)
                    self.logger.info(f"Stored {len(data_points)} records for {symbol}")
                
                return data
            except Exception as e:
                self.logger.error(f"Error fetching stock data from API: {str(e)}")
        
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
