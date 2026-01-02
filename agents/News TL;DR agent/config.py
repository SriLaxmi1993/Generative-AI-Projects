"""
Configuration module for News TL;DR Agent
Handles environment variables, API initialization, and default settings
"""

import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from newsapi import NewsApiClient

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# Model Configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_NUM_SEARCHES = int(os.getenv("DEFAULT_NUM_SEARCHES", "10"))
DEFAULT_NUM_ARTICLES_TLDR = int(os.getenv("DEFAULT_NUM_ARTICLES_TLDR", "3"))
MAX_ARTICLES_TO_SCRAPE = int(os.getenv("MAX_ARTICLES_TO_SCRAPE", "10"))

# Logging Configuration
def setup_logging():
    """Configure application logging"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Set log level
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler("news_tldr.log"),
            logging.StreamHandler()
        ]
    )
    
    # Reduce verbosity of some libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()

def initialize_llm(temperature: float = 0.7) -> ChatOpenAI:
    """
    Initialize and return the ChatOpenAI LLM instance
    
    Args:
        temperature: Temperature setting for the LLM (default: 0.7)
        
    Returns:
        ChatOpenAI: Configured LLM instance
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")
    
    return ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=temperature,
        api_key=OPENAI_API_KEY
    )

def initialize_newsapi() -> NewsApiClient:
    """
    Initialize and return the NewsApiClient instance
    
    Returns:
        NewsApiClient: Configured NewsAPI client instance
        
    Raises:
        ValueError: If NEWSAPI_KEY is not set
    """
    if not NEWSAPI_KEY:
        raise ValueError("NEWSAPI_KEY not found in environment variables. Please set it in your .env file.")
    
    return NewsApiClient(api_key=NEWSAPI_KEY)

def validate_config() -> tuple[bool, str]:
    """
    Validate required configuration
    
    Returns:
        tuple: (is_valid, message)
    """
    if not OPENAI_API_KEY:
        return False, "OPENAI_API_KEY not found in environment variables"
    
    if not NEWSAPI_KEY:
        return False, "NEWSAPI_KEY not found in environment variables"
    
    if OPENAI_API_KEY.startswith("your_") or (OPENAI_API_KEY.startswith("sk-") and len(OPENAI_API_KEY) < 20):
        if OPENAI_API_KEY.startswith("your_"):
            return False, "Please replace the placeholder OPENAI_API_KEY with your actual API key"
    
    if NEWSAPI_KEY.startswith("your_"):
        return False, "Please replace the placeholder NEWSAPI_KEY with your actual API key"
    
    return True, "Configuration validated successfully"


