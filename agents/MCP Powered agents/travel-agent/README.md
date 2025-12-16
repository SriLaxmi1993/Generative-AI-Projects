# AI Travel Assistant - Multi-Agent System with MCP

A sophisticated travel planning system powered by LangChain and MCP (Model Context Protocol) tools, designed to work through Cursor's AI assistant.

## 🎯 What This Does

Search for **top 10 Airbnb properties** and **flight schedules** by simply asking in Cursor's AI chat. The system uses specialized AI agents to:
- Parse your travel requirements
- Search Airbnb via MCP
- Find flight schedules via Aviationstack MCP
- Score and rank properties (0-100)
- Return formatted results with booking links

## 💡 Why I Built This

Searching Airbnb directly takes 30-45 minutes: filling forms, browsing listings, reading reviews, comparing prices. This system does it in 30 seconds.

**What makes it better:**
- **Natural language understanding** - Just describe what you want, no form filling
- **Intelligent scoring (0-100)** - Properties ranked by YOUR needs (amenities, reviews, budget), not just price/rating
- **Automated review analysis** - Sentiment analysis from hundreds of reviews, pros/cons generated automatically
- **Cross-domain integration** - Properties + flights in one query
- **Guaranteed results** - Always returns exactly 10 properties with complete analysis

**Why LangChain?** It provides tool-calling agents, orchestration, and workflows that would take months to build from scratch. Without it, you'd need custom frameworks for every step.

**Why not just use Airbnb?** Airbnb shows listings but doesn't provide intelligent analysis, personalized scoring, or integrated flight search. This system adds that intelligence layer on top.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd travel-agent
pip install -r requirements.txt
```

### 2. Add OpenAI API Key

Edit `.env`:
```
OPENAI_API_KEY=your_openai_key_here
```

### 3. Just Ask in Cursor Chat!

```
Search for top 10 Airbnb properties in Coorg, India 
from Dec 25-28, 2025. I need 2 bedrooms, WiFi essential, 
budget ₹15,000-30,000. Flying from Delhi.
```

That's it! The AI will use the multi-agent system to search and analyze properties for you.

## 📋 Example Queries

**Basic Search:**
```
Find top 10 Airbnbs in Bali for Jan 15-20, 2025
```

**With Specific Requirements:**
```
Search Goa properties for 4 adults, need WiFi and pool,
near beach, Dec 28-31. Budget ₹5000-8000 per night.
```

**Include Flights:**
```
I want to visit Dubai from Mumbai, March 1-5, 2025.
Show me properties and flight options. Budget ₹40,000 total.
```

**Detailed Requirements:**
```
Find me properties in Paris for 2 adults, Jan 10-15.
Must have kitchen and washer. Prefer quiet neighborhood.
Budget €100-150/night. Flying from London.
```

## 🏗️ Project Structure

```
travel-agent/
├── src/
│   ├── agents/              # Specialized AI agents
│   │   ├── parser_agent.py      # Extracts requirements from queries
│   │   ├── property_agent.py    # Searches Airbnb properties
│   │   ├── flight_agent.py      # Searches flight schedules
│   │   ├── analysis_agent.py    # Scores & ranks properties
│   │   └── orchestrator.py      # Coordinates all agents
│   ├── tools/               # MCP tool wrappers
│   │   ├── mcp_connector.py     # MCP protocol bridge
│   │   ├── airbnb_tools.py      # Airbnb MCP wrappers
│   │   └── flight_tools.py      # Flight MCP wrappers
│   └── prompts/
│       └── agent_prompts.py     # Agent system prompts
├── requirements.txt         # Python dependencies
├── .env                     # API keys (gitignored)
└── README.md
```

## 🔧 How It Works

### Architecture

```
Your Query in Cursor Chat
    ↓
Parser Agent (extracts requirements)
    ↓
Property Agent (searches Airbnb via MCP)
    ↓
Flight Agent (searches flights via MCP)
    ↓
Analysis Agent (scores properties)
    ↓
Formatted Results with Links
```

### The Agents

1. **Parser Agent**: Understands natural language and extracts:
   - Destination, dates, guests
   - Budget, amenities, preferences

2. **Property Agent**: 
   - Calls Airbnb MCP `airbnb_search`
   - Returns top 10 matching properties
   - Preserves booking URLs

3. **Flight Agent**:
   - Calls Aviationstack MCP
   - Searches multiple airlines (IndiGo, Air India, Emirates, etc.)
   - Returns schedules (not pricing)

4. **Analysis Agent**:
   - Optionally calls `airbnb_listing_details` for deep analysis
   - Scores properties based on:
     - Rating (20 pts)
     - Amenities match (40 pts)
     - Reviews (30 pts)
     - Price fit (10 pts)

5. **Orchestrator**: Coordinates all agents and formats results

## 🛠️ MCP Tools Used

### Airbnb MCP
- `airbnb_search`: Find properties by location, dates, filters
- `airbnb_listing_details`: Get detailed info, reviews, amenities

### Aviationstack MCP
- `future_flights_arrival_departure_schedule`: Flight schedules by date
- `flights_with_airline`: Airline-specific flights

## 📊 What You Get

For each property:
- ✅ Property name and rating
- ✅ Price breakdown (per night + total)
- ✅ Match score (0-100)
- ✅ Bedroom/bed configuration
- ✅ Badges (Guest favourite, Superhost)
- ✅ Pros and cons
- ✅ **Direct Airbnb booking link**

For flights:
- ✅ Airline and flight number
- ✅ Departure/arrival times
- ✅ Aircraft type
- ✅ Terminal information
- ⚠️ Schedules only (no pricing)

## 📝 Response Format

The system follows a standardized response format to ensure consistency. See `EXAMPLE_RESPONSE_FORMAT.md` for the complete example structure.

**Key requirements:**
- ✅ Always returns **exactly 10 properties** (never fewer)
- ✅ Each property includes: name, rating, price (per night + total), availability dates, direct booking link, location, pros/cons
- ✅ Flight information included when origin is specified
- ✅ Summary with top 3 recommendations

The AI agents are configured to follow this format automatically. The example document serves as a reference for the expected output structure.

## ⚠️ Important Notes

### This is NOT a Standalone App

**MCP tools ONLY work through Cursor's AI assistant.** This means:

❌ Cannot run as:
- Standalone Python script
- Web application
- CLI tool
- Background service
- API with webhooks

✅ Works as:
- Interactive queries in Cursor AI chat
- The AI calls MCP tools on your behalf
- Perfect for assisted travel planning

### Why Not Standalone?

MCP (Model Context Protocol) tools are designed for AI assistant contexts. They:
- Run within Cursor's environment
- Only accessible during AI interactions
- Cannot be called from external Python processes

If you need a standalone app, you would need direct API keys instead of MCP.

## 🎓 Example Interaction

**You:** Search for Airbnbs in Coorg for Dec 25-28

**AI:** 
```
Found 10 properties in Coorg:

