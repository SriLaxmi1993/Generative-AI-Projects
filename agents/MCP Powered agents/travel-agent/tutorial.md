# Building an AI Travel Assistant: A Multi-Agent System Tutorial

## 🎯 Introduction

Imagine having a personal travel assistant that understands your natural language requests, searches for hotels, finds flights, and provides intelligent recommendations—all in one go. In this tutorial, we'll explore how to build exactly that using modern AI agent frameworks.

This isn't just a simple chatbot. We're building a **multi-agent system** where specialized AI agents work together, each handling a specific task, orchestrated by a central coordinator. Think of it like a team of experts: one agent parses your request, another searches for properties, another finds flights, and a final one analyzes and scores everything.

---

## 🤖 What is an AI Agent?

An **AI agent** is an autonomous program that can perceive its environment, make decisions, and take actions to achieve specific goals. Unlike traditional programs that follow fixed instructions, AI agents use language models (like GPT-4) to:

- **Understand context**: Interpret natural language queries
- **Plan actions**: Decide what steps to take
- **Use tools**: Call external APIs, search databases, execute functions
- **Adapt**: Handle unexpected situations and errors gracefully

### Key Components of an AI Agent:

1. **LLM (Large Language Model)**: The "brain" that processes language and makes decisions
2. **Tools**: External functions the agent can call (APIs, databases, calculators, etc.)
3. **Memory**: Context about previous interactions
4. **Orchestrator**: Logic that coordinates the agent's actions

### Why Agents Matter:

Traditional software requires explicit programming for every scenario. AI agents can:
- Handle ambiguous or incomplete requests
- Chain multiple operations together intelligently
- Adapt to new situations without code changes
- Provide natural, conversational interfaces

---

## 🏗️ Architecture Overview

Our travel assistant uses a **multi-agent architecture** with four specialized agents:

```
┌─────────────────────────────────────────────────────────┐
│              Orchestrator Agent (Coordinator)            │
│  - Receives user query                                   │
│  - Coordinates all sub-agents                            │
│  - Combines results into final summary                  │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Parser Agent │ │Property Agent│ │ Flight Agent │
│              │ │              │ │              │
│ Extracts:    │ │ Searches:    │ │ Searches:    │
│ - Dates      │ │ - Airbnb     │ │ - Flights    │
│ - Location   │ │ - Properties │ │ - Schedules  │
│ - Guests     │ │ - Prices     │ │ - Airlines   │
│ - Budget     │ │ - Ratings    │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
                        │
                        ▼
                ┌──────────────┐
                │Analysis Agent│
                │              │
                │ Scores:      │
                │ - Properties │
                │ - Matches    │
                │ - Rankings   │
                └──────────────┘
```

### Workflow:

1. **User Query** → "I'm traveling from Mumbai to Dubai on Feb 25, 2026. Show me hotels and flights."
2. **Parser Agent** → Extracts structured data: `{destination: "Dubai", origin: "Mumbai", checkin: "2026-02-25", ...}`
3. **Property Agent** → Searches Airbnb for properties in Dubai
4. **Flight Agent** → Searches for flights from Mumbai to Dubai
5. **Analysis Agent** → Scores and ranks properties based on user requirements
6. **Orchestrator** → Combines everything into a cohesive summary

---

## 🛠️ Frameworks and Tools

### 1. LangChain

**What it is**: LangChain is a framework for building applications powered by language models. It provides abstractions for:

- **Agent creation**: Easy-to-use APIs for building tool-calling agents
- **Tool integration**: Standardized way to connect LLMs with external tools
- **Prompt management**: Templates and chains for complex workflows
- **Memory**: Conversation history and context management

**Why we use it**: 
- Simplifies agent creation (no need to manually handle tool calling logic)
- Handles complex interactions between LLM and tools
- Provides robust error handling and retry mechanisms
- Supports multiple LLM providers (OpenAI, Anthropic, etc.)

**Key Components We Use**:
- `create_tool_calling_agent()`: Creates agents that can use tools
- `StructuredTool`: Wraps functions as tools the agent can call
- `AgentExecutor`: Runs the agent with tool execution

### 2. Model Context Protocol (MCP)

**What it is**: MCP is a protocol that allows AI assistants to securely connect to external data sources and tools. It's designed for AI-first applications.

**Why we use it**:
- **Standardized interface**: One protocol for all external tools
- **Security**: Controlled access to external APIs
- **Ease of integration**: Simple JSON-RPC communication
- **IDE integration**: Works seamlessly with Cursor IDE

