# Multi-Agent Newsletter Pipeline with LangGraph

## Overview

Multi-Agent Newsletter Pipeline is an intelligent system that aggregates, analyzes, and synthesizes content from multiple newsletter sources. Built with LangGraph, this system uses a 3-agent architecture to fetch posts, extract metadata, identify themes, rank trends, and generate newsletter drafts with proper citations.

## Architecture

### Multi-Agent Pipeline (3 Agents)

1. **Fetcher Agent**: Retrieves posts from newsletter sources
   - Tries RSS feeds first, falls back to web scraping
   - Filters posts by time window (default: 14 days)
   - Limits items per source (default: 10)

2. **Analysis Agent**: Combined analysis agent that:
   - Extracts and normalizes metadata (title, date, author, summary, URL, tags)
   - Identifies common themes and clusters posts using hybrid approach (embeddings + LLM analysis)
   - Ranks topics by trendiness: `trendiness = recency × cross-source frequency × salience`

3. **Newsletter Generator Agent**: Produces formatted newsletter draft
   - Focuses on top trending topic
   - Includes proper citations [1], [2], etc.
   - Formats output in Markdown with headline, TL;DR, key developments

## Newsletter Sources

The system fetches from the following allowlist:
- https://www.news.aakashg.com/
- https://www.theunwindai.com/
- https://creatoreconomy.so/
- https://www.lennysnewsletter.com/
- https://ruben.substack.com/

## Features

- **Multi-Source Aggregation**: Fetches posts from multiple newsletter sources
- **RSS & Web Scraping**: Automatically tries RSS feeds, falls back to web scraping
- **Metadata Extraction**: Normalizes post metadata with structured output
- **Theme Clustering**: Uses hybrid approach (embeddings + LLM) for semantic clustering
- **Trend Ranking**: Calculates trendiness scores based on recency, frequency, and salience
- **Newsletter Generation**: Creates formatted newsletter drafts with citations
- **Guardrails**: Implements "Data Not Available" handling, citation system, and objective tone
- **Streamlit UI**: User-friendly interface with configuration options

## Technologies Used

- **Programming Language**: Python 3.10+
- **Framework**: [LangChain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- **Database**: [Qdrant](https://qdrant.tech/) for vector storage and semantic search
- **Models**:
  - Embeddings: [Google Gemini API (embedding-001)](https://ai.google.dev/gemini-api/docs/embeddings)
  - Chat: [Google Gemini API (gemini-2.0-flash)](https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.0-flash)
- **Libraries**:
  - `feedparser` for RSS feed parsing
  - `beautifulsoup4` for web scraping
  - `python-dateutil` for date parsing
  - `requests` for HTTP requests
- **User Interface**: [Streamlit](https://docs.streamlit.io/)

## Requirements

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Get API Keys**:
   - **Google Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Qdrant Host URL**: Your Qdrant instance URL
   - **Qdrant API Key**: Your Qdrant API key

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

4. **Use the Application**:
   - Configure API keys in the sidebar
   - Adjust pipeline configuration (time window, max items per source)
   - Click "Generate Newsletter" to run the pipeline
   - Download the generated newsletter draft

## Configuration Options

- **Time Window (days)**: Consider items published within this window (default: 14)
- **Max Items per Source**: Maximum number of items to fetch per source (default: 10)
- **Language**: Currently supports "en" (English)

## Newsletter Output Format

The generated newsletter includes:
- **Headline**: Objective and specific
- **TL;DR**: One sentence summary (≤40 words)
- **Why it matters**: 3 bullet points
- **Key developments**: Bulleted list with citations [1], [2], etc.
- **Sources**: Full source URLs mapped to citation numbers

## Guardrails

- **No Hallucination**: Uses only data from fetched posts
- **Data Not Available**: Writes exactly "Data Not Available" for missing data
- **Objective Tone**: Keeps tone factual and non-opinionated
- **Valid Markdown**: All tables and formatting are valid Markdown
- **Proper Citations**: Inline numeric footnotes [1], [2] mapped to Sources section

## Workflow

1. **Fetcher Agent** retrieves posts from all sources
2. **Analysis Agent** processes posts:
   - Extracts normalized metadata
   - Creates embeddings and stores in Qdrant
   - Identifies themes using hybrid approach
   - Ranks topics by trendiness
3. **Newsletter Generator Agent** creates formatted draft:
   - Focuses on top trending topic
   - Formats with proper structure
   - Adds citations and sources section

## License

See LICENSE file for details.
