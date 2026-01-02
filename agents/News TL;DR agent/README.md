# News TL;DR Agent

## Overview

This project demonstrates the creation of a news summarization agent that uses large language models (LLMs) for decision making and summarization, as well as NewsAPI calls for retrieving current news articles. The integration of LangGraph to coordinate sequential and cyclical processes, OpenAI to choose and condense articles, NewsAPI to retrieve relevant article metadata, and BeautifulSoup for web scraping allows for the generation of relevant current event article TL;DRs from a single query.

## Motivation

Although LLMs demonstrate excellent conversational and educational ability, they lack access to knowledge of current events. This project allows users to ask about a news topic they are interested in and receive a TL;DR of relevant articles. The goal is to allow users to conveniently follow their interests and stay current with their connection to world events.

## Key Components

1. **LangGraph**: Orchestrates the overall workflow, managing the flow of data between different stages of the process.
2. **GPT-4o-mini (via LangChain)**: Generates search terms, selects relevant articles, parses HTML, provides article summaries
3. **NewsAPI**: Retrieves article metadata from keyword search
4. **BeautifulSoup**: Retrieves HTML from web pages
5. **Asyncio**: Allows separate LLM calls to be made concurrently for speed efficiency

## Method

The news research follows these high-level steps:

1. **NewsAPI Parameter Creation (LLM 1)**: Given a user query, the model generates a formatted parameter dict for the news search.

2. **Article Metadata Retrieval**: An API call to NewsAPI retrieves relevant article metadata.

3. **Article Text Retrieval**: Beautiful Soup scrapes the full article text from the URLs to ensure validity.

4. **Conditional Logic**: Conditional logic either: repeats 1-3 if article threshold not reached, proceeds to step 5, or ends with no articles found.

5. **Relevant Article Selection (LLM 2)**: The model selects URLs from the most relevant n-articles for the user query based on the short synopsis provided by the API.

6. **Generate TL;DR (LLM 3+)**: A summarized set of bullet points for each article is generated concurrently with Asyncio.

This workflow is managed by LangGraph to make sure that the appropriate prompt is fed to each LLM call.

## Project Structure

```
News TL;DR agent/
├── agents.py          # Main LangGraph workflow definition
├── config.py          # Configuration and environment setup
├── tools.py           # NewsAPI and web scraping functions
├── utils.py           # Helper functions and data models
├── main.py            # CLI entry point
├── streamlit_app.py   # Streamlit web UI
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── .env.example       # Environment variable template
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at https://platform.openai.com/)
- NewsAPI key (get a free one at https://newsapi.org/ - 100 requests per day)

### 2. Installation

1. Clone or navigate to this directory:
   ```bash
   cd "News TL;DR agent"
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   NEWSAPI_KEY=your-newsapi-key-here
   ```

   **Note**: Never commit your `.env` file to version control!

### 4. Verify Configuration

You can verify your configuration by running:
```bash
python -c "import config; print(config.validate_config())"
```

## Usage

### Command Line Interface

Run the agent from the command line:

```bash
python main.py "what are the top AI news of today?"
```

**Options:**
- `--searches N`: Number of search attempts (default: 10)
- `--articles N`: Number of articles to summarize (default: 3)
- `--verbose` or `-v`: Enable verbose logging

**Examples:**

```bash
# Basic usage
python main.py "climate change news"

# Custom number of articles
python main.py "tech news" --articles 5

# More search attempts
python main.py "breaking news" --searches 15 --articles 3

# Verbose output
python main.py "AI developments" --verbose
```

### Streamlit Web UI

For a user-friendly web interface, use the Streamlit app:

```bash
streamlit run streamlit_app.py
```

This will open a web browser with an interactive interface where you can:
- Enter news queries in a text input
- Adjust the number of articles and search attempts with sliders
- View results in an organized, expandable format
- See real-time progress updates

**Features:**
- Clean, modern UI with gradient styling
- Sidebar configuration panel
- Example queries for quick testing
- Progress indicators during processing
- Formatted article display with expandable sections
- Metrics showing search statistics

### Programmatic Usage

You can also use the agent programmatically:

```python
import asyncio
from agents import app
import utils

async def get_news_summary():
    initial_state = utils.create_initial_state(
        news_query="artificial intelligence news",
        num_searches_remaining=10,
        num_articles_tldr=3
    )
    
    result = await app.ainvoke(initial_state)
    print(result["formatted_results"])

# Run it
asyncio.run(get_news_summary())
```

## Workflow Details

### Graph Nodes

1. **generate_newsapi_params**: Uses LLM to generate NewsAPI search parameters from user query
2. **retrieve_articles_metadata**: Calls NewsAPI to get article metadata
3. **retrieve_articles_text**: Scrapes full article text from URLs
4. **select_top_urls**: Uses LLM to select most relevant articles
5. **summarize_articles_parallel**: Generates TL;DR summaries for selected articles
6. **format_results**: Formats the final output

### Decision Logic

The workflow includes conditional logic that:
- Continues searching if not enough articles are found
- Stops searching if the maximum number of attempts is reached
- Proceeds to summarization when enough articles are collected
- Handles errors gracefully

## Configuration Options

You can customize the agent behavior by setting environment variables in your `.env` file:

```env
# API Keys (required)
OPENAI_API_KEY=your-key-here
NEWSAPI_KEY=your-key-here

# Model Configuration
OPENAI_MODEL=gpt-4o-mini  # Default model

# Application Settings
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
DEFAULT_NUM_SEARCHES=10  # Default search attempts
DEFAULT_NUM_ARTICLES_TLDR=3  # Default articles to summarize
MAX_ARTICLES_TO_SCRAPE=10  # Maximum articles to scrape per search
```

## Limitations

- **NewsAPI Free Tier**: Limited to 100 requests per day and articles between 1 day and 1 month old
- **Web Scraping**: Some websites may block automated scraping
- **Rate Limits**: OpenAI API has rate limits based on your subscription tier
- **Article Quality**: Summarization quality depends on the scraped article text quality

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Ensure your `.env` file exists and contains `OPENAI_API_KEY=your-key`
   - Check that you're running from the correct directory

2. **"NEWSAPI_KEY not found"**
   - Add your NewsAPI key to the `.env` file
   - Verify the key is valid at https://newsapi.org/

3. **"No articles with text found"**
   - The articles may not be accessible (blocked or removed)
   - Try a different query or increase `--searches`
   - Check your internet connection

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Verify you're using the correct Python version (3.8+)

## Future Enhancements

Although the current implementation only retrieves bulleted summaries, it could be elaborated to:
- Start a dialogue with the user that allows them to ask questions about articles
- Get more information about specific articles
- Collectively generate a coherent opinion
- Support multiple languages
- Add caching to reduce API calls
- Implement article quality scoring

## License

This project is part of the Generative AI Projects collection.

## Acknowledgments

- LangGraph for workflow orchestration
- OpenAI for language model capabilities
- NewsAPI for news article metadata
- BeautifulSoup for web scraping