**How it works**:
```
Agent → MCP Connector → MCP Server → External API (Airbnb, Aviationstack)
```

**MCP Servers We Use**:
- **Airbnb MCP Server**: Provides Airbnb property search and listing details
- **Aviationstack MCP Server**: Provides flight schedules and airline information

### 3. OpenAI GPT-4

**What it is**: OpenAI's most capable language model, capable of complex reasoning and tool use.

**Why we use it**:
- **Tool calling**: Native support for function calling
- **High accuracy**: Better at understanding context and making decisions
- **Reliability**: Consistent performance across varied queries

**API Usage**:
- Each agent uses GPT-4 for reasoning and decision-making
- Tool calls are handled automatically by the model
- Responses are structured and parseable

### 4. Pydantic

**What it is**: Data validation library using Python type annotations.

**Why we use it**:
- **Type safety**: Validates data structures before processing
- **Schema definition**: Defines input/output formats for tools
- **Error handling**: Clear validation errors

**Note**: We use `pydantic.v1` for tool schemas (LangChain compatibility) and `pydantic` v2 for other validations.

### 5. Streamlit

**What it is**: Python framework for building web apps quickly.

**Why we use it**:
- **Rapid prototyping**: Build UIs in minutes, not hours
- **No frontend knowledge needed**: Pure Python
- **Interactive**: Real-time updates and user input
- **Perfect for demos**: Great for showcasing AI applications

---

## 📁 Project Structure

```
travel-agent/
├── main.py                 # CLI entry point
├── streamlit_app.py        # Web UI entry point
├── requirements.txt        # Python dependencies
│
└── src/
    ├── agents/             # AI Agent implementations
    │   ├── orchestrator.py    # Main coordinator
    │   ├── parser_agent.py    # Extracts requirements
    │   ├── property_agent.py  # Searches properties
    │   ├── flight_agent.py    # Searches flights
    │   └── analysis_agent.py  # Scores and ranks
    │
    ├── tools/              # External tool integrations
    │   ├── mcp_connector.py   # MCP protocol handler
    │   ├── airbnb_tools.py    # Airbnb search tools
    │   └── flight_tools.py    # Flight search tools
    │
    └── prompts/            # Agent prompt templates
        └── agent_prompts.py   # System prompts for each agent
```

### Key Files Explained:

#### `orchestrator.py`
The **brain** of the system. Coordinates all agents, manages the workflow, and combines results. It doesn't do the actual work—it delegates to specialized agents.

#### `parser_agent.py`
Converts natural language to structured data. Uses GPT-4 to extract:
- Dates (handles "Feb 25", "next week", etc.)
- Locations (cities, regions)
- Guest counts (adults, children, infants, pets)
- Budget constraints
- Preferences and deal-breakers

#### `property_agent.py`
Searches for Airbnb properties. Uses the Airbnb MCP tool to:
- Search by location and dates
- Filter by price, guests, amenities
- Extract property details (name, price, rating, URL)
- Format results for display

#### `flight_agent.py`
Searches for flight schedules. Uses the Aviationstack MCP tool to:
- Find flights by route and date
- Get departure/arrival times
- Retrieve airline and aircraft information
- Handle multiple airlines and airports

#### `analysis_agent.py`
Intelligently scores and ranks properties. Considers:
- Price vs. budget
- Rating and reviews
- Amenities match
- Location preferences
- Guest capacity

#### `mcp_connector.py`
Handles communication with MCP servers. Implements the JSON-RPC protocol to:
- Send tool requests to MCP servers
- Parse responses
- Handle errors and timeouts
- Manage subprocess communication

---

## 🔧 How Multi-Agent Systems Work

### Agent Communication Pattern:

```
User Query
    ↓
Orchestrator
    ↓
┌─────────────────────────────────────┐
│ 1. Parser Agent                     │
│    Input: "Travel to Dubai Feb 25"  │
│    Output: {destination: "Dubai",   │
│             checkin: "2026-02-25"}  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Property Agent                   │
│    Input: Parsed requirements        │
│    Tool: airbnb_search              │
│    Output: List of properties       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Flight Agent                     │
│    Input: Origin, destination, date │
│    Tool: flight_arrival_departure   │
│    Output: Flight schedules        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. Analysis Agent                   │
│    Input: Properties + Requirements │
│    Process: Score and rank          │
│    Output: Top 10 ranked properties│
└─────────────────────────────────────┘
    ↓
Orchestrator combines results
    ↓
Final Summary to User
```

### Why Multi-Agent?

**Single Agent Approach** (Not Used):
- One agent tries to do everything
- Prone to errors and confusion
- Hard to debug and improve
- Context window limitations

