"""
Prediction Engine
ML-based stock price prediction using ensemble methods
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error, r2_score
import joblib
import os

logger = logging.getLogger(__name__)

class PredictionEngine:
    def __init__(self, model_path: str = "models"):
        self.model_path = model_path
        os.makedirs(model_path, exist_ok=True)
        self.scaler = StandardScaler()
        self.model = None
    
    def prepare_features(self, historical_data: Dict, indicators: Dict) -> pd.DataFrame:
        """
        Prepare feature matrix from historical data and indicators
        
        Args:
            historical_data: OHLCV data
            indicators: Technical indicators
            
        Returns:
            DataFrame with features
        """
        try:
            df = pd.DataFrame({
                'open': historical_data['open'],
                'high': historical_data['high'],
                'low': historical_data['low'],
                'close': historical_data['close'],
                'volume': historical_data['volume']
            })
            
            # Add technical indicators
            if 'sma_20' in indicators:
                df['sma_20'] = indicators['sma_20']
            if 'sma_50' in indicators:
                df['sma_50'] = indicators['sma_50']
            if 'ema_12' in indicators:
                df['ema_12'] = indicators['ema_12']
            if 'ema_26' in indicators:
                df['ema_26'] = indicators['ema_26']
            if 'rsi' in indicators:
                df['rsi'] = indicators['rsi']
            if 'macd' in indicators:
                df['macd'] = indicators['macd']['macd']
                df['macd_signal'] = indicators['macd']['signal']
            if 'bollinger' in indicators:
                df['bb_upper'] = indicators['bollinger']['upper']
                df['bb_lower'] = indicators['bollinger']['lower']
            if 'atr' in indicators:
                df['atr'] = indicators['atr']
            
            # Add price-based features
            df['price_change'] = df['close'].pct_change()
            df['high_low_range'] = (df['high'] - df['low']) / df['close']
            df['close_open_diff'] = (df['close'] - df['open']) / df['open']
            
            # Add momentum features
            df['momentum_5'] = df['close'].pct_change(periods=5)
            df['momentum_10'] = df['close'].pct_change(periods=10)
            
            # Add volatility
            df['volatility_5'] = df['close'].rolling(window=5).std()
            df['volatility_20'] = df['close'].rolling(window=20).std()
            
            # Drop NaN values
            df = df.bfill().ffill()
            
            return df
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            return pd.DataFrame()
    
    def train_model(self, features_df: pd.DataFrame, target_col: str = 'close') -> Dict:
        """
        Train ensemble model
        
        Args:
            features_df: Feature DataFrame
            target_col: Target column name
            
        Returns:
            Dictionary with training metrics
        """
        try:
            # Prepare data
            X = features_df.drop(columns=[target_col])
            y = features_df[target_col]
            
            # Create future target (next day's close)
            y_future = y.shift(-1)
            
            # Remove last row (no future target)
            X = X[:-1]
            y_future = y_future[:-1]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_future, test_size=0.2, shuffle=False
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train ensemble model
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            rf_model.fit(X_train_scaled, y_train)
            gb_model.fit(X_train_scaled, y_train)
            
            # Ensemble predictions
            rf_pred = rf_model.predict(X_test_scaled)
            gb_pred = gb_model.predict(X_test_scaled)
            ensemble_pred = (rf_pred + gb_pred) / 2
            
            # Calculate metrics
            mape = mean_absolute_percentage_error(y_test, ensemble_pred) * 100
            r2 = r2_score(y_test, ensemble_pred)
            
            # Store models
            self.model = {
                'rf': rf_model,
                'gb': gb_model,
                'scaler': self.scaler,
                'feature_names': X.columns.tolist()
            }
            
            return {
                'mape': mape,
                'r2': r2,
                'train_size': len(X_train),
                'test_size': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {}
    
    def predict_future(self, features_df: pd.DataFrame, days: int = 7) -> Dict:
        """
        Predict future stock prices
        
        Args:
            features_df: Feature DataFrame
            days: Number of days to predict
            
        Returns:
            Dictionary with predictions and confidence intervals
        """
        try:
            if self.model is None:
                # Train model if not already trained
                metrics = self.train_model(features_df)
                logger.info(f"Model trained with MAPE: {metrics.get('mape', 0):.2f}%")
            
            predictions = []
            confidence_lower = []
            confidence_upper = []
            
            # Get last known data
            last_features = features_df.iloc[-1:].drop(columns=['close'])
            last_price = features_df.iloc[-1]['close']
            
            # Calculate volatility from recent data
            recent_returns = features_df['close'].pct_change().tail(30)
            volatility = recent_returns.std()
            if pd.isna(volatility) or volatility == 0:
                volatility = 0.015  # Default 1.5% volatility

            # Get Model Prediction for next day to determine trend
            last_features = features_df.iloc[-1:].drop(columns=['close'])
            scaled_features = self.model['scaler'].transform(last_features)
            
            rf_pred = self.model['rf'].predict(scaled_features)[0]
            gb_pred = self.model['gb'].predict(scaled_features)[0]
            model_next_day = (rf_pred + gb_pred) / 2
            
            # Calculate drift based on model's prediction
            # We trust the model's direction for the immediate term
            drift = (model_next_day - last_price) / last_price
            
            # Dampen drift for longer term (mean reversion assumption)
            drift = np.clip(drift, -0.03, 0.03)
            
            current_price = last_price
            
            for day in range(days):
                # Apply random noise based on historical volatility
                # random.normal(loc=mean, scale=std)
                noise = np.random.normal(0, volatility)
                
                # Combine drift and noise
                # Day 1 is heavily weighted to model, subsequent days add noise
                move = drift + noise
                
                next_price = current_price * (1 + move)
                predictions.append(next_price)
                
                # Calculate confidence interval
                # Widens as we go further into future
                confidence_range = volatility * (day + 1) * 1.96  # ~95% CI approximation scaling with sqrt(time) roughly
                confidence_lower.append(next_price * (1 - confidence_range))
                confidence_upper.append(next_price * (1 + confidence_range))
                
                current_price = next_price
            
            # Calculate trend
            trend = "upward" if predictions[-1] > last_price else "downward"
            change_percent = ((predictions[-1] - last_price) / last_price) * 100
            
            return {
                'predictions': predictions,
                'confidence_lower': confidence_lower,
                'confidence_upper': confidence_upper,
                'trend': trend,
                'change_percent': change_percent,
                'last_price': last_price
            }
            
        except Exception as e:
            logger.error(f"Error predicting future: {str(e)}")
            return {}
    
    def get_prediction_with_backtest(self, historical_data: Dict, indicators: Dict, days: int = 7) -> Dict:
        """
        Get predictions with backtesting metrics
        
        Args:
            historical_data: OHLCV data
            indicators: Technical indicators
            days: Number of days to predict
            
        Returns:
            Dictionary with predictions and backtest metrics
        """
        try:
            # Prepare features
            features_df = self.prepare_features(historical_data, indicators)
            
            if features_df.empty:
                return {}
            
            # Train and get metrics
            metrics = self.train_model(features_df)
            
            # Get predictions
            predictions = self.predict_future(features_df, days)
            
            # Combine results
            result = {
                **predictions,
                'backtest_metrics': metrics
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in prediction with backtest: {str(e)}")
            return {}


# Singleton instance
_predictor = None

def get_predictor() -> PredictionEngine:
    """Get or create prediction engine instance"""
    global _predictor
    if _predictor is None:
        _predictor = PredictionEngine()
    return _predictor
