"""
Configuration module for Competitor Analysis System
Handles environment variables, constants, and logging setup
"""

import os
import logging
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_COMPETITORS = int(os.getenv("MAX_COMPETITORS", "5"))
DEFAULT_COMPETITORS = int(os.getenv("DEFAULT_COMPETITORS", "3"))
ANALYSIS_DEPTH = os.getenv("ANALYSIS_DEPTH", "standard")

# Industry Categories
INDUSTRIES = [
    "Technology / Software",
    "E-commerce / Retail",
    "Financial Services",
    "Healthcare",
    "Manufacturing",
    "Consulting / Professional Services",
    "Media / Entertainment",
    "Food & Beverage",
    "Automotive",
    "Real Estate",
    "Education",
    "Telecommunications",
    "Energy",
    "Transportation / Logistics",
    "Other"
]

# Analysis Depth Configuration
ANALYSIS_DEPTH_CONFIG: Dict[str, Dict] = {
    "quick": {
        "description": "Basic competitor overview (5-10 min)",
        "max_search_results": 5,
        "detail_level": "high-level",
        "research_iterations": 1
    },
    "standard": {
        "description": "Comprehensive analysis (10-20 min)",
        "max_search_results": 10,
        "detail_level": "detailed",
        "research_iterations": 2
    },
    "deep": {
        "description": "In-depth strategic analysis (20-30 min)",
        "max_search_results": 15,
        "detail_level": "comprehensive",
        "research_iterations": 3
    }
}

# Agent Prompts Templates
RESEARCH_AGENT_ROLE = "Competitor Research Specialist"
RESEARCH_AGENT_GOAL = """Discover and gather comprehensive data on competitors in the {industry} industry.
Focus on finding accurate, up-to-date information about {company_name}'s main competitors including their 
market position, products/services, pricing strategies, and customer sentiment."""

RESEARCH_AGENT_BACKSTORY = """You are an expert market researcher with over 15 years of experience in competitive 
intelligence gathering. You excel at finding reliable information from multiple sources, validating data accuracy, 
and identifying key differentiators in competitive landscapes. Your research has helped numerous companies 
understand their market position and make strategic decisions."""

ANALYSIS_AGENT_ROLE = "Market Analysis Expert"
ANALYSIS_AGENT_GOAL = """Analyze the competitive landscape for {company_name} in the {industry} industry.
Perform SWOT analysis, identify competitive advantages and weaknesses, compare features and pricing,
and assess market positioning for each competitor."""

ANALYSIS_AGENT_BACKSTORY = """You are a strategic business analyst with an MBA and 20 years of experience in 
competitive analysis across multiple industries. You have a keen eye for identifying market trends, competitive 
advantages, and strategic opportunities. Your analysis frameworks have been used by Fortune 500 companies to 
refine their competitive strategies."""

REPORT_AGENT_ROLE = "Business Intelligence Reporter"
REPORT_AGENT_GOAL = """Synthesize competitive intelligence into a clear, actionable report for {company_name}.
Create strategic recommendations based on competitor analysis, identify opportunities and threats,
and present insights in a professional, executive-ready format."""

REPORT_AGENT_BACKSTORY = """You are a senior business consultant specializing in transforming complex data into 
strategic insights. With expertise in management consulting and business intelligence, you create reports that 
drive executive decision-making. Your recommendations are known for being practical, data-driven, and aligned 
with business objectives."""

# Search Query Templates
COMPETITOR_SEARCH_QUERIES: List[str] = [
    "{company_name} competitors {industry}",
    "top companies in {industry} like {company_name}",
    "{company_name} alternatives",
    "best {industry} companies 2024"
]

PRICING_SEARCH_QUERIES: List[str] = [
    "{competitor_name} pricing",
    "{competitor_name} plans and pricing",
    "{competitor_name} cost"
]

REVIEW_SEARCH_QUERIES: List[str] = [
    "{competitor_name} reviews",
    "{competitor_name} customer feedback",
    "{competitor_name} pros and cons"
]

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
            logging.FileHandler("competitor_analysis.log"),
            logging.StreamHandler()
        ]
    )
    
    # Reduce verbosity of some libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# Validation Functions
def validate_config() -> tuple[bool, str]:
    """Validate required configuration"""
    if not OPENAI_API_KEY:
        return False, "OPENAI_API_KEY not found in environment variables"
    
    if not SERPAPI_API_KEY:
        return False, "SERPAPI_API_KEY not found in environment variables"
    
    if OPENAI_API_KEY.startswith("your_") or OPENAI_API_KEY.startswith("sk-"):
        if OPENAI_API_KEY.startswith("your_"):
            return False, "Please replace the placeholder OPENAI_API_KEY with your actual API key"
    
    if SERPAPI_API_KEY.startswith("your_"):
        return False, "Please replace the placeholder SERPAPI_API_KEY with your actual API key"
    
    return True, "Configuration validated successfully"

# Initialize logger
logger = setup_logging()

