"""
AI Summary Generator
Generates natural language summaries and Buy/Hold/Sell verdicts
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class AISummaryGenerator:
    @staticmethod
    def generate_technical_summary(indicators: Dict, fundamentals: Dict) -> str:
        """Generate summary of technical analysis"""
        try:
            latest = indicators.get('latest', {})
            rsi = latest.get('rsi_current', 0)
            macd = latest.get('macd_current', 0)
            macd_signal = latest.get('macd_signal', 0)
            price_vs_sma20 = latest.get('price_vs_sma20', 0)
            price_vs_sma50 = latest.get('price_vs_sma50', 0)
            
            summary_parts = []
            
            # RSI Analysis
            if rsi > 70:
                summary_parts.append(f"RSI at {rsi:.1f} indicates overbought conditions, suggesting potential downward pressure.")
            elif rsi < 30:
                summary_parts.append(f"RSI at {rsi:.1f} indicates oversold conditions, suggesting potential upward reversal.")
            else:
                summary_parts.append(f"RSI at {rsi:.1f} is in neutral territory.")
            
            # MACD Analysis
            if macd > macd_signal:
                summary_parts.append("MACD shows bullish momentum with the line above signal.")
            else:
                summary_parts.append("MACD shows bearish momentum with the line below signal.")
            
            # Moving Average Analysis
            if price_vs_sma20 > 5:
                summary_parts.append(f"Price is {price_vs_sma20:.1f}% above 20-day SMA, showing strong upward trend.")
            elif price_vs_sma20 < -5:
                summary_parts.append(f"Price is {abs(price_vs_sma20):.1f}% below 20-day SMA, indicating weakness.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating technical summary: {str(e)}")
            return "Technical analysis unavailable."
    
    @staticmethod
    def generate_fundamental_summary(fundamentals: Dict) -> str:
        """Generate summary of fundamental analysis"""
        try:
            summary_parts = []
            
            pe_ratio = fundamentals.get('pe_ratio', 0)
            roe = fundamentals.get('roe', 0)
            debt_to_equity = fundamentals.get('debt_to_equity', 0)
            revenue_growth = fundamentals.get('revenue_growth', 0)
            
            # P/E Analysis
            if pe_ratio > 0:
                if pe_ratio < 15:
                    summary_parts.append(f"P/E ratio of {pe_ratio:.1f} suggests the stock may be undervalued.")
                elif pe_ratio > 30:
                    summary_parts.append(f"P/E ratio of {pe_ratio:.1f} indicates premium valuation.")
                else:
                    summary_parts.append(f"P/E ratio of {pe_ratio:.1f} is within reasonable range.")
            
            # ROE Analysis
            if roe > 15:
                summary_parts.append(f"Strong ROE of {roe:.1f}% indicates efficient use of equity.")
            elif roe > 0:
                summary_parts.append(f"ROE of {roe:.1f}% is moderate.")
            
            # Growth Analysis
            if revenue_growth > 15:
                summary_parts.append(f"Revenue growth of {revenue_growth:.1f}% shows strong business expansion.")
            elif revenue_growth < 0:
                summary_parts.append(f"Revenue declined by {abs(revenue_growth):.1f}%, which is concerning.")
            
            # Debt Analysis
            if debt_to_equity > 2:
                summary_parts.append(f"High debt-to-equity ratio of {debt_to_equity:.1f} indicates elevated financial risk.")
            elif debt_to_equity < 0.5:
                summary_parts.append("Low debt levels indicate strong financial health.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating fundamental summary: {str(e)}")
            return "Fundamental analysis unavailable."
    
    @staticmethod
    def generate_sentiment_summary(sentiment: Dict, news: List[Dict]) -> str:
        """Generate summary of news sentiment"""
        try:
            label = sentiment.get('label', 'neutral')
            score = sentiment.get('score', 0)
            positive_count = sentiment.get('positive_count', 0)
            negative_count = sentiment.get('negative_count', 0)
            
            summary_parts = []
            
            if label == 'positive':
                summary_parts.append(f"News sentiment is positive with {positive_count} favorable articles.")
            elif label == 'negative':
                summary_parts.append(f"News sentiment is negative with {negative_count} unfavorable articles.")
            else:
                summary_parts.append("News sentiment is neutral with mixed coverage.")
            
            # Mention key news if available
            if news and len(news) > 0:
                recent_news = news[0]
                summary_parts.append(f"Recent headline: '{recent_news.get('title', '')[:100]}...'")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating sentiment summary: {str(e)}")
            return "Sentiment analysis unavailable."
    
    @staticmethod
    def generate_prediction_summary(prediction: Dict) -> str:
        """Generate summary of price prediction"""
        try:
            trend = prediction.get('trend', 'neutral')
            change_percent = prediction.get('change_percent', 0)
            predictions = prediction.get('predictions', [])
            
            if not predictions:
                return "Price prediction unavailable."
            
            if trend == 'upward':
                return f"AI model predicts upward movement of approximately {change_percent:.1f}% over the next 7 days."
            else:
                return f"AI model predicts downward movement of approximately {abs(change_percent):.1f}% over the next 7 days."
            
        except Exception as e:
            logger.error(f"Error generating prediction summary: {str(e)}")
            return "Prediction unavailable."
    
    @staticmethod
    def generate_verdict(
        fundamentals: Dict,
        indicators: Dict,
        sentiment: Dict,
        prediction: Dict
    ) -> Dict:
        """
        Generate final Buy/Hold/Sell verdict with reasoning
        
        Args:
            fundamentals: Fundamental data
            indicators: Technical indicators
            sentiment: News sentiment
            prediction: Price prediction
            
        Returns:
            Dictionary with verdict and confidence
        """
        try:
            # Scoring system
            score = 0
            reasons = []
            
            # Technical Score (40%)
            latest = indicators.get('latest', {})
            rsi = latest.get('rsi_current', 50)
            macd = latest.get('macd_current', 0)
            macd_signal = latest.get('macd_signal', 0)
            price_vs_sma20 = latest.get('price_vs_sma20', 0)
            
            if rsi < 30:
                score += 15
                reasons.append("Oversold RSI suggests buying opportunity")
            elif rsi > 70:
                score -= 15
                reasons.append("Overbought RSI suggests caution")
            
            if macd > macd_signal:
                score += 10
                reasons.append("Bullish MACD crossover")
            else:
                score -= 10
                reasons.append("Bearish MACD signal")
            
            if price_vs_sma20 > 0:
                score += 15
                reasons.append("Price above 20-day moving average")
            else:
                score -= 15
                reasons.append("Price below 20-day moving average")
            
            # Fundamental Score (30%)
            pe_ratio = fundamentals.get('pe_ratio', 0)
            roe = fundamentals.get('roe', 0)
            revenue_growth = fundamentals.get('revenue_growth', 0)
            
            if 0 < pe_ratio < 20:
                score += 10
                reasons.append("Attractive valuation")
            elif pe_ratio > 40:
                score -= 10
                reasons.append("High valuation concerns")
            
            if roe > 15:
                score += 10
                reasons.append("Strong return on equity")
            
            if revenue_growth > 10:
                score += 10
                reasons.append("Strong revenue growth")
            elif revenue_growth < 0:
                score -= 10
                reasons.append("Declining revenues")
            
            # Sentiment Score (15%)
            sentiment_label = sentiment.get('label', 'neutral')
            if sentiment_label == 'positive':
                score += 15
                reasons.append("Positive news sentiment")
            elif sentiment_label == 'negative':
                score -= 15
                reasons.append("Negative news sentiment")
            
            # Prediction Score (15%)
            trend = prediction.get('trend', 'neutral')
            change_percent = prediction.get('change_percent', 0)
            
            if trend == 'upward' and change_percent > 5:
                score += 15
                reasons.append("AI predicts significant upside")
            elif trend == 'downward' and change_percent < -5:
                score -= 15
                reasons.append("AI predicts significant downside")
            
            # Determine verdict
            if score >= 40:
                verdict = "BUY"
                confidence = min(70 + (score - 40), 95)
            elif score <= -40:
                verdict = "SELL"
                confidence = min(70 + abs(score + 40), 95)
            else:
                verdict = "HOLD"
                confidence = 60 + abs(score) / 2
            
            return {
                "verdict": verdict,
                "confidence": round(confidence, 1),
                "score": score,
                "reasons": reasons[:5],  # Top 5 reasons
                "disclaimer": "This is an AI-generated recommendation based on historical data and should not be considered as financial advice. Please conduct your own research and consult with a financial advisor before making investment decisions."
            }
            
        except Exception as e:
            logger.error(f"Error generating verdict: {str(e)}")
            return {
                "verdict": "HOLD",
                "confidence": 0,
                "score": 0,
                "reasons": ["Unable to generate verdict due to insufficient data"],
                "disclaimer": "Analysis unavailable. Please consult a financial advisor."
            }
    
    @staticmethod
    def generate_complete_summary(
        fundamentals: Dict,
        indicators: Dict,
        sentiment: Dict,
        news: List[Dict],
        prediction: Dict
    ) -> Dict:
        """Generate complete AI summary with all components"""
        
        technical_summary = AISummaryGenerator.generate_technical_summary(indicators, fundamentals)
        fundamental_summary = AISummaryGenerator.generate_fundamental_summary(fundamentals)
        sentiment_summary = AISummaryGenerator.generate_sentiment_summary(sentiment, news)
        prediction_summary = AISummaryGenerator.generate_prediction_summary(prediction)
        verdict = AISummaryGenerator.generate_verdict(fundamentals, indicators, sentiment, prediction)
        
        return {
            "technical_summary": technical_summary,
            "fundamental_summary": fundamental_summary,
            "sentiment_summary": sentiment_summary,
            "prediction_summary": prediction_summary,
            "verdict": verdict
        }


# Singleton instance
_generator = None

def get_summary_generator() -> AISummaryGenerator:
    """Get or create summary generator instance"""
    global _generator
    if _generator is None:
        _generator = AISummaryGenerator()
    return _generator
