"""
Orchestrator Agent - Coordinates all specialized agents for travel planning
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .parser_agent import create_parser_agent
from .property_agent import create_property_agent
from .flight_agent import create_flight_agent
from .analysis_agent import create_analysis_agent


class OrchestratorAgent:
    """
    Main agent that orchestrates the entire travel planning workflow.
    Coordinates parser, property, flight, and analysis agents.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the orchestrator with all sub-agents.
        
        Args:
            model_name: OpenAI model to use for all agents
        """
        print("Initializing Orchestrator Agent...")
        self.parser_agent = create_parser_agent(model_name)
        self.property_agent = create_property_agent(model_name)
        self.flight_agent = create_flight_agent(model_name)
        self.analysis_agent = create_analysis_agent(model_name)
        print("All agents initialized successfully!")
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Execute the full travel planning workflow.
        
        Args:
            query: Natural language travel request from user
            
        Returns:
            Dictionary with:
                - requirements: parsed requirements
                - properties: top 10 analyzed properties with scores
                - flights: available flight options (if origin specified)
                - summary: text summary of recommendations
        """
        print(f"\n{'='*60}")
        print("Starting Travel Planning Workflow")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Parse requirements
            print("Step 1: Parsing travel requirements...")
            requirements = self.parser_agent.parse(query)
            print(f"✓ Requirements parsed:")
            print(f"  - Destination: {requirements.get('destination')}")
            print(f"  - Dates: {requirements.get('checkin_date')} to {requirements.get('checkout_date')}")
            print(f"  - Guests: {requirements.get('guests')}")
            print()
            
            # Step 2: Search properties
            print("Step 2: Searching for properties...")
            properties = self.property_agent.search(requirements)
            print(f"✓ Found {len(properties)} properties")
            print()
            
            # Step 3: Check flights (if origin specified)
            flights = []
            if requirements.get("origin"):
                print("Step 3: Searching for flights...")
                try:
                    flights = self.flight_agent.search(
                        origin=requirements["origin"],
                        destination=requirements["destination"],
                        date=requirements["checkin_date"]
                    )
                    print(f"✓ Found {len(flights)} flight options")
                except Exception as e:
                    print(f"⚠ Flight search failed: {e}")
                print()
            else:
                print("Step 3: Skipped (no origin specified)")
                print()
            
            # Step 4: Analyze properties
            print("Step 4: Analyzing properties in detail...")
            analyzed_properties = self.analysis_agent.analyze(properties, requirements)
            print(f"✓ Analyzed {len(analyzed_properties)} properties")
            print()
            
            # Step 5: Generate summary
            print("Step 5: Generating recommendations...")
            summary = self._generate_summary(
                requirements,
                analyzed_properties,
                flights
            )
            print("✓ Recommendations ready!")
            print(f"\n{'='*60}\n")
            
            # Return results
            return {
                "requirements": requirements,
                "properties": analyzed_properties,
                "flights": flights,
                "summary": summary
            }
            
        except Exception as e:
            print(f"\n❌ Error in workflow: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "error": str(e),
                "requirements": {},
                "properties": [],
                "flights": [],
                "summary": f"An error occurred: {str(e)}"
            }
    
    def _generate_summary(
        self,
        requirements: Dict[str, Any],
        properties: list,
        flights: list
    ) -> str:
        """
        Generate a human-readable summary of recommendations.
        """
        lines = []
        
        # Header
        dest = requirements.get("destination", "your destination")
        checkin = requirements.get("checkin_date", "")
        checkout = requirements.get("checkout_date", "")
        
        lines.append(f"# Travel Recommendations for {dest}")
        lines.append(f"**Dates:** {checkin} to {checkout}")
        lines.append("")
        
        # Top 3 properties
        lines.append("## Top 3 Recommended Properties")
        lines.append("")
        
        for idx, prop in enumerate(properties[:3], 1):
            lines.append(f"### {idx}. {prop.get('name', 'Property')}")
            lines.append(f"**Score:** {prop.get('score', 0)}/100")
            lines.append(f"**Rating:** {prop.get('rating', 'N/A')}/5")
            lines.append(f"**Price:** {prop.get('price', 'N/A')}")
            
            pros = prop.get('pros', [])
            if pros:
                lines.append(f"**Pros:** {', '.join(pros[:3])}")
            
            cons = prop.get('cons', [])
            if cons:
                lines.append(f"**Cons:** {', '.join(cons[:2])}")
            
            lines.append(f"[View on Airbnb]({prop.get('url', '#')})")
            lines.append("")
        
        # Flight info
        if flights:
            lines.append("## Flight Options")
            lines.append("")
            lines.append(f"Found {len(flights)} flight(s) on your travel date:")
            lines.append("")
            
            for flight in flights[:3]:
                airline = flight.get('airline', '')
                flight_num = flight.get('flight_number', '')
                dept = flight.get('departure_time', '')
                arr = flight.get('arrival_time', '')
                lines.append(f"- **{airline} {flight_num}**: {dept} → {arr}")
            
            lines.append("")
            lines.append("*Note: Flight schedules only. Check airline websites for current pricing.*")
            lines.append("")
        
        # Summary note
        lines.append("## Planning Tips")
        lines.append("")
        lines.append("- All property links lead directly to Airbnb for booking")
        lines.append("- Scores are based on ratings, amenities, and requirement matches")
        lines.append("- Book early for best availability, especially during peak season")
        
        return "\n".join(lines)
    
    def format_recommendations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format analysis results for display.
        
        Args:
            analysis_result: Raw result from run()
            
        Returns:
            Formatted dictionary ready for Streamlit display
        """
        properties = analysis_result.get("properties", [])
        flights = analysis_result.get("flights", [])
        
        return {
            "properties": properties,
            "flights": flights,
            "summary": analysis_result.get("summary", "")
        }


def create_orchestrator(model_name: str = "gpt-4") -> OrchestratorAgent:
    """
    Factory function to create an orchestrator agent.
    
    Args:
        model_name: OpenAI model to use
        
    Returns:
        Configured OrchestratorAgent instance
    """
    return OrchestratorAgent(model_name=model_name)

