# 🔍 AI Domain Deep Research Agent

An advanced AI research agent built using the Agno Agent framework and OpenAI's GPT models. This agent helps users conduct comprehensive research on any topic by generating research questions, finding answers through multiple search engines, and compiling professional reports with multiple export options.

## Features

### 🧠 **Intelligent Question Generation**

- Automatically generates customizable research questions (3-10 questions)
- Supports multiple question types: yes/no, open-ended, comparative, and analytical
- Tailors questions to your specified domain
- Dynamic question generation based on research needs

### 🔎 **Multi-Source Research**

- Uses **SerpApi** (Google Search API) for comprehensive web results with source tracking
- Leverages **Perplexity AI** for deeper analysis
- Combines multiple sources for thorough research
- Parallel processing for faster research execution
- Automatic citation extraction and tracking

### 📊 **Professional Report Generation**

- Compiles research findings into a McKinsey-style report
- Structures content with executive summary, analysis, and conclusion
- Includes comprehensive source citations
- Multiple export formats: PDF, Markdown, and JSON

### 📥 **Export Capabilities**

- **PDF Export**: Professional formatted PDF reports
- **Markdown Export**: Markdown format for easy editing and sharing
- **JSON Export**: Structured data export for programmatic use
- One-click download buttons for all formats

### 📚 **Research History**

- Saves research sessions automatically
- Access previous research topics from sidebar
- Quick reload of past research sessions
- Maintains last 10 research sessions

### ⚡ **Performance Enhancements**

- Parallel question research using asyncio
- Real-time progress tracking
- Optimized agent calls
- Faster research completion

### 🖥️ **User-Friendly Interface**

- Clean Streamlit UI with intuitive workflow
- Collapsible sections for better organization
- Real-time progress indicators
- Expandable sections to view detailed results
- Research settings customization panel

## How to Run

### 1. **Setup Environment**

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure API Keys**

You'll need the following API keys:

- **OpenAI API Key** (Required): Get from [OpenAI Platform](https://platform.openai.com)
- **SerpApi Key** (Required): Get from [SerpApi](https://serpapi.com)
- **Perplexity API Key** (Optional): Get from [Perplexity AI](https://www.perplexity.ai/settings/api)

**Setting up SerpApi:**
1. Go to [SerpApi](https://serpapi.com) and sign up for an account
2. Get your API key from the dashboard
3. SerpApi provides Google Search results via their API (no need for Google Cloud setup)

Add these to a `.env` file:
```env
OPENAI_API_KEY=your_openai_key_here
SERPAPI_KEY=your_serpapi_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
```

Or enter them directly in the app sidebar.

### 3. **Run the Application**

```bash
streamlit run app.py
```

## Usage

1. Launch the application using the command above
2. Enter your OpenAI API key and SerpApi key in the sidebar (Perplexity is optional)
3. Input your research topic and domain in the main interface
4. **Customize Research Settings**:
   - Select number of questions (3-10)
   - Choose question type (yes/no, open-ended, comparative, analytical)
5. Click "Generate Research Questions" to create specific questions
6. Review the questions and click "Start Research" to begin the parallel research process
7. View research results with source citations
8. Once research is complete, click "Compile Final Report" to generate a professional report
9. **Export your report** in PDF, Markdown, or JSON format
10. View the report in the app and access it in Google Docs

## New Features

### Question Customization
- Adjust the number of research questions (3-10)
- Select from different question types for varied research approaches

### Parallel Research Processing
- Research multiple questions simultaneously for faster results
- Real-time progress tracking for each question

### Citation Tracking
- Automatic extraction of source URLs from search results
- Source credibility indicators
- Comprehensive citations section in reports

### Export Options
- Download reports in multiple formats
- PDF for professional presentations
- Markdown for easy editing
- JSON for data analysis

### Research History
- Automatic saving of research sessions
- Quick access to previous research
- Reload past research with one click

## Technical Details

- **Agno Framework**: Used for creating and orchestrating AI agents
- **OpenAI**: Provides GPT-4 model for advanced language processing
- **SerpApi**: Google Search API service for comprehensive web results
- **Perplexity AI**: Deep analysis and research capabilities (optional)
- **Streamlit**: Powers the user interface with interactive elements
- **Asyncio**: Enables parallel processing for faster research

## Dependencies

- `agno>=2.2.10` - Agent framework
- `streamlit` - Web interface
- `openai` - OpenAI API client
- `requests` - HTTP library for API integrations (SerpApi, Perplexity)
- `reportlab` - PDF generation
- `python-dotenv` - Environment variable management

## Example Use Cases

- **Academic Research**: Quickly gather information on academic topics across various disciplines
- **Market Analysis**: Research market trends, competitors, and industry developments
- **Policy Research**: Analyze policy implications and historical context
- **Technology Evaluation**: Research emerging technologies and their potential impact
- **Competitive Intelligence**: Analyze competitors and market positioning
- **Trend Analysis**: Track and analyze industry trends

