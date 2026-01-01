"""
Agent definitions for Competitor Analysis System
Defines three specialized agents: Research, Analysis, and Report
"""

import logging
from crewai import Agent
from langchain_openai import ChatOpenAI
import config
from tools import (
    competitor_search_tool,
    company_info_tool,
    pricing_search_tool,
    review_search_tool,
    data_processor_tool
)

logger = logging.getLogger(__name__)


def create_llm(temperature: float = 0.7):
    """Create and configure the LLM instance"""
    return ChatOpenAI(
        model=config.OPENAI_MODEL,
        temperature=temperature,
        api_key=config.OPENAI_API_KEY
    )


def create_research_agent(company_name: str, industry: str) -> Agent:
    """
    Create Research Agent - Specialist in gathering competitor data
    
    Args:
        company_name: Name of the company being analyzed
        industry: Industry sector
        
    Returns:
        Agent: Configured research agent
    """
    logger.info(f"Creating Research Agent for {company_name} in {industry}")
    
    role = config.RESEARCH_AGENT_ROLE
    
    goal = config.RESEARCH_AGENT_GOAL.format(
        company_name=company_name,
        industry=industry
    )
    
    backstory = config.RESEARCH_AGENT_BACKSTORY
    
    agent = Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=[
            competitor_search_tool,
            company_info_tool,
            pricing_search_tool,
            review_search_tool
        ],
        llm=create_llm(temperature=0.5),
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        memory=True
    )
    
    logger.info("Research Agent created successfully")
    return agent


def create_analysis_agent(company_name: str, industry: str) -> Agent:
    """
    Create Analysis Agent - Expert in competitive analysis and SWOT
    
    Args:
        company_name: Name of the company being analyzed
        industry: Industry sector
        
    Returns:
        Agent: Configured analysis agent
    """
    logger.info(f"Creating Analysis Agent for {company_name} in {industry}")
    
    role = config.ANALYSIS_AGENT_ROLE
    
    goal = config.ANALYSIS_AGENT_GOAL.format(
        company_name=company_name,
        industry=industry
    )
    
    backstory = config.ANALYSIS_AGENT_BACKSTORY
    
    agent = Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=[data_processor_tool],
        llm=create_llm(temperature=0.4),
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        memory=True
    )
    
    logger.info("Analysis Agent created successfully")
    return agent


def create_report_agent(company_name: str, industry: str) -> Agent:
    """
    Create Report Agent - Specialist in synthesizing insights and recommendations
    
    Args:
        company_name: Name of the company being analyzed
        industry: Industry sector
        
    Returns:
        Agent: Configured report agent
    """
    logger.info(f"Creating Report Agent for {company_name} in {industry}")
    
    role = config.REPORT_AGENT_ROLE
    
    goal = config.REPORT_AGENT_GOAL.format(
        company_name=company_name,
        industry=industry
    )
    
    backstory = config.REPORT_AGENT_BACKSTORY
    
    agent = Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=[],  # Report agent synthesizes, doesn't need search tools
        llm=create_llm(temperature=0.6),
        verbose=True,
        allow_delegation=False,
        max_iter=10,
        memory=True
    )
    
    logger.info("Report Agent created successfully")
    return agent


def create_all_agents(company_name: str, industry: str) -> dict:
    """
    Create all three agents for the competitor analysis system
    
    Args:
        company_name: Name of the company being analyzed
        industry: Industry sector
        
    Returns:
        dict: Dictionary containing all three agents
    """
    logger.info(f"Creating all agents for {company_name} in {industry}")
    
    agents = {
        "research": create_research_agent(company_name, industry),
        "analysis": create_analysis_agent(company_name, industry),
        "report": create_report_agent(company_name, industry)
    }
    
    logger.info("All agents created successfully")
    return agents

