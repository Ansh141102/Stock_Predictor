"""
News & Sentiment Engine
Fetches news and performs sentiment analysis
"""
import os
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .data_cache_manager import get_cache

logger = logging.getLogger(__name__)

class NewsSentimentEngine:
    def __init__(self, api_key: str, cache_ttl: int = 43200):  # 12 hours default
        self.api_key = api_key
        self.news_client = NewsApiClient(api_key=api_key) if api_key else None
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.cache = get_cache()
        self.cache_ttl = cache_ttl
    
    def get_market_news(self, limit: int = 10) -> List[Dict]:
        """
        Fetch general Indian stock market news
        
        Args:
            limit: Maximum number of articles
            
        Returns:
            List of news articles with sentiment
        """
        cache_key = "news:market:india"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info("Cache hit for market news")
            return cached[:limit]
        
        if not self.news_client:
            logger.warning("NewsAPI client not initialized")
            return []
        
        try:
            # Fetch news from specific Indian domains
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # List of reliable Indian financial news domains
            indian_domains = 'moneycontrol.com,economictimes.indiatimes.com,livemint.com,business-standard.com,financialexpress.com,ndtv.com'
            
            response = self.news_client.get_everything(
                q='(stock market OR NIFTY OR SENSEX) AND India',
                domains=indian_domains,
                language='en',
                sort_by='publishedAt',
                from_param=from_date,
                page_size=30
            )
            
            articles = response.get('articles', [])
            
            # Process and add sentiment
            processed_articles = []
            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)
            
            # Cache the results
            self.cache.set(cache_key, processed_articles, category="news", ttl=self.cache_ttl)
            
            return processed_articles[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching market news: {str(e)}")
            return []
    
    def get_company_news(self, company_name: str, symbol: str, limit: int = 5) -> List[Dict]:
        """
        Fetch company-specific news
        
        Args:
            company_name: Company name
            symbol: Stock symbol
            limit: Maximum number of articles
            
        Returns:
            List of news articles with sentiment
        """
        cache_key = f"news:company:{symbol}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Cache hit for company news: {symbol}")
            return cached[:limit]
        
        if not self.news_client:
            logger.warning("NewsAPI client not initialized")
            return []
        
        try:
            # Clean company name (remove Ltd, Limited, etc.)
            clean_name = company_name.replace(' Limited', '').replace(' Ltd', '').replace('.', '')
            
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            indian_domains = 'moneycontrol.com,economictimes.indiatimes.com,livemint.com,business-standard.com,financialexpress.com,ndtv.com'
            
            response = self.news_client.get_everything(
                q=f'"{clean_name}" AND (India OR stock OR share)',
                domains=indian_domains,
                language='en',
                sort_by='publishedAt',
                from_param=from_date,
                page_size=20
            )
            
            articles = response.get('articles', [])
            
            # Process and add sentiment
            processed_articles = []
            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)
            
            # Cache the results
            self.cache.set(cache_key, processed_articles, category="news", ttl=self.cache_ttl)
            
            return processed_articles[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching company news for {symbol}: {str(e)}")
            return []
    
    def _process_article(self, article: Dict) -> Optional[Dict]:
        """Process and analyze sentiment of a news article"""
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            
            if not title:
                return None
            
            # Combine title and description for sentiment analysis
            text = f"{title}. {description}" if description else title
            
            # Analyze sentiment
            sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
            
            # Determine sentiment label
            compound = sentiment_scores['compound']
            if compound >= 0.05:
                sentiment_label = "positive"
            elif compound <= -0.05:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            return {
                "title": title,
                "description": description or "No description available",
                "url": article.get('url', ''),
                "source": article.get('source', {}).get('name', 'Unknown'),
                "published_at": article.get('publishedAt', ''),
                "image_url": article.get('urlToImage', ''),
                "sentiment": {
                    "label": sentiment_label,
                    "compound": compound,
                    "positive": sentiment_scores['pos'],
                    "negative": sentiment_scores['neg'],
                    "neutral": sentiment_scores['neu']
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            return None
    
    def calculate_overall_sentiment(self, articles: List[Dict]) -> Dict:
        """
        Calculate overall sentiment from multiple articles
        
        Args:
            articles: List of processed articles
            
        Returns:
            Dictionary with overall sentiment metrics
        """
        if not articles:
            return {
                "label": "neutral",
                "score": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "confidence": 0
            }
        
        positive_count = sum(1 for a in articles if a['sentiment']['label'] == 'positive')
        negative_count = sum(1 for a in articles if a['sentiment']['label'] == 'negative')
        neutral_count = sum(1 for a in articles if a['sentiment']['label'] == 'neutral')
        
        # Calculate weighted average (recent news weighted more)
        total_score = 0
        total_weight = 0
        
        for i, article in enumerate(articles):
            # More recent articles get higher weight
            weight = len(articles) - i
            total_score += article['sentiment']['compound'] * weight
            total_weight += weight
        
        avg_score = total_score / total_weight if total_weight > 0 else 0
        
        # Determine overall label
        if avg_score >= 0.1:
            label = "positive"
        elif avg_score <= -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        # Calculate confidence based on consistency
        total_articles = len(articles)
        max_count = max(positive_count, negative_count, neutral_count)
        confidence = (max_count / total_articles) * 100 if total_articles > 0 else 0
        
        return {
            "label": label,
            "score": avg_score,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "confidence": confidence
        }


# Singleton instance
_engine = None

def get_news_engine(api_key: str = None) -> NewsSentimentEngine:
    """Get or create news sentiment engine instance"""
    global _engine
    if _engine is None:
        if api_key is None:
            api_key = os.getenv('NEWS_API_KEY')
        _engine = NewsSentimentEngine(api_key)
    return _engine
