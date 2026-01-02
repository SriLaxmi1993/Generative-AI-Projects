"""
CrewAI Crew for Finance Analysis
"""
from crewai import Crew, Process
from agents import spending_analyst, financial_advisor
from tasks import create_analysis_task, create_recommendation_task

def analyze_finances(transaction_data: str) -> dict:
    """
    Run the finance analysis crew
    
    Args:
        transaction_data: String representation of transaction data
        
    Returns:
        dict: Combined results from both agents
    """
    # Create tasks
    analysis_task = create_analysis_task(transaction_data)
    
    # First crew: Analyze spending
    analysis_crew = Crew(
        agents=[spending_analyst],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute analysis
    analysis_result = analysis_crew.kickoff()
    
    # Create recommendation task based on analysis
    recommendation_task = create_recommendation_task(str(analysis_result))
    
    # Second crew: Generate recommendations
    recommendation_crew = Crew(
        agents=[financial_advisor],
        tasks=[recommendation_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute recommendations
    recommendation_result = recommendation_crew.kickoff()
    
    return {
        'analysis': str(analysis_result),
        'recommendations': str(recommendation_result)
    }
