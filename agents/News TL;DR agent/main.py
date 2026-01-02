"""
Main entry point for News TL;DR Agent
Provides CLI interface for running the workflow
"""

import asyncio
import argparse
import logging
import sys

import config
import utils
from agents import app

logger = logging.getLogger(__name__)


async def run_workflow(
    query: str,
    num_searches_remaining: int = None,
    num_articles_tldr: int = None
) -> str:
    """
    Run the LangGraph workflow and return results.
    
    Args:
        query: User's news query
        num_searches_remaining: Number of search attempts (default from config)
        num_articles_tldr: Number of articles to summarize (default from config)
        
    Returns:
        str: Formatted results or error message
    """
    if num_searches_remaining is None:
        num_searches_remaining = config.DEFAULT_NUM_SEARCHES
    
    if num_articles_tldr is None:
        num_articles_tldr = config.DEFAULT_NUM_ARTICLES_TLDR
    
    # Create initial state
    initial_state = utils.create_initial_state(
        news_query=query,
        num_searches_remaining=num_searches_remaining,
        num_articles_tldr=num_articles_tldr
    )
    
    try:
        logger.info(f"Starting workflow with query: {query}")
        result = await app.ainvoke(initial_state)
        
        formatted_results = result.get("formatted_results", "No results generated.")
        logger.info("Workflow completed successfully")
        return formatted_results
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="News TL;DR Agent - Generate summaries of current news articles"
    )
    parser.add_argument(
        "query",
        type=str,
        help="News query to search for (e.g., 'AI news today')"
    )
    parser.add_argument(
        "--searches",
        type=int,
        default=config.DEFAULT_NUM_SEARCHES,
        help=f"Number of search attempts (default: {config.DEFAULT_NUM_SEARCHES})"
    )
    parser.add_argument(
        "--articles",
        type=int,
        default=config.DEFAULT_NUM_ARTICLES_TLDR,
        help=f"Number of articles to summarize (default: {config.DEFAULT_NUM_ARTICLES_TLDR})"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate configuration
    is_valid, message = config.validate_config()
    if not is_valid:
        print(f"Configuration Error: {message}", file=sys.stderr)
        print("\nPlease ensure you have:")
        print("1. Created a .env file in the project directory")
        print("2. Added your OPENAI_API_KEY and NEWSAPI_KEY to the .env file")
        print("\nSee .env.example for the required format.")
        sys.exit(1)
    
    # Run the workflow
    try:
        results = asyncio.run(run_workflow(
            query=args.query,
            num_searches_remaining=args.searches,
            num_articles_tldr=args.articles
        ))
        print("\n" + "="*80)
        print(results)
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        logger.exception("Fatal error in main")
        sys.exit(1)


if __name__ == "__main__":
    main()


