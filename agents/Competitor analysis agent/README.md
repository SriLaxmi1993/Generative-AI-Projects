# Competitive Intelligence CrewAI System

A 4-agent CrewAI system for automated competitive intelligence gathering and reporting.

## 🤖 Agents

1. **Web Researcher** - Searches competitor news, websites, and Product Hunt
2. **Social Monitor** - Tracks Twitter and Hacker News for social activity
3. **Analyst** - Synthesizes data, detects changes, assigns priority (High/Medium/Low)
4. **Slack Reporter** - Sends insights via Slack (immediate alerts, daily digests, weekly reports)

## 🗄️ Features

- **SQLite Database** - Historical data storage for all intelligence items
- **Priority System** - Automatic classification (High/Medium/Low) based on keywords and impact
- **Automated Scheduling** - Daily runs at 9am, weekly reports Friday 5pm
- **Slack Integration** - Immediate high-priority alerts, daily digests, weekly summaries
- **Multi-Source Intelligence** - SerpAPI, Twitter, Hacker News, Product Hunt

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (for CrewAI LLM)
- SerpAPI key
- Twitter API credentials (v2)
- Slack Bot token and channel ID

## 🚀 Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `OPENAI_API_KEY` - Your OpenAI API key
- `SERPAPI_API_KEY` - Your SerpAPI key
- `TWITTER_BEARER_TOKEN` - Twitter API v2 bearer token
- `SLACK_BOT_TOKEN` - Your Slack bot token
- `SLACK_CHANNEL_ID` - Slack channel ID for reports
- `COMPETITORS` - Comma-separated list of competitors to track
- `KEYWORDS` - Comma-separated list of keywords to monitor

## 🔧 Configuration

### Setting up Slack

1. Create a Slack app at https://api.slack.com/apps
2. Add the following bot token scopes:
   - `chat:write`
   - `chat:write.public`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token to `SLACK_BOT_TOKEN`
5. Get your channel ID and add to `SLACK_CHANNEL_ID`

### Setting up Twitter API

1. Apply for Twitter API access at https://developer.twitter.com
2. Create a new app and generate API keys
3. Copy the Bearer Token to `TWITTER_BEARER_TOKEN`

### Setting up SerpAPI

1. Sign up at https://serpapi.com
2. Get your API key from the dashboard
3. Add to `SERPAPI_API_KEY`

## 📊 Usage

### Run Once (Manual)

```bash
python crew.py
```

### Run with Scheduler (Automated)

```bash
python scheduler.py
```

This will:
- Run intelligence gathering daily at 9:00 AM
- Send daily digests with all findings
- Send weekly reports every Friday at 5:00 PM
- Send immediate Slack alerts for high-priority items

### Custom Runs

```python
from crew import CompetitiveIntelligenceCrew

crew = CompetitiveIntelligenceCrew()

# Run intelligence gathering
results = crew.run_intelligence_gathering()

# Send daily digest
crew.send_daily_digest()

# Send weekly report
crew.send_weekly_report()
```

## 📁 Project Structure

```
Competitor analysis agent/
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your actual environment variables (not in git)
├── config.py                # Configuration management
├── database.py              # SQLite database management
├── tools.py                 # Custom CrewAI tools for APIs
├── agents.py                # Agent definitions
├── tasks.py                 # Task definitions
├── crew.py                  # Main crew orchestration
├── slack_integration.py     # Slack reporting
├── scheduler.py             # Automated scheduling
├── data/                    # Database storage (auto-created)
│   └── intelligence.db      # SQLite database
└── README.md               # This file
```

## 🗃️ Database Schema

The system uses SQLite with the following tables:

- **competitors** - Tracked competitors
- **intelligence_items** - All intelligence findings with priority
- **social_activity** - Social media activity tracking
- **reports** - Sent reports history
- **change_detection** - Detected changes over time

## 🎯 Priority System

Intelligence items are automatically prioritized:

**High Priority** (🔴):
- Funding announcements
- Acquisitions
- Major product launches
- Strategic pivots
- Significant partnerships

**Medium Priority** (🟡):
- Feature updates
- Hiring announcements
- Events/conferences
- Awards/milestones

**Low Priority** (🟢):
- Minor updates
- General discussions
- Informational content

## 📱 Slack Notifications

### Immediate Alerts
High-priority items trigger immediate Slack notifications with:
- Competitor name
- What happened
- Why it matters
- Source link

### Daily Digest (9 AM)
Comprehensive summary of all findings:
- Grouped by priority
- Top items highlighted
- Full source links

### Weekly Report (Friday 5 PM)
Strategic overview including:
- Executive summary
- Activity by competitor
- Trend analysis
- Key metrics

## 🔄 Customization

### Add More Competitors
Edit `.env`:
```
COMPETITORS=competitor1,competitor2,competitor3,newcompetitor
```

### Change Schedule Times
Edit `config.py`:
```python
DAILY_RUN_TIME = "09:00"  # 24-hour format
WEEKLY_REPORT_DAY = "friday"
WEEKLY_REPORT_TIME = "17:00"
```

### Adjust Priority Keywords
Edit `config.py`:
```python
PRIORITY_HIGH_KEYWORDS = [
    "funding", "acquisition", "your_keyword"
]
```

## 🐛 Troubleshooting

### Database Issues
Delete the database and it will be recreated:
```bash
rm data/intelligence.db
```

### API Rate Limits
- SerpAPI: 100 searches/month on free tier
- Twitter: 500,000 tweets/month on free tier

### Slack Messages Not Sending
- Verify bot token is correct
- Check bot has permission to post in channel
- Ensure channel ID is correct (not channel name)

## 📝 License

MIT License - feel free to use and modify as needed.

## 🤝 Contributing

This is a specialized agent system. Customize for your specific competitive intelligence needs!
