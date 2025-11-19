import streamlit as st
from typing import List, Dict, Any
from typing_extensions import TypedDict
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import feedparser
import requests
from bs4 import BeautifulSoup
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from uuid import uuid4
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph, START
import json
import time

st.set_page_config(page_title="Newsletter Pipeline", page_icon="📰")
st.header(":blue[Multi-Agent Newsletter Pipeline] :green[with LangGraph]")

# Configuration
SOURCES_ALLOWLIST = [
    "https://www.news.aakashg.com/",
    "https://www.theunwindai.com/",
    "https://creatoreconomy.so/",
    "https://www.lennysnewsletter.com/",
    "https://ruben.substack.com/",
]

# Initialize session state
if 'qdrant_host' not in st.session_state:
    st.session_state.qdrant_host = ""
if 'qdrant_api_key' not in st.session_state:
    st.session_state.qdrant_api_key = ""
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

def set_sidebar():
    """Setup sidebar for API keys and configuration."""
    with st.sidebar:
        st.subheader("API Configuration")
        
        qdrant_host = st.text_input("Enter your Qdrant Host URL:", value=st.session_state.qdrant_host, type="default")
        qdrant_api_key = st.text_input("Enter your Qdrant API key:", value=st.session_state.qdrant_api_key, type="password")
        gemini_api_key = st.text_input("Enter your Gemini API key:", value=st.session_state.gemini_api_key, type="password")

        if st.button("Save Configuration"):
            if qdrant_host and qdrant_api_key and gemini_api_key:
                st.session_state.qdrant_host = qdrant_host
                st.session_state.qdrant_api_key = qdrant_api_key
                st.session_state.gemini_api_key = gemini_api_key
                st.success("API keys saved!")
            else:
                st.warning("Please fill all API fields")
        
        st.subheader("Pipeline Configuration")
        time_window_days = st.number_input("Time Window (days):", min_value=1, max_value=30, value=14)
        max_items_per_source = st.number_input("Max Items per Source:", min_value=1, max_value=50, value=10)
        language = st.selectbox("Language:", ["en"], index=0)
        use_embeddings_config = st.checkbox("Enable Embeddings (for semantic clustering)", value=True, 
                                           help="Disable if experiencing timeout issues. App will work in LLM-only mode.")
        
        st.session_state.config = {
            "time_window_days": time_window_days,
            "max_items_per_source": max_items_per_source,
            "language": language,
            "use_embeddings": use_embeddings_config
        }

def initialize_components():
    """Initialize components that require API keys.
    Returns: (embedding_model, client, db) or (None, client, None) if embeddings fail.
    Embeddings are optional - app can work without them."""
    if not all([st.session_state.qdrant_host, 
               st.session_state.qdrant_api_key, 
               st.session_state.gemini_api_key]):
        return None, None, None

    embedding_model = None
    db = None
    
    # Initialize Qdrant client first (required)
    try:
        client = QdrantClient(
            url=st.session_state.qdrant_host,
            api_key=st.session_state.qdrant_api_key if st.session_state.qdrant_api_key else None,
            timeout=30
        )
    except Exception as client_error:
        st.error(f"Failed to connect to Qdrant: {str(client_error)}")
        return None, None, None

    # Try to initialize embedding model (optional - app can work without it)
    # Check if embeddings are enabled in config
    use_embeddings_config = st.session_state.get("config", {}).get("use_embeddings", True)
    
    if not use_embeddings_config:
        st.info("ℹ️ Embeddings disabled in configuration. Running in LLM-only mode.")
        embedding_model = None
    else:
        try:
            embedding_model = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=st.session_state.gemini_api_key
            )
            st.success("✅ Embedding model initialized")
        except Exception as embed_init_error:
            error_str = str(embed_init_error)
            if "504" in error_str or "Deadline" in error_str or "timeout" in error_str.lower():
                st.warning("⚠️ Embedding model initialization timed out. The app will continue without embeddings (LLM-only mode).")
            else:
                st.warning(f"⚠️ Could not initialize embedding model: {error_str[:200]}. The app will continue without embeddings.")
            # Continue without embeddings - don't fail initialization
            embedding_model = None

    # Initialize Qdrant collection (only if we have embedding model)
    if embedding_model:
        collection_name = "newsletter_db"
        # Try to get collection info to check if it exists
        try:
            client.get_collection(collection_name)
            st.info("ℹ️ Qdrant collection already exists")
        except Exception:
            # Collection doesn't exist, create it
            from qdrant_client.models import Distance, VectorParams
            # Google embedding-001 uses 768 dimensions
            embedding_dim = 768
            try:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
                )
                st.success("✅ Qdrant collection created successfully")
            except Exception as create_error:
                error_msg = str(create_error)
                if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                    st.info("ℹ️ Collection already exists")
                else:
                    st.warning(f"⚠️ Could not create collection: {error_msg[:200]}. Continuing without vector storage.")

        # Initialize vector store (only if embedding model is available)
        if embedding_model:
            try:
                db = QdrantVectorStore(
                    client=client,
                    collection_name=collection_name,
                    embedding=embedding_model
                )
            except Exception as db_init_error:
                st.warning(f"⚠️ Could not initialize vector store: {str(db_init_error)[:200]}. Continuing without vector storage.")
                db = None

    return embedding_model, client, db

