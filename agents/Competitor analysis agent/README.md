# 🔍 AI-Powered Competitor Analysis System

A production-ready multi-agent competitor analysis system built with CrewAI and Streamlit. This system uses three specialized AI agents to automatically research, analyze, and report on competitive landscapes.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-0.28-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.33-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **Multi-Agent Architecture**: Three specialized AI agents working in sequence
  - 🔎 **Research Agent**: Discovers and gathers competitor data
  - 📊 **Analysis Agent**: Performs SWOT and competitive analysis
  - 📝 **Report Agent**: Generates strategic insights and recommendations

- **Comprehensive Analysis**:
  - Competitor discovery and profiling
  - SWOT analysis for each competitor
  - Competitive comparison matrices
  - Market positioning analysis
  - Strategic recommendations

- **Professional UI**:
  - Clean Streamlit interface
  - Real-time progress tracking
  - Tabbed results display
  - PDF report export

- **Flexible Configuration**:
  - Multiple industry options
  - Adjustable analysis depth
  - Configurable number of competitors
  - Environment-based settings

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Keys Setup](#-api-keys-setup)
- [Cost Estimation](#-cost-estimation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🏗️ Architecture

```
User Input → Streamlit UI → CrewAI Orchestrator
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              Research Agent   Analysis Agent   Report Agent
                    ↓               ↓               ↓
                SerpAPI         Data Processing   Synthesis
                    ↓               ↓               ↓
              Competitor      SWOT Analysis    Final Report
                 Data         Comparisons      & Recommendations
```

### Agent Workflow

1. **Research Agent**:
   - Searches for competitors using SerpAPI
   - Gathers company information, pricing, and reviews
   - Collects market positioning data
   - Output: Structured competitor dataset

2. **Analysis Agent**:
   - Receives competitor data from Research Agent
   - Performs SWOT analysis for each competitor
   - Creates competitive comparison matrices
   - Identifies market trends and gaps
   - Output: Comprehensive competitive analysis

3. **Report Agent**:
   - Synthesizes research and analysis
   - Generates executive summary
   - Creates strategic recommendations
   - Identifies opportunities and threats
   - Output: Final professional report

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- SerpAPI key
- pip package manager

### Step 1: Clone or Download

```bash
# Navigate to the project directory
cd "Competitor analysis agent"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Add API Keys

Edit `.env` file with your API keys:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# SerpAPI Configuration
SERPAPI_API_KEY=your_serpapi_api_key_here

# Application Settings
LOG_LEVEL=INFO
MAX_COMPETITORS=5
DEFAULT_COMPETITORS=3
ANALYSIS_DEPTH=standard
```

### Step 3: Verify Configuration

The application will automatically validate your configuration on startup.

## 🔑 API Keys Setup

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key and add to `.env` file

**Pricing**: 
- GPT-4 Turbo: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
- GPT-3.5 Turbo: ~$0.0005 per 1K input tokens, ~$0.0015 per 1K output tokens

### SerpAPI Key

1. Go to [SerpAPI](https://serpapi.com/)
2. Sign up for a free account
3. Navigate to [API Key Management](https://serpapi.com/manage-api-key)
4. Copy your API key
5. Add to `.env` file

**Pricing**: 
- Free tier: 100 searches/month
- Paid plans start at $50/month for 5,000 searches

## 💻 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Interface

1. **Enter Company Information** (Sidebar):
   - Company Name: Enter the company to analyze
   - Industry: Select from dropdown
   - Number of Competitors: Choose 1-5 competitors
   - Analysis Depth: Select Quick/Standard/Deep

2. **Start Analysis**:
   - Click "🚀 Start Analysis" button
   - Wait for agents to complete (5-30 minutes depending on depth)
   - Watch progress indicators

3. **Review Results**:
   - Navigate through tabs:
     - Overview: Executive summary and key findings
     - Detailed Analysis: Full competitor breakdowns
     - Competitor Matrix: Feature/pricing comparisons
     - Recommendations: Strategic insights

4. **Export Report**:
   - Click "📄 Download PDF" for formatted report
   - Or "📝 Download Text" for plain text version

### Example Use Cases

**Technology Startup**:
```
Company: Slack
Industry: Technology / Software
Competitors: 3
Depth: Standard
```

**E-commerce Business**:
```
Company: Shopify
Industry: E-commerce / Retail
Competitors: 5
Depth: Deep
```

**Consulting Firm**:
```
Company: McKinsey
Industry: Consulting / Professional Services
Competitors: 3
Depth: Quick
```

## 📁 Project Structure

```
Competitor analysis agent/
│
├── app.py                    # Main Streamlit application
├── agents.py                 # Agent definitions (3 agents)
├── tasks.py                  # Task definitions (3 tasks)
├── tools.py                  # Custom tools (SerpAPI, data processing)
├── config.py                 # Configuration management
├── utils.py                  # Utility functions (PDF export, formatting)
│
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your actual environment variables (not in git)
│
├── README.md                # This file
└── competitor_analysis.log  # Application logs (auto-generated)
```

### Key Files

- **app.py**: Streamlit UI, user interaction, and workflow orchestration
- **agents.py**: Defines the three AI agents with roles, goals, and tools
- **tasks.py**: Defines sequential tasks for research, analysis, and reporting
- **tools.py**: Custom CrewAI tools for web search and data processing
- **config.py**: Configuration loading, validation, and constants
- **utils.py**: PDF generation, data formatting, and helper functions

## 💰 Cost Estimation

### Per Analysis Costs (Approximate)

**Standard Analysis** (3 competitors, standard depth):
- OpenAI API (GPT-4): ~$0.50 - $2.00
- SerpAPI searches: ~10-15 searches (free tier)
- Total: ~$0.50 - $2.00 per analysis

**Deep Analysis** (5 competitors, deep depth):
- OpenAI API (GPT-4): ~$2.00 - $5.00
- SerpAPI searches: ~20-30 searches (free tier)
- Total: ~$2.00 - $5.00 per analysis

**Monthly Costs** (example: 20 analyses/month):
- OpenAI: ~$40 - $60
- SerpAPI: Free tier sufficient (or $50 for paid tier)
- Total: ~$40 - $110/month

### Cost Optimization Tips

1. **Use GPT-3.5-turbo** for Research Agent (change in `config.py`)
2. **Start with Quick analysis** to test functionality
3. **Cache results** (already implemented in session state)
4. **Monitor SerpAPI usage** to stay within free tier

## 🐛 Troubleshooting

### Common Issues

**1. API Key Errors**

```
Error: OPENAI_API_KEY not found
```

**Solution**: 
- Verify `.env` file exists in project root
- Check API key is correctly formatted
- Restart Streamlit application

**2. Import Errors**

```
ModuleNotFoundError: No module named 'crewai'
```

**Solution**: 
```bash
pip install -r requirements.txt
```

**3. SerpAPI Rate Limits**

```
Error: Rate limit exceeded
```

**Solution**: 
- Wait for rate limit to reset
- Upgrade to paid SerpAPI plan
- Reduce number of competitors analyzed

**4. Analysis Takes Too Long**

**Solution**: 
- Use "Quick" analysis depth
- Reduce number of competitors
- Check internet connection
- Verify API services are operational

**5. PDF Generation Fails**

```
Error generating PDF
```

**Solution**: 
- Ensure reportlab is installed: `pip install reportlab`
- Check sufficient disk space
- Try downloading as text instead

### Debug Mode

Enable debug logging in `.env`:

```env
LOG_LEVEL=DEBUG
```

Check logs in `competitor_analysis.log` file.

### Getting Help

If you encounter issues:

1. Check the logs: `competitor_analysis.log`
2. Verify API keys are valid and have sufficient credits
3. Ensure all dependencies are installed
4. Try with a simpler analysis first (1 competitor, quick depth)
5. Check [CrewAI Documentation](https://docs.crewai.com/)
6. Check [Streamlit Documentation](https://docs.streamlit.io/)

## 🔧 Advanced Configuration

### Customizing Agents

Edit `agents.py` to modify agent behavior:

```python
# Change LLM temperature for more creative/conservative outputs
llm=create_llm(temperature=0.7)  # 0.0 = conservative, 1.0 = creative

# Change max iterations
max_iter=20  # More iterations = more thorough but slower
```

### Customizing Search

Edit `config.py` to modify search queries:

```python
COMPETITOR_SEARCH_QUERIES = [
    "{company_name} competitors {industry}",
    "your custom query here"
]
```

### Adding Custom Industries

Edit `config.py`:

```python
INDUSTRIES = [
    "Technology / Software",
    "Your Custom Industry",
    # ... add more
]
```

## 🚀 Deployment

### Local Deployment

Already configured for local use. Just run:

```bash
streamlit run app.py
```

### Streamlit Cloud Deployment

1. Push code to GitHub repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Add secrets in Streamlit Cloud dashboard:
   - `OPENAI_API_KEY`
   - `SERPAPI_API_KEY`
5. Deploy!

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Build and run:

```bash
docker build -t competitor-analysis .
docker run -p 8501:8501 --env-file .env competitor-analysis
```

## 📊 Performance Tips

1. **Use Caching**: Results are cached in session state (already implemented)
2. **Optimize Depth**: Start with "Quick" for testing
3. **Batch Analyses**: Run multiple analyses together to optimize API usage
4. **Monitor Logs**: Check `competitor_analysis.log` for performance insights

## 🔐 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys** regularly
4. **Monitor API usage** to detect anomalies
5. **Limit user access** if deploying publicly

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support and questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review logs in `competitor_analysis.log`
- Consult [CrewAI Documentation](https://docs.crewai.com/)

## 🙏 Acknowledgments

- Built with [CrewAI](https://www.crewai.com/)
- UI powered by [Streamlit](https://streamlit.io/)
- LLM by [OpenAI](https://openai.com/)
- Search by [SerpAPI](https://serpapi.com/)

---

**Made with ❤️ using AI and automation**

