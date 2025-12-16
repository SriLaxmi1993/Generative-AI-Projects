"""
Flight Agent - Searches for flight schedules matching travel requirements
"""
import json
import os
from typing import Dict, Any, List, Optional
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from ..prompts.agent_prompts import FLIGHT_AGENT_PROMPT
from ..tools.flight_tools import future_flights_schedule_tool, flights_with_airline_tool

# Load environment variables
load_dotenv()


# Common airport codes
AIRPORT_CODES = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "chennai": "MAA",
    "kolkata": "CCU",
    "hyderabad": "HYD",
    "pune": "PNQ",
    "goa": "GOI",
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "london": "LHR",
    "new york": "JFK",
    "singapore": "SIN"
}

# Common airline codes
AIRLINE_CODES = {
    "indigo": "6E",
    "air india": "AI",
    "emirates": "EK",
    "british airways": "BA",
    "lufthansa": "LH",
    "qatar airways": "QR"
}


class FlightAgent:
    """
    Agent that searches for flight schedules between origin and destination.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the flight agent.
        
        Args:
            model_name: OpenAI model to use
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create agent with flight tools
        self.tools = [future_flights_schedule_tool, flights_with_airline_tool]
        self.agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            FLIGHT_AGENT_PROMPT
        )
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            return_intermediate_steps=True
        )
    
    def search(
        self,
        origin: str,
        destination: str,
        date: str
    ) -> List[Dict[str, Any]]:
        """
        Search for flights between origin and destination.
        
        Args:
            origin: Origin city or airport code
            destination: Destination city or airport code
            date: Travel date in YYYY-MM-DD format
            
        Returns:
            List of flight information dictionaries
        """
        if not origin:
            return []
        
        try:
            # Convert city names to airport codes
            origin_airport = self._get_airport_code(origin)
            dest_airport = self._get_airport_code(destination)
            
            if not origin_airport or not dest_airport:
                print(f"Could not find airport codes for {origin} or {destination}")
                return []
            
            # Execute agent
            result = self.executor.invoke({
                "origin_airport": origin_airport,
                "destination_airport": dest_airport,
                "date": date
            })
            
            # Extract flights from result
            flights = self._extract_flights(result)
            
            return flights
            
        except Exception as e:
            print(f"Error searching flights: {e}")
            return []
    
    def _get_airport_code(self, location: str) -> Optional[str]:
        """
        Convert city name to IATA airport code.
        """
        if not location:
            return None
        
        location_lower = location.lower().strip()
        
        # Check if already an airport code (3 letters)
        if len(location_lower) == 3 and location_lower.isalpha():
            return location.upper()
        
        # Look up in our mapping
        for city, code in AIRPORT_CODES.items():
            if city in location_lower:
                return code
        
        # If not found, return None
        return None
    
    def _extract_flights(self, agent_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract flight data from agent result.
        """
        flights = []
        
        try:
            # Get intermediate steps
            intermediate_steps = agent_result.get("intermediate_steps", [])
            
            for action, observation in intermediate_steps:
                if action.tool == "future_flights_schedule":
                    # Parse the observation
                    try:
                        flight_data = json.loads(observation)
                        
                        if isinstance(flight_data, list):
                            for flight in flight_data:
                                formatted_flight = self._format_flight(flight)
                                if formatted_flight:
                                    flights.append(formatted_flight)
                        
                    except json.JSONDecodeError:
                        continue
            
            # Remove duplicates and limit to 10
            seen = set()
            unique_flights = []
            for flight in flights:
                flight_id = f"{flight.get('flight_number')}_{flight.get('departure_time')}"
                if flight_id not in seen:
                    seen.add(flight_id)
                    unique_flights.append(flight)
            
            return unique_flights[:10]
            
        except Exception as e:
            print(f"Error extracting flights: {e}")
            return []
    
    def _format_flight(self, raw_flight: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw flight data into standardized structure.
        """
        try:
            return {
                "airline": raw_flight.get("airline", "").title(),
                "flight_number": raw_flight.get("flight_number", "").upper(),
                "departure_time": raw_flight.get("departure_scheduled_time", ""),
                "arrival_time": raw_flight.get("arrival_scheduled_time", ""),
                "departure_airport": raw_flight.get("departure_airport_code", "").upper(),
                "arrival_airport": raw_flight.get("arrival_airport_code", "").upper(),
                "arrival_terminal": raw_flight.get("arrival_terminal", ""),
                "aircraft": raw_flight.get("aircraft", "").title()
            }
            
        except Exception as e:
            print(f"Error formatting flight: {e}")
            return None


def create_flight_agent(model_name: str = "gpt-4") -> FlightAgent:
    """
    Factory function to create a flight agent.
    
    Args:
        model_name: OpenAI model to use
        
    Returns:
        Configured FlightAgent instance
    """
    return FlightAgent(model_name=model_name)