**Multi-Agent Approach** (Our System):
- ✅ **Specialization**: Each agent is an expert in one domain
- ✅ **Modularity**: Easy to improve individual agents
- ✅ **Scalability**: Add new agents without breaking existing ones
- ✅ **Reliability**: If one agent fails, others continue
- ✅ **Maintainability**: Clear separation of concerns

---

## 🛠️ Tools and Integrations

### Tool Architecture:

```
Agent → LangChain Tool → MCP Connector → MCP Server → External API
```

### 1. Airbnb Search Tool

**Purpose**: Find available properties matching user criteria

**How it works**:
1. Agent calls `airbnb_search` tool with location, dates, guests
2. Tool wrapper formats request for MCP protocol
3. MCP connector sends to Airbnb MCP server
4. Server queries Airbnb API
5. Results flow back through the chain
6. Agent receives JSON with property listings

**Data returned**:
- Property names and descriptions
- Prices per night
- Ratings and review counts
- Amenities
- Direct booking URLs

### 2. Flight Schedule Tool

**Purpose**: Find flight schedules for specific routes and dates

**How it works**:
1. Agent calls `flight_arrival_departure_schedule` tool
2. Tool formats airport codes, dates, airline info
3. MCP connector sends to Aviationstack MCP server
4. Server queries Aviationstack API
5. Results include flight times, airlines, aircraft

**Data returned**:
- Departure/arrival times
- Airline names and codes
- Aircraft types
- Terminal information
- Flight status

### Tool Wrapper Pattern:

We wrap MCP tools in LangChain `StructuredTool` objects so agents can use them:

```python
# Simplified example
airbnb_search_tool = StructuredTool.from_function(
    func=airbnb_search_wrapper,
    name="airbnb_search",
    description="Search for Airbnb properties",
    args_schema=AirbnbSearchInput  # Pydantic model
)
```

This allows the agent to:
- Understand what the tool does (from description)
- Know what parameters to provide (from schema)
- Call it naturally in conversation

---

## 🔑 API Keys Setup

### 1. OpenAI API Key

**Why needed**: All agents use GPT-4 for reasoning and decision-making.

**How to get**:
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-...`)

**How to set**:
```bash
# Option 1: Environment variable
export OPENAI_API_KEY=sk-your-key-here

# Option 2: .env file (recommended)
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Cost**: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens. A typical query costs $0.10-0.50.

### 2. Aviationstack API Key

**Why needed**: Flight search functionality requires Aviationstack API access.

**How to get**:
1. Go to [aviationstack.com](https://aviationstack.com)
2. Sign up for a free account
3. Navigate to **Dashboard** → **API Keys**
4. Copy your API key

**How to set**:
Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "Aviationstack MCP": {
      "command": "uvx",
      "args": ["aviationstack-mcp"],
      "env": {
        "AVIATION_STACK_API_KEY": "your-key-here"
      }
    }
  }
}
```

**Cost**: Free tier includes 1,000 requests/month. Paid plans start at $9.99/month.

### 3. MCP Server Configuration

**Airbnb MCP Server** (No API key needed):
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

**Location**: `~/.cursor/mcp.json` (macOS/Linux) or `%APPDATA%\Cursor\mcp.json` (Windows)

**Note**: MCP servers work best when running through Cursor IDE's AI assistant, but can also work standalone.

---

## 🧭 Using MCP In This Project (End-to-End)

This section shows exactly how MCP is used from your query all the way to external APIs, and how to set it up and verify it’s working.

### 1) What happens at runtime

```
You type a query in the UI / CLI
    ↓
Orchestrator calls a specialized agent (property/flight)
    ↓
Agent decides to use a tool (e.g., airbnb_search)
    ↓
LangChain StructuredTool → calls our tool wrapper (Python function)
    ↓
Tool wrapper → calls MCPConnector.call_mcp_tool(...)
    ↓
MCPConnector → launches the MCP server (npx/uvx) and speaks JSON-RPC
    ↓
MCP server → talks to the external API (Airbnb or Aviationstack)
    ↓
Response bubbles back (MCP → connector → tool → agent → orchestrator)
```

Where this lives in code:
- Tool wrappers: `src/tools/airbnb_tools.py`, `src/tools/flight_tools.py`
- MCP bridge: `src/tools/mcp_connector.py`
- Agents that use tools: `src/agents/property_agent.py`, `src/agents/flight_agent.py`

### 2) Minimal MCP config (copy‑paste)

Put this in `~/.cursor/mcp.json`:

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
      "args": ["aviationstack-mcp"],
      "env": {
        "AVIATION_STACK_API_KEY": "your-aviationstack-key"
      }
    }
  }
}
```

