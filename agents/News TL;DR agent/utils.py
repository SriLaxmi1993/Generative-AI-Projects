"""
Utility functions and data models for News TL;DR Agent
"""

import re
from datetime import datetime
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class NewsApiParams(BaseModel):
    """Pydantic model for NewsAPI parameters"""
    q: str = Field(description="1-3 concise keyword search terms that are not too specific")
    sources: str = Field(
        description="comma-separated list of sources from: 'abc-news,abc-news-au,associated-press,australian-financial-review,axios,bbc-news,bbc-sport,bloomberg,business-insider,cbc-news,cbs-news,cnn,financial-post,fortune'"
    )
    from_param: str = Field(description="date in format 'YYYY-MM-DD' Two days ago minimum. Extend up to 30 days on second and subsequent requests.")
    to: str = Field(description="date in format 'YYYY-MM-DD' today's date unless specified")
    language: str = Field(description="language of articles 'en' unless specified one of ['ar', 'de', 'en', 'es', 'fr', 'he', 'it', 'nl', 'no', 'pt', 'ru', 'se', 'ud', 'zh']")
    sort_by: str = Field(description="sort by 'relevancy', 'popularity', or 'publishedAt'")
    
    class Config:
        # Allow 'from' as a field name by using 'from_param'
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "q": "artificial intelligence",
                "sources": "bbc-news,techcrunch",
                "from_param": "2024-01-01",
                "to": "2024-01-15",
                "language": "en",
                "sort_by": "relevancy"
            }
        }


def format_date(date: datetime = None) -> str:
    """
    Format a datetime object as YYYY-MM-DD string
    
    Args:
        date: Datetime object (defaults to today)
        
    Returns:
        str: Formatted date string
    """
    if date is None:
        date = datetime.now()
    return date.strftime("%Y-%m-%d")


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract URLs from text using regex pattern
    
    Args:
        text: Text containing URLs
        
    Returns:
        List[str]: List of extracted URLs
    """
    url_pattern = r'(https?://[^\s",]+)'
    urls = re.findall(url_pattern, text)
    return urls


def create_initial_state(
    news_query: str,
    num_searches_remaining: int = 10,
    num_articles_tldr: int = 3
) -> Dict[str, Any]:
    """
    Create initial state dictionary for the LangGraph workflow
    
    Args:
        news_query: User's news query
        num_searches_remaining: Number of search attempts remaining
        num_articles_tldr: Number of articles to create TL;DR for
        
    Returns:
        Dict: Initial state dictionary
    """
    return {
        "news_query": news_query,
        "num_searches_remaining": num_searches_remaining,
        "newsapi_params": {},
        "past_searches": [],
        "articles_metadata": [],
        "scraped_urls": [],
        "num_articles_tldr": num_articles_tldr,
        "potential_articles": [],
        "tldr_articles": [],
        "formatted_results": "No articles with text found."
    }


def format_article_metadata(articles: List[Dict]) -> str:
    """
    Format article metadata for LLM prompt
    
    Args:
        articles: List of article dictionaries with 'url' and 'description' keys
        
    Returns:
        str: Formatted string of article metadata
    """
    return "\n".join([f"{article['url']}\n{article['description']}\n" for article in articles])


