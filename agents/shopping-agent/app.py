"""
Shopping Agent
Redefining the concept of online shopping experience with agentic AI.

This is a lightweight, runnable translation of the provided notebook code:
- LangGraph workflow orchestration
- Tavily web search + content loading
- Groq Llama 3.1 (via langchain-groq) for extraction/comparison
- YouTube Data API for review link
- Optional SMTP email sending (Gmail SMTP)
"""

from __future__ import annotations

import argparse
import json
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from googleapiclient.discovery import build
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from tavily import TavilyClient
from typing_extensions import TypedDict


# -----------------------------
# Environment / clients
# -----------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set. Add it to your environment or a .env file.")
    return value


def build_llm() -> ChatGroq:
    api_key = _require_env("GROQ_API_KEY")
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
        api_key=api_key,
        temperature=float(os.getenv("GROQ_TEMPERATURE", "0.5")),
    )


def build_tavily() -> TavilyClient:
    api_key = _require_env("TAVILY_API_KEY")
    return TavilyClient(api_key=api_key)


def build_youtube_client():
    if not YOUTUBE_API_KEY:
        return None
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


# -----------------------------
# Pydantic schemas (structured outputs)
# -----------------------------

class ProductHighlights(BaseModel):
    Camera: Optional[str] = None
    Performance: Optional[str] = None
    Display: Optional[str] = None
    Fast_Charging: Optional[str] = None


class ProductReview(BaseModel):
    title: str = Field(..., description="The product name/title")
    url: Optional[str] = Field(None, description="Source URL")
    content: Optional[str] = Field(None, description="Concise summary of the product")
    pros: Optional[List[str]] = Field(None, description="Pros list")
    cons: Optional[List[str]] = Field(None, description="Cons list")
    highlights: Optional[dict] = Field(None, description="Notable specs/features")
    score: Optional[float] = Field(0.0, description="Numeric score if available, else 0.0")


class ListOfProductReviews(BaseModel):
    products: List[ProductReview] = Field(..., description="List of extracted products")


class SpecsComparison(BaseModel):
    processor: str = Field(..., description="Processor type and model")
    battery: str = Field(..., description="Battery capacity and type")
    camera: str = Field(..., description="Camera specs")
    display: str = Field(..., description="Display specs")
    storage: str = Field(..., description="Storage specs")


class RatingsComparison(BaseModel):
    overall_rating: float = Field(..., description="Overall rating out of 5")
    performance: float = Field(..., description="Performance rating out of 5")
    battery_life: float = Field(..., description="Battery life rating out of 5")
    camera_quality: float = Field(..., description="Camera quality rating out of 5")
    display_quality: float = Field(..., description="Display quality rating out of 5")


