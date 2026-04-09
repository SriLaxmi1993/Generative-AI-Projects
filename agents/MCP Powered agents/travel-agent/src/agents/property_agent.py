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
            max_iterations=2,  # Reduced to avoid context issues
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )
    
    def search(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for properties matching the requirements.
        
        Args:
            requirements: Parsed travel requirements
            
        Returns:
            List of property dictionaries with details and URLs
        """
        # Keep the codepath deterministic and robust by using direct MCP tool parsing.
        # The LLM+tool loop can exceed context window with large Airbnb payloads.
        properties = self._direct_search(requirements)
        if properties:
            return properties

        # Fallback to agent path only if direct search unexpectedly fails.
        try:
            requirements_str = json.dumps(requirements, indent=2)
            result = self.executor.invoke({"requirements": requirements_str})
            return self._extract_properties(result, requirements)
        except Exception as e:
            print(f"Error searching properties: {e}")
            return []
    
    def _direct_search(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Direct search bypassing agent (fallback for context issues).
        """
        try:
            from ..tools.airbnb_tools import airbnb_search_wrapper
            
            location = requirements.get("destination", "")
            checkin = requirements.get("checkin_date", "")
            checkout = requirements.get("checkout_date", "")
            guests = requirements.get("guests", {})
            budget = requirements.get("budget", {})
            
            result_str = airbnb_search_wrapper(
                location=location,
                checkin=checkin,
                checkout=checkout,
                adults=guests.get("adults", 1),
                children=guests.get("children", 0),
                infants=guests.get("infants", 0),
                pets=guests.get("pets", 0),
                min_price=budget.get("min"),
                max_price=budget.get("max")
            )
            
            # Parse and extract - handle MCP response format
            search_results = None
            try:
                # Try parsing as JSON
                parsed = json.loads(result_str)
                
                # Handle MCP content array format
                if isinstance(parsed, dict):
                    if "content" in parsed:
                        content = parsed["content"]
                        if isinstance(content, list) and len(content) > 0:
                            text_content = content[0].get("text", "")
                            if text_content:
                                try:
                                    search_results = json.loads(text_content)
                                except json.JSONDecodeError:
                                    # Extract JSON from text
                                    start_idx = text_content.find('{')
                                    end_idx = text_content.rfind('}')
                                    if start_idx != -1 and end_idx > start_idx:
                                        json_str = text_content[start_idx:end_idx+1]
                                        search_results = json.loads(json_str)
                    elif "searchResults" in parsed:
                        search_results = parsed
                elif isinstance(parsed, dict) and "searchResults" in parsed:
                    search_results = parsed
            except json.JSONDecodeError:
                # Try to extract JSON from string
                if '"searchResults"' in result_str:
                    start_idx = result_str.find('{')
                    end_idx = result_str.rfind('}')
                    if start_idx != -1 and end_idx > start_idx:
                        json_str = result_str[start_idx:end_idx+1]
                        try:
                            search_results = json.loads(json_str)
                        except json.JSONDecodeError:
                            pass
            
            properties = []
            
            if search_results and "searchResults" in search_results:
                for prop in search_results["searchResults"][:10]:
                    formatted = self._format_property(prop, requirements)
                    if formatted:
                        properties.append(formatted)
            
            return properties
            
        except Exception as e:
            print(f"Direct search failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_from_failed_agent(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract properties from agent's intermediate steps even if agent failed.
        """
        # This would require access to the executor's state, which is tricky
        # For now, fall back to direct search
        return self._direct_search(requirements)
    
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
            # Try to extract JSON from intermediate steps
            intermediate_steps = agent_result.get("intermediate_steps", [])
            
            for action, observation in intermediate_steps:
                if action.tool == "airbnb_search":
                    # Parse the observation (tool output)
                    try:
                        # Handle different response formats
                        search_results = None
                        
                        # Try parsing as direct JSON
                        if isinstance(observation, str):
                            try:
                                search_results = json.loads(observation)
                            except json.JSONDecodeError:
                                # Try to extract JSON from text content
                                # Some MCP tools wrap responses in content arrays
                                if '"content"' in observation or '"searchResults"' in observation:
                                    # Try to find JSON object in the string
                                    start_idx = observation.find('{')
                                    if start_idx != -1:
                                        # Find matching closing brace
                                        brace_count = 0
                                        end_idx = start_idx
                                        for i in range(start_idx, len(observation)):
                                            if observation[i] == '{':
                                                brace_count += 1
                                            elif observation[i] == '}':
                                                brace_count -= 1
                                                if brace_count == 0:
                                                    end_idx = i + 1
                                                    break
                                        if end_idx > start_idx:
                                            json_str = observation[start_idx:end_idx]
                                            search_results = json.loads(json_str)
                        
                        # Handle structured content format (MCP response format)
                        if not search_results:
                            # Check if observation is already a dict (from MCP)
                            if isinstance(observation, dict):
                                # Handle MCP content array format
                                if "content" in observation:
                                    content = observation["content"]
                                    if isinstance(content, list) and len(content) > 0:
                                        # Get text from first content item
                                        first_item = content[0]
                                        if isinstance(first_item, dict):
                                            text_content = first_item.get("text", "")
                                            if text_content:
                                                try:
                                                    search_results = json.loads(text_content)
                                                except json.JSONDecodeError:
                                                    # Try to extract JSON from text (find first { to last })
                                                    start_idx = text_content.find('{')
                                                    if start_idx != -1:
                                                        # Find the last } to get complete JSON
                                                        end_idx = text_content.rfind('}')
                                                        if end_idx > start_idx:
                                                            json_str = text_content[start_idx:end_idx+1]
                                                            try:
                                                                search_results = json.loads(json_str)
                                                            except json.JSONDecodeError:
                                                                pass
                                # Handle structuredContent format
                                elif "structuredContent" in observation:
                                    result_text = observation.get("structuredContent", {}).get("result", "")
                                    if result_text:
                                        try:
                                            search_results = json.loads(result_text)
                                        except json.JSONDecodeError:
                                            pass
                            # If observation is a string, try to parse it
                            elif isinstance(observation, str):
                                # Look for JSON in the string
                                if '"searchResults"' in observation or '"content"' in observation:
                                    start_idx = observation.find('{')
                                    if start_idx != -1:
                                        end_idx = observation.rfind('}')
                                        if end_idx > start_idx:
                                            json_str = observation[start_idx:end_idx+1]
                                            try:
                                                search_results = json.loads(json_str)
                                            except json.JSONDecodeError:
                                                pass
                        
                        # Extract properties from search results
                        if search_results:
                            # Handle different response structures
                            raw_properties = []
                            
                            if "searchResults" in search_results:
                                raw_properties = search_results["searchResults"]
                            elif isinstance(search_results, list):
                                raw_properties = search_results
                            elif "results" in search_results:
                                raw_properties = search_results["results"]
                            
                            # Limit to 10 properties to avoid context issues
                            for prop in raw_properties[:10]:
                                property_data = self._format_property(prop, requirements)
                                if property_data:
                                    properties.append(property_data)
                                    if len(properties) >= 10:
                                        break
                        
                    except Exception as e:
                        print(f"Error parsing property data: {e}")
                        continue
            
            return properties[:10]  # Ensure max 10 properties
            
        except Exception as e:
            print(f"Error extracting properties: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _format_property(self, raw_property: Dict[str, Any], requirements: Dict[str, Any] = None) -> Dict[str, Any]:
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
            
            # Fix URL to use requested dates if provided
            if requirements and url:
                checkin = requirements.get("checkin_date", "")
                checkout = requirements.get("checkout_date", "")
                guests = requirements.get("guests", {})
                
                if checkin and checkout:
                    # Rebuild URL with correct dates
                    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    
                    # Update dates
                    params['checkin'] = [checkin]
                    params['checkout'] = [checkout]
                    
                    # Update guests
                    params['adults'] = [str(guests.get("adults", 1))]
                    params['children'] = [str(guests.get("children", 0))]
                    params['infants'] = [str(guests.get("infants", 0))]
                    if guests.get("pets", 0) > 0:
                        params['pets'] = [str(guests.get("pets", 0))]
                    
                    # Rebuild URL
                    new_query = urlencode(params, doseq=True)
                    url = urlunparse((
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        parsed.params,
                        new_query,
                        parsed.fragment
                    ))
            
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

