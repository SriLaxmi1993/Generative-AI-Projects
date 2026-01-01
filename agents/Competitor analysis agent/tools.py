"""
Custom tools for Competitor Analysis System
Includes SerpAPI wrapper and data processing utilities
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from serpapi import GoogleSearch
from crewai_tools import BaseTool
from pydantic import Field
import config

logger = logging.getLogger(__name__)


class CompetitorSearchTool(BaseTool):
    """Tool for searching competitor information using SerpAPI"""
    
    name: str = "Competitor Search Tool"
    description: str = """Search for competitor information, company details, pricing, and reviews.
    Input should be a search query string. Returns structured information about competitors."""
    
    api_key: str = Field(default=config.SERPAPI_API_KEY)
    max_results: int = Field(default=10)
    
    def _run(self, query: str) -> str:
        """Execute competitor search"""
        try:
            logger.info(f"Searching for: {query}")
            
            # Execute search
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": self.max_results,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Process results
            processed_results = self._process_search_results(results)
            
            return json.dumps(processed_results, indent=2)
            
        except Exception as e:
            logger.error(f"Search error for query '{query}': {str(e)}")
            return json.dumps({
                "error": str(e),
                "query": query,
                "results": []
            })
    
    def _process_search_results(self, results: Dict) -> Dict:
        """Process and structure search results"""
        processed = {
            "organic_results": [],
            "knowledge_graph": {},
            "related_searches": []
        }
        
        # Extract organic results
        if "organic_results" in results:
            for result in results["organic_results"][:self.max_results]:
                processed["organic_results"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0)
                })
        
        # Extract knowledge graph if available
        if "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            processed["knowledge_graph"] = {
                "title": kg.get("title", ""),
                "type": kg.get("type", ""),
                "description": kg.get("description", ""),
                "website": kg.get("website", "")
            }
        
        # Extract related searches
        if "related_searches" in results:
            processed["related_searches"] = [
                rs.get("query", "") for rs in results["related_searches"]
            ]
        
        return processed


class CompanyInfoTool(BaseTool):
    """Tool for getting detailed company information"""
    
    name: str = "Company Information Tool"
    description: str = """Get detailed information about a specific company including 
    description, website, industry, and key facts. Input should be the company name."""
    
    api_key: str = Field(default=config.SERPAPI_API_KEY)
    
    def _run(self, company_name: str) -> str:
        """Get company information"""
        try:
            logger.info(f"Getting info for company: {company_name}")
            
            # Search for company information
            params = {
                "q": f"{company_name} company information",
                "api_key": self.api_key,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract company info
            company_info = self._extract_company_info(results, company_name)
            
            return json.dumps(company_info, indent=2)
            
        except Exception as e:
            logger.error(f"Error getting company info for '{company_name}': {str(e)}")
            return json.dumps({
                "error": str(e),
                "company_name": company_name
            })
    
    def _extract_company_info(self, results: Dict, company_name: str) -> Dict:
        """Extract structured company information from search results"""
        info = {
            "name": company_name,
            "description": "",
            "website": "",
            "industry": "",
            "founded": "",
            "headquarters": "",
            "key_facts": []
        }
        
        # Try to get info from knowledge graph
        if "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            info["description"] = kg.get("description", "")
            info["website"] = kg.get("website", "")
            info["founded"] = kg.get("founded", "")
            info["headquarters"] = kg.get("headquarters", "")
            
            # Extract key facts
            if "key_facts" in kg:
                info["key_facts"] = kg.get("key_facts", [])
        
        # Fallback to organic results for description
        if not info["description"] and "organic_results" in results:
            if results["organic_results"]:
                info["description"] = results["organic_results"][0].get("snippet", "")
                info["website"] = results["organic_results"][0].get("link", "")
        
        return info


class PricingSearchTool(BaseTool):
    """Tool for finding pricing information"""
    
    name: str = "Pricing Search Tool"
    description: str = """Search for pricing information for a specific company or product.
    Input should be the company/product name. Returns pricing details if available."""
    
    api_key: str = Field(default=config.SERPAPI_API_KEY)
    
    def _run(self, company_name: str) -> str:
        """Search for pricing information"""
        try:
            logger.info(f"Searching pricing for: {company_name}")
            
            # Search for pricing
            params = {
                "q": f"{company_name} pricing plans cost",
                "api_key": self.api_key,
                "engine": "google",
                "num": 5
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract pricing info
            pricing_info = self._extract_pricing_info(results, company_name)
            
            return json.dumps(pricing_info, indent=2)
            
        except Exception as e:
            logger.error(f"Error searching pricing for '{company_name}': {str(e)}")
            return json.dumps({
                "error": str(e),
                "company_name": company_name
            })
    
    def _extract_pricing_info(self, results: Dict, company_name: str) -> Dict:
        """Extract pricing information from search results"""
        pricing = {
            "company_name": company_name,
            "pricing_found": False,
            "pricing_details": [],
            "sources": []
        }
        
        if "organic_results" in results:
            for result in results["organic_results"]:
                snippet = result.get("snippet", "").lower()
                
                # Look for pricing indicators
                if any(keyword in snippet for keyword in ["price", "pricing", "$", "cost", "plan"]):
                    pricing["pricing_found"] = True
                    pricing["pricing_details"].append({
                        "source": result.get("title", ""),
                        "link": result.get("link", ""),
                        "description": result.get("snippet", "")
                    })
                    pricing["sources"].append(result.get("link", ""))
        
        return pricing


class ReviewSearchTool(BaseTool):
    """Tool for finding customer reviews and sentiment"""
    
    name: str = "Review Search Tool"
    description: str = """Search for customer reviews and feedback about a company or product.
    Input should be the company/product name. Returns review summaries and sentiment."""
    
    api_key: str = Field(default=config.SERPAPI_API_KEY)
    
    def _run(self, company_name: str) -> str:
        """Search for reviews"""
        try:
            logger.info(f"Searching reviews for: {company_name}")
            
            # Search for reviews
            params = {
                "q": f"{company_name} reviews customer feedback",
                "api_key": self.api_key,
                "engine": "google",
                "num": 5
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract review info
            review_info = self._extract_review_info(results, company_name)
            
            return json.dumps(review_info, indent=2)
            
        except Exception as e:
            logger.error(f"Error searching reviews for '{company_name}': {str(e)}")
            return json.dumps({
                "error": str(e),
                "company_name": company_name
            })
    
    def _extract_review_info(self, results: Dict, company_name: str) -> Dict:
        """Extract review information from search results"""
        reviews = {
            "company_name": company_name,
            "reviews_found": False,
            "review_sources": [],
            "sentiment_indicators": []
        }
        
        if "organic_results" in results:
            for result in results["organic_results"]:
                snippet = result.get("snippet", "")
                
                # Look for review indicators
                if any(keyword in snippet.lower() for keyword in ["review", "rating", "customer", "feedback"]):
                    reviews["reviews_found"] = True
                    reviews["review_sources"].append({
                        "source": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": snippet
                    })
        
        return reviews


class DataProcessorTool(BaseTool):
    """Tool for processing and structuring competitor data"""
    
    name: str = "Data Processor Tool"
    description: str = """Process raw competitor data into structured format.
    Input should be JSON string of competitor data. Returns cleaned and structured data."""
    
    def _run(self, data: str) -> str:
        """Process competitor data"""
        try:
            # Parse input data
            if isinstance(data, str):
                try:
                    data_dict = json.loads(data)
                except json.JSONDecodeError:
                    data_dict = {"raw_data": data}
            else:
                data_dict = data
            
            # Structure the data
            processed = self._structure_data(data_dict)
            
            return json.dumps(processed, indent=2)
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return json.dumps({
                "error": str(e),
                "raw_data": str(data)
            })
    
    def _structure_data(self, data: Dict) -> Dict:
        """Structure data into standard format"""
        structured = {
            "competitors": [],
            "market_overview": {},
            "data_quality": "processed"
        }
        
        # Process competitor information
        if "competitors" in data:
            for comp in data["competitors"]:
                structured["competitors"].append({
                    "name": comp.get("name", ""),
                    "website": comp.get("website", ""),
                    "description": comp.get("description", ""),
                    "strengths": comp.get("strengths", []),
                    "weaknesses": comp.get("weaknesses", [])
                })
        
        return structured


# Create tool instances
competitor_search_tool = CompetitorSearchTool()
company_info_tool = CompanyInfoTool()
pricing_search_tool = PricingSearchTool()
review_search_tool = ReviewSearchTool()
data_processor_tool = DataProcessorTool()

