"""
Task definitions for Competitor Analysis System
Defines three sequential tasks: Research, Analysis, and Report Generation
"""

import logging
from crewai import Task
import config

logger = logging.getLogger(__name__)


def create_research_task(agent, company_name: str, industry: str, num_competitors: int) -> Task:
    """
    Create Competitor Research Task
    
    This task focuses on discovering and gathering comprehensive data about competitors
    
    Args:
        agent: Research agent to execute the task
        company_name: Name of the company being analyzed
        industry: Industry sector
        num_competitors: Number of competitors to research
        
    Returns:
        Task: Configured research task
    """
    logger.info(f"Creating research task for {company_name}")
    
    description = f"""
    Conduct comprehensive competitor research for {company_name} in the {industry} industry.
    
    Your objectives:
    1. Identify the top {num_competitors} direct competitors of {company_name}
    2. For each competitor, gather:
       - Company name and website
       - Brief description and main products/services
       - Target market and customer base
       - Key differentiators
       - Recent news or developments
    3. Search for pricing information when available
    4. Look for customer reviews and sentiment indicators
    5. Identify market positioning and brand perception
    
    Use multiple search queries to ensure comprehensive coverage:
    - "{company_name} competitors {industry}"
    - "Top companies in {industry}"
    - "{company_name} alternatives"
    - "Best {industry} companies 2024"
    
    Focus on finding accurate, recent, and relevant information from reliable sources.
    Prioritize official company websites, industry reports, and reputable business publications.
    """
    
    expected_output = f"""
    A detailed research report containing:
    
    1. COMPETITOR LIST ({num_competitors} competitors):
       For each competitor:
       - Company Name
       - Website URL
       - Description (2-3 sentences)
       - Main Products/Services
       - Target Market
       - Key Differentiators
       
    2. PRICING INFORMATION:
       - Available pricing data for each competitor
       - Pricing model (subscription, one-time, freemium, etc.)
       - Price ranges or tiers
       
    3. CUSTOMER SENTIMENT:
       - Review highlights for each competitor
       - Common praise points
       - Common complaints
       - Overall sentiment (positive/neutral/negative)
       
    4. MARKET POSITIONING:
       - How each competitor positions themselves
       - Their unique value propositions
       - Target customer segments
    
    Format the output as structured text with clear sections and bullet points.
    Include sources/links where information was found.
    """
    
    task = Task(
        description=description,
        expected_output=expected_output,
        agent=agent
    )
    
    logger.info("Research task created successfully")
    return task


def create_analysis_task(agent, company_name: str, industry: str, context_tasks: list) -> Task:
    """
    Create Competitive Analysis Task
    
    This task analyzes the research data to provide strategic insights
    
    Args:
        agent: Analysis agent to execute the task
        company_name: Name of the company being analyzed
        industry: Industry sector
        context_tasks: List of tasks to use as context (research task)
        
    Returns:
        Task: Configured analysis task
    """
    logger.info(f"Creating analysis task for {company_name}")
    
    description = f"""
    Analyze the competitive landscape for {company_name} based on the research data provided.
    
    Your objectives:
    1. Perform SWOT analysis for each major competitor:
       - Strengths: What they do well
       - Weaknesses: Areas where they fall short
       - Opportunities: Market gaps they could fill
       - Threats: Challenges they face
       
    2. Create a competitive comparison matrix:
       - Compare key features across all competitors
       - Compare pricing strategies
       - Compare target markets and positioning
       - Identify competitive advantages and disadvantages
       
    3. Analyze market positioning:
       - Map competitors on key dimensions (price vs. value, features vs. simplicity, etc.)
       - Identify market leaders, challengers, and niche players
       - Assess market saturation and white space opportunities
       
    4. Identify patterns and trends:
       - Common strengths across competitors
       - Emerging trends in the industry
       - Gaps in the market
       - Areas of intense competition vs. underserved segments
    
    Use analytical frameworks and data-driven insights. Be objective and thorough.
    """
    
    expected_output = f"""
    A comprehensive competitive analysis report containing:
    
    1. EXECUTIVE SUMMARY:
       - Overview of competitive landscape
       - Key findings (3-5 bullet points)
       - Market dynamics summary
       
    2. COMPETITOR SWOT ANALYSIS:
       For each major competitor:
       - Strengths (3-5 points)
       - Weaknesses (3-5 points)
       - Opportunities (2-3 points)
       - Threats (2-3 points)
       
    3. COMPETITIVE COMPARISON MATRIX:
       | Feature/Aspect | Competitor 1 | Competitor 2 | Competitor 3 | ... |
       |----------------|-------------|-------------|-------------|-----|
       | Pricing        |             |             |             |     |
       | Key Features   |             |             |             |     |
       | Target Market  |             |             |             |     |
       | Strengths      |             |             |             |     |
       | Weaknesses     |             |             |             |     |
       
    4. MARKET POSITIONING ANALYSIS:
       - Competitive positioning map
       - Market segmentation insights
       - Leader/Challenger/Niche classification
       
    5. COMPETITIVE INSIGHTS:
       - Key trends in the competitive landscape
       - Market gaps and opportunities
       - Areas of competitive intensity
       - Differentiation strategies observed
    
    Format as structured text with clear sections, tables, and bullet points.
    Be specific and reference the research data.
    """
    
    task = Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context_tasks
    )
    
    logger.info("Analysis task created successfully")
    return task


