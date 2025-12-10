"""
Tasks for the Finance Analysis Agents
"""
from crewai import Task
from agents import spending_analyst, financial_advisor

def create_analysis_task(transaction_data: str) -> Task:
    """Create a task for analyzing spending behavior"""
    return Task(
        description=f"""You are a financial analyst. Analyze these bank transactions and provide insights.

Transactions:
{transaction_data}

Provide your analysis in this exact format:

CATEGORIES:
List each spending category and total amount

TOP 5 CATEGORIES:
1. Category name - Amount - Percentage
2. Category name - Amount - Percentage
(continue for 5 categories)

TOTAL SPENDING: $X,XXX.XX

AVERAGE DAILY SPENDING: $XX.XX

LARGEST TRANSACTIONS:
1. Description - Amount
2. Description - Amount
(continue for 5 transactions)

KEY INSIGHTS:
- Insight 1
- Insight 2
- Insight 3
""",
        agent=spending_analyst,
        expected_output="A detailed spending analysis with categories, totals, and insights in the specified format"
    )

def create_recommendation_task(analysis_result: str) -> Task:
    """Create a task for generating financial recommendations"""
    return Task(
        description=f"""You are a financial advisor. Based on this spending analysis, provide actionable recommendations.

Analysis:
{analysis_result}

Provide your recommendations in this exact format:

PRIORITY RECOMMENDATIONS:
1. First recommendation with specific action
2. Second recommendation with specific action
3. Third recommendation with specific action

SUGGESTED BUDGETS:
Category 1: $XXX per month
Category 2: $XXX per month
(continue for main categories)

SAVINGS POTENTIAL: $XXX per month

POSITIVE HABITS:
- Good habit 1
- Good habit 2

30-DAY ACTION PLAN:
Week 1: Action item
Week 2: Action item
Week 3: Action item
Week 4: Action item
""",
        agent=financial_advisor,
        expected_output="Personalized financial recommendations with specific actions and budget suggestions"
    )
