"""
Aviationstack MCP Tool Wrappers for LangChain
"""
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional
from .mcp_connector import get_mcp_connector


class FutureFlightsInput(BaseModel):
    """Input schema for future flights search."""
    airport_code: str = Field(description="Airport IATA code (e.g., 'DEL' for Delhi, 'DXB' for Dubai)")
    schedule_type: str = Field(description="Either 'departure' or 'arrival'")
    airline_iata: str = Field(description="Airline IATA code (e.g., '6E' for IndiGo, 'AI' for Air India, 'EK' for Emirates)")
    date: str = Field(description="Flight date in YYYY-MM-DD format")
    number_of_flights: int = Field(default=10, description="Number of flights to return")


class FlightsWithAirlineInput(BaseModel):
    """Input schema for flights by airline."""
    airline_name: str = Field(description="Airline name (e.g., 'indigo', 'air india', 'emirates')")
    number_of_flights: int = Field(default=10, description="Number of flights to return")


def future_flights_schedule_wrapper(
    airport_code: str,
    schedule_type: str,
    airline_iata: str,
    date: str,
    number_of_flights: int = 10
) -> str:
    """
    Get future flight schedules for a specific airport, airline, and date.
    
    Args:
        airport_code: Airport IATA code
        schedule_type: 'departure' or 'arrival'
        airline_iata: Airline IATA code
        date: Date in YYYY-MM-DD format
        number_of_flights: Number of results to return
        
    Returns:
        JSON string with flight schedules including times, aircraft, and terminals
    """
    connector = get_mcp_connector()
    
    arguments = {
        "airport_iata_code": airport_code,
        "schedule_type": schedule_type,
        "airline_iata": airline_iata,
        "date": date,
        "number_of_flights": number_of_flights
    }
    
    try:
        result = connector.call_mcp_tool(
            server_name="Aviationstack MCP",
            tool_name="future_flights_arrival_departure_schedule",
            arguments=arguments
        )
        
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        import json
        return json.dumps({"error": str(e), "search_params": arguments})


def flights_with_airline_wrapper(
    airline_name: str,
    number_of_flights: int = 10
) -> str:
    """
    Get current/recent flights for a specific airline.
    
    Args:
        airline_name: Name of the airline
        number_of_flights: Number of results to return
        
    Returns:
        JSON string with flight information
    """
    connector = get_mcp_connector()
    
    arguments = {
        "airline_name": airline_name,
        "number_of_flights": number_of_flights
    }
    
    try:
        result = connector.call_mcp_tool(
            server_name="Aviationstack MCP",
            tool_name="flights_with_airline",
            arguments=arguments
        )
        
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        import json
        return json.dumps({"error": str(e), "airline": airline_name})


# Create LangChain tools
future_flights_schedule_tool = StructuredTool.from_function(
    func=future_flights_schedule_wrapper,
    name="future_flights_schedule",
    description=(
        "Search for future flight schedules between airports. "
        "Provides departure/arrival times, aircraft types, and terminal information. "
        "Use this to find flights for specific routes and dates. "
        "Note: Does NOT include pricing - only schedules. "
        "Common airline codes: 6E=IndiGo, AI=Air India, EK=Emirates, BA=British Airways"
    ),
    args_schema=FutureFlightsInput,
    return_direct=False
)

flights_with_airline_tool = StructuredTool.from_function(
    func=flights_with_airline_wrapper,
    name="flights_with_airline",
    description=(
        "Get flights operated by a specific airline. "
        "Useful for finding all flights from a particular carrier."
    ),
    args_schema=FlightsWithAirlineInput,
    return_direct=False
)


# Export tools
__all__ = [
    'future_flights_schedule_tool',
    'flights_with_airline_tool',
    'FutureFlightsInput',
    'FlightsWithAirlineInput'
]

