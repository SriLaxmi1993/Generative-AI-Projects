"""
Streamlit UI for News TL;DR Agent
Provides a user-friendly web interface for the news summarization agent
"""

import streamlit as st
import asyncio
import sys
import os

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import utils
from agents import app

# Page configuration
st.set_page_config(
    page_title="News TL;DR Agent",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #0f0f23;
    }
    .stApp {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .article-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📰 News TL;DR Agent")
st.markdown("### AI-Powered News Summarization with LangGraph")
st.markdown("Enter a news topic and get instant TL;DR summaries of the most relevant articles from current news sources.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Number of articles to summarize
    num_articles = st.slider(
        "Number of Articles",
        min_value=1,
        max_value=10,
        value=config.DEFAULT_NUM_ARTICLES_TLDR,
        help="How many articles to summarize"
    )
    
    # Number of search attempts
    num_searches = st.slider(
        "Search Attempts",
        min_value=1,
        max_value=20,
        value=config.DEFAULT_NUM_SEARCHES,
        help="Maximum number of search attempts to find articles"
    )
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.markdown("""
    This application uses **LangGraph** to orchestrate a multi-step workflow:
    
    🔍 **Step 1**: Generate NewsAPI search parameters
    📡 **Step 2**: Fetch article metadata
    🌐 **Step 3**: Scrape full article text
    🎯 **Step 4**: Select most relevant articles
    ✍️ **Step 5**: Generate TL;DR summaries
    
    Powered by:
    - **OpenAI GPT-4o-mini** for intelligent search and summarization
    - **NewsAPI** for current news articles
    - **BeautifulSoup** for web scraping
    """)
    
    st.markdown("---")
    st.markdown("**API Status:**")
    
    # Check API keys
    is_valid, message = config.validate_config()
    if is_valid:
        st.success("✅ API Keys Configured")
    else:
        st.error(f"❌ {message}")
        st.info("Please configure your API keys in the `.env` file")

# Main content area
# Query input
query = st.text_input(
    "🔍 Enter your news query",
    placeholder="e.g., AI news today, climate change, tech developments",
    help="Enter a topic or question about current news"
)

# Search button
if st.button("🚀 Get News Summaries", type="primary", use_container_width=True):
    
    if not query:
        st.warning("⚠️ Please enter a news query")
        st.stop()
    
    if not is_valid:
        st.error("❌ Please configure your API keys in the `.env` file before using the app")
        st.stop()
    
    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()
    
    try:
        # Create initial state
        initial_state = utils.create_initial_state(
            news_query=query,
            num_searches_remaining=num_searches,
            num_articles_tldr=num_articles
        )
        
        # Run the workflow asynchronously
        status_text.text("🔄 Starting workflow...")
        progress_bar.progress(10)
        
        # Use asyncio to run the async workflow
        async def run_workflow_async():
            result = await app.ainvoke(initial_state)
            return result
        
        # Run the async function
        result = asyncio.run(run_workflow_async())
        
        progress_bar.progress(90)
        status_text.text("✅ Processing complete!")
        
        # Get formatted results
        formatted_results = result.get("formatted_results", "No results generated.")
        
        # Display results
        progress_bar.progress(100)
        status_text.empty()
        progress_bar.empty()
        
        # Show results in a nice format
        results_container.markdown("---")
        results_container.markdown("## 📊 Results")
        
        # Parse and display articles nicely
        if "No articles" in formatted_results or "No results" in formatted_results:
            st.warning(formatted_results)
        else:
            # Split results by article
            articles_text = formatted_results.split("\n\n")
            
            # Display header (first part before articles)
            if len(articles_text) > 0:
                header = articles_text[0]
                st.info(header)
            
            # Display each article
            for i, article_text in enumerate(articles_text[1:], 1):
                if article_text.strip():
                    with st.expander(f"📄 Article {i}", expanded=True):
                        # Split article into lines
                        lines = article_text.split("\n")
                        
                        # Display title and URL
                        if len(lines) > 0:
                            title = lines[0].strip()
                            st.markdown(f"### {title}")
                        
                        if len(lines) > 1:
                            url = lines[1].strip()
                            if url.startswith("http"):
                                st.markdown(f"🔗 [{url}]({url})")
                        
                        # Display summary bullets
                        if len(lines) > 2:
                            summary_lines = [line.strip() for line in lines[2:] if line.strip() and line.strip().startswith("*")]
                            if summary_lines:
                                st.markdown("**Summary:**")
                                for bullet in summary_lines:
                                    st.markdown(f"  {bullet}")
        
        # Show metrics
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Articles Found", len(articles_text) - 1 if len(articles_text) > 1 else 0)
        
        with col2:
            searches_used = num_searches - result.get("num_searches_remaining", 0)
            st.metric("Searches Used", searches_used)
        
        with col3:
            articles_scraped = len(result.get("potential_articles", []))
            st.metric("Articles Scraped", articles_scraped)
        
    except KeyboardInterrupt:
        st.warning("⚠️ Process interrupted by user")
        progress_bar.empty()
        status_text.empty()
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)
        progress_bar.empty()
        status_text.empty()

else:
    # Show example queries when no search has been performed
    st.info("👆 Enter a news query above and click 'Get News Summaries' to get started!")
    
    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    
    example_queries = [
        "AI news today",
        "climate change developments",
        "tech industry updates",
        "space exploration news",
        "healthcare innovations",
        "sports highlights"
    ]
    
    cols = st.columns(3)
    for i, example in enumerate(example_queries):
        with cols[i % 3]:
            if st.button(f"🔍 {example}", key=f"example_{i}", use_container_width=True):
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 How It Works")
    
    with st.expander("Learn more about the workflow"):
        st.markdown("""
        1. **Query Processing**: Your query is analyzed to generate optimal NewsAPI search parameters
        
        2. **Article Discovery**: The system searches multiple news sources using NewsAPI
        
        3. **Content Extraction**: Full article text is scraped from the web using BeautifulSoup
        
        4. **Relevance Filtering**: An AI model selects the most relevant articles based on your query
        
        5. **Summarization**: Each selected article is summarized into concise bullet points
        
        6. **Results Display**: All summaries are formatted and presented to you
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Powered by LangGraph & OpenAI | Your queries are processed securely</p>
</div>
""", unsafe_allow_html=True)

