"""
Tasks for the Finance Analysis Agents
"""
from crewai import Task
from agents import spending_analyst, financial_advisor

def create_analysis_task(transaction_data: str) -> Task:
    """Create a task for analyzing spending behavior"""
    return Task(
        description=f"""You are a financial data analyst. Analyze the JSON array of transactions provided below.

CRITICAL: You MUST compute and display ACTUAL NUMBERS from the transaction data. DO NOT use placeholders like "XXXX" or "$X,XXX.XX". Calculate real values.

Transactions JSON:
{transaction_data}

Instructions:
1. Parse the JSON array and extract all transactions
2. Calculate the ACTUAL total spending by summing all negative amounts (expenses)
3. Categorize each transaction by analyzing the description field (look for keywords like: grocery, food, restaurant, dining, coffee, bill, utility, subscription, UPI, transfer, service, etc.)
4. For each category, calculate the ACTUAL total amount spent
5. Calculate percentages based on ACTUAL totals
6. Calculate average daily spending by dividing total spending by the number of days in the date range
7. Identify the largest transactions by absolute amount

IMPORTANT: 
- Use the currency symbol from the transactions (₹ for Indian Rupees, $ for dollars, etc.)
- Show amounts with 2 decimal places
- If you cannot find a date, estimate based on transaction order
- DO NOT use placeholder text or "XXXX" - always show real calculated numbers

Provide your analysis in this exact format:

CATEGORIES:
Category Name: ₹X,XXX.XX
Category Name: ₹X,XXX.XX
(continue for all categories found)

TOP 5 CATEGORIES:
1. Category name - ₹X,XXX.XX - XX.X% of total spending
2. Category name - ₹X,XXX.XX - XX.X% of total spending
3. Category name - ₹X,XXX.XX - XX.X% of total spending
4. Category name - ₹X,XXX.XX - XX.X% of total spending
5. Category name - ₹X,XXX.XX - XX.X% of total spending

TOTAL SPENDING: ₹X,XXX.XX

AVERAGE DAILY SPENDING: ₹XXX.XX

LARGEST TRANSACTIONS:
1. [Exact description from transaction] - ₹X,XXX.XX
2. [Exact description from transaction] - ₹X,XXX.XX
3. [Exact description from transaction] - ₹X,XXX.XX
4. [Exact description from transaction] - ₹X,XXX.XX
5. [Exact description from transaction] - ₹X,XXX.XX

KEY INSIGHTS:
- [Specific insight mentioning actual category names and amounts from the data]
- [Specific insight mentioning actual spending patterns with numbers]
- [Actionable insight with specific recommendations based on actual data]
""",
        agent=spending_analyst,
        expected_output="A detailed spending analysis with REAL calculated numbers, categories, totals, and insights - NO placeholders allowed"
    )

def create_recommendation_task(analysis_result: str) -> Task:
    """Create a task for generating financial recommendations"""
    return Task(
        description=f"""You are a trusted financial advisor. Use the spending analysis below to provide personalized recommendations.

CRITICAL: Reference ACTUAL numbers from the analysis. DO NOT use placeholders. Extract real amounts and categories from the analysis text.

Analysis:
{analysis_result}

Instructions:
1. Extract the ACTUAL total spending amount from the analysis
2. Extract the ACTUAL category names and their amounts
3. Extract the ACTUAL largest transactions
4. Use these real numbers to create specific, actionable recommendations
5. Calculate savings potential based on actual spending patterns
6. Create budgets that are realistic based on the actual spending shown

IMPORTANT:
- Reference specific category names and amounts from the analysis
- Use the same currency symbol (₹ or $) that appears in the analysis
- Show actual rupee/dollar amounts, not placeholders
- Base all recommendations on the real data provided

Provide your recommendations in this exact format:

PRIORITY RECOMMENDATIONS:
1. [Specific recommendation mentioning actual category name and amount from analysis]
2. [Specific recommendation mentioning actual category name and amount from analysis]
3. [Specific recommendation mentioning actual category name and amount from analysis]

SUGGESTED BUDGETS:
[Category from analysis]: ₹X,XXX per month
[Category from analysis]: ₹X,XXX per month
[Category from analysis]: ₹X,XXX per month
(continue for main categories mentioned in the analysis - use ACTUAL category names)

SAVINGS POTENTIAL: ₹X,XXX per month

POSITIVE HABITS:
- [Habit that reflects actual spending patterns shown in analysis]
- [Habit that supports goals based on real data]

30-DAY ACTION PLAN:
Week 1: [Specific action based on actual categories/amounts from analysis]
Week 2: [Specific action based on actual spending patterns]
Week 3: [Specific action based on largest transactions or categories]
Week 4: [Specific action to maintain progress]
""",
        agent=financial_advisor,
        expected_output="Personalized financial recommendations with ACTUAL numbers and specific actions - NO placeholders"
    )
