# Customer Support Agent with LangGraph

An intelligent customer support agent built using LangGraph that categorizes customer queries, analyzes sentiment, and provides appropriate responses or escalates issues when necessary.

## Overview

This project demonstrates how to create a sophisticated customer support system using LangGraph, a powerful tool for building complex language model workflows. The agent automatically processes customer inquiries through a structured workflow that:

1. **Categorizes** queries into Technical, Billing, or General categories
2. **Analyzes sentiment** to determine if the customer is Positive, Neutral, or Negative
3. **Routes** queries to appropriate handlers based on category and sentiment
4. **Escalates** negative sentiment queries to human agents
5. **Generates** appropriate responses for each query type

## Features

- **State Management**: Uses TypedDict to define and manage the state of each customer interaction
- **Query Categorization**: Automatically classifies customer queries into Technical, Billing, or General categories
- **Sentiment Analysis**: Determines the emotional tone of customer queries (Positive, Neutral, Negative)
- **Response Generation**: Creates contextually appropriate responses based on query category
- **Escalation Mechanism**: Automatically escalates queries with negative sentiment to human agents
- **Workflow Graph**: Utilizes LangGraph to create a flexible and extensible workflow

## Architecture

The agent uses a graph-based workflow with the following structure:

```
categorize → analyze_sentiment → [route_query] → 
    ├─ handle_technical → END
    ├─ handle_billing → END
    ├─ handle_general → END
    └─ escalate → END
```

### Workflow Steps

1. **Categorize**: Classifies the query into Technical, Billing, or General
2. **Analyze Sentiment**: Determines if sentiment is Positive, Neutral, or Negative
3. **Route Query**: Routes based on sentiment and category:
   - Negative sentiment → Escalate
   - Technical category → Handle Technical
   - Billing category → Handle Billing
   - General category → Handle General
4. **Generate Response**: Creates appropriate response or escalates

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. **Navigate to the project directory**
   ```bash
   cd "agents/customer support"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project directory:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Running with Example Queries

Run the agent with built-in example queries:

```bash
python app.py
```

This will run four example queries demonstrating different scenarios:
- Escalation case (negative sentiment)
- Technical query
- Billing query
- General query

### Running with Custom Query

Provide your own query as a command-line argument:

```bash
python app.py "My internet connection keeps dropping. Can you help?"
```

### Using as a Module

You can also import and use the agent in your own Python code:

```python
from app import run_customer_support

result = run_customer_support("I need help with my account")
print(f"Category: {result['category']}")
print(f"Sentiment: {result['sentiment']}")
print(f"Response: {result['response']}")
```

## Project Structure

```
customer support/
├── app.py                 # Main agent implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env.example          # Environment variables template
├── .env                  # Your actual environment variables (not in git)
└── config.py             # Configuration management
```

## Key Components

### State Definition

The `State` TypedDict holds the query information throughout the workflow:

```python
class State(TypedDict):
    query: str        # Customer's query
    category: str     # Query category (Technical, Billing, General)
    sentiment: str   # Sentiment (Positive, Neutral, Negative)
    response: str     # Generated response
```

### Node Functions

- **`categorize()`**: Categorizes queries into Technical, Billing, or General
- **`analyze_sentiment()`**: Analyzes sentiment as Positive, Neutral, or Negative
- **`handle_technical()`**: Generates technical support responses
- **`handle_billing()`**: Generates billing support responses
- **`handle_general()`**: Generates general support responses
- **`escalate()`**: Escalates negative sentiment queries
- **`route_query()`**: Routes queries based on sentiment and category

## Example Output

```
Query: My internet connection keeps dropping. Can you help?
Category: Technical
Sentiment: Negative
Response: This query has been escalated to a human agent due to its negative sentiment.

Query: I need help talking to chatGPT
Category: Technical
Sentiment: Neutral
Response: [Technical support response...]

Query: where can i find my receipt?
Category: Billing
Sentiment: Neutral
Response: [Billing support response...]

Query: What are your business hours?
Category: General
Sentiment: Neutral
Response: [General support response...]
```

## Customization

### Adjusting Categories

To add or modify categories, update:
1. The `categorize()` function prompt
2. The `route_query()` function logic
3. Add corresponding handler functions

### Modifying Sentiment Analysis

To change sentiment analysis behavior, update the `analyze_sentiment()` function prompt.

### Customizing Responses

Modify the handler functions (`handle_technical`, `handle_billing`, `handle_general`) to customize response generation.

## Troubleshooting

### API Key Issues

If you encounter errors about missing API keys:
1. Ensure you have created a `.env` file
2. Verify your `OPENAI_API_KEY` is set correctly
3. Check that the `.env` file is in the same directory as `app.py`

### Import Errors

If you get import errors:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Verify you're using Python 3.8 or higher
3. Check that you're in the correct directory

## Dependencies

- **langgraph**: Graph-based workflow orchestration
- **langchain-core**: Core LangChain functionality
- **langchain-openai**: OpenAI integration for LangChain
- **python-dotenv**: Environment variable management

## License

MIT License - feel free to use and modify as needed.

## Contributing

This is a demonstration project showcasing LangGraph capabilities. Feel free to extend and customize it for your specific customer support needs!

