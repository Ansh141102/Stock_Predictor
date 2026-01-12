"""
Demo Data for Stock Predictor
Used when yfinance is rate-limited or markets are closed
"""
import random
import numpy as np
from datetime import datetime, timedelta

# Keep some hardcoded ones for consistency in demos
DEMO_STOCKS = {
    "RELIANCE.NS": {
        "symbol": "RELIANCE.NS",
        "name": "Reliance Industries Limited",
        "sector": "Energy",
        "industry": "Oil & Gas Refining & Marketing",
        "cmp": 2450.75,
        "previous_close": 2438.50,
        "open": 2442.00,
        "day_high": 2458.90,
        "day_low": 2435.20,
        "volume": 8542000,
        "market_cap": 16580000000000,
        "pe_ratio": 24.35,
        "forward_pe": 22.10,
        "peg_ratio": 1.85,
        "price_to_book": 2.45,
        "dividend_yield": 0.35,
        "eps": 100.65,
        "beta": 1.12,
        "52_week_high": 2856.00,
        "52_week_low": 2220.30,
        "50_day_avg": 2520.45,
        "200_day_avg": 2485.30,
        "profit_margin": 8.45,
        "operating_margin": 12.30,
        "roe": 9.85,
        "roa": 5.20,
        "debt_to_equity": 45.20,
        "current_ratio": 1.15,
        "revenue": 8500000000000,
        "revenue_growth": 12.5,
        "earnings_growth": 15.2,
        "recommendation": "buy",
        "target_price": 2750.00,
        "change": 12.25,
        "change_percent": 0.50
    },
    "TCS.NS": {
        "symbol": "TCS.NS",
        "name": "Tata Consultancy Services Limited",
        "sector": "Technology",
        "industry": "Information Technology Services",
        "cmp": 3685.40,
        "previous_close": 3672.15,
        "open": 3675.00,
        "day_high": 3695.80,
        "day_low": 3668.50,
        "volume": 2145000,
        "market_cap": 13450000000000,
        "pe_ratio": 28.45,
        "forward_pe": 26.80,
        "peg_ratio": 2.15,
        "price_to_book": 11.25,
        "dividend_yield": 1.45,
        "eps": 129.50,
        "beta": 0.85,
        "52_week_high": 4045.00,
        "52_week_low": 3200.00,
        "50_day_avg": 3750.20,
        "200_day_avg": 3650.80,
        "profit_margin": 19.85,
        "operating_margin": 25.40,
        "roe": 45.20,
        "roa": 32.50,
        "debt_to_equity": 0.00,
        "current_ratio": 2.85,
        "revenue": 2250000000000,
        "revenue_growth": 8.5,
        "earnings_growth": 10.2,
        "recommendation": "hold",
        "target_price": 3850.00,
        "change": 13.25,
        "change_percent": 0.36
    },
    "HDFCBANK.NS": {
        "symbol": "HDFCBANK.NS",
        "name": "HDFC Bank Limited",
        "sector": "Financial Services",
        "industry": "Banks - Private Sector",
        "cmp": 1642.30,
        "previous_close": 1635.80,
        "open": 1638.00,
        "day_high": 1648.90,
        "day_low": 1632.50,
        "volume": 12450000,
        "market_cap": 12500000000000,
        "pe_ratio": 19.85,
        "forward_pe": 18.20,
        "peg_ratio": 1.65,
        "price_to_book": 2.95,
        "dividend_yield": 1.15,
        "eps": 82.75,
        "beta": 0.95,
        "52_week_high": 1795.00,
        "52_week_low": 1450.00,
        "50_day_avg": 1665.40,
        "200_day_avg": 1620.50,
        "profit_margin": 22.50,
        "operating_margin": 28.75,
        "roe": 16.85,
        "roa": 1.85,
        "debt_to_equity": 0.00,
        "current_ratio": 1.05,
        "revenue": 1850000000000,
        "revenue_growth": 14.8,
        "earnings_growth": 18.5,
        "recommendation": "buy",
        "target_price": 1850.00,
        "change": 6.50,
        "change_percent": 0.40
    }
}

