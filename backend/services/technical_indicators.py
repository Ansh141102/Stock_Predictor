"""
Technical Indicators Service
Calculates technical indicators for stock analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return [None] * len(prices)
        
        df = pd.DataFrame({'price': prices})
        sma = df['price'].rolling(window=period).mean()
        return sma.tolist()
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return [None] * len(prices)
        
        df = pd.DataFrame({'price': prices})
        ema = df['price'].ewm(span=period, adjust=False).mean()
        return ema.tolist()
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return [None] * len(prices)
        
        df = pd.DataFrame({'price': prices})
        delta = df['price'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.tolist()
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return {
                "macd": [None] * len(prices),
                "signal": [None] * len(prices),
                "histogram": [None] * len(prices)
            }
        
        df = pd.DataFrame({'price': prices})
        
        ema_fast = df['price'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['price'].ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return {
            "macd": macd.tolist(),
            "signal": signal_line.tolist(),
            "histogram": histogram.tolist()
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {
                "upper": [None] * len(prices),
                "middle": [None] * len(prices),
                "lower": [None] * len(prices)
            }
        
        df = pd.DataFrame({'price': prices})
        
        middle = df['price'].rolling(window=period).mean()
        std = df['price'].rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            "upper": upper.tolist(),
            "middle": middle.tolist(),
            "lower": lower.tolist()
        }
    
    @staticmethod
    def calculate_atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """Calculate Average True Range"""
        if len(high) < period + 1:
            return [None] * len(high)
        
        df = pd.DataFrame({
            'high': high,
            'low': low,
            'close': close
        })
        
        df['h-l'] = df['high'] - df['low']
        df['h-pc'] = abs(df['high'] - df['close'].shift(1))
        df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        
        df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        atr = df['tr'].rolling(window=period).mean()
        
        return atr.tolist()
    
    @staticmethod
    def calculate_stochastic(high: List[float], low: List[float], close: List[float], period: int = 14) -> Dict:
        """Calculate Stochastic Oscillator"""
        if len(high) < period:
            return {
                "k": [None] * len(high),
                "d": [None] * len(high)
            }
        
        df = pd.DataFrame({
            'high': high,
            'low': low,
            'close': close
        })
        
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=3).mean()
        
        return {
            "k": k.tolist(),
            "d": d.tolist()
        }
    
    @staticmethod
    def calculate_all_indicators(historical_data: Dict) -> Dict:
        """
        Calculate all technical indicators from historical data
        
        Args:
            historical_data: Dictionary with OHLCV data
            
        Returns:
            Dictionary with all calculated indicators
        """
        try:
            close_prices = historical_data['close']
            high_prices = historical_data['high']
            low_prices = historical_data['low']
            
            indicators = {
                "sma_20": TechnicalIndicators.calculate_sma(close_prices, 20),
                "sma_50": TechnicalIndicators.calculate_sma(close_prices, 50),
                "sma_200": TechnicalIndicators.calculate_sma(close_prices, 200),
                "ema_12": TechnicalIndicators.calculate_ema(close_prices, 12),
                "ema_26": TechnicalIndicators.calculate_ema(close_prices, 26),
                "rsi": TechnicalIndicators.calculate_rsi(close_prices, 14),
                "macd": TechnicalIndicators.calculate_macd(close_prices),
                "bollinger": TechnicalIndicators.calculate_bollinger_bands(close_prices),
                "atr": TechnicalIndicators.calculate_atr(high_prices, low_prices, close_prices),
                "stochastic": TechnicalIndicators.calculate_stochastic(high_prices, low_prices, close_prices)
            }
            
            # Get latest values for analysis
            latest = {
                "rsi_current": indicators["rsi"][-1] if indicators["rsi"][-1] is not None else 0,
                "macd_current": indicators["macd"]["macd"][-1] if indicators["macd"]["macd"][-1] is not None else 0,
                "macd_signal": indicators["macd"]["signal"][-1] if indicators["macd"]["signal"][-1] is not None else 0,
                "price_vs_sma20": ((close_prices[-1] / indicators["sma_20"][-1]) - 1) * 100 if indicators["sma_20"][-1] else 0,
                "price_vs_sma50": ((close_prices[-1] / indicators["sma_50"][-1]) - 1) * 100 if indicators["sma_50"][-1] else 0,
                "price_vs_sma200": ((close_prices[-1] / indicators["sma_200"][-1]) - 1) * 100 if indicators["sma_200"][-1] else 0,
            }
            
            indicators["latest"] = latest
            
            # Sanitize indicators (replace NaN with None)
            def sanitize_value(v):
                if isinstance(v, (float, np.float64, np.float32)):
                    if np.isnan(v) or np.isinf(v):
                        return None
                return v

            # Recursively sanitize dictionary
            def sanitize_dict(d):
                clean = {}
                for k, v in d.items():
                    if isinstance(v, dict):
                        clean[k] = sanitize_dict(v)
                    elif isinstance(v, list):
                        clean[k] = [sanitize_value(i) for i in v]
                    else:
                        clean[k] = sanitize_value(v)
                return clean

            indicators = sanitize_dict(indicators)
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            return {}


# Singleton instance
_indicators = None

def get_indicators() -> TechnicalIndicators:
    """Get or create technical indicators instance"""
    global _indicators
    if _indicators is None:
        _indicators = TechnicalIndicators()
    return _indicators
