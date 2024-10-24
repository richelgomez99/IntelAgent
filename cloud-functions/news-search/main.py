"""
Cloud Function: News Search
Fetches news articles from Google News RSS
Ported from AWS IntelAgent news_search Lambda
"""
from google.cloud import firestore
import feedparser
from datetime import datetime, timedelta
import logging
import hashlib
import json
import requests
from typing import Dict, List, Any

db = firestore.Client()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_google_news(query: str, days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Search Google News RSS feed
    Ported from AWS Lambda
    
    Args:
        query: Search query (company name)
        days_back: Number of days to look back
        
    Returns:
        List of article dictionaries
    """
    # Construct Google News RSS URL
    base_url = "https://news.google.com/rss/search"
    params = {
        'q': query,
        'hl': 'en',
        'gl': 'US',
        'ceid': 'US:en'
    }
    
    # Build URL
    query_string = '&'.join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
    url = f"{base_url}?{query_string}"
    
    # Parse RSS feed
    feed = feedparser.parse(url)
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    articles = []
    for entry in feed.entries[:50]:  # Limit to 50 entries
        # Parse publication date
        pub_date = None
        if hasattr(entry, 'published_parsed'):
            try:
                pub_date = datetime(*entry.published_parsed[:6])
            except (TypeError, ValueError):
                pub_date = datetime.utcnow()
        
        # Filter by date if possible
        if pub_date and pub_date >= cutoff_date:
            # Extract source
            source = extract_source(entry)
            
            # Extract sentiment
            sentiment = analyze_sentiment(entry.title + ' ' + entry.get('summary', ''))
            
            # Get full summary/description from feed
            full_summary = entry.get('summary', '')
            
            articles.append({
                'title': entry.get('title', 'N/A'),
                'source': source,
                'url': entry.get('link', ''),
                'published_date': pub_date.isoformat() if pub_date else datetime.utcnow().isoformat(),
                'snippet': full_summary[:300],  # Short preview
                'content': full_summary[:2000],  # Longer content for analysis
                'sentiment': sentiment
            })
    
    return articles


def extract_source(entry: Any) -> str:
    """
    Extract source name from RSS entry
    Same logic as AWS Lambda
    """
    if hasattr(entry, 'source'):
        return entry.source.get('title', 'Unknown')
    
    # Try to extract from title (Google News format: "Title - Source")
    title = entry.get('title', '')
    if ' - ' in title:
        return title.split(' - ')[-1]
    
    return 'Unknown'


def analyze_sentiment(text: str) -> str:
    """
    Simple keyword-based sentiment analysis
    Ported from AWS Lambda
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment: 'positive', 'negative', or 'neutral'
    """
    text_lower = text.lower()
    
    # Positive keywords
    positive_keywords = [
        'breakthrough', 'success', 'launch', 'achieve', 'win', 'milestone',
        'innovation', 'advance', 'partner', 'growth', 'funding', 'expand',
        'improve', 'excel', 'leader', 'award', 'celebrate'
    ]
    
    # Negative keywords
    negative_keywords = [
        'lawsuit', 'layoff', 'controversy', 'failure', 'decline', 'loss',
        'criticism', 'concern', 'issue', 'problem', 'challenge', 'threat',
        'investigate', 'violate', 'scandal', 'delay'
    ]
    
    positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'


def extract_news_insights(articles: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """
    Extract high-level insights from news data
    Same logic as AWS Lambda
    
    Args:
        articles: List of article dictionaries
        query: Search query
        
    Returns:
        Dictionary of insights
    """
    if not articles:
        return {
            'summary': f'No recent news found for {query}',
            'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0},
            'top_sources': []
        }
    
    # Count sentiments
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    for article in articles:
        sentiment = article.get('sentiment', 'neutral')
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
    
    # Count sources
    source_counts = {}
    for article in articles:
        source = article.get('source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Sort sources by count
    top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'summary': f'Found {len(articles)} recent articles about {query}',
        'sentiment_breakdown': sentiment_counts,
        'top_sources': [{'name': source, 'count': count} for source, count in top_sources]
    }


def news_search(request):
    """
    Cloud Function entry point
    HTTP-triggered function for news search
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response with news data
    """
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    # Parse request
    request_json = request.get_json(silent=True)
    query = request_json.get("company", "Anthropic") if request_json else "Anthropic"
    days_back = request_json.get("days_back", 7) if request_json else 7
    
    try:
        logger.info(f"Searching news for: {query}")
        
        # Search Google News
        articles = search_google_news(query, days_back)
        
        # Extract insights
        insights = extract_news_insights(articles, query)
        
        # Store in Firestore
        for article in articles:
            # Create unique ID from URL
            article_id = hashlib.md5(article['url'].encode()).hexdigest()
            
            article['company'] = query
            article['scraped_at'] = datetime.utcnow().isoformat()
            
            # Store in Firestore
            db.collection("news").document(article_id).set(article)
        
        return (json.dumps({
            'success': True,
            'query': query,
            'article_count': len(articles),
            'articles': articles[:20],  # Limit for response size
            'insights': insights,
            'timestamp': datetime.utcnow().isoformat()
        }), 200, headers)
        
    except Exception as e:
        logger.error(f"Error fetching news for {query}: {e}")
        return (json.dumps({
            'success': False,
            'error': str(e)
        }), 500, headers)


# For local testing
if __name__ == "__main__":
    class MockRequest:
        def __init__(self):
            self.method = 'POST'
            
        def get_json(self, silent=False):
            return {"company": "Anthropic", "days_back": 7}
    
    result = news_search(MockRequest())
    print(result[0])