def generate_dynamic_fundamental(symbol: str):
    """Generate consistent random fundamental data for a symbol"""
    # Seed based on symbol string to ensure same symbol gets same values
    seed_val = sum(ord(c) for c in symbol)
    random.seed(seed_val)
    
    # Base price between 100 and 5000
    base_price = random.uniform(100, 5000)
    change = random.uniform(-base_price*0.05, base_price*0.05)
    
    return {
        "symbol": symbol,
        "name": f"{symbol.split('.')[0]} Limited",
        "sector": random.choice(["Technology", "Finance", "Energy", "Healthcare", "Consumer Goods"]),
        "industry": "Diversified",
        "cmp": round(base_price, 2),
        "previous_close": round(base_price - change, 2),
        "open": round(base_price - change * 0.5, 2),
        "day_high": round(base_price * 1.02, 2),
        "day_low": round(base_price * 0.98, 2),
        "volume": random.randint(10000, 5000000),
        "market_cap": random.randint(1000, 50000) * 10000000,  # 1000-50000 Cr
        "pe_ratio": round(random.uniform(10, 80), 2),
        "forward_pe": round(random.uniform(10, 80) * 0.9, 2),
        "peg_ratio": round(random.uniform(0.5, 3.0), 2),
        "price_to_book": round(random.uniform(1, 15), 2),
        "dividend_yield": round(random.uniform(0, 5), 2),
        "eps": round(base_price / random.uniform(15, 30), 2),
        "beta": round(random.uniform(0.5, 1.8), 2),
        "52_week_high": round(base_price * 1.2, 2),
        "52_week_low": round(base_price * 0.8, 2),
        "50_day_avg": round(base_price * 0.95, 2),
        "200_day_avg": round(base_price * 0.9, 2),
        "profit_margin": round(random.uniform(5, 30), 2),
        "operating_margin": round(random.uniform(10, 40), 2),
        "roe": round(random.uniform(10, 30), 2),
        "roa": round(random.uniform(5, 15), 2),
        "debt_to_equity": round(random.uniform(0, 2), 2),
        "current_ratio": round(random.uniform(1, 4), 2),
        "revenue": random.randint(5000, 100000) * 10000000,
        "revenue_growth": round(random.uniform(0, 25), 1),
        "earnings_growth": round(random.uniform(0, 30), 1),
        "recommendation": random.choice(["buy", "hold", "sell"]),
        "target_price": round(base_price * 1.15, 2),
        "change": round(change, 2),
        "change_percent": round((change / (base_price - change)) * 100, 2)
    }

def get_demo_stock(symbol: str):
    """Get demo stock data"""
    if symbol in DEMO_STOCKS:
        return DEMO_STOCKS[symbol]
    
    # Generate dynamic data for unknown symbols
    return generate_dynamic_fundamental(symbol)

def get_all_demo_symbols():
    """Get list of all demo symbols"""
    return list(DEMO_STOCKS.keys())

def generate_demo_historical_data(symbol: str, days: int = 252):
    """Generate realistic historical data for demo stocks"""
    
    # First get fundamental info to base price on
    stock_data = get_demo_stock(symbol)
    if not stock_data:
        # Should not happen with new dynamic generator
        return None
    
    # Generate dates (trading days only - Mon-Fri)
    dates = []
    current_date = datetime.now()
    while len(dates) < days:
        current_date -= timedelta(days=1)
        # Skip weekends
        if current_date.weekday() < 5:  # 0-4 is Mon-Fri
            dates.append(current_date.strftime('%Y-%m-%d'))
    
    dates.reverse()  # Oldest to newest
    
    # Generate realistic price data with trend
    base_price = stock_data['cmp']
    prices = []
    
    # Create a realistic price movement
    np.random.seed(sum(ord(c) for c in symbol))  # Consistent random data for same symbol
    
    # Start price (backwards from current)
    # We want the LAST price to match base_price roughly
    
    # Generate random walk
    walk = np.random.normal(0, 0.015, days) # 1.5% daily volatility
    walk[0] = 0
    cumulative_returns = np.exp(np.cumsum(walk))
    
    # Adjust last value to match current price
    adjustment = base_price / cumulative_returns[-1]
    prices = cumulative_returns * adjustment
    
    prices = prices.tolist()
    
    # Generate OHLCV data
    historical_data = {
        "dates": dates,
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "volume": []
    }
    
    for i, close_price in enumerate(prices):
        # Generate realistic OHLC
        daily_range = close_price * 0.02  # 2% daily range
        
        # Randomize relationship within day
        r1 = np.random.uniform(-0.5, 0.5)
        r2 = np.random.uniform(0, 0.5)
        
        open_price = close_price * (1 + r1 * 0.01)
        high_price = max(open_price, close_price) * (1 + r2 * 0.01)
        low_price = min(open_price, close_price) * (1 - r2 * 0.01)
        
        historical_data["close"].append(round(close_price, 2))
        historical_data["open"].append(round(open_price, 2))
        historical_data["high"].append(round(high_price, 2))
        historical_data["low"].append(round(low_price, 2))
        
        # Generate volume (with some variation)
        base_volume = stock_data['volume']
        volume = int(base_volume * (0.7 + np.random.random() * 0.6))
        historical_data["volume"].append(volume)
    
    return historical_data
