"""Task definitions for the competitive intelligence crew."""
from crewai import Task
from typing import List
from config import COMPETITORS, KEYWORDS


def create_web_research_task(agent, competitors: List[str] = None) -> Task:
    """Create web research task."""
    competitors = competitors or COMPETITORS
    competitors_str = ", ".join(competitors)
    
    return Task(
        description=(
            f"Research the following competitors: {competitors_str}\n\n"
            "For each competitor, search for:\n"
            "1. Recent news articles and press releases\n"
            "2. Product Hunt launches or updates\n"
            "3. Blog posts and company announcements\n"
            "4. Website changes or new features\n\n"
            "Focus on information from the last 7 days. Look for:\n"
            "- Product launches or updates\n"
            "- Funding announcements\n"
            "- Partnerships or acquisitions\n"
            "- Strategic pivots or changes\n"
            "- Customer feedback and sentiment\n"
            "- Market positioning changes\n\n"
            "Provide detailed findings with sources and URLs."
        ),
        expected_output=(
            "A comprehensive report containing:\n"
            "- List of all findings organized by competitor\n"
            "- Title, description, and URL for each finding\n"
            "- Source type (news, Product Hunt, etc.)\n"
            "- Date discovered\n"
            "- Brief summary of significance\n"
            "Format as structured JSON for easy processing."
        ),
        agent=agent
    )


def create_social_monitoring_task(agent, competitors: List[str] = None, keywords: List[str] = None) -> Task:
    """Create social media monitoring task."""
    competitors = competitors or COMPETITORS
    keywords = keywords or KEYWORDS
    
    search_terms = competitors + keywords
    search_str = ", ".join(search_terms)
    
    return Task(
        description=(
            f"Monitor social media for mentions of: {search_str}\n\n"
            "Search the following platforms:\n"
            "1. Twitter - Find recent tweets, measure engagement, identify influencers\n"
            "2. Hacker News - Find discussions, launches, and community sentiment\n\n"
            "For each platform, analyze:\n"
            "- Volume of mentions (trending up or down?)\n"
            "- Sentiment (positive, negative, neutral)\n"
            "- Engagement levels (likes, retweets, comments)\n"
            "- Key influencers or thought leaders discussing the topic\n"
            "- Emerging narratives or concerns\n"
            "- Viral content or trending discussions\n\n"
            "Focus on the last 24-48 hours for Twitter, last 7 days for Hacker News."
        ),
        expected_output=(
            "A detailed social intelligence report containing:\n"
            "- Platform-by-platform breakdown of findings\n"
            "- Top posts/tweets by engagement\n"
            "- Sentiment analysis summary\n"
            "- Notable influencers or discussions\n"
            "- Trending topics or concerns\n"
            "- URLs to significant posts\n"
            "Format as structured JSON for easy processing."
        ),
        agent=agent
    )


def create_analysis_task(agent, web_research_task: Task, social_monitoring_task: Task) -> Task:
    """Create intelligence analysis task."""
    return Task(
        description=(
            "Analyze the data collected from web research and social monitoring to create actionable intelligence.\n\n"
            "Your analysis should:\n"
            "1. Synthesize findings from both sources\n"
            "2. Identify significant changes or developments\n"
            "3. Detect patterns and trends\n"
            "4. Assess strategic implications\n"
            "5. Assign priority levels to each finding:\n"
            "   - HIGH: Immediate business impact (funding, acquisitions, major launches, significant pivots)\n"
            "   - MEDIUM: Notable but not urgent (feature updates, partnerships, events, hiring)\n"
            "   - LOW: Informational (minor updates, general discussions)\n\n"
            "For each intelligence item, provide:\n"
            "- Competitor name\n"
            "- Title/headline\n"
            "- Summary of what happened\n"
            "- Why it matters (strategic implications)\n"
            "- Priority level (High/Medium/Low)\n"
            "- Source and URL\n"
            "- Recommended actions (if applicable)\n\n"
            "Group findings by priority level and competitor."
        ),
        expected_output=(
            "A structured intelligence report in JSON format containing:\n"
            "- Executive summary of key findings\n"
            "- Intelligence items grouped by priority (High/Medium/Low)\n"
            "- Each item with: competitor, title, summary, implications, priority, source, url\n"
            "- Trend analysis and patterns observed\n"
            "- Recommended actions for high-priority items\n"
            "- Metadata: total items, breakdown by priority, date range analyzed"
        ),
        agent=agent,
        context=[web_research_task, social_monitoring_task]
    )


def create_reporting_task(agent, analysis_task: Task, report_type: str = "daily") -> Task:
    """Create Slack reporting task."""
    
    if report_type == "immediate":
        description = (
            "Create an immediate alert for HIGH PRIORITY intelligence items.\n\n"
            "Format the alert to be:\n"
            "- Attention-grabbing but professional\n"
            "- Concise and actionable\n"
            "- Clearly stating why this is urgent\n"
            "- Including relevant links and sources\n\n"
            "Use Slack formatting (bold, bullets, emojis) for readability."
        )
        expected_output = (
            "A Slack message formatted for immediate alert containing:\n"
            "- 🚨 Alert header\n"
            "- Competitor name and what happened\n"
            "- Why it matters\n"
            "- Recommended actions\n"
            "- Source links\n"
            "Ready to send via Slack MCP."
        )
    
    elif report_type == "daily":
        description = (
            "Create a daily digest of competitive intelligence findings.\n\n"
            "The digest should:\n"
            "- Summarize all findings from the last 24 hours\n"
            "- Group by priority level (High/Medium/Low)\n"
            "- Highlight key trends or patterns\n"
            "- Be scannable and easy to read\n"
            "- Include links to sources\n\n"
            "Use Slack formatting for a professional, readable digest."
        )
        expected_output = (
            "A formatted daily digest Slack message containing:\n"
            "- 📊 Daily Intelligence Digest header with date\n"
            "- Summary of total findings\n"
            "- High priority items (if any)\n"
            "- Medium priority items\n"
            "- Low priority items\n"
            "- Key trends observed\n"
            "- All with proper Slack formatting\n"
            "Ready to send via Slack MCP."
        )
    
    else:  # weekly
        description = (
            "Create a comprehensive weekly intelligence report.\n\n"
            "The report should:\n"
            "- Provide an executive summary of the week\n"
            "- Highlight the most significant developments\n"
            "- Show trends and patterns over the week\n"
            "- Compare competitor activities\n"
            "- Provide strategic recommendations\n"
            "- Include metrics (total items, by priority, by competitor)\n\n"
            "Make it comprehensive but well-organized and scannable."
        )
        expected_output = (
            "A comprehensive weekly report Slack message containing:\n"
            "- 📈 Weekly Intelligence Report header with date range\n"
            "- Executive summary\n"
            "- Key highlights of the week\n"
            "- Breakdown by competitor\n"
            "- Trend analysis\n"
            "- Metrics and statistics\n"
            "- Strategic recommendations\n"
            "- All with proper Slack formatting\n"
            "Ready to send via Slack MCP."
        )
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=[analysis_task]
    )
