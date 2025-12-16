"""
Airbnb MCP Tool Wrappers for LangChain
"""
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from .mcp_connector import get_mcp_connector


class AirbnbSearchInput(BaseModel):
    """Input schema for Airbnb search."""
    location: str = Field(description="City or region to search (e.g., 'Coorg, India')")
    checkin: str = Field(description="Check-in date in YYYY-MM-DD format")
    checkout: str = Field(description="Check-out date in YYYY-MM-DD format")
    adults: int = Field(default=1, description="Number of adults")
    children: Optional[int] = Field(default=0, description="Number of children")
    infants: Optional[int] = Field(default=0, description="Number of infants")
    pets: Optional[int] = Field(default=0, description="Number of pets")
    min_price: Optional[int] = Field(default=None, description="Minimum price filter")
    max_price: Optional[int] = Field(default=None, description="Maximum price filter")


class AirbnbListingDetailsInput(BaseModel):
    """Input schema for Airbnb listing details."""
    listing_id: str = Field(description="The Airbnb listing ID")
    checkin: Optional[str] = Field(default=None, description="Check-in date in YYYY-MM-DD format")
    checkout: Optional[str] = Field(default=None, description="Check-out date in YYYY-MM-DD format")
    adults: Optional[int] = Field(default=1, description="Number of adults")


def airbnb_search_wrapper(
    location: str,
    checkin: str,
    checkout: str,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    pets: int = 0,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None
) -> str:
    """
    Search for Airbnb properties matching the criteria.
    
    Returns:
        JSON string containing search results with property details and URLs
    """
    connector = get_mcp_connector()
    
    arguments = {
        "location": location,
        "checkin": checkin,
        "checkout": checkout,
        "adults": adults,
        "ignoreRobotsText": True  # Required to bypass robots.txt
    }
    
    # Add optional parameters if provided
    if children > 0:
        arguments["children"] = children
    if infants > 0:
        arguments["infants"] = infants
    if pets > 0:
        arguments["pets"] = pets
    if min_price:
        arguments["minPrice"] = min_price
    if max_price:
        arguments["maxPrice"] = max_price
    
    try:
        result = connector.call_mcp_tool(
            server_name="airbnb",
            tool_name="airbnb_search",
            arguments=arguments
        )
        
        # Convert result to JSON string for LangChain
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "search_params": arguments})


def airbnb_listing_details_wrapper(
    listing_id: str,
    checkin: Optional[str] = None,
    checkout: Optional[str] = None,
    adults: int = 1
) -> str:
    """
    Get detailed information about a specific Airbnb listing.
    
    Returns:
        JSON string containing detailed listing information including reviews and amenities
    """
    connector = get_mcp_connector()
    
    arguments = {
        "id": listing_id,
        "ignoreRobotsText": True
    }
    
    # Add optional date parameters
    if checkin:
        arguments["checkin"] = checkin
    if checkout:
        arguments["checkout"] = checkout
    if adults:
        arguments["adults"] = adults
    
    try:
        result = connector.call_mcp_tool(
            server_name="airbnb",
            tool_name="airbnb_listing_details",
            arguments=arguments
        )
        
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        import json
        return json.dumps({"error": str(e), "listing_id": listing_id})


# Create LangChain tools
airbnb_search_tool = StructuredTool.from_function(
    func=airbnb_search_wrapper,
    name="airbnb_search",
    description=(
        "Search for Airbnb properties in a location with specified dates and guest count. "
        "Returns top 10+ properties with names, prices, ratings, URLs, and basic details. "
        "Each result includes a direct Airbnb booking link."
    ),
    args_schema=AirbnbSearchInput,
    return_direct=False
)

airbnb_listing_details_tool = StructuredTool.from_function(
    func=airbnb_listing_details_wrapper,
    name="airbnb_listing_details",
    description=(
        "Get detailed information about a specific Airbnb listing including reviews, "
        "amenities, host information, and cancellation policies. "
        "Use this after airbnb_search to get in-depth property analysis."
    ),
    args_schema=AirbnbListingDetailsInput,
    return_direct=False
)


# Export tools
__all__ = [
    'airbnb_search_tool',
    'airbnb_listing_details_tool',
    'AirbnbSearchInput',
    'AirbnbListingDetailsInput'
]

