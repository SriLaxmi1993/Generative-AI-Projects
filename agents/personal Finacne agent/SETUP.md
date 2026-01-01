# Quick Setup Guide

## 1. Clone and Setup

```bash
git clone <your-repo-url>
cd "personal Finacne agent"
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure API Key

```bash
# Create .env file
touch .env
# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Get your API key**: [OpenAI Platform](https://platform.openai.com/api-keys)

## 3. Run the App

```bash
./run_streamlit.sh
```

Or manually:
```bash
streamlit run streamlit_app.py
```

## 4. Use the App

1. Open http://localhost:8501 in your browser
2. Upload a bank statement (CSV, Excel, or PDF)
3. Click "Analyze My Spending"
4. View AI-powered insights and recommendations

That's it! 🎉