class Comparison(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    specs_comparison: SpecsComparison
    ratings_comparison: RatingsComparison
    reviews_summary: str = Field(..., description="Summary of key points from user reviews")


class BestProduct(BaseModel):
    product_name: str = Field(..., description="Name of the best product")
    justification: str = Field(..., description="Why this is the best choice")


class ProductComparison(BaseModel):
    comparisons: List[Comparison]
    best_product: BestProduct


class EmailRecommendation(BaseModel):
    subject: str
    heading: str
    justification_line: str


# -----------------------------
# LangGraph state
# -----------------------------

class State(TypedDict, total=False):
    query: str
    email: str
    blogs_content: List[dict]
    product_schema: List[dict]
    comparison: List[dict]
    best_product: dict
    youtube_link: Optional[str]


# -----------------------------
# Email utilities
# -----------------------------

def send_email(recipient_email: str, subject: str, body_html: str) -> None:
    """Send an email using Gmail SMTP (requires GMAIL_USER and GMAIL_PASS)."""
    if not GMAIL_USER or not GMAIL_PASS:
        raise ValueError("GMAIL_USER/GMAIL_PASS not set; cannot send email.")

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    message = MIMEMultipart()
    message["From"] = GMAIL_USER
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(message)


EMAIL_TEMPLATE_PROMPT = """
You are an expert email content writer.

Generate an email recommendation based on the following inputs:
- Product Name: {product_name}
- Justification Line: {justification_line}
- User Query: "{user_query}" (a general idea of the user's interest)

Return your output in the following JSON format:
{format_instructions}
"""


EMAIL_HTML_TEMPLATE = """
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5;">
    <h2>{heading}</h2>
    <p><strong>Our Top Pick:</strong> {product_name}</p>
    <p>{justification}</p>
    {youtube_section}
    <hr />
    <p style="font-size: 12px; color: #666;">Shopping Agent • Generated recommendation</p>
  </body>
</html>
"""


# -----------------------------
# Web loading / search nodes
# -----------------------------

def load_blog_content(page_url: str) -> str:
    try:
        loader = WebBaseLoader(
            web_paths=[page_url],
            bs_get_text_kwargs={"separator": " ", "strip": True},
        )
        loaded_content = loader.load()
        return " ".join(doc.page_content for doc in loaded_content)
    except Exception as e:
        print(f"Error loading blog content from URL {page_url}: {e}")
        return ""


def tavily_search_node_factory(tavily_client: TavilyClient):
    def tavily_search_node(state: State) -> Dict[str, Any]:
        query = state.get("query", "")
        if not query:
            return {"blogs_content": []}

        try:
            max_results = int(os.getenv("TAVILY_MAX_RESULTS", "3"))
            response = tavily_client.search(query=query, max_results=max_results)
            results = response.get("results") or []
            if not results:
                return {"blogs_content": []}

            blogs_content: List[dict] = []
            for blog in results:
                blog_url = blog.get("url") or ""
                if not blog_url:
                    continue
                content = load_blog_content(blog_url)
                if not content:
                    continue
                blogs_content.append(
                    {
                        "title": blog.get("title", ""),
                        "url": blog_url,
                        "content": content,
                        "score": blog.get("score", 0.0),
                    }
                )

            return {"blogs_content": blogs_content}
        except Exception as e:
            print(f"Error with Tavily search: {e}")
            return {"blogs_content": []}

    return tavily_search_node


def schema_mapping_node_factory(llm: ChatGroq):
    def schema_mapping_node(state: State) -> Dict[str, Any]:
        blogs_content = state.get("blogs_content") or []
        if not blogs_content:
            print("No blog content available; schema extraction skipped.")
            return {"product_schema": []}

        max_retries = int(os.getenv("SCHEMA_MAX_RETRIES", "2"))
        wait_time = int(os.getenv("SCHEMA_RETRY_WAIT_SECONDS", "30"))

        prompt_template = """
You are a professional assistant tasked with extracting structured product information from blog content.

### Instructions:
For each product mentioned, populate the `products` array with:
- title
- url
- content (concise summary)
- pros (if available; else infer from content)
- cons (if available; else infer from content)
- highlights (key specs/features; if available; else infer)
- score (numeric rating if present; else 0.0)

### Blogs Content:
{blogs_content}

Return ONLY valid JSON matching:
{format_instructions}
"""

        parser = JsonOutputParser(pydantic_object=ListOfProductReviews)
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["blogs_content"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        for attempt in range(1, max_retries + 1):
            try:
                chain = prompt | llm | parser
                response = chain.invoke({"blogs_content": blogs_content})
                products = response.get("products") or []
                if len(products) >= 2:
                    return {"product_schema": products}

                print(f"Attempt {attempt} produced <2 products; retrying...")
            except Exception as e:
                print(f"Attempt {attempt} failed during schema extraction: {e}")

            if attempt < max_retries:
                time.sleep(wait_time)

        return {"product_schema": []}

    return schema_mapping_node


def product_comparison_node_factory(llm: ChatGroq):
    def product_comparison_node(state: State) -> Dict[str, Any]:
        product_schema = state.get("product_schema") or []
        if len(product_schema) < 2:
            print("Not enough products to compare; skipping comparison.")
            return {"comparison": [], "best_product": {}}

        prompt_template = """
You are an expert product comparison assistant.

Compare the products below and return a JSON object with:
- comparisons: list of per-product comparisons
- best_product: the best product + justification

Products:
{product_data}

Return ONLY valid JSON matching:
{format_instructions}
"""

        parser = JsonOutputParser(pydantic_object=ProductComparison)
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["product_data"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm | parser
        response = chain.invoke({"product_data": json.dumps(product_schema)})

        return {
            "comparison": response.get("comparisons", []),
            "best_product": response.get("best_product", {}),
        }

    return product_comparison_node


def youtube_review_node_factory(youtube_client):
    def youtube_review_node(state: State) -> Dict[str, Any]:
        best_product_name = (state.get("best_product") or {}).get("product_name")
        if not best_product_name or youtube_client is None:
            return {"youtube_link": None}

        try:
            search_response = (
                youtube_client.search()
                .list(
                    q=f"{best_product_name} review",
                    part="snippet",
                    type="video",
                    maxResults=1,
                )
                .execute()
            )
            items = search_response.get("items") or []
            if not items:
                return {"youtube_link": None}
            video_id = items[0]["id"]["videoId"]
            return {"youtube_link": f"https://www.youtube.com/watch?v={video_id}"}
        except Exception as e:
            print(f"Error during YouTube search: {e}")
            return {"youtube_link": None}

    return youtube_review_node


def display_node(state: State) -> Dict[str, Any]:
    return {
        "products": state.get("product_schema", []),
        "best_product": state.get("best_product", {}),
        "comparison": state.get("comparison", []),
        "youtube_link": state.get("youtube_link"),
    }


def send_email_node_factory(llm: ChatGroq):
    def send_email_node(state: State) -> Dict[str, Any]:
        recipient_email = state.get("email") or ""
        best_product = state.get("best_product") or {}
        if not recipient_email or not best_product:
            return {}

        best_product_name = best_product.get("product_name", "")
        justification = best_product.get("justification", "")
        youtube_link = state.get("youtube_link")

        parser = JsonOutputParser(pydantic_object=EmailRecommendation)
        prompt = PromptTemplate(
            template=EMAIL_TEMPLATE_PROMPT,
            input_variables=["product_name", "justification_line", "user_query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | llm | parser
        response = chain.invoke(
            {
                "product_name": best_product_name,
                "justification_line": justification,
                "user_query": state.get("query", ""),
            }
        )

        youtube_section = ""
        if youtube_link:
            youtube_section = (
                f'<p><a href="{youtube_link}">Watch the review on YouTube</a></p>'
            )

        html_content = EMAIL_HTML_TEMPLATE.format(
            heading=response["heading"],
            product_name=best_product_name,
            justification=response["justification_line"],
            youtube_section=youtube_section,
        )

        try:
            send_email(recipient_email, subject=response["subject"], body_html=html_content)
            print(f"Email sent successfully to {recipient_email}.")
        except Exception as e:
            print(f"Failed to send email: {e}")

        return {}

    return send_email_node


# -----------------------------
# Graph assembly / runner
# -----------------------------

def build_graph():
    llm = build_llm()
    tavily_client = build_tavily()
    youtube_client = build_youtube_client()

    builder = StateGraph(State)
    builder.add_node("tavily_search", tavily_search_node_factory(tavily_client))
    builder.add_node("schema_mapping", schema_mapping_node_factory(llm))
    builder.add_node("product_comparison", product_comparison_node_factory(llm))
    builder.add_node("youtube_review", youtube_review_node_factory(youtube_client))
    builder.add_node("display", display_node)
    builder.add_node("send_email", send_email_node_factory(llm))

    builder.add_edge(START, "tavily_search")
    builder.add_edge("tavily_search", "schema_mapping")
    builder.add_edge("schema_mapping", "product_comparison")
    builder.add_edge("product_comparison", "youtube_review")
    builder.add_edge("youtube_review", "display")
    builder.add_edge("display", END)
    builder.add_edge("youtube_review", "send_email")
    builder.add_edge("send_email", END)

    return builder.compile()


def run_shopping_agent(query: str, email: Optional[str] = None) -> Dict[str, Any]:
    graph = build_graph()
    initial_state: State = {"query": query}
    if email:
        initial_state["email"] = email
    return graph.invoke(initial_state)


def main() -> None:
    parser = argparse.ArgumentParser(description="Shopping Agent (LangGraph + Groq + Tavily + YouTube)")
    parser.add_argument("--query", required=False, help="Shopping query, e.g. 'Best smartphones under $1000'")
    parser.add_argument("--email", required=False, help="Optional: email to send recommendation to")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    query = args.query or "Best smartphones under $1000"

    try:
        result = run_shopping_agent(query=query, email=args.email)
    except Exception as e:
        print(f"Error: {e}")
        print(
            "Make sure you set GROQ_API_KEY and TAVILY_API_KEY (and optionally YOUTUBE_API_KEY) in your environment/.env."
        )
        sys.exit(1)

    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