# State Definition
class NewsletterState(TypedDict):
    raw_posts: List[Dict[str, Any]]
    extracted_metadata: List[Dict[str, Any]]
    themes: List[Dict[str, Any]]
    ranked_topics: List[Dict[str, Any]]
    newsletter_draft: str
    sources: Dict[int, str]
    config: Dict[str, Any]

# Helper Functions for Fetching
def try_rss_feed(url: str) -> List[Dict[str, Any]]:
    """Try to fetch posts from RSS feed."""
    try:
        # Try common RSS feed URLs
        rss_urls = [
            url.rstrip('/') + '/feed',
            url.rstrip('/') + '/rss',
            url.rstrip('/') + '/feed.xml',
            url.rstrip('/') + '/rss.xml',
            url.rstrip('/') + '/atom.xml',
        ]
        
        for rss_url in rss_urls:
            try:
                feed = feedparser.parse(rss_url)
                if feed.entries:
                    posts = []
                    for entry in feed.entries:
                        post = {
                            "title": getattr(entry, 'title', 'Data Not Available'),
                            "link": getattr(entry, 'link', url),
                            "published": getattr(entry, 'published', 'Data Not Available'),
                            "summary": getattr(entry, 'summary', getattr(entry, 'description', 'Data Not Available')),
                            "author": getattr(entry, 'author', 'Data Not Available'),
                            "source_url": url
                        }
                        posts.append(post)
                    return posts
            except:
                continue
        return []
    except Exception as e:
        return []

def scrape_web_page(url: str) -> List[Dict[str, Any]]:
    """Fallback to web scraping if RSS fails."""
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        posts = []
        # Try to find article/post links
        article_links = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in x.lower() or 'article' in x.lower() or 'entry' in x.lower()), limit=10)
        
        for article in article_links[:10]:
            title_elem = article.find(['h1', 'h2', 'h3', 'a'])
            link_elem = article.find('a', href=True)
            
            if title_elem:
                post = {
                    "title": title_elem.get_text(strip=True) or 'Data Not Available',
                    "link": link_elem['href'] if link_elem else url,
                    "published": 'Data Not Available',
                    "summary": article.get_text(strip=True)[:500] or 'Data Not Available',
                    "author": 'Data Not Available',
                    "source_url": url
                }
                posts.append(post)
        
        if not posts:
            # Fallback: create a single post from the page
            title = soup.find('title')
            posts.append({
                "title": title.get_text(strip=True) if title else 'Data Not Available',
                "link": url,
                "published": 'Data Not Available',
                "summary": soup.get_text(strip=True)[:1000] or 'Data Not Available',
                "author": 'Data Not Available',
                "source_url": url
            })
        
        return posts
    except Exception as e:
        return []