def create_report_task(agent, company_name: str, industry: str, context_tasks: list) -> Task:
    """
    Create Report Generation Task
    
    This task synthesizes all insights into an actionable strategic report
    
    Args:
        agent: Report agent to execute the task
        company_name: Name of the company being analyzed
        industry: Industry sector
        context_tasks: List of tasks to use as context (research + analysis tasks)
        
    Returns:
        Task: Configured report task
    """
    logger.info(f"Creating report task for {company_name}")
    
    description = f"""
    Create a comprehensive, executive-ready competitor analysis report for {company_name}.
    
    Synthesize insights from the research and analysis phases into a strategic report that:
    
    1. Provides a clear overview of the competitive landscape
    2. Highlights key competitive threats and opportunities
    3. Offers actionable strategic recommendations
    4. Presents information in a professional, easy-to-digest format
    
    Your objectives:
    1. Write an executive summary (1-2 paragraphs) that captures the essence of the analysis
    2. Present key findings in a clear, prioritized manner
    3. Provide strategic recommendations based on the competitive analysis
    4. Identify specific actions {company_name} should consider
    5. Highlight risks and opportunities in the competitive landscape
    
    The report should be:
    - Professional and business-focused
    - Data-driven with specific examples
    - Actionable with clear recommendations
    - Well-structured and easy to navigate
    - Free of jargon and highly readable
    """
    
    expected_output = f"""
    A complete competitor analysis report for {company_name} with the following structure:
    
    # COMPETITOR ANALYSIS REPORT: {company_name}
    Industry: {industry}
    Date: [Current Date]
    
    ## EXECUTIVE SUMMARY
    [2-3 paragraphs summarizing the competitive landscape, key findings, and strategic implications]
    
    ## KEY FINDINGS
    1. [Most important insight]
    2. [Second most important insight]
    3. [Third most important insight]
    4. [Fourth insight]
    5. [Fifth insight]
    
    ## COMPETITIVE LANDSCAPE OVERVIEW
    [Detailed overview of the competitive environment, market structure, and key players]
    
    ## DETAILED COMPETITOR ANALYSIS
    For each major competitor:
    ### [Competitor Name]
    - **Overview**: [Brief description]
    - **Strengths**: [Key strengths]
    - **Weaknesses**: [Key weaknesses]
    - **Market Position**: [How they're positioned]
    - **Competitive Threat Level**: [High/Medium/Low with explanation]
    
    ## COMPETITIVE COMPARISON MATRIX
    [Structured comparison of all competitors across key dimensions]
    
    ## MARKET OPPORTUNITIES
    1. [Opportunity 1 with explanation]
    2. [Opportunity 2 with explanation]
    3. [Opportunity 3 with explanation]
    
    ## COMPETITIVE THREATS
    1. [Threat 1 with explanation]
    2. [Threat 2 with explanation]
    3. [Threat 3 with explanation]
    
    ## STRATEGIC RECOMMENDATIONS
    ### Immediate Actions (0-3 months)
    1. [Specific actionable recommendation]
    2. [Specific actionable recommendation]
    3. [Specific actionable recommendation]
    
    ### Short-term Initiatives (3-6 months)
    1. [Specific actionable recommendation]
    2. [Specific actionable recommendation]
    
    ### Long-term Strategy (6-12 months)
    1. [Specific actionable recommendation]
    2. [Specific actionable recommendation]
    
    ## CONCLUSION
    [Final thoughts and summary of strategic direction]
    
    ---
    Report Generated by AI-Powered Competitor Analysis System
    """
    
    task = Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context_tasks
    )
    
    logger.info("Report task created successfully")
    return task


def create_all_tasks(agents: dict, company_name: str, industry: str, num_competitors: int) -> list:
    """
    Create all three tasks in proper sequence with dependencies
    
    Args:
        agents: Dictionary containing all three agents
        company_name: Name of the company being analyzed
        industry: Industry sector
        num_competitors: Number of competitors to analyze
        
    Returns:
        list: List of tasks in execution order
    """
    logger.info(f"Creating all tasks for {company_name}")
    
    # Task 1: Research (no dependencies)
    research_task = create_research_task(
        agents["research"],
        company_name,
        industry,
        num_competitors
    )
    
    # Task 2: Analysis (depends on research)
    analysis_task = create_analysis_task(
        agents["analysis"],
        company_name,
        industry,
        context_tasks=[research_task]
    )
    
    # Task 3: Report (depends on research + analysis)
    report_task = create_report_task(
        agents["report"],
        company_name,
        industry,
        context_tasks=[research_task, analysis_task]
    )
    
    tasks = [research_task, analysis_task, report_task]
    
    logger.info("All tasks created successfully")
    return tasks

