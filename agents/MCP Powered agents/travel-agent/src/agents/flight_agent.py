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
from ..tools.flight_tools import (
    future_flights_schedule_tool,
    flights_with_airline_tool,
    flights_with_airline_wrapper,
)

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
            try:
                result = self.executor.invoke({
                    "origin_airport": origin_airport,
                    "destination_airport": dest_airport,
                    "date": date
                })
                
                # Extract flights from result
                flights = self._extract_flights(result)
                if flights:
                    return flights

                # Fallback: if schedule endpoint fails/rate-limits, use airline endpoint.
                print("⚠️  No schedule flights found, trying airline-based fallback...")
                fallback_flights = self._fallback_airline_search(origin, destination)
                if fallback_flights:
                    print(f"✓ Fallback found {len(fallback_flights)} flight options")
                    return fallback_flights
                
                return []
                
            except Exception as agent_error:
                error_msg = str(agent_error)
                # Check for API rate limiting or bad request errors
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    print("⚠️  Flight API rate limit reached. Please try again later.")
                elif "400" in error_msg or "bad request" in error_msg.lower():
                    print("⚠️  Flight API request error. The date or airport codes may be invalid.")
                else:
                    print(f"Error searching flights: {agent_error}")

                # Try fallback even when agent path errors out.
                fallback_flights = self._fallback_airline_search(origin, destination)
                if fallback_flights:
                    print(f"✓ Fallback found {len(fallback_flights)} flight options")
                    return fallback_flights
                return []
            
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
            intermediate_steps = agent_result.get("intermediate_steps", [])
            for action, observation in intermediate_steps:
                if action.tool != "future_flights_schedule":
                    continue

                try:
                    parsed = observation
                    if isinstance(observation, str):
                        try:
                            parsed = json.loads(observation)
                        except json.JSONDecodeError:
                            continue

                    payload = parsed
                    if isinstance(parsed, dict) and "content" in parsed:
                        content = parsed.get("content", [])
                        if isinstance(content, list) and content and isinstance(content[0], dict):
                            text = content[0].get("text", "")
                            if text:
                                try:
                                    payload = json.loads(text)
                                except json.JSONDecodeError:
                                    continue
                    elif isinstance(parsed, dict) and "structuredContent" in parsed:
                        result_text = parsed.get("structuredContent", {}).get("result", "")
                        if result_text:
                            try:
                                payload = json.loads(result_text)
                            except json.JSONDecodeError:
                                continue

                    # Handle API error envelopes without false positives on "isError": false
                    if isinstance(payload, dict) and payload.get("ok") is False:
                        print(f"⚠️  Flight API error: {payload.get('error', 'unknown error')}")
                        continue

                    flight_list = []
                    if isinstance(payload, list):
                        flight_list = payload
                    elif isinstance(payload, dict):
                        if isinstance(payload.get("data"), list):
                            flight_list = payload["data"]
                        elif isinstance(payload.get("flights"), list):
                            flight_list = payload["flights"]

                    for flight in flight_list:
                        formatted_flight = self._format_flight(flight)
                        if formatted_flight:
                            flights.append(formatted_flight)
                except Exception as e:
                    print(f"Error parsing flight data: {e}")
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
            import traceback
            traceback.print_exc()
            return []
    
    def _format_flight(self, raw_flight: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw flight data into standardized structure.
        """
        try:
            return {
                "airline": raw_flight.get("airline", "").title(),
                "flight_number": raw_flight.get("flight_number", "").upper(),
                "departure_time": raw_flight.get("departure_scheduled_time", raw_flight.get("departure_time", "")),
                "arrival_time": raw_flight.get("arrival_scheduled_time", raw_flight.get("arrival_time", "")),
                "departure_airport": (
                    raw_flight.get("departure_airport_code", "") or raw_flight.get("departure_airport", "")
                ).upper(),
                "arrival_airport": (
                    raw_flight.get("arrival_airport_code", "") or raw_flight.get("arrival_airport", "")
                ).upper(),
                "arrival_terminal": raw_flight.get("arrival_terminal", ""),
                "aircraft": raw_flight.get("aircraft", "").title()
            }
            
        except Exception as e:
            print(f"Error formatting flight: {e}")
            return None

    def _fallback_airline_search(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        """
        Fallback search using flights_with_airline when schedule endpoint fails.
        """
        candidate_airlines = ["Emirates", "Air India", "IndiGo", "British Airways"]
        origin_l = (origin or "").lower()
        destination_l = (destination or "").lower()

        # Light heuristic to prioritize likely carriers.
        if "dubai" in destination_l or "dxb" in destination_l:
            candidate_airlines = ["Emirates", "Air India", "IndiGo"]

        flights: List[Dict[str, Any]] = []
        for airline in candidate_airlines:
            try:
                raw = flights_with_airline_wrapper(airline_name=airline, number_of_flights=8)
                parsed = json.loads(raw)

                items = []
                if isinstance(parsed, dict) and "content" in parsed:
                    content = parsed.get("content", [])
                    if isinstance(content, list) and content and isinstance(content[0], dict):
                        text = content[0].get("text", "")
                        if text:
                            try:
                                items = json.loads(text)
                            except json.JSONDecodeError:
                                items = []
                elif isinstance(parsed, list):
                    items = parsed

                for item in items:
                    dep_airport = str(item.get("departure_airport", ""))
                    arr_airport = str(item.get("arrival_airport", ""))
                    route_blob = f"{dep_airport} {arr_airport}".lower()

                    # Keep only likely route matches to avoid unrelated flights.
                    origin_match = (origin_l and origin_l in route_blob)
                    destination_match = (destination_l and destination_l in route_blob)
                    dxb_hint = ("dubai" in destination_l or "dxb" in destination_l) and (
                        "dubai" in route_blob or "dxb" in route_blob
                    )
                    if (origin_match and destination_match) or (origin_match and dxb_hint):
                        flights.append(self._format_fallback_flight(item))

                if len(flights) >= 8:
                    break
            except Exception:
                continue

        # Dedupe and trim
        unique = []
        seen = set()
        for f in flights:
            if not f:
                continue
            key = f"{f.get('airline','')}_{f.get('flight_number','')}_{f.get('departure_time','')}"
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique[:10]

    def _format_fallback_flight(self, raw_flight: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize flights_with_airline response shape to app's flight schema."""
        return {
            "airline": raw_flight.get("airline", ""),
            "flight_number": str(raw_flight.get("flight_number", "")).upper(),
            "departure_time": raw_flight.get("departure_time", ""),
            "arrival_time": raw_flight.get("arrival_time", ""),
            "departure_airport": raw_flight.get("departure_airport", ""),
            "arrival_airport": raw_flight.get("arrival_airport", ""),
            "arrival_terminal": raw_flight.get("arrival_terminal", ""),
            "aircraft": raw_flight.get("aircraft", ""),
        }


def create_flight_agent(model_name: str = "gpt-4") -> FlightAgent:
    """
    Factory function to create a flight agent.
    
    Args:
        model_name: OpenAI model to use
        
    Returns:
        Configured FlightAgent instance
    """
    return FlightAgent(model_name=model_name)

