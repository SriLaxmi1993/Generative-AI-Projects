# Project Overview

## What This Is

A **multi-agent travel planning system** that works through Cursor's AI assistant chat.

## How to Use

Simply ask in Cursor chat:

```
Search for top 10 Airbnb properties in [destination] from [dates].
I need [requirements]. Budget: [amount].
```

Example:
```
Search for top 10 Airbnbs in Coorg, India from Dec 25-28, 2025.
2 bedrooms, WiFi essential, budget ₹15,000-30,000.
Flying from Delhi.
```

## What You Get

- ✅ Top 10 properties ranked by match score
- ✅ Direct Airbnb booking links
- ✅ Flight schedules (if origin specified)
- ✅ Property analysis with pros/cons
- ✅ Prices and ratings

## Project Structure

```
travel-agent/
├── src/
│   ├── agents/
│   │   ├── parser_agent.py      # Understands your query
│   │   ├── property_agent.py    # Searches Airbnb
│   │   ├── flight_agent.py      # Searches flights
│   │   ├── analysis_agent.py    # Scores properties
│   │   └── orchestrator.py      # Coordinates everything
│   ├── tools/
│   │   ├── mcp_connector.py     # Connects to MCP
│   │   ├── airbnb_tools.py      # Airbnb tools
│   │   └── flight_tools.py      # Flight tools
│   └── prompts/
│       └── agent_prompts.py     # Agent instructions
├── requirements.txt
├── .env
└── README.md
```

## Setup

1. Install: `pip install -r requirements.txt`
2. Add OpenAI key to `.env`
3. Ensure MCP servers configured in Cursor
4. Ask in chat!

## Why Not a Web App?

MCP tools only work through Cursor's AI assistant, not from standalone Python scripts or web apps.

**This is a chat-based assistant, not a standalone application.**

For more details, see [README.md](README.md).

