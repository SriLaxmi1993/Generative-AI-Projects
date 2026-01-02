"""
Main LangGraph workflow for News TL;DR Agent
Defines the graph state, node functions, decision logic, and workflow construction
"""

import os
import re
import logging
from typing import TypedDict, Annotated, List, Dict, Any
from datetime import datetime

from langgraph.graph import Graph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

import config
import tools
import utils

logger = logging.getLogger(__name__)

# Initialize LLM (will be set up in the module)
llm: ChatOpenAI = None


class GraphState(TypedDict):
    """State structure for the LangGraph workflow"""
    news_query: Annotated[str, "Input query to extract news search parameters from."]
    num_searches_remaining: Annotated[int, "Number of articles to search for."]
    newsapi_params: Annotated[dict, "Structured argument for the News API."]
    past_searches: Annotated[List[dict], "List of search params already used."]
    articles_metadata: Annotated[List[dict], "Article metadata response from the News API"]
    scraped_urls: Annotated[List[str], "List of urls already scraped."]
    num_articles_tldr: Annotated[int, "Number of articles to create TL;DR for."]
    potential_articles: Annotated[List[Dict[str, str]], "Article with full text to consider summarizing."]
    tldr_articles: Annotated[List[Dict[str, str]], "Selected article TL;DRs."]
    formatted_results: Annotated[str, "Formatted results to display."]


def initialize_llm_instance():
    """Initialize the LLM instance for use in node functions"""
    global llm
    if llm is None:
        llm = config.initialize_llm()
    return llm


