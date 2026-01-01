"""
Customer Support Agent with LangGraph

An intelligent customer support agent that categorizes queries, analyzes sentiment,
and provides appropriate responses or escalates issues when necessary.
"""
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# Set OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables.")
    print("Please set it in your .env file or environment.")
else:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


class State(TypedDict):
    """State structure for the customer support workflow."""
    query: str
    category: str
    sentiment: str
    response: str


def categorize(state: State) -> State:
    """Categorize the customer query into Technical, Billing, or General."""
    prompt = ChatPromptTemplate.from_template(
        "Categorize the following customer query into one of these categories: "
        "Technical, Billing, General. Query: {query}"
    )
    chain = prompt | ChatOpenAI(temperature=0)
    category = chain.invoke({"query": state["query"]}).content
    return {"category": category}


def analyze_sentiment(state: State) -> State:
    """Analyze the sentiment of the customer query as Positive, Neutral, or Negative."""
    prompt = ChatPromptTemplate.from_template(
        "Analyze the sentiment of the following customer query. "
        "Respond with either 'Positive', 'Neutral', or 'Negative'. Query: {query}"
    )
    chain = prompt | ChatOpenAI(temperature=0)
    sentiment = chain.invoke({"query": state["query"]}).content
    return {"sentiment": sentiment}


def handle_technical(state: State) -> State:
    """Provide a technical support response to the query."""
    prompt = ChatPromptTemplate.from_template(
        "Provide a technical support response to the following query: {query}"
    )
    chain = prompt | ChatOpenAI(temperature=0)
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}


def handle_billing(state: State) -> State:
    """Provide a billing support response to the query."""
    prompt = ChatPromptTemplate.from_template(
        "Provide a billing support response to the following query: {query}"
    )
    chain = prompt | ChatOpenAI(temperature=0)
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}


def handle_general(state: State) -> State:
    """Provide a general support response to the query."""
    prompt = ChatPromptTemplate.from_template(
        "Provide a general support response to the following query: {query}"
    )
    chain = prompt | ChatOpenAI(temperature=0)
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}


def escalate(state: State) -> State:
    """Escalate the query to a human agent due to negative sentiment."""
    return {"response": "This query has been escalated to a human agent due to its negative sentiment."}


def route_query(state: State) -> str:
    """Route the query based on its sentiment and category."""
    if state["sentiment"] == "Negative":
        return "escalate"
    elif state["category"] == "Technical":
        return "handle_technical"
    elif state["category"] == "Billing":
        return "handle_billing"
    else:
        return "handle_general"


# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("categorize", categorize)
workflow.add_node("analyze_sentiment", analyze_sentiment)
workflow.add_node("handle_technical", handle_technical)
workflow.add_node("handle_billing", handle_billing)
workflow.add_node("handle_general", handle_general)
workflow.add_node("escalate", escalate)

# Add edges
workflow.add_edge("categorize", "analyze_sentiment")
workflow.add_conditional_edges(
    "analyze_sentiment",
    route_query,
    {
        "handle_technical": "handle_technical",
        "handle_billing": "handle_billing",
        "handle_general": "handle_general",
        "escalate": "escalate"
    }
)
workflow.add_edge("handle_technical", END)
workflow.add_edge("handle_billing", END)
workflow.add_edge("handle_general", END)
workflow.add_edge("escalate", END)

# Set entry point
workflow.set_entry_point("categorize")

# Compile the graph
app = workflow.compile()


def run_customer_support(query: str) -> Dict[str, str]:
    """Process a customer query through the LangGraph workflow.
    
    Args:
        query (str): The customer's query
        
    Returns:
        Dict[str, str]: A dictionary containing the query's category, sentiment, and response
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set. Please configure it in your .env file.")
    
    results = app.invoke({"query": query})
    return {
        "category": results["category"],
        "sentiment": results["sentiment"],
        "response": results["response"]
    }


def main():
    """Main function to run the customer support agent."""
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY is not set.")
        print("Please create a .env file with your OPENAI_API_KEY or set it as an environment variable.")
        sys.exit(1)
    
    # Check if query is provided as command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = run_customer_support(query)
        print(f"\nQuery: {query}")
        print(f"Category: {result['category']}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Response: {result['response']}\n")
    else:
        # Run example queries
        print("=" * 80)
        print("Customer Support Agent - Example Queries")
        print("=" * 80)
        
        example_queries = [
            ("My internet connection keeps dropping. Can you help?", "Escalation case (negative sentiment)"),
            ("I need help talking to chatGPT", "Technical query"),
            ("where can i find my receipt?", "Billing query"),
            ("What are your business hours?", "General query")
        ]
        
        for query, description in example_queries:
            print(f"\n{'-' * 80}")
            print(f"Example: {description}")
            print(f"Query: {query}")
            print(f"{'-' * 80}")
            try:
                result = run_customer_support(query)
                print(f"Category: {result['category']}")
                print(f"Sentiment: {result['sentiment']}")
                print(f"Response: {result['response']}")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        print(f"\n{'-' * 80}")
        print("To use with your own query, run:")
        print("  python app.py 'Your query here'")
        print("=" * 80)


if __name__ == "__main__":
    main()

