"""
Analysis Agent - Analyzes and scores properties against requirements
"""
import json
import os
from typing import Dict, Any, List
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from ..prompts.agent_prompts import ANALYSIS_AGENT_PROMPT
from ..tools.airbnb_tools import airbnb_listing_details_tool

# Load environment variables
load_dotenv()


class AnalysisAgent:
    """
    Agent that analyzes properties in detail and scores them against requirements.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the analysis agent.
        
        Args:
            model_name: OpenAI model to use
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create agent with listing details tool
        self.tools = [airbnb_listing_details_tool]
        self.agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            ANALYSIS_AGENT_PROMPT
        )
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=15,  # Need more iterations for analyzing 10 properties
            return_intermediate_steps=True
        )
    
    def analyze(
        self,
        properties: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze properties against requirements and score them.
        
        Args:
            properties: List of properties from property agent
            requirements: Parsed travel requirements
            
        Returns:
            List of analyzed properties with scores, pros, cons
        """
        if not properties:
            return []
        
        try:
            # Prepare property IDs and data
            property_ids = [p["id"] for p in properties]
            property_data = json.dumps(properties, indent=2)
            requirements_str = json.dumps(requirements, indent=2)
            
            # Execute agent
            result = self.executor.invoke({
                "property_ids": property_ids,
                "property_data": property_data,
                "requirements": requirements_str
            })
            
            # Merge analysis with original property data
            analyzed_properties = self._merge_analysis(properties, result, requirements)
            
            # Sort by score
            analyzed_properties.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return analyzed_properties[:10]
            
        except Exception as e:
            print(f"Error analyzing properties: {e}")
            # Return properties with basic scores if analysis fails
            return self._fallback_analysis(properties, requirements)
    
    def _merge_analysis(
        self,
        properties: List[Dict[str, Any]],
        agent_result: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Merge analysis results with property data.
        """
        analyzed = []
        
        try:
            # Try to extract analysis from agent output
            output = agent_result.get("output", "")
            
            # For each property, create analyzed version
            for prop in properties:
                analyzed_prop = prop.copy()
                
                # Add basic score if not from agent
                if "score" not in analyzed_prop:
                    analyzed_prop["score"] = self._calculate_basic_score(prop, requirements)
                
                # Add pros/cons if not present
                if "pros" not in analyzed_prop:
                    analyzed_prop["pros"] = self._extract_pros(prop)
                if "cons" not in analyzed_prop:
                    analyzed_prop["cons"] = []
                
                # Add location info
                if "location" not in analyzed_prop:
                    analyzed_prop["location"] = requirements.get("destination", "")
                
                analyzed.append(analyzed_prop)
            
            return analyzed
            
        except Exception as e:
            print(f"Error merging analysis: {e}")
            return self._fallback_analysis(properties, requirements)
    
    def _calculate_basic_score(
        self,
        property: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> int:
        """
        Calculate a basic score for a property.
        """
        score = 50  # Base score
        
        # Add points for rating
        rating = property.get("rating", 0)
        if rating >= 4.8:
            score += 20
        elif rating >= 4.5:
            score += 15
        elif rating >= 4.0:
            score += 10
        
        # Add points for badges
        badges = property.get("badges", "").lower()
        if "guest favourite" in badges:
            score += 10
        if "superhost" in badges:
            score += 10
        
        # Check price (basic estimation)
        price_str = property.get("price", "")
        budget = requirements.get("budget", {})
        if budget.get("max"):
            # This is a simplified check - would need actual price parsing
            score += 10
        
        return min(score, 100)
    
    def _extract_pros(self, property: Dict[str, Any]) -> List[str]:
        """
        Extract basic pros from property data.
        """
        pros = []
        
        # High rating
        rating = property.get("rating", 0)
        if rating >= 4.8:
            pros.append(f"Excellent rating: {rating}/5")
        
        # Badges
        badges = property.get("badges", "")
        if badges:
            pros.append(badges)
        
        # Accommodation info
        accom = property.get("accommodation", "")
        if accom:
            pros.append(accom)
        
        return pros
    
    def _fallback_analysis(
        self,
        properties: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Provide fallback analysis if agent fails.
        """
        analyzed = []
        
        for prop in properties:
            prop_copy = prop.copy()
            prop_copy["score"] = self._calculate_basic_score(prop, requirements)
            prop_copy["pros"] = self._extract_pros(prop)
            prop_copy["cons"] = ["Detailed analysis unavailable"]
            prop_copy["location"] = requirements.get("destination", "")
            analyzed.append(prop_copy)
        
        # Sort by score
        analyzed.sort(key=lambda x: x["score"], reverse=True)
        
        return analyzed


def create_analysis_agent(model_name: str = "gpt-4") -> AnalysisAgent:
    """
    Factory function to create an analysis agent.
    
    Args:
        model_name: OpenAI model to use
        
    Returns:
        Configured AnalysisAgent instance
    """
    return AnalysisAgent(model_name=model_name)