def generate_newsapi_params(state: GraphState) -> GraphState:
    """
    Based on the query, generate News API params using LLM.
    
    Args:
        state: Current graph state
        
    Returns:
        GraphState: Updated state with newsapi_params
    """
    initialize_llm_instance()
    
    # Initialize parser to define the structure of the response
    parser = JsonOutputParser(pydantic_object=utils.NewsApiParams)

    # Retrieve today's date
    today_date = utils.format_date()

    # Retrieve list of past search params
    past_searches = state["past_searches"]

    # Retrieve number of searches remaining
    num_searches_remaining = state["num_searches_remaining"]

    # Retrieve the user's query
    news_query = state["news_query"]

    # Format past searches for display
    past_searches_str = "\n".join([str(search) for search in past_searches]) if past_searches else "None"
    
    template = """
    Today is {today_date}.

    Create a param dict for the News API based on the user query:
    {query}

    These searches have already been made. Loosen the search terms to get more results.
    {past_searches}
    
    Following these formatting instructions:
    {format_instructions}

    Including this one, you have {num_searches_remaining} searches remaining.
    If this is your last search, use all news sources and a 30 days search range.
    """

    # Create a prompt template to merge the query, today's date, and the format instructions
    prompt_template = PromptTemplate(
        template=template,
        input_variables=["today_date", "query", "past_searches", "num_searches_remaining"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # Create prompt chain template
    chain = prompt_template | llm | parser

    try:
        # Invoke the chain with the news api query
        result = chain.invoke({
            "query": news_query,
            "today_date": today_date,
            "past_searches": past_searches_str,
            "num_searches_remaining": num_searches_remaining
        })

        # Update the state
        state["newsapi_params"] = result
        logger.info(f"Generated NewsAPI params: {result}")
        
    except Exception as e:
        logger.error(f"Error generating NewsAPI params: {str(e)}")
        # Set default params on error
        state["newsapi_params"] = {
            "q": news_query,
            "sources": "",
            "from_param": utils.format_date(datetime.now()),
            "to": utils.format_date(),
            "language": "en",
            "sort_by": "relevancy"
        }

    return state


def retrieve_articles_metadata(state: GraphState) -> GraphState:
    """
    Using the NewsAPI params, perform API call to retrieve article metadata.
    
    Args:
        state: Current graph state
        
    Returns:
        GraphState: Updated state with articles_metadata
    """
    # Parameters generated for the News API
    newsapi_params = state["newsapi_params"]

    # Decrement the number of searches remaining
    state['num_searches_remaining'] -= 1

    try:
        # Retrieve the metadata of the new articles
        articles_response = tools.fetch_article_metadata(newsapi_params)

        # Append this search term to the past searches to avoid duplicates
        state['past_searches'].append(newsapi_params)

        # Load urls that have already been returned and scraped
        scraped_urls = state["scraped_urls"]
        potential_articles_count = len(state['potential_articles'])

        # Filter out articles that have already been scraped
        new_articles = tools.filter_new_articles(
            articles_response.get('articles', []),
            scraped_urls,
            max_articles=config.MAX_ARTICLES_TO_SCRAPE - potential_articles_count
        )

        # Reassign new articles to the state
        state["articles_metadata"] = new_articles
        logger.info(f"Retrieved {len(new_articles)} new articles")

    except Exception as e:
        logger.error(f"Error retrieving articles metadata: {str(e)}")
        state["articles_metadata"] = []

    return state


def retrieve_articles_text(state: GraphState) -> GraphState:
    """
    Web scrape to retrieve article text from URLs.
    
    Args:
        state: Current graph state
        
    Returns:
        GraphState: Updated state with potential_articles populated
    """
    # Load retrieved article metadata
    articles_metadata = state["articles_metadata"]

    # Create list to store valid article dicts
    potential_articles = []

    # Iterate over the articles
    for article in articles_metadata:
        # Extract the url
        url = article.get('url')
        if not url:
            continue

        # Use BeautifulSoup to extract the article content
        text = tools.scrape_article_text(url)

        if text:
            # Append article dict to list
            potential_articles.append({
                "title": article.get("title", "No title"),
                "url": url,
                "description": article.get("description", ""),
                "text": text
            })

            # Append the url to the processed urls
            state["scraped_urls"].append(url)
            logger.info(f"Successfully scraped article: {article.get('title', url)}")

    # Append the processed articles to the state
    state["potential_articles"].extend(potential_articles)
    logger.info(f"Total potential articles: {len(state['potential_articles'])}")

    return state


def select_top_urls(state: GraphState) -> GraphState:
    """
    Based on the article synopses, choose the top-n articles to summarize.
    
    Args:
        state: Current graph state
        
    Returns:
        GraphState: Updated state with tldr_articles selected
    """
    initialize_llm_instance()
    
    news_query = state["news_query"]
    num_articles_tldr = state["num_articles_tldr"]
    
    # Load all processed articles with full text but no summaries
    potential_articles = state["potential_articles"]

    if not potential_articles:
        logger.warning("No potential articles to select from")
        state["tldr_articles"] = []
        return state

    # Format the metadata
    formatted_metadata = utils.format_article_metadata(potential_articles)

    prompt = f"""
    Based on the user news query:
    {news_query}

    Reply with a list of strings of up to {num_articles_tldr} relevant urls.
    Don't add any urls that are not relevant or aren't listed specifically.
    {formatted_metadata}
    """
    
    try:
        result = llm.invoke(prompt).content

        # Use regex to extract the urls as a list
        urls = utils.extract_urls_from_text(result)

        # Add the selected article metadata to the state
        tldr_articles = [article for article in potential_articles if article['url'] in urls]
        
        logger.info(f"Selected {len(tldr_articles)} articles for TL;DR")
        state["tldr_articles"] = tldr_articles
        
    except Exception as e:
        logger.error(f"Error selecting articles: {str(e)}")
        # Fallback: select first N articles
        tldr_articles = potential_articles[:num_articles_tldr]
        state["tldr_articles"] = tldr_articles

    return state


async def summarize_articles_parallel(state: GraphState) -> GraphState:
    """
    Summarize the articles based on full text.
    
    Args:
        state: Current graph state
        
    Returns:
        GraphState: Updated state with summaries added to tldr_articles
    """
    initialize_llm_instance()
    
    tldr_articles = state["tldr_articles"]

    prompt = """
    Create a * bulleted summarizing tldr for the article:
    {text}
      
    Be sure to follow the following format exactly with nothing else:
    {title}
    {url}
    * tl;dr bulleted summary
    * use bullet points for each sentence
    """

    # Iterate over the selected articles and collect summaries
    for i in range(len(tldr_articles)):
        text = tldr_articles[i]["text"]
        title = tldr_articles[i]["title"]
        url = tldr_articles[i]["url"]
        
        try:
            # Invoke the llm
            result = llm.invoke(prompt.format(title=title, url=url, text=text))
            tldr_articles[i]["summary"] = result.content
            logger.info(f"Generated summary for article {i+1}/{len(tldr_articles)}")
        except Exception as e:
            logger.error(f"Error summarizing article {i+1}: {str(e)}")
            tldr_articles[i]["summary"] = f"Error generating summary: {str(e)}"

    state["tldr_articles"] = tldr_articles

    return state


def format_results(state: GraphState) -> GraphState:
    """
    Format the results for display.
    
    Args:
        state: Current graph state
        
    Returns:
        GraphState: Updated state with formatted_results
    """
    # Load a list of past search queries
    q = [newsapi_params.get("q", "") for newsapi_params in state["past_searches"]]
    formatted_results = f"Here are the top {len(state['tldr_articles'])} articles based on search terms:\n{', '.join(q)}\n\n"

    # Load the summarized articles
    tldr_articles = state["tldr_articles"]

    # Format article tl;dr summaries
    article_summaries = "\n\n".join([f"{article['summary']}" for article in tldr_articles])

    # Concatenate summaries to the formatted results
    formatted_results += article_summaries

    state["formatted_results"] = formatted_results

    return state


def articles_text_decision(state: GraphState) -> str:
    """
    Check results of retrieve_articles_text to determine next step.
    
    Args:
        state: Current graph state
        
    Returns:
        str: Next node name or "END"
    """
    if state["num_searches_remaining"] == 0:
        # If no articles with text were found return END
        if len(state["potential_articles"]) == 0:
            state["formatted_results"] = "No articles with text found."
            return "END"
        # If some articles were found, move on to selecting the top urls
        else:
            return "select_top_urls"
    else:
        # If the number of articles found is less than the number of articles to summarize, continue searching
        if len(state["potential_articles"]) < state["num_articles_tldr"]:
            return "generate_newsapi_params"
        # Otherwise move on to selecting the top urls
        else:
            return "select_top_urls"


def create_workflow() -> Graph:
    """
    Create and compile the LangGraph workflow.
    
    Returns:
        Graph: Compiled workflow graph
    """
    workflow = Graph()

    workflow.set_entry_point("generate_newsapi_params")

    # Add nodes
    workflow.add_node("generate_newsapi_params", generate_newsapi_params)
    workflow.add_node("retrieve_articles_metadata", retrieve_articles_metadata)
    workflow.add_node("retrieve_articles_text", retrieve_articles_text)
    workflow.add_node("select_top_urls", select_top_urls)
    workflow.add_node("summarize_articles_parallel", summarize_articles_parallel)
    workflow.add_node("format_results", format_results)

    # Add edges
    workflow.add_edge("generate_newsapi_params", "retrieve_articles_metadata")
    workflow.add_edge("retrieve_articles_metadata", "retrieve_articles_text")
    
    # Conditional edge: decide whether to search more or proceed
    workflow.add_conditional_edges(
        "retrieve_articles_text",
        articles_text_decision,
        {
            "generate_newsapi_params": "generate_newsapi_params",
            "select_top_urls": "select_top_urls",
            "END": END
        }
    )
    
    workflow.add_edge("select_top_urls", "summarize_articles_parallel")
    
    # Conditional edge: check if we have articles to format
    workflow.add_conditional_edges(
        "summarize_articles_parallel",
        lambda state: "format_results" if len(state.get("tldr_articles", [])) > 0 else "END",
        {
            "format_results": "format_results",
            "END": END
        }
    )
    
    workflow.add_edge("format_results", END)

    return workflow.compile()


# Create the compiled app
app = create_workflow()

