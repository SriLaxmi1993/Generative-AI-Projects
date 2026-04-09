# AI Travel Assistant - Multi-Agent System

An intelligent travel planning assistant built with LangChain, OpenAI GPT-4, and Model Context Protocol (MCP). This multi-agent system helps users find Airbnb properties and flight schedules through natural language queries.

## 🎯 Features

- **Natural Language Processing**: Understands travel queries in plain English
- **Multi-Agent Architecture**: Specialized agents for parsing, property search, flight search, and analysis
- **Airbnb Integration**: Search and filter properties by location, dates, guests, and budget
- **Flight Schedules**: Find flight schedules for specific routes and dates
- **Intelligent Analysis**: AI-powered scoring and ranking of properties
- **Web UI**: Beautiful Streamlit interface for easy interaction
- **CLI Support**: Command-line interface for programmatic use

## 🏗️ Architecture

This project uses a multi-agent system with four specialized agents:

1. **Parser Agent**: Extracts structured requirements from natural language queries
2. **Property Agent**: Searches Airbnb for available properties
3. **Flight Agent**: Finds flight schedules using Aviationstack API
4. **Analysis Agent**: Scores and ranks properties based on user requirements
5. **Orchestrator**: Coordinates all agents and combines results

See [tutorial.md](tutorial.md) for detailed architecture and implementation details.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Aviationstack API key (optional, for flight search)
- MCP servers configured (for Cursor IDE integration)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd travel-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

4. Configure MCP servers (for Cursor IDE):
   - Edit `~/.cursor/mcp.json`
   - Add Airbnb and Aviationstack MCP server configurations
   - See [tutorial.md](tutorial.md) for detailed setup instructions

### Running the Application

**Option 1: Streamlit UI (Recommended)**
```bash
streamlit run streamlit_app.py
```
Opens at `http://localhost:8501`

**Option 2: Command Line Interface**
```bash
python main.py
```

## 📖 Usage Examples

- "I'm traveling from Mumbai to Dubai on Feb 25, 2026. Show me hotels and flights."
- "Find me a place in Coorg, India for Dec 25-30, 2 adults, 1 child, budget $100-200 per night"
- "Show me flights from Delhi to Dubai on February 25, 2026"

## 📚 Documentation

- **[tutorial.md](tutorial.md)**: Comprehensive tutorial covering:
  - What is an AI agent
  - Frameworks and tools used
  - Architecture overview
  - Multi-agent system design
  - API key setup
  - Challenges and solutions
  - Performance considerations

## 🛠️ Tech Stack

- **LangChain**: Agent framework and tool integration
- **OpenAI GPT-4**: Language model for agent reasoning
- **Model Context Protocol (MCP)**: Protocol for external tool integration
- **Streamlit**: Web UI framework
- **Pydantic**: Data validation
- **Python-dotenv**: Environment variable management

## 📁 Project Structure

```
travel-agent/
├── main.py                 # CLI entry point
├── streamlit_app.py        # Web UI entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── tutorial.md             # Comprehensive tutorial
├── .gitignore             # Git ignore rules
│
└── src/
    ├── agents/             # AI Agent implementations
    │   ├── orchestrator.py    # Main coordinator
    │   ├── parser_agent.py    # Extracts requirements
    │   ├── property_agent.py  # Searches properties
    │   ├── flight_agent.py     # Searches flights
    │   └── analysis_agent.py   # Scores and ranks
    │
    ├── tools/              # External tool integrations
    │   ├── mcp_connector.py   # MCP protocol handler
    │   ├── airbnb_tools.py    # Airbnb search tools
    │   └── flight_tools.py    # Flight search tools
    │
    └── prompts/            # Agent prompt templates
        └── agent_prompts.py   # System prompts
```

## 🔑 API Keys

### OpenAI API Key
1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Create an API key in the dashboard
3. Add to `.env` file: `OPENAI_API_KEY=sk-your-key-here`

### Aviationstack API Key (Optional)
1. Sign up at [aviationstack.com](https://aviationstack.com)
2. Get your API key from the dashboard
3. Add to MCP server configuration in `~/.cursor/mcp.json`

See [tutorial.md](tutorial.md) for detailed setup instructions.

## ⚠️ Important Notes

- MCP tools work best when running through Cursor IDE's AI assistant
- The system requires internet connectivity for API calls
- API usage incurs costs (see [tutorial.md](tutorial.md) for pricing details)
- Some features may be rate-limited by external APIs

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [LangChain](https://python.langchain.com) for the agent framework
- [OpenAI](https://openai.com) for GPT-4
- [Model Context Protocol](https://modelcontextprotocol.io) for tool integration
- [Streamlit](https://streamlit.io) for the UI framework

---

For detailed technical documentation, architecture explanations, and implementation details, see [tutorial.md](tutorial.md).
