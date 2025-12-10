"""
Finance Analysis Agents using CrewAI
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
import os

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Agent 1: Spending Behavior Analyst
spending_analyst = Agent(
    role='Spending Behavior Analyst',
    goal='Analyze bank statements to identify spending patterns, categorize expenses, and create insightful visualizations',
    backstory="""You are an expert financial data analyst with years of experience in 
    personal finance management. You excel at identifying spending patterns, categorizing 
    transactions, and creating beautiful, insightful visualizations that help people 
    understand their financial behavior. You have a keen eye for detail and can spot 
    trends that others might miss.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Agent 2: Financial Advisor
financial_advisor = Agent(
    role='Personal Financial Advisor',
    goal='Provide personalized spending recommendations based on analyzed financial data',
    backstory="""You are a certified financial advisor with expertise in personal finance 
    and budgeting. You have helped thousands of people improve their financial health 
    through practical, actionable advice. You understand that everyone's financial 
    situation is unique and provide tailored recommendations that are realistic and 
    achievable. Your advice is always constructive, empowering, and focused on long-term 
    financial wellness.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)
