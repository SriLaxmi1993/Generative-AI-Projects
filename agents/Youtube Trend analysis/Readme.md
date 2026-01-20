# YouTube Trend Analysis with CrewAI and YouTube Data API

A powerful YouTube trend analysis tool that scrapes videos from multiple channels, extracts transcripts, and uses AI agents to analyze trends, topics, sentiment, and patterns across video content.

## Features

- 🔍 **Multi-Channel Analysis**: Analyze videos from multiple YouTube channels simultaneously
- 📅 **Date Range Filtering**: Filter videos by specific date ranges
- 🤖 **AI-Powered Analysis**: Uses CrewAI agents to analyze transcripts and identify trends
- 📊 **Comprehensive Reports**: Generates detailed reports on topics, trends, sentiment, and keywords
- 🎥 **Visual Interface**: Streamlit-based web interface with video previews
- 💾 **Export Reports**: Download analysis results as Markdown files

## Technology Stack

- **Streamlit**: Web interface framework
- **CrewAI**: Multi-agent AI orchestration for analysis
- **YouTube Data API v3**: YouTube video search and metadata
- **youtube-transcript-api**: Transcript extraction from YouTube videos
- **OpenAI GPT-4o**: Large language model for transcript analysis
- **Python**: Backend logic and data processing

## Prerequisites

- Python 3.11 or later
- Google Cloud project with YouTube Data API v3 enabled
- OpenAI API account

## Setup and Installation

### 1. Get API Keys

- **YouTube Data API Key**: 
  - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
  - Enable **YouTube Data API v3**
  - Create an API key (API key only, no OAuth needed)

- **OpenAI API Key**: 
  - Sign up for an account at [OpenAI](https://platform.openai.com)
  - Go to [API Keys](https://platform.openai.com/api-keys) section
  - Create and copy your API key

### 2. Configure Environment Variables

Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Then edit the `.env` file and add your API keys:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install streamlit crewai crewai-tools python-dotenv langchain-openai youtube-transcript-api requests pyyaml tqdm
```

**Note**: Make sure you have compatible versions:
- `langchain<0.2.0` (required by CrewAI)
- `langchain-openai<0.2.0` (compatible with CrewAI)
- `openai<2.0.0` (required by CrewAI)

If you encounter version conflicts, install compatible versions:

```bash
pip install "langchain<0.2.0" "langchain-openai<0.2.0" "openai<2.0.0"
```

## Usage

### Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Or specify a custom port to avoid conflicts with other Streamlit apps:

```bash
streamlit run app.py --server.port 8502
```

The application will open in your default web browser at `http://localhost:8501` (or the port you specified)

### How to Use

1. **Add YouTube Channels**: 
   - In the sidebar, enter one or more YouTube channel URLs
   - Click "Add Channel ➕" to add additional channels

2. **Set Date Range**: 
   - Select the start and end dates for the videos you want to analyze

3. **Start Analysis**: 
   - Click the "Start Analysis 🚀" button
   - The system will:
     - Scrape videos from the specified channels
     - Extract and process video transcripts
     - Display the scraped videos
     - Run AI analysis on the transcripts
     - Generate a comprehensive trend analysis report

4. **View Results**: 
   - The analysis report will be displayed in the main area
   - Download the report as a Markdown file using the download button

## Project Structure

```
.
├── app.py                  # Main Streamlit application
├── youtube_api_scraper.py  # YouTube Data API scraper for YouTube videos
├── config.yaml            # CrewAI agent and task configuration
├── .env                   # Environment variables (API keys) - NOT in git
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
├── TUTORIAL.md            # Comprehensive tutorial guide
└── transcripts/           # Directory for saved video transcripts (created automatically)
```

## How It Works

1. **User Input**: User provides YouTube channel URLs and date range via Streamlit UI
2. **Scraping Phase**: Uses YouTube Data API v3 to search and scrape YouTube videos from specified channels within the date range
3. **Transcript Extraction**: Uses `youtube-transcript-api` to extract formatted transcripts from each video (or falls back to title/description if unavailable)
4. **File Processing**: Saves transcripts to individual text files in the `transcripts/` directory
5. **AI Agent Orchestration**: 
   - **Analysis Agent**: Uses CrewAI and GPT-4o to analyze transcripts for topics, trends, sentiment, and keywords
   - **Response Synthesizer Agent**: Synthesizes the detailed analysis into a concise, actionable report
   - Both agents work sequentially using CrewAI's Process.sequential
6. **Report Generation**: Displays the final analysis report and provides download functionality

## Key Features

- ✅ **Multi-Agent System**: Two specialized AI agents working together
- ✅ **Robust Error Handling**: Gracefully handles missing transcripts, API errors, and edge cases
- ✅ **Flexible Response Handling**: Works with both string responses and CrewAI response objects
- ✅ **Quick Mode**: Option to skip transcript extraction for faster processing
- ✅ **Multi-Channel Support**: Analyze multiple channels simultaneously
- ✅ **Date Range Filtering**: Focus analysis on specific time periods

## Configuration

The AI agents and their tasks are configured in `config.yaml`. You can customize:
- Agent roles and goals
- Analysis tasks and expected outputs
- Agent backstories and behaviors

## Troubleshooting

### Common Issues

- **"No videos found"**: Check date range, channel URL format, or API quota
- **Import errors**: Ensure compatible package versions (see Installation section)
- **Port conflicts**: Use `--server.port` flag to specify a different port
- **API key errors**: Verify `.env` file exists and keys are correctly named

For detailed troubleshooting, see [TUTORIAL.md](TUTORIAL.md).

## Documentation

- **[TUTORIAL.md](TUTORIAL.md)**: Comprehensive guide covering AI agents, architecture, setup, and usage
- **[README.md](README.md)**: This file - quick start and overview

## Contributing

Contributions are welcome! Please feel free to submit a pull request with your improvements.

## License

This project is open source and available for use and modification.