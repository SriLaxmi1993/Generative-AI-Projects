"""
Property Agent - Searches for Airbnb properties matching requirements
"""
import json
import os
from typing import Dict, Any, List
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from ..prompts.agent_prompts import PROPERTY_AGENT_PROMPT
from ..tools.airbnb_tools import airbnb_search_tool

# Load environment variables
load_dotenv()


class PropertyAgent:
    """
    Agent that searches for properties matching user requirements.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the property agent.
        
        Args:
            model_name: OpenAI model to use
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create agent with Airbnb search tool
        self.tools = [airbnb_search_tool]
        self.agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            PROPERTY_AGENT_PROMPT
        )
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,
            return_intermediate_steps=True
        )
    
    def search(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for properties matching the requirements.
        
        Args:
            requirements: Parsed travel requirements
            
        Returns:
            List of property dictionaries with details and URLs
        """
        try:
            # Convert requirements to string for the agent
            requirements_str = json.dumps(requirements, indent=2)
            
            # Execute agent
            result = self.executor.invoke({
                "requirements": requirements_str
            })
            
            # Extract properties from result
            properties = self._extract_properties(result, requirements)
            
            return properties
            
        except Exception as e:
            print(f"Error searching properties: {e}")
            return []
    
    def _extract_properties(
        self, 
        agent_result: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract and format property data from agent result.
        """
        properties = []
        
        try:
            # Get the agent's output
            output = agent_result.get("output", "")
            
            # Try to extract JSON from intermediate steps
            intermediate_steps = agent_result.get("intermediate_steps", [])
            
            for action, observation in intermediate_steps:
                if action.tool == "airbnb_search":
                    # Parse the observation (tool output)
                    try:
                        search_results = json.loads(observation)
                        
                        # Extract properties from search results
                        if "searchResults" in search_results:
                            raw_properties = search_results["searchResults"][:10]
                            
                            for prop in raw_properties:
                                property_data = self._format_property(prop)
                                if property_data:
                                    properties.append(property_data)
                        
                    except json.JSONDecodeError:
                        continue
            
            return properties[:10]  # Ensure max 10 properties
            
        except Exception as e:
            print(f"Error extracting properties: {e}")
            return []
    
    def _format_property(self, raw_property: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw property data into standardized structure.
        """
        try:
            # Extract key fields
            prop_id = raw_property.get("id", "")
            url = raw_property.get("url", "")
            
            # Get name from nested structure
            name = ""
            if "demandStayListing" in raw_property:
                desc = raw_property["demandStayListing"].get("description", {})
                name_obj = desc.get("name", {})
                name = name_obj.get("localizedStringWithTranslationPreference", "")
            
            # Get rating
            rating_label = raw_property.get("avgRatingA11yLabel", "")
            rating = self._extract_rating(rating_label)
            
            # Get price
            price = ""
            if "structuredDisplayPrice" in raw_property:
                price_info = raw_property["structuredDisplayPrice"].get("primaryLine", {})
                price = price_info.get("accessibilityLabel", "")
            
            # Get accommodation info
            structured_content = raw_property.get("structuredContent", {})
            primary_line = structured_content.get("primaryLine", "")
            
            # Get badges (Guest favourite, Superhost, etc.)
            badges = raw_property.get("badges", "")
            
            return {
                "id": prop_id,
                "name": name,
                "url": url,
                "price": price,
                "rating": rating,
                "accommodation": primary_line,
                "badges": badges,
                "raw_data": raw_property  # Keep for later analysis
            }
            
        except Exception as e:
            print(f"Error formatting property: {e}")
            return None
    
    def _extract_rating(self, rating_label: str) -> float:
        """
        Extract numeric rating from accessibility label.
        Example: "4.95 out of 5 average rating, 62 reviews" -> 4.95
        """
        try:
            if not rating_label:
                return 0.0
            
            parts = rating_label.split()
            if parts:
                return float(parts[0])
            return 0.0
            
        except (ValueError, IndexError):
            return 0.0


def create_property_agent(model_name: str = "gpt-4") -> PropertyAgent:
    """
    Factory function to create a property agent.
    
    Args:
        model_name: OpenAI model to use
        
    Returns:
        Configured PropertyAgent instance
    """
    return PropertyAgent(model_name=model_name)