➡️ Replace `your-aviationstack-key` with your real key from the Aviationstack dashboard.

### 3) Verify MCP servers

- Restart Cursor after editing `mcp.json`
- In Cursor: Settings → Tools & Integrations → MCP → refresh
- Both servers should show as connected/ready

CLI spot-checks:
- Airbnb: `npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt` (should start the server)
- Aviationstack: `uvx aviationstack-mcp` (requires API key in env)

### 4) How the Python side talks MCP

In `mcp_connector.py`, we:
- Read `~/.cursor/mcp.json`
- Start the configured command (e.g., `npx …` or `uvx …`) as a subprocess
- Send JSON-RPC initialize + tool call over stdio
- Read the tool response line(s) and return a Python dict

You don’t need to call MCP servers directly—agents call the tools, which call MCP under the hood.

### 5) Troubleshooting MCP

- Timeout on Airbnb (common first-run issue)
  - Add `--ignore-robots-txt` flag (already shown)
  - Ensure Node.js + npx installed (`node -v`, `npx -v`)
  - Restart Cursor after changing `mcp.json`

- Aviationstack “rate_limit_reached” or “validation_error”
  - Free plans hit limits—retry in a few minutes
  - Confirm your date/airport codes are valid
  - Make sure the API key is present in the MCP server env

- “No server info found” / “Server not created yet”
  - Restart Cursor
  - Re-check the `mcp.json` path and JSON format
  - Test the MCP server manually using `npx` / `uvx`

---

## 🎯 Challenges and Solutions

### Challenge 1: Context Window Limitations

**Problem**: GPT-4 has a token limit (~128K tokens). When searching for properties, we might get hundreds of results, each with detailed descriptions. Sending all this to the LLM causes token overflow.

**Solution**:
- **Direct tool calls**: Bypass LLM for simple searches, parse results directly
- **Result limiting**: Only send top 10 properties to analysis agent
- **Simplified payloads**: Send only essential fields (name, price, rating) instead of full descriptions
- **Fallback mechanisms**: If analysis fails due to context, use deterministic scoring

**Code approach**:
```python
# Instead of sending full property data to LLM
def _direct_search(self, requirements):
    # Call tool directly, parse JSON response
    result = airbnb_search_wrapper(...)
    # Extract and format properties
    return formatted_properties[:10]  # Limit results
```

### Challenge 2: Date Parsing Ambiguity

**Problem**: Users say "Feb 25" without a year, or "next week" which is relative.

**Solution**:
- **Intelligent inference**: If only month/day provided, assume current year (or next year if date passed)
- **Relative date conversion**: Convert "next week" to actual dates based on today
- **Validation**: Ensure checkout is after checkin, default to +1 day if missing

**Code approach**:
```python
def _normalize_requirements(self, requirements):
    # Infer year if missing
    if len(checkin_date) == 5:  # "02-25"
        inferred_date = datetime(current_year, month, day)
        if inferred_date < datetime.now():
            inferred_date = datetime(current_year + 1, month, day)
```

### Challenge 3: MCP Response Format Variations

**Problem**: MCP servers return data in different formats:
- Sometimes JSON directly
- Sometimes wrapped in `content` arrays
- Sometimes in `structuredContent` fields
- Sometimes as error messages

**Solution**:
- **Robust parsing**: Handle multiple response formats
- **Error detection**: Check for error indicators before parsing
- **Fallback parsing**: Try multiple extraction methods
- **Graceful degradation**: If parsing fails, return partial results

**Code approach**:
```python
def _extract_properties(self, result):
    # Try direct JSON
    if isinstance(result, dict) and "searchResults" in result:
        return result["searchResults"]
    
    # Try content array
    if "content" in result:
        text = result["content"][0].get("text", "")
        return json.loads(text)
    
    # Try extracting JSON from string
    start_idx = result_str.find('{')
    end_idx = result_str.rfind('}')
    return json.loads(result_str[start_idx:end_idx+1])
```

### Challenge 4: API Rate Limits and Errors

**Problem**: External APIs (Aviationstack, Airbnb) can:
- Return 429 (Too Many Requests)
- Return 400 (Bad Request) for invalid parameters
- Timeout on slow connections
- Return unexpected error formats

**Solution**:
- **Error handling**: Catch and parse API errors
- **Fallback tools**: Use alternative search methods (e.g., airline search if schedule search fails)
- **User-friendly messages**: Convert technical errors to readable messages
- **Retry logic**: Built into LangChain's AgentExecutor

