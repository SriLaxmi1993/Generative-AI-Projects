# Simple Data Analysis Agent (PydanticAI)

An AI-powered data analysis agent built with **PydanticAI** that allows you to analyze datasets using natural language queries. This agent can understand questions about your data and automatically generate pandas queries to extract insights.

**Built by:** Sri Laxmi

📚 **New to AI Agents?** Check out the comprehensive [TUTORIAL.md](TUTORIAL.md) for a complete guide covering:
- What AI agents are and how they work
- Framework comparison and why we chose PydanticAI
- Architecture deep dive with diagrams
- Step-by-step setup instructions
- API key management and security
- Common challenges and solutions
- Multi-agent systems explained
- And much more!

## 🎯 Overview

This agent democratizes data analysis by allowing non-technical users to explore datasets through natural language. Simply ask questions like "What is the average price?" or "Which salesperson sold the most cars?" and the agent will automatically query your data and provide answers.

## ✨ Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Flexible Data Input**: Upload CSV files or use synthetic sample data
- **Interactive Web Interface**: Beautiful Streamlit app with chat interface
- **Command Line Interface**: Simple CLI for quick data analysis
- **Smart Error Handling**: Automatic retry mechanism for query corrections
- **Safe Query Execution**: Limited pandas expression evaluation for security

## 🏗️ Architecture

### Key Components

1. **Agent Core** (`src/agent.py`): 
   - PydanticAI agent with dependency injection
   - Custom `df_query` tool for pandas DataFrame operations
   - Retry mechanism using `ModelRetry` for error correction

2. **Data Generator** (`src/data.py`):
   - Synthetic car sales dataset generator
   - Configurable dataset size and seed for reproducibility

3. **Streamlit App** (`streamlit_app.py`):
   - Interactive web interface
   - File upload support
   - Chat-based Q&A interface
   - Dataset preview and statistics

4. **CLI App** (`app.py`):
   - Command-line interface for quick analysis
   - Support for custom CSV files

### How It Works

1. **Data Loading**: Loads a pandas DataFrame (from CSV or synthetic data)
2. **Dependency Injection**: Injects the DataFrame into the agent via PydanticAI's dependency system
3. **Query Processing**: Agent receives natural language questions
4. **Tool Execution**: Agent uses the `df_query` tool to evaluate pandas expressions
5. **Response Generation**: Returns human-readable answers based on query results

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## 🚀 Setup

1. **Clone/Navigate to the project:**
   ```bash
   cd "agents/Simple Data Analysis Agent (PydanticAI)"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

## 💻 Usage

### Option 1: Streamlit Web App (Recommended)

Launch the interactive web interface:

```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

**Features:**
- 📁 Upload your own CSV files or use sample data
- 💬 Chat interface for asking questions
- 📊 View and download your dataset
- 📋 See dataset statistics
- 🔑 API key configuration in the UI

**Example Questions:**
- "What are the column names in this dataset?"
- "How many rows are in this dataset?"
- "What is the average price of cars sold?"
- "Which salesperson sold the most cars?"
- "What is the most common car color?"

### Option 2: Command Line Interface

**With synthetic dataset (car sales):**
```bash
python app.py
```

**With your own CSV file:**
```bash
python app.py --csv /path/to/your/data.csv
```

## 📁 Project Structure

```
Simple Data Analysis Agent (PydanticAI)/
├── src/
│   ├── __init__.py
│   ├── agent.py          # Agent definition and tool registration
│   └── data.py            # Synthetic data generator
├── app.py                 # CLI interface
├── streamlit_app.py      # Web interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Technical Details

### Agent Configuration

- **Model**: OpenAI GPT-4o-mini (configurable via `PYDANTICAI_MODEL` env var)
- **Retries**: 10 attempts for query error correction
- **Tool**: `df_query` - Evaluates pandas expressions using `pd.eval()`

### Security Features

The `df_query` tool includes safety guardrails:
- Blocks dangerous operations (`import`, `exec`, `open`, etc.)
- Limited to pandas expression evaluation
- No arbitrary code execution

### Query Examples

The agent can handle various pandas operations:
- Column access: `df['Price']`
- Aggregations: `df['Price'].mean()`
- Filtering: `df[df['Year'] > 2020]`
- Grouping: `df.groupby('Make')['Price'].mean()`

## 🛠️ Customization

### Change the Model

Set the `PYDANTICAI_MODEL` environment variable:
```bash
export PYDANTICAI_MODEL="openai:gpt-4"
```

### Modify System Prompt

Edit `SYSTEM_PROMPT` in `src/agent.py` to change agent behavior.

### Adjust Retry Count

Modify the `retries` parameter in `build_agent()` function.

## 📝 Example Workflow

1. **Start the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Enter your API key** in the sidebar

3. **Load data:**
   - Click "Generate Sample Data" for demo data, or
   - Upload your own CSV file

4. **Ask questions:**
   - Type questions in the chat interface
   - Get instant answers about your data

5. **Explore insights:**
   - View dataset statistics
   - Download analyzed data
   - Continue asking follow-up questions

## 🐛 Troubleshooting

### API Key Not Set
- Set `OPENAI_API_KEY` environment variable
- Or enter it in the Streamlit sidebar

### Port Already in Use
```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502

# Or stop existing Streamlit processes
pkill -f streamlit
```

### Query Errors
- The agent will automatically retry with corrected syntax
- Check that your CSV has proper column names
- Ensure data types are compatible with pandas operations

## 📚 Dependencies

- `pydantic-ai>=0.0.20` - Agent framework
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical operations
- `python-dotenv>=1.0.0` - Environment variable management
- `streamlit>=1.28.0` - Web interface

## 🤝 Contributing

This is a personal project. Feel free to fork and modify for your own use!

## 📄 License

[Specify your license here]

## 🙏 Acknowledgments

- Built using [PydanticAI](https://ai.pydantic.dev/)
- Inspired by the LangChain Data Analysis Agent tutorial
- Uses OpenAI's GPT models for natural language understanding

---

**Built with ❤️ using PydanticAI**