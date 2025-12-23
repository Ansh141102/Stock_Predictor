# 🚀 AI Stock Price Predictor - Indian Stock Market

A production-grade AI-powered stock analysis and prediction platform for NSE & BSE listed companies, utilizing **free APIs** (yfinance, NewsAPI) and machine learning.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Key Features

- **Real-Time Data**: Live NSE/BSE stock data via `yfinance`.
- **AI Predictions**: 7-day price forecasting using Random Forest & Gradient Boosting.
- **Analysis**: Technical indicators (RSI, MACD), fundamentals, and sentiment analysis.
- **Smart Caching**: Efficient SQLite caching to handle API rate limits.
- **Modern UI**: Responsive Dark/Light mode interface.

## 🛠️ Installation & Run

1.  **Clone & Setup**:
    ```bash
    git clone https://github.com/Ansh141102/Stock_Predictor.git
    cd Stock_Predictor
    pip install -r requirements.txt
    ```

2.  **Run Application**:
    ```bash
    python main.py
    ```

3.  **Access**: Open `http://localhost:5000`

## 🏗️ Architecture Overview

- **Frontend**: Vanilla JS, Chart.js, HTML/CSS.
- **Backend**: FastAPI, Python.
- **ML Models**: Scikit-Learn (RandomForest, GradientBoosting).
- **Data**: yfinance (Prices), NewsAPI (News/Sentiment).

## ⚠️ Disclaimer

This application is for **informational purposes only** and does not constitute financial advice. Market investments are subject to risk.

---
*Built with ❤️ using FastAPI, yfinance, and ML.*
