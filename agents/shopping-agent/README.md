# Shopping Agent

Redefining the concept of online shopping customer experience with agentic AI.

Shopping Agent is a LangGraph-based agent that:
- uses **Tavily** to search the web and fetch product roundups/reviews
- uses **Llama 3.1 70B** via **Groq** to extract structured product data, compare options, and select a best pick
- optionally uses the **YouTube Data API** to fetch a review video link for the best product
- optionally sends an **email** recommendation via **SMTP (Gmail)**

## Tutorial (Substack-ready)

Read the full tutorial with architecture diagrams, tools rationale, API key setup, and challenges:
- **`tutorial.md`**

## Key Features

- **Tavily web search**
- **Groq Llama 3.1 70B** for structuring + comparing products
- **Best product recommendation** with justification
- **YouTube review link** for self-satisfaction
- **SMTP email** with recommendation (optional)

## Project Files

```
agents/shopping-agent/
├── app.py
├── requirements.txt
├── tutorial.md
└── README.md
```

## Setup

### 1) Install dependencies

```bash
cd "agents/shopping-agent"
python -m pip install -r requirements.txt
```

### 2) Configure environment variables

Create a `.env` file in `agents/shopping-agent/` (or export variables in your shell):

```bash
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key

# Optional (YouTube link):
YOUTUBE_API_KEY=your_youtube_api_key

# Optional (email sending via Gmail SMTP):
GMAIL_USER=you@gmail.com
GMAIL_PASS=your_app_password
```

Notes:
- For Gmail, use an **App Password** (recommended) instead of your normal password.
- If `YOUTUBE_API_KEY` is not set, Shopping Agent will skip YouTube search.
- If `GMAIL_USER/GMAIL_PASS` are not set, Shopping Agent will skip email sending (even if you pass `--email`).

## Run

### Basic run

```bash
python app.py --query "Best smartphones under $1000" --pretty
```

### Send recommendation email (optional)

```bash
python app.py --query "Best laptops for video editing under $1500" --email "someone@example.com" --pretty
```

## Getting API Keys (quick links)

- **Groq**: create an API key and set `GROQ_API_KEY`
- **Tavily**: create an API key and set `TAVILY_API_KEY`
- **YouTube (optional)**: enable *YouTube Data API v3* in Google Cloud and set `YOUTUBE_API_KEY`
- **Gmail SMTP (optional)**: generate a Gmail **App Password** and set `GMAIL_USER`/`GMAIL_PASS`

## Tech Stack

- **LangGraph**
- **LangChain (core + community)**
- **Groq** (`langchain-groq`)
- **Tavily** (`tavily-python`)
- **YouTube Data API** (`google-api-python-client`)
- **BeautifulSoup4** (HTML parsing used by `WebBaseLoader`)

