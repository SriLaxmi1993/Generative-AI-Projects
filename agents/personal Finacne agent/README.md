# 💰 Finance Insights - AI Multi-Agent Finance Tracker

An intelligent finance tracking application powered by **CrewAI** multi-agent system that analyzes bank statements and provides personalized financial insights and recommendations.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-0.28.8-purple.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### 🤖 Multi-Agent System
- **Spending Analyst Agent**: Analyzes transactions, categorizes expenses, and identifies spending patterns
- **Financial Advisor Agent**: Provides personalized recommendations and creates action plans

### 🎯 Smart Processing
- **Universal Format Support**: Handles CSV, Excel, and PDF bank statements
- **AI-Powered Extraction**: Uses GPT-4 to intelligently extract transaction data from any format
- **No Rigid Requirements**: Works with any column structure or layout

### 💡 Comprehensive Analysis
- Automatic spending categorization
- Top spending categories identification
- Average daily/weekly spending calculations
- Largest transaction tracking
- Behavioral pattern recognition
- Personalized budget recommendations
- 30-day action plans

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Agent
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Running the Application

**Option 1: Using the startup script**
```bash
./run_streamlit.sh
```

**Option 2: Manual start**
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 📖 Usage

1. **Upload Your Bank Statement**
   - Click the upload button
   - Select your bank statement file (CSV, Excel, or PDF)
   - Any format works - the AI will extract the data!

2. **Analyze**
   - Click "🚀 Analyze My Spending"
   - Wait 30-60 seconds for AI processing

3. **Review Insights**
   - View spending analysis from the Analyst Agent
   - Read personalized recommendations from the Advisor Agent
   - Get your 30-day action plan

## 📊 Supported File Formats

### CSV Files
```csv
Date,Description,Amount
2024-01-01,Grocery Store,-125.50
2024-01-02,Coffee Shop,-4.50
```

### Excel Files
- `.xlsx` and `.xls` formats
- Any column structure

### PDF Files
- Bank statement PDFs
- AI extracts transaction data automatically

## 🏗️ Project Structure

```
Agent/
├── streamlit_app.py       # Main Streamlit application
├── agents.py              # CrewAI agent definitions
├── tasks.py               # Agent task definitions
├── crew.py                # Multi-agent orchestration
├── smart_processor.py     # AI-powered file processor
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── run_streamlit.sh      # Startup script
└── README.md             # This file
```

## 🔧 Configuration

### Agent Configuration
Edit `agents.py` to customize:
- LLM model (default: GPT-4)
- Agent roles and behaviors
- Temperature settings

### Task Configuration
Edit `tasks.py` to customize:
- Analysis format
- Recommendation structure
- Output requirements

## �️ Security & Privacy

- ✅ Bank statements are processed locally
- ✅ Files are deleted immediately after processing
- ✅ No permanent data storage
- ✅ API calls to OpenAI are made over HTTPS
- ✅ `.env` file is gitignored (never commit your API key)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI)
- UI powered by [Streamlit](https://streamlit.io/)
- AI capabilities by [OpenAI](https://openai.com/)

## 📧 Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🎯 Roadmap

- [ ] Multi-month trend analysis
- [ ] Budget tracking and alerts
- [ ] Recurring transaction detection
- [ ] Savings goal tracking
- [ ] Export reports as PDF
- [ ] Multiple account support
- [ ] Mobile app version

---

**Made with ❤️ using CrewAI Multi-Agent System**