#1 - Poovilla Home (Score: 95/100)
   - Rating: 5.0/5 ⭐ (4 reviews)
   - Price: ₹24,308 for 3 nights (₹8,103/night)
   - 2 bedrooms, 2 double beds ✅
   - Pros: Perfect rating, meets requirements
   - Book: https://airbnb.com/rooms/1030247081736187001

#2 - Kokaris Coorg Homestay (Score: 92/100)
   - Price: ₹17,871 for 3 nights - Great value!
   - 2 bedrooms, 3 beds ✅
   - Book: https://airbnb.com/rooms/1088887119641039509

... (8 more properties)

Flights from Delhi (if you want to fly):
- Air India AI 2757: Delhi → Bangalore, 00:15 → 03:10
  (Then 4-5 hour drive to Coorg)
```

## 💡 Pro Tips

1. **Be specific**: Mention dates, guests, budget, must-have amenities
2. **Request "top 10"**: Get comprehensive results
3. **Mention origin**: Get flight schedules automatically
4. **Ask follow-ups**: "Tell me more about property #2"
5. **Budget per night**: Helps filter better (e.g., "₹5000-10000/night")

## 🔐 Configuration Required

1. **OpenAI API Key**: In `.env` file
2. **MCP Servers**: Configured in Cursor (`~/.cursor/mcp.json`):
   - Airbnb MCP
   - Aviationstack MCP

## 🔌 Setting Up MCP Servers in Cursor

This project uses two MCP servers from [Playbooks](https://playbooks.com/mcp):

### 1. Airbnb MCP Setup

**Source**: [Airbnb MCP on Playbooks](https://playbooks.com/mcp/openbnb-airbnb)

1. Go to **Cursor Settings > Tools & Integrations > New MCP Server**
2. Add the following to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "npx",
      "args": [
        "-y",
        "@openbnb/mcp-server-airbnb",
        "--ignore-robots-txt"
      ]
    }
  }
}
```

**Note**: The `--ignore-robots-txt` flag is included to bypass robots.txt restrictions when searching Airbnb.

### 2. Aviationstack MCP Setup

**Source**: [Aviationstack MCP on Playbooks](https://playbooks.com/mcp/pradumnasaraf-aviationstack)

1. Get a free API key from [Aviationstack](https://aviationstack.com/)
2. Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "Aviationstack MCP": {
      "command": "uvx",
      "args": [
        "aviationstack-mcp"
      ],
      "env": {
        "AVIATION_STACK_API_KEY": "your_aviation_stack_api_key_here"
      }
    }
  }
}
```

**Replace** `your_aviation_stack_api_key_here` with your actual Aviationstack API key.

### Complete MCP Configuration

Your final `~/.cursor/mcp.json` should look like this:

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "npx",
      "args": [
        "-y",
        "@openbnb/mcp-server-airbnb",
        "--ignore-robots-txt"
      ]
    },
    "Aviationstack MCP": {
      "command": "uvx",
      "args": [
        "aviationstack-mcp"
      ],
      "env": {
        "AVIATION_STACK_API_KEY": "your_aviation_stack_api_key_here"
      }
    }
  }
}
```

### Restart Cursor

After adding the MCP servers, **restart Cursor** for the changes to take effect. You can verify the MCP servers are working by going to **Settings > MCP** and clicking the refresh button.

## 📦 Dependencies

- `langchain==0.2.16` - Multi-agent framework
- `langchain-openai==0.1.23` - OpenAI integration
- `langchain-core==0.2.39` - Core functionality
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variables
- `requests>=2.31.0` - HTTP client

## 🎯 Use Cases

Perfect for:
- ✅ Quick property searches with AI assistance
- ✅ Comparing multiple options with scoring
- ✅ Getting flight schedules along with properties
- ✅ Finding properties that match specific criteria

Not suitable for:
- ❌ Automated booking systems
- ❌ Standalone web applications
- ❌ Background processing
- ❌ API integrations

## 🤝 How to Contribute

This is a demonstration of:
- Multi-agent architectures with LangChain
- MCP tool integration
- Intelligent property scoring
- Natural language understanding

Feel free to adapt the agent prompts, scoring logic, or add new capabilities!

## 📄 License

MIT

## 🙏 Acknowledgments

Built with:
- LangChain - Multi-agent framework
- MCP - Model Context Protocol
- Cursor - AI-powered IDE
- OpenAI - Language models
