"""
Fundamentals Fetcher Service
Fetches stock fundamentals using yfinance with caching
"""
import yfinance as yf
from typing import Dict, Optional
import logging
from .data_cache_manager import get_cache
from .demo_data import get_demo_stock, generate_demo_historical_data

logger = logging.getLogger(__name__)

class FundamentalsFetcher:
    def __init__(self, cache_ttl: int = 86400):  # 24 hours default
        self.cache = get_cache()
        self.cache_ttl = cache_ttl
    
    def get_fundamentals(self, symbol: str) -> Optional[Dict]:
        """
        Fetch fundamental data for a stock
        
        Args:
            symbol: Stock symbol (e.g., RELIANCE.NS)
            
        Returns:
            Dictionary with fundamental metrics or None if error
        """
        # Check cache first
        cache_key = f"fundamentals:{symbol}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Cache hit for fundamentals: {symbol}")
            return cached
        
        try:
            logger.info(f"Fetching fundamentals for {symbol}")
            ticker = yf.Ticker(symbol)
            
            # Use custom User-Agent to avoid blocking
            ticker.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            
            info = ticker.info
            
            # Check if we got valid data
            if not info or len(info) < 5:
                logger.warning(f"yfinance returned minimal data for {symbol}, trying historical approach")
                # Try to get data from history instead
                hist = ticker.history(period="5d")
                if hist.empty:
                    # If initial fetch fails and symbol doesn't have suffix, try adding .NS
                    if not symbol.endswith(('.NS', '.BO')):
                        retry_symbol = f"{symbol}.NS"
                        logger.info(f"Retrying with suffix: {retry_symbol}")
                        return self.get_fundamentals(retry_symbol)
                        
                    logger.warning(f"No real data available for {symbol}, falling back to demo data")
                    raise Exception("No data found")
                
                # Build fundamentals from historical data
                latest_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else latest_price
                
                fundamentals = {
                    "symbol": symbol,
                    "name": symbol.replace('.NS', '').replace('.BO', ''),
                    "sector": "N/A",
                    "industry": "N/A",
                    "cmp": round(latest_price, 2),
                    "previous_close": round(previous_price, 2),
                    "open": round(hist['Open'].iloc[-1], 2) if not hist.empty else 0,
                    "day_high": round(hist['High'].iloc[-1], 2) if not hist.empty else 0,
                    "day_low": round(hist['Low'].iloc[-1], 2) if not hist.empty else 0,
                    "volume": int(hist['Volume'].iloc[-1]) if not hist.empty else 0,
                    "market_cap": 0,
                    "pe_ratio": 0,
                    "forward_pe": 0,
                    "peg_ratio": 0,
                    "price_to_book": 0,
                    "dividend_yield": 0,
                    "eps": 0,
                    "beta": 0,
                    "52_week_high": round(hist['High'].max(), 2) if not hist.empty else 0,
                    "52_week_low": round(hist['Low'].min(), 2) if not hist.empty else 0,
                    "50_day_avg": 0,
                    "200_day_avg": 0,
                    "profit_margin": 0,
                    "operating_margin": 0,
                    "roe": 0,
                    "roa": 0,
                    "debt_to_equity": 0,
                    "current_ratio": 0,
                    "revenue": 0,
                    "revenue_growth": 0,
                    "earnings_growth": 0,
                    "recommendation": "none",
                    "target_price": 0,
                }
                
                fundamentals["change"] = round(latest_price - previous_price, 2)
                fundamentals["change_percent"] = round((fundamentals["change"] / previous_price) * 100, 2)
                
                logger.info(f"Built fundamentals from historical data for {symbol}")
                self.cache.set(cache_key, fundamentals, category="fundamentals", ttl=self.cache_ttl)
                return fundamentals
            
            # Extract key fundamentals
            fundamentals = {
                "symbol": symbol,
                "name": info.get("longName", symbol.replace('.NS', '').replace('.BO', '')),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "cmp": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "previous_close": info.get("previousClose", 0),
                "open": info.get("open", 0),
                "day_high": info.get("dayHigh", 0),
                "day_low": info.get("dayLow", 0),
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "forward_pe": info.get("forwardPE", 0),
                "peg_ratio": info.get("pegRatio", 0),
                "price_to_book": info.get("priceToBook", 0),
                "dividend_yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0,
                "eps": info.get("trailingEps", 0),
                "beta": info.get("beta", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "50_day_avg": info.get("fiftyDayAverage", 0),
                "200_day_avg": info.get("twoHundredDayAverage", 0),
                "profit_margin": info.get("profitMargins", 0) * 100 if info.get("profitMargins") else 0,
                "operating_margin": info.get("operatingMargins", 0) * 100 if info.get("operatingMargins") else 0,
                "roe": info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0,
                "roa": info.get("returnOnAssets", 0) * 100 if info.get("returnOnAssets") else 0,
                "debt_to_equity": info.get("debtToEquity", 0),
                "current_ratio": info.get("currentRatio", 0),
                "revenue": info.get("totalRevenue", 0),
                "revenue_growth": info.get("revenueGrowth", 0) * 100 if info.get("revenueGrowth") else 0,
                "earnings_growth": info.get("earningsGrowth", 0) * 100 if info.get("earningsGrowth") else 0,
                "recommendation": info.get("recommendationKey", "none"),
                "target_price": info.get("targetMeanPrice", 0),
            }
            
            # Calculate additional metrics
            if fundamentals["cmp"] and fundamentals["previous_close"]:
                fundamentals["change"] = fundamentals["cmp"] - fundamentals["previous_close"]
                fundamentals["change_percent"] = (fundamentals["change"] / fundamentals["previous_close"]) * 100
            else:
                fundamentals["change"] = 0
                fundamentals["change_percent"] = 0
            
            # Cache the result
            self.cache.set(cache_key, fundamentals, category="fundamentals", ttl=self.cache_ttl)
            
            return fundamentals
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {str(e)}")
            
            # Try demo data as fallback for ALL errors
            logger.warning(f"Falling back to generated/demo data for {symbol}")
            demo_data = get_demo_stock(symbol)
            if demo_data:
                # Cache demo data for short time to allow retry later
                self.cache.set(cache_key, demo_data, category="fundamentals", ttl=300)
                return demo_data
            
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """
        Fetch historical price data
        
        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Dictionary with historical data or None if error
        """
        cache_key = f"historical:{symbol}:{period}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Cache hit for historical data: {symbol}")
            return cached
        
        try:
            logger.info(f"Fetching historical data for {symbol}")
            ticker = yf.Ticker(symbol)
            
            # Use custom User-Agent
            ticker.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.warning(f"History empty for {symbol}")
                raise Exception("Empty history")
            
            # Convert to dictionary format
            historical_data = {
                "dates": hist.index.strftime('%Y-%m-%d').tolist(),
                "open": hist['Open'].tolist(),
                "high": hist['High'].tolist(),
                "low": hist['Low'].tolist(),
                "close": hist['Close'].tolist(),
                "volume": hist['Volume'].tolist(),
            }
            
            # Cache for shorter time (6 hours for historical data)
            self.cache.set(cache_key, historical_data, category="historical", ttl=21600)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            
            # Try demo data as fallback
            logger.warning(f"Falling back to generated demo historical data for {symbol}")
            demo_hist = generate_demo_historical_data(symbol)
            if demo_hist:
                # Cache demo data for shorter time
                self.cache.set(cache_key, demo_hist, category="historical", ttl=3600)
                return demo_hist
            
            return None
    
    def get_market_indices(self) -> Dict:
        """
        Fetch NIFTY 50 and SENSEX data
        
        Returns:
            Dictionary with index data
        """
        cache_key = "market:indices"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info("Cache hit for market indices")
            return cached
        
        indices_data = {}
        
        # NIFTY 50
        try:
            logger.info("Fetching NIFTY 50 data")
            nifty = yf.Ticker("^NSEI")
            nifty_hist = nifty.history(period="5d")
            
            if not nifty_hist.empty:
                latest_price = nifty_hist['Close'].iloc[-1]
                previous_price = nifty_hist['Close'].iloc[-2] if len(nifty_hist) > 1 else latest_price
                
                indices_data["nifty50"] = {
                    "name": "NIFTY 50",
                    "value": round(latest_price, 2),
                    "previous_close": round(previous_price, 2),
                    "change": round(latest_price - previous_price, 2),
                    "change_percent": round(((latest_price - previous_price) / previous_price) * 100, 2)
                }
                logger.info(f"NIFTY 50: {indices_data['nifty50']['value']}")
            else:
                # Fallback data
                indices_data["nifty50"] = {
                    "name": "NIFTY 50",
                    "value": 21731.40,
                    "previous_close": 21697.50,
                    "change": 33.90,
                    "change_percent": 0.16
                }
                logger.warning("Using fallback data for NIFTY 50 (market closed)")
        except Exception as e:
            logger.error(f"Error fetching NIFTY 50: {str(e)}")
            # Fallback data
            indices_data["nifty50"] = {
                "name": "NIFTY 50",
                "value": 21731.40,
                "previous_close": 21697.50,
                "change": 33.90,
                "change_percent": 0.16
            }
        
        # SENSEX
        try:
            logger.info("Fetching SENSEX data")
            sensex = yf.Ticker("^BSESN")
            sensex_hist = sensex.history(period="5d")
            
            if not sensex_hist.empty:
                latest_price = sensex_hist['Close'].iloc[-1]
                previous_price = sensex_hist['Close'].iloc[-2] if len(sensex_hist) > 1 else latest_price
                
                indices_data["sensex"] = {
                    "name": "SENSEX",
                    "value": round(latest_price, 2),
                    "previous_close": round(previous_price, 2),
                    "change": round(latest_price - previous_price, 2),
                    "change_percent": round(((latest_price - previous_price) / previous_price) * 100, 2)
                }
                logger.info(f"SENSEX: {indices_data['sensex']['value']}")
            else:
                # Fallback data
                indices_data["sensex"] = {
                    "name": "SENSEX",
                    "value": 71752.11,
                    "previous_close": 71657.71,
                    "change": 94.40,
                    "change_percent": 0.13
                }
                logger.warning("Using fallback data for SENSEX (market closed)")
        except Exception as e:
            logger.error(f"Error fetching SENSEX: {str(e)}")
            # Fallback data
            indices_data["sensex"] = {
                "name": "SENSEX",
                "value": 71752.11,
                "previous_close": 71657.71,
                "change": 94.40,
                "change_percent": 0.13
            }
        
        # Cache for 5 minutes
        self.cache.set(cache_key, indices_data, category="market", ttl=300)
        
        return indices_data


# Singleton instance
_fetcher = None

def get_fetcher() -> FundamentalsFetcher:
    """Get or create fundamentals fetcher instance"""
    global _fetcher
    if _fetcher is None:
        _fetcher = FundamentalsFetcher()
    return _fetcher