**Code approach**:
```python
try:
    result = connector.call_mcp_tool(...)
except Exception as e:
    if "429" in str(e):
        return "Rate limited. Please try again later."
    elif "400" in str(e):
        return "Invalid search parameters. Please check dates and locations."
    # Try fallback method
    return self._fallback_airline_search(...)
```

### Challenge 5: Pydantic Version Compatibility

**Problem**: LangChain's `StructuredTool` expects Pydantic v1 models, but we have Pydantic v2 installed.

**Solution**:
- Use `pydantic.v1` for tool schemas
- Use `pydantic` v2 for other validations
- Import both: `from pydantic.v1 import BaseModel, Field`

**Why this matters**: Tool schemas must be compatible with LangChain's internal serialization.

### Challenge 6: URL Generation for Booking Links

**Problem**: Airbnb URLs need specific parameters (dates, guests) to work correctly. Raw URLs from API might not include user's requested dates.

**Solution**:
- **URL rebuilding**: Extract base URL from API response
- **Parameter injection**: Add checkin, checkout, and guest parameters
- **Validation**: Ensure dates match user's request

**Code approach**:
```python
def _format_property(self, prop, requirements):
    base_url = prop.get("url", "")
    # Rebuild URL with correct dates
    url = f"{base_url}?check_in={requirements['checkin_date']}&check_out={requirements['checkout_date']}&adults={requirements['guests']['adults']}"
    return {**prop, "url": url}
```

---

## 🚀 Running the Application

### Prerequisites:
1. Python 3.11+
2. OpenAI API key
3. Aviationstack API key (optional, for flights)
4. MCP servers configured (for Cursor IDE)

### Installation:

```bash
# Clone or navigate to project
cd travel-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Running:

**Option 1: Streamlit UI (Recommended)**
```bash
streamlit run streamlit_app.py
```
Opens at `http://localhost:8501`

**Option 2: Command Line**
```bash
python main.py
```

### Example Queries:

- "I'm traveling from Mumbai to Dubai on Feb 25, 2026. Show me hotels and flights."
- "Find me a place in Coorg, India for Dec 25-30, 2 adults, 1 child, budget $100-200 per night"
- "Show me flights from Delhi to Dubai on February 25, 2026"

---

## 📊 Performance Considerations

### Token Usage:
- **Parser Agent**: ~500-1000 tokens per query
- **Property Agent**: ~2000-5000 tokens (depends on results)
- **Flight Agent**: ~1000-3000 tokens
- **Analysis Agent**: ~3000-8000 tokens (depends on property count)
- **Total**: ~$0.10-0.50 per complete query

### Response Time:
- **Parser**: < 2 seconds
- **Property Search**: 3-10 seconds (depends on Airbnb API)
- **Flight Search**: 2-8 seconds (depends on Aviationstack API)
- **Analysis**: 5-15 seconds (depends on property count)
- **Total**: 15-40 seconds for complete workflow

### Optimization Tips:
- Limit property results to top 10
- Use direct tool calls instead of LLM when possible
- Cache frequently searched locations
- Implement request queuing for high traffic

---

## 🎓 Key Takeaways

1. **Multi-agent systems** are more robust and maintainable than single agents
2. **LangChain** simplifies agent creation and tool integration
3. **MCP protocol** provides standardized access to external tools
4. **Specialized agents** outperform general-purpose agents
5. **Error handling** and fallbacks are crucial for production systems
6. **Context management** is essential when working with large datasets
7. **Tool wrappers** bridge the gap between agents and external APIs

---

## 🔮 Future Enhancements

- **Caching**: Store search results to reduce API calls
- **Multi-modal**: Add image analysis for property recommendations
- **Booking integration**: Direct booking through APIs
- **Price tracking**: Monitor price changes over time
- **Recommendation engine**: Learn from user preferences
- **Multi-language support**: Handle queries in different languages
- **Voice interface**: Add speech-to-text and text-to-speech

---

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Pydantic Documentation](https://docs.pydantic.dev)

---

## 💡 Conclusion

Building a multi-agent travel assistant demonstrates the power of modern AI frameworks. By combining specialized agents, robust tooling, and intelligent orchestration, we create a system that's more than the sum of its parts.

The key is understanding when to use agents (complex reasoning) vs. direct tool calls (simple operations), and how to structure your system for maintainability and scalability.

Whether you're building a travel assistant, customer service bot, or data analysis tool, the principles remain the same: **specialize, orchestrate, and handle errors gracefully**.

---

*Happy building! 🚀*
