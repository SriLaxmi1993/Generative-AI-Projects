"""
External API and utility functions for News TL;DR Agent
Handles NewsAPI calls and web scraping with BeautifulSoup
"""

import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from newsapi import NewsApiClient
import config

logger = logging.getLogger(__name__)


def fetch_article_metadata(newsapi_params: Dict) -> Dict:
    """
    Fetch article metadata from NewsAPI
    
    Args:
        newsapi_params: Dictionary of NewsAPI parameters
        
    Returns:
        Dict: NewsAPI response containing articles metadata
        
    Raises:
        Exception: If NewsAPI call fails
    """
    try:
        newsapi = config.initialize_newsapi()
        
        # Extract parameters - NewsAPI Python client uses 'from_param' to avoid Python keyword conflict
        q = newsapi_params.get('q', '')
        sources = newsapi_params.get('sources', '')
        from_date = newsapi_params.get('from_param', '')
        to_date = newsapi_params.get('to', '')
        language = newsapi_params.get('language', 'en')
        sort_by = newsapi_params.get('sort_by', 'relevancy')
        
        # Build parameters dict, only including non-empty values
        api_params = {}
        if q:
            api_params['q'] = q
        if sources:
            api_params['sources'] = sources
        if from_date:
            api_params['from_param'] = from_date  # NewsAPI uses 'from_param' to avoid Python keyword
        if to_date:
            api_params['to'] = to_date
        if language:
            api_params['language'] = language
        if sort_by:
            api_params['sort_by'] = sort_by
        
        logger.info(f"Fetching articles with params: {api_params}")
        articles = newsapi.get_everything(**api_params)
        
        logger.info(f"Retrieved {len(articles.get('articles', []))} articles from NewsAPI")
        return articles
        
    except Exception as e:
        logger.error(f"Error fetching articles from NewsAPI: {str(e)}")
        raise


def scrape_article_text(url: str) -> Optional[str]:
    """
    Scrape full article text from a URL using BeautifulSoup
    
    Args:
        url: URL of the article to scrape
        
    Returns:
        Optional[str]: Extracted article text, or None if scraping fails
    """
    try:
        # Add headers to simulate a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text = soup.get_text(strip=True)
            
            logger.info(f"Successfully scraped article from {url} ({len(text)} characters)")
            return text
        else:
            logger.warning(f"Failed to scrape {url}: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error scraping {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return None


def filter_new_articles(
    articles: List[Dict],
    scraped_urls: List[str],
    max_articles: int = 10
) -> List[Dict]:
    """
    Filter out articles that have already been scraped
    
    Args:
        articles: List of article dictionaries
        scraped_urls: List of URLs that have already been scraped
        max_articles: Maximum number of articles to return
        
    Returns:
        List[Dict]: Filtered list of new articles
    """
    new_articles = []
    for article in articles:
        url = article.get('url')
        if url and url not in scraped_urls and len(new_articles) < max_articles:
            new_articles.append(article)
    
    logger.info(f"Filtered {len(new_articles)} new articles from {len(articles)} total")
    return new_articles