def filter_by_time_window(posts: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
    """Filter posts by time window."""
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered = []
    
    for post in posts:
        try:
            if post.get('published') and post['published'] != 'Data Not Available':
                pub_date = date_parser.parse(post['published'])
                if pub_date >= cutoff_date:
                    filtered.append(post)
            else:
                # Include posts with unknown dates
                filtered.append(post)
        except:
            # Include posts if date parsing fails
            filtered.append(post)
    
    return filtered

# Agent 1: Fetcher Agent
def fetcher_agent(state: NewsletterState) -> NewsletterState:
    """Fetches posts from newsletter sources."""
    st.info("🔍 Fetching posts from newsletter sources...")
    config = state.get("config", {})
    time_window = config.get("time_window_days", 14)
    max_items = config.get("max_items_per_source", 10)
    
    all_posts = []
    
    for source_url in SOURCES_ALLOWLIST:
        posts = try_rss_feed(source_url)
        
        if not posts:
            posts = scrape_web_page(source_url)
        
        if posts:
            # Filter by time window
            filtered_posts = filter_by_time_window(posts, time_window)
            # Limit items per source
            filtered_posts = filtered_posts[:max_items]
            all_posts.extend(filtered_posts)
    
    return {
        **state,
        "raw_posts": all_posts
    }

# Agent 2: Analysis Agent (Combined: Metadata + Themes + Ranking)
class PostMetadata(BaseModel):
    """Normalized metadata for a post."""
    title: str = Field(description="Post title")
    date: str = Field(description="Publication date in ISO format or 'Data Not Available'")
    author: str = Field(description="Author name or 'Data Not Available'")
    summary: str = Field(description="Brief summary (max 200 words)")
    url: str = Field(description="Post URL")
    tags: List[str] = Field(description="Relevant tags or topics", default_factory=list)

class ThemeCluster(BaseModel):
    """Theme cluster with posts."""
    theme: str = Field(description="Theme name")
    posts: List[int] = Field(description="Indices of posts in this cluster")
    salience: float = Field(description="Salience score (0-1)")

class RankedTopic(BaseModel):
    """Ranked topic with trendiness score."""
    topic: str = Field(description="Topic name")
    trendiness_score: float = Field(description="Trendiness score")
    recency: float = Field(description="Recency score (0-1)")
    frequency: float = Field(description="Cross-source frequency (0-1)")
    salience: float = Field(description="Salience score (0-1)")
    post_indices: List[int] = Field(description="Indices of posts related to this topic")

class AnalysisResult(BaseModel):
    """Complete analysis result."""
    metadata: List[PostMetadata]
    themes: List[ThemeCluster]
    ranked_topics: List[RankedTopic]

def analysis_agent(state: NewsletterState, embedding_model, db) -> NewsletterState:
    """Combined agent: extracts metadata, identifies themes, ranks trends."""
    st.info("🧠 Analyzing posts: extracting metadata, identifying themes, ranking trends...")
    
    raw_posts = state.get("raw_posts", [])
    if not raw_posts:
        return {
            **state,
            "extracted_metadata": [],
            "themes": [],
            "ranked_topics": []
        }
    
    gemini_api_key = st.session_state.gemini_api_key
    model = ChatGoogleGenerativeAI(
        api_key=gemini_api_key,
        temperature=0,
        model="gemini-2.0-flash"
    )
    
    try:
        # Check if embeddings are available
        use_embeddings = embedding_model is not None and db is not None
        
        if not use_embeddings:
            st.info("ℹ️ Running in LLM-only mode (embeddings not available)")
        
        # Get embeddings for clustering (hybrid approach) - only if available
        post_texts = [f"{p.get('title', '')} {p.get('summary', '')[:500]}" for p in raw_posts]
        
        # Try embedding with improved retry logic and timeout handling
        max_retries = 5
        embeddings = None
        valid_indices = None  # Track which original post indices have valid embeddings
        
        if use_embeddings and post_texts:  # Only try embeddings if model is available and we have posts
            st.info(f"🔄 Generating embeddings for {len(post_texts)} posts...")
            # Process one at a time to avoid timeout issues
            batch_size = 1
            all_embeddings = []
            failed_indices = []
            
            for i in range(0, len(post_texts), batch_size):
                batch = post_texts[i:i+batch_size]
                batch_success = False
                
                # Retry logic for each individual batch
                for attempt in range(max_retries):
                    try:
                        # Exponential backoff: 2^attempt seconds
                        if attempt > 0:
                            wait_time = min(2 ** attempt, 10)  # Cap at 10 seconds
                            st.info(f"⏳ Waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                        
                        # Generate embedding for this batch
                        batch_embeddings = embedding_model.embed_documents(batch)
                        all_embeddings.extend(batch_embeddings)
                        batch_success = True
                        
                        # Small delay between successful batches to avoid rate limiting
                        if i + batch_size < len(post_texts):
                            time.sleep(0.5)
                        break
                        
                    except Exception as embed_error:
                        error_str = str(embed_error)
                        if "504" in error_str or "Deadline" in error_str or "timeout" in error_str.lower():
                            if attempt < max_retries - 1:
                                st.warning(f"⏱️ Timeout for batch {i//batch_size + 1}/{len(post_texts)//batch_size + 1} (attempt {attempt + 1}/{max_retries})")
                                continue
                            else:
                                st.warning(f"⚠️ Failed to embed batch {i//batch_size + 1} after {max_retries} attempts. Skipping...")
                                failed_indices.append(i)
                                # Add None placeholder to maintain index alignment
                                all_embeddings.append(None)
                                break
                        else:
                            # Non-timeout error, log and skip
                            st.warning(f"⚠️ Embedding error for batch {i//batch_size + 1}: {error_str[:100]}. Skipping...")
                            failed_indices.append(i)
                            all_embeddings.append(None)
                            break
                
                # Update progress
                if (i // batch_size + 1) % 5 == 0 or i + batch_size >= len(post_texts):
                    progress = min(100, int((i + batch_size) / len(post_texts) * 100))
                    st.info(f"📊 Embedding progress: {progress}% ({i + batch_size}/{len(post_texts)})")
            
            # Filter out None values (failed embeddings)
            if None in all_embeddings:
                st.warning(f"⚠️ {len(failed_indices)} out of {len(post_texts)} embeddings failed. Continuing with available embeddings.")
                # Remove None values and corresponding post_texts
                valid_embeddings = []
                valid_indices = []
                for idx, emb in enumerate(all_embeddings):
                    if emb is not None:
                        valid_embeddings.append(emb)
                        valid_indices.append(idx)
                
                if len(valid_embeddings) == 0:
                    st.warning("⚠️ All embeddings failed. Continuing without embeddings for clustering.")
                    use_embeddings = False
                    valid_indices = None
                else:
                    embeddings = valid_embeddings
                    # Update post_texts to match valid embeddings
                    post_texts = [post_texts[i] for i in valid_indices]
                    st.success(f"✅ Successfully generated {len(valid_embeddings)}/{len(all_embeddings)} embeddings")
            else:
                embeddings = all_embeddings
                valid_indices = list(range(len(post_texts)))  # All indices are valid
                st.success(f"✅ Successfully generated all {len(embeddings)} embeddings")
        
        # Store in vector DB for semantic search (only if embeddings succeeded)
        if use_embeddings and embeddings and len(embeddings) > 0 and valid_indices is not None:
            try:
                from langchain_core.documents import Document
                # Map embeddings back to original raw_posts using valid_indices
                docs = []
                for idx, text in enumerate(post_texts):
                    # valid_indices maps embedding index to original post_texts index
                    # Since post_texts was created from raw_posts, the index is the same
                    original_idx = valid_indices[idx] if idx < len(valid_indices) else idx
                    if original_idx < len(raw_posts):
                        doc = Document(
                            page_content=text, 
                            metadata={
                                "index": original_idx, 
                                "source": raw_posts[original_idx].get("source_url", ""), 
                                "title": raw_posts[original_idx].get("title", "")
                            }
                        )
                        docs.append(doc)
                
                if docs:
                    uuids = [str(uuid4()) for _ in range(len(docs))]
                    db.add_documents(documents=docs, ids=uuids)
                    st.success(f"✅ {len(docs)} embeddings stored in vector database")
            except Exception as db_error:
                st.warning(f"⚠️ Could not store embeddings in database: {str(db_error)}. Continuing with LLM-only analysis.")
                use_embeddings = False
        
        # Prepare posts text for LLM analysis
        posts_text = "\n\n".join([
            f"Post {i+1}:\nTitle: {p.get('title', 'N/A')}\nLink: {p.get('link', 'N/A')}\nPublished: {p.get('published', 'N/A')}\nSummary: {p.get('summary', 'N/A')[:500]}\nAuthor: {p.get('author', 'N/A')}"
            for i, p in enumerate(raw_posts)
        ])
        
        # Combined analysis prompt (metadata extraction + theme identification + trend ranking)
        analysis_prompt = PromptTemplate(
            template="""You are analyzing newsletter posts to extract metadata, identify themes, and rank trends.

Posts to analyze:
{posts}

Tasks:
1. Extract normalized metadata for each post (title, date, author, summary, url, tags)
2. Identify common themes and cluster posts by theme
3. Rank topics by trendiness using: trendiness = recency × cross-source frequency × salience

Rules:
- For missing data, write exactly "Data Not Available"
- Keep tone objective and factual
- Recency: Calculate based on publication date (more recent = higher score, 0-1)
- Frequency: Count how many sources mention the topic (normalize to 0-1)
- Salience: Assess importance/impact (0-1)
- Trendiness = recency × frequency × salience

Provide complete analysis with metadata, themes, and ranked topics.""",
            input_variables=["posts"]
        )
        
        llm_with_analysis = model.with_structured_output(AnalysisResult)
        chain = analysis_prompt | llm_with_analysis
        
        # Perform initial analysis
        try:
            result = chain.invoke({"posts": posts_text})
            # Validate result structure
            if not hasattr(result, 'metadata') or not hasattr(result, 'themes') or not hasattr(result, 'ranked_topics'):
                raise ValueError("Invalid analysis result structure")
        except Exception as analysis_error:
            st.error(f"Failed to perform initial analysis: {str(analysis_error)}")
            raise  # Re-raise to be caught by outer exception handler
        
        # Refine analysis - use embeddings if available, otherwise skip refinement
        if use_embeddings and embeddings:
            try:
                # Use embeddings for semantic clustering enhancement
                retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": min(5, len(raw_posts))})
                
                # Refine analysis with embedding-based insights
                analysis_refinement_prompt = PromptTemplate(
                    template="""Refine the analysis using semantic similarity insights from embeddings.

Initial Analysis:
Metadata: {metadata}
Themes: {themes}
Ranked Topics: {rankings}

Refinement Guidelines:
- Use semantic similarity to improve theme clustering
- Adjust trendiness scores based on:
  * Recency: More recent posts (within last 7 days) = 0.8-1.0, older = 0.3-0.7
  * Frequency: Topics in 3+ sources = 0.8-1.0, 2 sources = 0.5-0.7, 1 source = 0.2-0.4
  * Salience: High impact topics = 0.7-1.0, moderate = 0.4-0.6, low = 0.1-0.3
- Ensure trendiness_score = recency × frequency × salience

Provide refined analysis.""",
                    input_variables=["metadata", "themes", "rankings"]
                )
                
                # Safely convert to dict
                try:
                    metadata_json = json.dumps([m.dict() if hasattr(m, 'dict') else m for m in result.metadata])
                    themes_json = json.dumps([t.dict() if hasattr(t, 'dict') else t for t in result.themes])
                    rankings_json = json.dumps([r.dict() if hasattr(r, 'dict') else r for r in result.ranked_topics])
                except Exception as dict_error:
                    st.warning(f"⚠️ Error converting to dict: {str(dict_error)}. Skipping refinement.")
                    refined_result = result
                else:
                    refinement_chain = analysis_refinement_prompt | model.with_structured_output(AnalysisResult)
                    refined_result = refinement_chain.invoke({
                        "metadata": metadata_json,
                        "themes": themes_json,
                        "rankings": rankings_json
                    })
            except Exception as refine_error:
                st.warning(f"⚠️ Could not refine analysis with embeddings: {str(refine_error)}. Using initial analysis.")
                refined_result = result
        else:
            # Skip refinement if embeddings are not available
            refined_result = result
        
        # Sort ranked topics by trendiness score
        try:
            ranked_topics_sorted = sorted(
                [r.dict() if hasattr(r, 'dict') else r for r in refined_result.ranked_topics],
                key=lambda x: x.get("trendiness_score", 0) if isinstance(x, dict) else getattr(x, "trendiness_score", 0),
                reverse=True
            )
        except Exception as sort_error:
            st.warning(f"⚠️ Error sorting ranked topics: {str(sort_error)}")
            ranked_topics_sorted = []
        
        # Build source mapping
        sources = {}
        for post in raw_posts:
            source_url = post.get("source_url", "")
            if source_url and source_url not in sources.values():
                sources[len(sources) + 1] = source_url
        
        # Safely convert metadata and themes to dict
        try:
            extracted_metadata = [m.dict() if hasattr(m, 'dict') else m for m in refined_result.metadata]
            themes = [t.dict() if hasattr(t, 'dict') else t for t in refined_result.themes]
        except Exception as convert_error:
            st.warning(f"⚠️ Error converting results: {str(convert_error)}")
            extracted_metadata = []
            themes = []
        
        return {
            **state,
            "extracted_metadata": extracted_metadata,
            "themes": themes,
            "ranked_topics": ranked_topics_sorted,
            "sources": sources
        }
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        st.exception(e)  # Show full traceback for debugging
        # Build source mapping even on error
        sources = {}
        for post in raw_posts:
            source_url = post.get("source_url", "")
            if source_url and source_url not in sources.values():
                sources[len(sources) + 1] = source_url
        
        return {
            **state,
            "extracted_metadata": [],
            "themes": [],
            "ranked_topics": [],
            "sources": sources
        }

# Agent 3: Newsletter Generator Agent
def newsletter_generator_agent(state: NewsletterState) -> NewsletterState:
    """Generates formatted newsletter draft with citations."""
    st.info("✍️ Generating newsletter draft...")
    
    ranked_topics = state.get("ranked_topics", [])
    extracted_metadata = state.get("extracted_metadata", [])
    sources = state.get("sources", {})
    
    if not ranked_topics:
        return {
            **state,
            "newsletter_draft": "# Newsletter\n\nNo trending topics found in the specified time window."
        }
    
    # Get top trend
    top_topic = ranked_topics[0]
    
    gemini_api_key = st.session_state.gemini_api_key
    model = ChatGoogleGenerativeAI(
        api_key=gemini_api_key,
        temperature=0,
        model="gemini-2.0-flash"
    )
    
    # Get posts related to top topic
    related_post_indices = top_topic.get("post_indices", [])
    related_posts = [extracted_metadata[i] for i in related_post_indices if i < len(extracted_metadata)]
    
    # If no specific post indices, use all metadata
    if not related_posts:
        related_posts = extracted_metadata[:5]  # Limit to top 5
    
    # Build source citations - map post URLs to citation numbers
    post_to_citation = {}
    for post in related_posts:
        post_url = post.get("url", "")
        # Find matching source
        matched = False
        for cit_num, source_url in sources.items():
            if source_url in post_url or post_url.startswith(source_url):
                post_to_citation[post_url] = cit_num
                matched = True
                break
        # If no match found, assign new citation
        if not matched and post_url:
            new_cit = len(sources) + 1
            sources[new_cit] = post_url
            post_to_citation[post_url] = new_cit
    
    # Prepare posts with citation numbers
    posts_with_citations = []
    for i, post in enumerate(related_posts):
        post_url = post.get("url", "")
        citation_num = post_to_citation.get(post_url, i + 1)
        posts_with_citations.append({
            "citation": citation_num,
            "title": post.get("title", "Data Not Available"),
            "url": post_url,
            "summary": post.get("summary", "Data Not Available")
        })
    
    newsletter_prompt = PromptTemplate(
        template="""Generate a newsletter draft focused on the top trending topic.
        
        Top Topic: {topic}
        Trendiness Score: {score}
        Related Posts with Citations: {posts}
        
        Format exactly as follows:
        
        # [Headline - objective and specific]
        
        **TL;DR:** [One sentence summary, maximum 40 words]
        
        ## Why it matters
        
        - [First reason]
        - [Second reason]
        - [Third reason]
        
        ## Key developments
        
        - [First development] [{citation}]
        - [Second development] [{citation}]
        - [Additional developments with citations]
        
        Rules:
        - Do not hallucinate data. Use only information from the provided posts.
        - If data is unavailable, write exactly "Data Not Available".
        - Keep tone objective, factual, and non-opinionated.
        - Use citations [1], [2], etc. matching the citation numbers in the posts.
        - All tables must be valid Markdown.
        - Each key development must have a citation number in brackets.
        
        Generate the newsletter draft in Markdown format following the exact format above.""",
        input_variables=["topic", "score", "posts"]
    )
    
    posts_text = "\n\n".join([
        f"Post [{p['citation']}]:\nTitle: {p['title']}\nURL: {p['url']}\nSummary: {p['summary']}"
        for p in posts_with_citations
    ])
    
    chain = newsletter_prompt | model | StrOutputParser()
    
    try:
        draft = chain.invoke({
            "topic": top_topic.get("topic", "Data Not Available"),
            "score": top_topic.get("trendiness_score", 0),
            "posts": posts_text
        })
        
        # Add Sources section
        sources_section = "\n\n## Sources\n\n"
        for cit_num, source_url in sources.items():
            sources_section += f"[{cit_num}] {source_url}\n"
        
        final_draft = draft + sources_section
        
        return {
            **state,
            "newsletter_draft": final_draft
        }
    except Exception as e:
        st.error(f"Newsletter generation error: {str(e)}")
        return {
            **state,
            "newsletter_draft": "# Newsletter\n\nError generating newsletter draft."
        }

# Build LangGraph Workflow
def create_newsletter_graph(embedding_model, db):
    """Create the LangGraph workflow."""
    workflow = StateGraph(NewsletterState)
    
    # Create a wrapper function for analysis agent to capture embedding_model and db
    def analysis_wrapper(state: NewsletterState) -> NewsletterState:
        return analysis_agent(state, embedding_model, db)
    
    # Add nodes
    workflow.add_node("fetcher", fetcher_agent)
    workflow.add_node("analysis", analysis_wrapper)
    workflow.add_node("generator", newsletter_generator_agent)
    
    # Add edges
    workflow.add_edge(START, "fetcher")
    workflow.add_edge("fetcher", "analysis")
    workflow.add_edge("analysis", "generator")
    workflow.add_edge("generator", END)
    
    return workflow.compile()

def main():
    set_sidebar()

    if not all([st.session_state.qdrant_host, 
                st.session_state.qdrant_api_key, 
                st.session_state.gemini_api_key]):
        st.warning("Please configure your API keys in the sidebar first")
        return

    if "config" not in st.session_state:
        st.session_state.config = {
            "time_window_days": 14,
            "max_items_per_source": 10,
            "language": "en",
            "use_embeddings": True
        }
    
    embedding_model, client, db = initialize_components()
    # Only require Qdrant client - embeddings are optional
    if client is None:
        st.error("❌ Failed to connect to Qdrant. Please check your Qdrant configuration.")
        return
    
    if embedding_model is None or db is None:
        st.info("ℹ️ Running in LLM-only mode (embeddings unavailable). The app will still work but without semantic clustering.")

    st.subheader("Newsletter Sources")
    st.write("Fetching from:")
    for source in SOURCES_ALLOWLIST:
        st.write(f"- {source}")
    
    if st.button("🚀 Generate Newsletter", type="primary"):
        initial_state = {
            "raw_posts": [],
            "extracted_metadata": [],
            "themes": [],
            "ranked_topics": [],
            "newsletter_draft": "",
            "sources": {},
            "config": st.session_state.config
        }
        
        graph = create_newsletter_graph(embedding_model, db)
        
        with st.spinner("Running newsletter pipeline..."):
            try:
                final_state = None
                for node_name, node_state in graph.stream(initial_state):
                    final_state = node_state
                    # Show progress
                    if node_name == "fetcher":
                        st.info("✅ Posts fetched")
                    elif node_name == "analysis":
                        st.info("✅ Analysis complete")
                    elif node_name == "generator":
                        st.info("✅ Newsletter generated")
                
                if final_state and "newsletter_draft" in final_state:
                    newsletter_draft = final_state.get("newsletter_draft", "")
                    
                    st.subheader("📰 Newsletter Draft")
                    st.markdown(newsletter_draft)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Newsletter",
                        data=newsletter_draft,
                        file_name=f"newsletter_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown"
                    )
            except Exception as e:
                st.error(f"Pipeline error: {str(e)}")
                st.exception(e)

    st.markdown("---")
    st.write("Built with :blue-background[LangChain] | :blue-background[LangGraph]")

if __name__ == "__main__":
    main()
