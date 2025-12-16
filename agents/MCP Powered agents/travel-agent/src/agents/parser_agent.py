"""
Parser Agent - Extracts structured requirements from natural language queries
"""
import json
import os
from typing import Dict, Any
from datetime import datetime, timedelta
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from ..prompts.agent_prompts import PARSER_PROMPT

# Load environment variables
load_dotenv()


class ParserAgent:
    """
    Agent that parses user travel queries into structured requirements.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the parser agent.
        
        Args:
            model_name: OpenAI model to use for parsing
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,  # Deterministic parsing
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.chain = PARSER_PROMPT | self.llm | StrOutputParser()
    
    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language travel query into structured requirements.
        
        Args:
            query: User's travel request in natural language
            
        Returns:
            Dictionary with structured travel requirements
        """
        try:
            # Invoke the LLM chain
            result = self.chain.invoke({"query": query})
            
            # Parse JSON response
            requirements = json.loads(result)
            
            # Validate and normalize the requirements
            requirements = self._normalize_requirements(requirements)
            
            return requirements
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Raw response: {result}")
            # Return a default structure
            return self._get_default_requirements()
        except Exception as e:
            print(f"Error parsing query: {e}")
            return self._get_default_requirements()
    
    def _normalize_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate parsed requirements.
        """
        # Ensure all expected fields exist
        defaults = self._get_default_requirements()
        
        for key, default_value in defaults.items():
            if key not in requirements:
                requirements[key] = default_value
        
        # Normalize dates to YYYY-MM-DD format
        if requirements.get("checkin_date"):
            requirements["checkin_date"] = self._normalize_date(requirements["checkin_date"])
        if requirements.get("checkout_date"):
            requirements["checkout_date"] = self._normalize_date(requirements["checkout_date"])
        
        # Ensure guests is a dict
        if not isinstance(requirements.get("guests"), dict):
            requirements["guests"] = {
                "adults": 1,
                "children": 0,
                "infants": 0,
                "pets": 0
            }
        
        # Ensure budget is a dict
        if not isinstance(requirements.get("budget"), dict):
            requirements["budget"] = {
                "min": None,
                "max": None,
                "currency": "INR"
            }
        
        return requirements
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize date string to YYYY-MM-DD format.
        """
        try:
            # Try parsing various formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # If no format matches, return as-is
            return date_str
            
        except Exception:
            return date_str
    
    def _get_default_requirements(self) -> Dict[str, Any]:
        """
        Get default requirements structure.
        """
        return {
            "destination": "",
            "origin": None,
            "checkin_date": "",
            "checkout_date": "",
            "guests": {
                "adults": 1,
                "children": 0,
                "infants": 0,
                "pets": 0
            },
            "required_amenities": [],
            "preferences": [],
            "deal_breakers": [],
            "budget": {
                "min": None,
                "max": None,
                "currency": "INR"
            }
        }


def create_parser_agent(model_name: str = "gpt-4") -> ParserAgent:
    """
    Factory function to create a parser agent.
    
    Args:
        model_name: OpenAI model to use
        
    Returns:
        Configured ParserAgent instance
    """
    return ParserAgent(model_name=model_name)

