"""
Technical analysis module for stock data.
"""

import pandas as pd
from typing import Dict, Any, Optional


class TechnicalAnalyzer:
    """Class for performing technical analysis on stock data."""
    
    def __init__(self):
        """Initialize the technical analyzer."""
        pass
    
    def calculate_moving_averages(self, data: pd.DataFrame, windows: list = [20, 50, 200]) -> pd.DataFrame:
        """Calculate moving averages for given windows.
        
        Args:
            data: Stock data DataFrame with 'Close' column
            windows: List of window sizes for moving averages
            
        Returns:
            DataFrame with moving averages added
        """
        result = data.copy()
        
        for window in windows:
            result[f'MA_{window}'] = result['Close'].rolling(window=window).mean()
        
        return result
    
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI).
        
        Args:
            data: Stock data DataFrame with 'Close' column
            window: Period for RSI calculation
            
        Returns:
            Series with RSI values
        """
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def analyze_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in stock data.
        
        Args:
            data: Stock data DataFrame
            
        Returns:
            Dictionary with trend analysis
        """
        if data.empty:
            return {}
        
        # Calculate basic trend indicators
        current_price = data['Close'].iloc[-1]
        ma_20 = data['Close'].rolling(20).mean().iloc[-1]
        ma_50 = data['Close'].rolling(50).mean().iloc[-1]
        
        # Determine trend
        if current_price > ma_20 > ma_50:
            trend = "Bullish"
        elif current_price < ma_20 < ma_50:
            trend = "Bearish"
        else:
            trend = "Sideways"
        
        return {
            'current_price': current_price,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'trend': trend,
            'price_change_pct': ((current_price - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
        }
