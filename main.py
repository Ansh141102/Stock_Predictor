"""
FastAPI Main Application
Stock Predictor API - Root Level
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
from dotenv import load_dotenv

from fastapi.encoders import jsonable_encoder
import numpy as np
import math

from backend.services.symbol_registry import get_registry
from backend.services.fundamentals_fetcher import get_fetcher
from backend.services.technical_indicators import get_indicators
from backend.services.news_sentiment_engine import get_news_engine
from backend.services.prediction_engine import get_predictor
from backend.services.ai_summary_generator import get_summary_generator
from backend.services.data_cache_manager import get_cache

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Stock Price Predictor",
    description="Indian Stock Market Analysis & Prediction API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount static files if frontend directory exists
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    logger.info(f"Mounted static files from: {FRONTEND_DIR}")
else:
    logger.warning(f"Frontend directory not found: {FRONTEND_DIR}")

# Pydantic models
class SearchResponse(BaseModel):
    symbol: str
    name: str
    exchange: str

class StockAnalysisResponse(BaseModel):
    fundamentals: dict
    technical_indicators: dict
    news: list
    sentiment: dict
    prediction: dict
    ai_summary: dict

# Routes
@app.get("/")
async def root():
    """Serve the frontend"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "AI Stock Price Predictor API", "docs": "/docs"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    cache = get_cache()
    stats = cache.get_stats()
    
    return {
        "status": "healthy",
        "cache_stats": stats,
        "server": "127.0.0.1:5000"
    }

@app.get("/api/search", response_model=List[SearchResponse])
async def search_stocks(q: str = "", limit: int = 10):
    """
    Search for stocks by name or symbol
    
    Args:
        q: Search query
        limit: Maximum results
    """
    try:
        registry = get_registry()
        results = registry.search(q, limit)
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-summary")
async def get_market_summary():
    """
    Get market overview with NIFTY 50 and SENSEX
    """
    try:
        fetcher = get_fetcher()
        news_engine = get_news_engine()
        
        # Get indices data
        indices = fetcher.get_market_indices()
        
        # Get market news
        news = news_engine.get_market_news(limit=10)
        
        return {
            "indices": indices,
            "news": news
        }
    except Exception as e:
        logger.error(f"Market summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}")
async def get_stock_analysis(symbol: str):
    """
    Get complete stock analysis
    
    Args:
        symbol: Stock symbol (e.g., RELIANCE.NS)
    """
    try:
        logger.info(f"Analyzing stock: {symbol}")
        
        # Initialize services
        fetcher = get_fetcher()
        indicators_service = get_indicators()
        news_engine = get_news_engine()
        predictor = get_predictor()
        summary_generator = get_summary_generator()
        
        # Get fundamentals
        logger.info(f"Fetching fundamentals for {symbol}")
        fundamentals = fetcher.get_fundamentals(symbol)
        logger.info(f"Fundamentals result: {fundamentals is not None}")
        
        if not fundamentals:
            logger.error(f"Fundamentals returned None for {symbol}")
            raise HTTPException(status_code=404, detail=f"Stock not found: {symbol}. Try RELIANCE.NS, TCS.NS, or HDFCBANK.NS for demo data.")
        
        # Get historical data
        logger.info(f"Fetching historical data for {symbol}")
        historical_data = fetcher.get_historical_data(symbol, period="1y")
        logger.info(f"Historical data result: {historical_data is not None}")
        
        if not historical_data:
            logger.error(f"Historical data returned None for {symbol}")
            raise HTTPException(status_code=404, detail="Historical data not available")
        
        # Calculate technical indicators
        technical_indicators = indicators_service.calculate_all_indicators(historical_data)
        
        # Get news and sentiment
        company_news = news_engine.get_company_news(
            fundamentals['name'],
            symbol,
            limit=5
        )
        sentiment = news_engine.calculate_overall_sentiment(company_news)
        
        # Get price prediction
        prediction = predictor.get_prediction_with_backtest(
            historical_data,
            technical_indicators,
            days=7
        )
        
        # Generate AI summary
        ai_summary = summary_generator.generate_complete_summary(
            fundamentals,
            technical_indicators,
            sentiment,
            company_news,
            prediction
        )
        
        response_data = {
            "fundamentals": fundamentals,
            "historical_data": historical_data,
            "technical_indicators": technical_indicators,
            "news": company_news,
            "sentiment": sentiment,
            "prediction": prediction,
            "ai_summary": ai_summary
        }
        
        # Sanitize whole response to remove NaN/Inf values
        def sanitize_json(obj):
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
            if isinstance(obj, dict):
                return {k: sanitize_json(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize_json(i) for i in obj]
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.float64, np.float32)):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            return obj
            
        return sanitize_json(response_data)
         
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cache/clear")
async def clear_cache(category: Optional[str] = None):
    """
    Clear cache entries
    
    Args:
        category: Optional category to clear (fundamentals, news, etc.)
    """
    try:
        cache = get_cache()
        
        if category:
            cache.clear_category(category)
            return {"message": f"Cleared {category} cache"}
        else:
            deleted = cache.clear_expired()
            return {"message": f"Cleared {deleted} expired entries"}
            
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/symbols")
async def get_all_symbols():
    """Get all available stock symbols"""
    try:
        registry = get_registry()
        symbols = registry.get_all_symbols()
        return {"symbols": symbols}
    except Exception as e:
        logger.error(f"Symbols error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-demo/{symbol}")
async def test_demo_data(symbol: str):
    """Test endpoint to check if demo data is working"""
    from backend.services.demo_data import get_demo_stock, generate_demo_historical_data
    
    demo_fund = get_demo_stock(symbol)
    demo_hist = generate_demo_historical_data(symbol)
    
    return {
        "symbol": symbol,
        "has_fundamentals": demo_fund is not None,
        "has_historical": demo_hist is not None,
        "fundamentals_sample": demo_fund.get("name") if demo_fund else None,
        "historical_days": len(demo_hist["dates"]) if demo_hist else 0
    }

if __name__ == "__main__":
    import uvicorn
    
    # Fixed configuration for localhost:5000
    HOST = "127.0.0.1"
    PORT = 5000
    
    logger.info(f"Starting server on http://{HOST}:{PORT}")
    logger.info(f"API Documentation: http://{HOST}:{PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
