"""Agent definitions for the competitive intelligence crew."""
from crewai import Agent
from langchain_openai import ChatOpenAI
from tools import (
    WebSearchTool,
    TwitterSearchTool,
    HackerNewsSearchTool,
    ProductHuntSearchTool
)
from config import OPENAI_API_KEY


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)


def create_web_researcher_agent() -> Agent:
    """Create the Web Researcher agent."""
    return Agent(
        role="Web Research Specialist",
        goal=(
            "Find and collect comprehensive information about competitors from the web, "
            "including news articles, blog posts, Product Hunt launches, "
            "and company websites. Identify significant updates, product launches, and strategic moves."
        ),
        backstory=(
            "You are an expert web researcher with years of experience in competitive intelligence. "
            "You know how to find valuable information across different platforms and can quickly "
            "identify what's important. You're skilled at using search engines, navigating forums, "
            "and discovering hidden insights about companies and their products."
        ),
        tools=[
            WebSearchTool(),
            ProductHuntSearchTool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=15
    )


def create_social_monitor_agent() -> Agent:
    """Create the Social Media Monitor agent."""
    return Agent(
        role="Social Media Intelligence Analyst",
        goal=(
            "Monitor and analyze competitor social media activity across Twitter and Hacker News. "
            "Track mentions, engagement patterns, sentiment, and trending discussions. "
            "Identify viral content, community reactions, and emerging narratives."
        ),
        backstory=(
            "You are a social media intelligence expert who understands the pulse of online communities. "
            "You can read between the lines of tweets, identify trending topics before they go viral, "
            "and understand what the tech community is saying about different companies and products. "
            "You're particularly skilled at gauging sentiment and spotting important signals in social noise."
        ),
        tools=[
            TwitterSearchTool(),
            HackerNewsSearchTool()
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=15
    )


def create_analyst_agent() -> Agent:
    """Create the Intelligence Analyst agent."""
    return Agent(
        role="Competitive Intelligence Analyst",
        goal=(
            "Synthesize data from web research and social monitoring to create actionable insights. "
            "Detect significant changes in competitor strategy, product offerings, or market position. "
            "Assign priority levels (High/Medium/Low) based on business impact and urgency. "
            "Identify patterns, trends, and strategic implications."
        ),
        backstory=(
            "You are a senior competitive intelligence analyst with deep expertise in market analysis "
            "and strategic thinking. You excel at connecting dots between disparate pieces of information "
            "to reveal the bigger picture. You understand what matters to businesses and can quickly "
            "assess the strategic importance of any development. Your analysis has helped companies "
            "stay ahead of their competition by anticipating market moves and identifying opportunities."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10
    )


def create_slack_reporter_agent() -> Agent:
    """Create the Slack Reporter agent."""
    return Agent(
        role="Intelligence Communications Specialist",
        goal=(
            "Communicate intelligence findings effectively through Slack. "
            "Send immediate alerts for high-priority items, compile daily digests, "
            "and create comprehensive weekly reports. Ensure all stakeholders are "
            "informed with clear, actionable intelligence."
        ),
        backstory=(
            "You are a communications expert who specializes in delivering intelligence reports. "
            "You know how to present complex information in a clear, concise, and actionable format. "
            "You understand the importance of timing - when to send immediate alerts versus when to "
            "batch information into digests. Your reports are known for being well-structured, "
            "easy to scan, and always highlighting what matters most."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10
    )
