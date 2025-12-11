"""Custom tools for the competitive intelligence agents."""
from crewai_tools import BaseTool
from typing import Type, Any, Dict, List
try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field
import requests
from serpapi import GoogleSearch
import tweepy
import json
from config import (
    SERPAPI_API_KEY,
    TWITTER_BEARER_TOKEN
)


# Tool Input Schemas
class WebSearchInput(BaseModel):
    """Input schema for web search tool."""
    query: str = Field(..., description="Search query for finding competitor information")
    num_results: int = Field(default=10, description="Number of results to return")


class TwitterSearchInput(BaseModel):
    """Input schema for Twitter search tool."""
    query: str = Field(..., description="Search query for Twitter")
    max_results: int = Field(default=10, description="Maximum number of tweets to return")


class HackerNewsSearchInput(BaseModel):
    """Input schema for Hacker News search tool."""
    query: str = Field(..., description="Search query for Hacker News")
    num_results: int = Field(default=10, description="Number of results to return")


# Custom Tools
class WebSearchTool(BaseTool):
    """Tool for searching the web using SerpAPI."""
    name: str = "Web Search Tool"
    description: str = (
        "Searches the web for competitor information using Google Search. "
        "Can find news articles, blog posts, Product Hunt launches, and company websites. "
        "Returns titles, snippets, and URLs."
    )
    args_schema: Type[BaseModel] = WebSearchInput
    
    def _run(self, query: str, num_results: int = 10) -> str:
        """Execute web search."""
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": SERPAPI_API_KEY,
                "num": num_results
            })
            results = search.get_dict()
            
            formatted_results = []
            
            # Organic results
            if "organic_results" in results:
                for result in results["organic_results"][:num_results]:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("link", ""),
                        "source": result.get("source", "")
                    })
            
            # News results
            if "news_results" in results:
                for result in results["news_results"][:5]:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("link", ""),
                        "source": result.get("source", ""),
                        "date": result.get("date", "")
                    })
            
            return json.dumps(formatted_results, indent=2)
        
        except Exception as e:
            return f"Error performing web search: {str(e)}"


class TwitterSearchTool(BaseTool):
    """Tool for searching Twitter using Twitter API v2."""
    name: str = "Twitter Search Tool"
    description: str = (
        "Searches Twitter for mentions of competitors, products, or keywords. "
        "Returns recent tweets with engagement metrics."
    )
    args_schema: Type[BaseModel] = TwitterSearchInput
    
    def _run(self, query: str, max_results: int = 10) -> str:
        """Execute Twitter search."""
        try:
            client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
            
            tweets = client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            if not tweets.data:
                return json.dumps({"message": "No tweets found"})
            
            # Create user lookup
            users = {user.id: user for user in tweets.includes.get('users', [])}
            
            formatted_results = []
            for tweet in tweets.data:
                author = users.get(tweet.author_id)
                formatted_results.append({
                    "text": tweet.text,
                    "author": author.username if author else "Unknown",
                    "author_name": author.name if author else "Unknown",
                    "created_at": str(tweet.created_at),
                    "likes": tweet.public_metrics['like_count'],
                    "retweets": tweet.public_metrics['retweet_count'],
                    "replies": tweet.public_metrics['reply_count'],
                    "url": f"https://twitter.com/{author.username}/status/{tweet.id}" if author else ""
                })
            
            return json.dumps(formatted_results, indent=2)
        
        except Exception as e:
            return f"Error searching Twitter: {str(e)}"


class HackerNewsSearchTool(BaseTool):
    """Tool for searching Hacker News using Algolia API."""
    name: str = "Hacker News Search Tool"
    description: str = (
        "Searches Hacker News for competitor mentions, product launches, and tech discussions. "
        "Returns stories with points and comment counts."
    )
    args_schema: Type[BaseModel] = HackerNewsSearchInput
    
    def _run(self, query: str, num_results: int = 10) -> str:
        """Execute Hacker News search."""
        try:
            url = "http://hn.algolia.com/api/v1/search"
            params = {
                "query": query,
                "tags": "story",
                "hitsPerPage": num_results
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            formatted_results = []
            for hit in data.get("hits", []):
                formatted_results.append({
                    "title": hit.get("title", ""),
                    "url": hit.get("url", ""),
                    "points": hit.get("points", 0),
                    "num_comments": hit.get("num_comments", 0),
                    "author": hit.get("author", ""),
                    "created_at": hit.get("created_at", ""),
                    "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                })
            
            return json.dumps(formatted_results, indent=2)
        
        except Exception as e:
            return f"Error searching Hacker News: {str(e)}"


class ProductHuntSearchTool(BaseTool):
    """Tool for searching Product Hunt."""
    name: str = "Product Hunt Search Tool"
    description: str = (
        "Searches Product Hunt for competitor product launches and updates. "
        "Uses web scraping to find relevant products."
    )
    args_schema: Type[BaseModel] = WebSearchInput
    
    def _run(self, query: str, num_results: int = 10) -> str:
        """Execute Product Hunt search via SerpAPI."""
        try:
            # Search Product Hunt via Google
            search_query = f"site:producthunt.com {query}"
            search = GoogleSearch({
                "q": search_query,
                "api_key": SERPAPI_API_KEY,
                "num": num_results
            })
            results = search.get_dict()
            
            formatted_results = []
            if "organic_results" in results:
                for result in results["organic_results"]:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("link", ""),
                        "source": "Product Hunt"
                    })
            
            return json.dumps(formatted_results, indent=2)
        
        except Exception as e:
            return f"Error searching Product Hunt: {str(e)}"
