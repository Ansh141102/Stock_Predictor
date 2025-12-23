# 🚀 AI Stock Price Predictor - Indian Stock Market

A production-grade AI-powered stock analysis and prediction platform for NSE & BSE listed companies. This project utilizes **free APIs** with intelligent caching and scalable architecture to provide real-time insights, technical analysis, and machine learning-based price forecasting.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Copyright](https://img.shields.io/badge/Copyright-Ansh%20Srivastava%20%40%202025-orange)

## 🎯 Project Overview

This project demonstrates **real-world engineering trade-offs** and **production-ready design patterns** for building an AI stock analysis platform using only **free APIs** with intelligent caching and scalable architecture.

> [!IMPORTANT]
> **📅 Best Time to Use This App**
> 
> **For Live Data:** Monday - Friday, 9:15 AM - 3:30 PM IST (Market Hours)
> 
> **Why?** This app uses `yfinance` (free API) which works best during market hours. On weekends and after hours, Yahoo Finance may rate-limit requests or return stale data.

### Key Features

- ✅ **5000+ NSE & BSE Stocks** - Comprehensive coverage of Indian stock market
- ✅ **7-Day Price Prediction** - ML-based ensemble forecasting with confidence intervals and realistic volatility modeling
- ✅ **Technical Analysis** - RSI, MACD, Bollinger Bands, Moving Averages, Stochastic Oscillator
- ✅ **Fundamental Analysis** - P/E, ROE, Market Cap, Revenue Growth, Dividend Yield
- ✅ **News Sentiment** - AI-powered sentiment analysis using VADER on Indian financial news sources
- ✅ **Buy/Hold/Sell Verdict** - Explainable AI recommendations with confidence scores
- ✅ **Modern UI** - Premium dark/light mode with responsive design and interactive charts
- ✅ **Smart Caching** - SQLite-based cache with TTL management for high performance
- ✅ **Free APIs Only** - No paid subscriptions required

## 🧠 Why Free APIs? (Engineering Decision)

### APIs Used

1. **yfinance** (Free, No API Key Required)
   - Historical price data (OHLCV)
   - Company fundamentals
   - NSE & BSE indices (NIFTY 50, SENSEX)
   
2. **NewsAPI** (Free Tier: 100 requests/day)
   - Indian stock market news
   - Company-specific headlines
   - Sentiment analysis source

### Handling Rate Limits

**Problem**: Free APIs have strict rate limits and cannot support real-time updates for 5000+ stocks.

**Solution**: Intelligent caching and on-demand processing.

```
┌─────────────────────────────────────────────────────┐
│  Cache Strategy (SQLite)                            │
├─────────────────────────────────────────────────────┤
│  • Fundamentals: 24-hour TTL                        │
│  • News: 12-hour TTL                                │
│  • Historical Data: 6-hour TTL                      │
│  • Market Indices: 5-minute TTL                     │
│  • Predictions: On-demand (not cached)              │
└─────────────────────────────────────────────────────┘
```

**Key Design Principles**:
- ✅ **On-Demand Inference**: ML predictions only run when a user searches for a stock
- ✅ **Local Symbol Registry**: Pre-compiled list of 5000+ stocks (no API calls for discovery)
- ✅ **Graceful Degradation**: System continues working even if news API quota is exhausted

This approach is **intentional** and demonstrates production-grade engineering for resource-constrained environments.

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend (Vanilla JS)                │
│  • Modern UI with Chart.js                              │
│  • Dark/Light Mode                                       │
│  • Responsive Design                                     │
└────────────────┬─────────────────────────────────────────┘
                 │ REST API
┌────────────────┴─────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Services Layer                                    │  │
│  │  • Symbol Registry (Fuzzy Search)                  │  │
│  │  • Data Cache Manager (SQLite)                     │  │
│  │  • Fundamentals Fetcher (yfinance)                 │  │
│  │  • Technical Indicators (RSI, MACD, etc.)          │  │
│  │  • Prediction Engine (XGBoost + RandomForest)      │  │
│  │  • News Sentiment Engine (NewsAPI + VADER)         │  │
│  │  • AI Summary Generator (Buy/Hold/Sell)            │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────────────────┐
│              Data Layer                                  │
│  • SQLite Cache (cache.db)                              │
│  • Symbol Master List (symbols.json)                    │
│  • ML Models (joblib)                                   │
└──────────────────────────────────────────────────────────┘
```

## � Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ansh141102/Stock_Predictor.git
   cd Stock_Predictor
   ```

2. **Create virtual environment** (Recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

5. **Access the Application**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## 📊 API Endpoints

### Market Summary
```http
GET /api/market-summary
```
Returns NIFTY 50, SENSEX data, and market news.

### Search Stocks
```http
GET /api/search?q=reliance&limit=10
```
Fuzzy search for stocks by name or symbol.

### Stock Analysis
```http
GET /api/stock/RELIANCE.NS
```
Complete analysis including:
- Fundamentals
- Technical indicators
- News & sentiment
- 7-day price prediction
- AI verdict

### Cache Management
```http
POST /api/cache/clear?category=news
```
Clear cache by category or expired entries.

## 🤖 Machine Learning Model

### Ensemble Approach

The prediction engine uses an **ensemble of two models**:

1. **Random Forest Regressor** (100 estimators)
   - Handles non-linear patterns
   - Robust to outliers
   
2. **Gradient Boosting Regressor** (100 estimators)
   - Sequential error correction
   - High accuracy on time series

**Final Prediction** = Average of both models + Dynamic Drift/Volatility Integration

### Features Used

- Historical OHLCV data
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR)
- Price momentum (5-day, 10-day)
- Volatility measures
- Price change patterns

### Model Evaluation

Metrics displayed for transparency:
- **MAPE** (Mean Absolute Percentage Error)
- **R²** (Coefficient of Determination)
- **Confidence Intervals** (±5% approximation)

### ⚠️ Important Disclaimers

1. **Not Financial Advice**: Predictions are statistical estimates, not guarantees
2. **Back-tested Metrics**: Performance shown is historical, not future
3. **Market Risks**: Stock markets are inherently unpredictable
4. **Decision Support**: Use as one input among many, not sole decision maker

## 🎨 Frontend Design

### Design Philosophy

- **Premium Aesthetics**: Vibrant gradients, glassmorphism effects
- **Dark Mode**: Full dark/light theme support
- **Responsive**: Mobile-first design
- **Performance**: Vanilla JS for minimal overhead
- **Accessibility**: Semantic HTML, ARIA labels

### Color Palette

```css
Primary: #6366f1 (Indigo)
Secondary: #06b6d4 (Cyan)
Success: #10b981 (Green)
Danger: #ef4444 (Red)
Warning: #f59e0b (Amber)
```

## 📁 Project Structure

```
Stock_Predictor/
├── backend/
│   ├── services/
│   │   ├── symbol_registry.py
│   │   ├── data_cache_manager.py
│   │   ├── fundamentals_fetcher.py
│   │   ├── technical_indicators.py
│   │   ├── prediction_engine.py
│   │   ├── news_sentiment_engine.py
│   │   └── ai_summary_generator.py
│   ├── main.py
│   └── __init__.py
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── index.html
├── data/
│   ├── cache.db (auto-generated)
│   └── symbols.json (auto-generated)
├── models/ (auto-generated)
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 🧪 Testing

### Manual Testing Checklist

1. ✅ Search for "Reliance" - verify data loads
2. ✅ Check NIFTY 50 and SENSEX values
3. ✅ Verify 7-day prediction chart displays
4. ✅ Confirm AI verdict shows Buy/Hold/Sell
5. ✅ Test dark mode toggle
6. ✅ Verify news sentiment analysis
7. ✅ Check responsive design on mobile

### API Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Search
curl http://localhost:5000/api/search?q=tcs

# Stock analysis
curl http://localhost:5000/api/stock/TCS.NS
```

## 🔧 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install -r requirements.txt
```

**Issue**: NewsAPI quota exceeded
- The app will continue working with cached news
- Free tier resets daily (100 requests/day)

**Issue**: Stock not found
- Ensure symbol format is correct (e.g., `RELIANCE.NS` for NSE)
- Check if stock is in symbol registry

**Issue**: Prediction takes long time
- First prediction trains the model (30-60 seconds)
- Subsequent predictions are faster

## 🚀 Production Deployment

### Recommended Enhancements

1. **Database**: Migrate from SQLite to PostgreSQL
2. **Caching**: Add Redis for distributed caching
3. **Background Jobs**: Use Celery for scheduled cache warming
4. **API Gateway**: Add rate limiting and authentication
5. **Monitoring**: Integrate Prometheus + Grafana
6. **CDN**: Serve static assets via CDN

### Environment Variables

```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

## 📈 Future Enhancements

- [ ] Add more ML models (LSTM, Prophet)
- [ ] Portfolio tracking and management
- [ ] Real-time WebSocket updates
- [ ] Email/SMS alerts for price targets
- [ ] Backtesting simulator
- [ ] Social sentiment from Twitter/Reddit
- [ ] Options chain analysis

## 🤝 Contributing

This is a demonstration project. Feel free to fork and enhance!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

MIT License - Free to use for educational and commercial purposes.

---

<div align="center">
  <h3>Copyright © Ansh Srivastava @ 2025</h3>
  <p>All rights reserved.</p>
</div>
