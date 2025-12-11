"""Configuration management for the Competitive Intelligence System."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# SerpAPI Configuration
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Twitter API Configuration
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Slack Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# Competitor Configuration
COMPETITORS = os.getenv("COMPETITORS", "").split(",")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/intelligence.db")

# Scheduling Configuration
DAILY_RUN_TIME = "09:00"
WEEKLY_REPORT_DAY = "friday"
WEEKLY_REPORT_TIME = "17:00"

# Priority Thresholds
PRIORITY_HIGH_KEYWORDS = [
    "funding", "acquisition", "partnership", "launch", "release",
    "pivot", "shutdown", "layoff", "expansion", "merger"
]

PRIORITY_MEDIUM_KEYWORDS = [
    "update", "feature", "improvement", "announcement", "hiring",
    "event", "conference", "award", "milestone"
]
