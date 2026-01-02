#!/bin/bash

# Simple Streamlit Startup Script for Finance Insights

echo "🚀 Starting Finance Insights - Streamlit Edition"
echo ""

# Activate virtual environment
source venv/bin/activate

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Please make sure you have your OpenAI API key in .env"
    exit 1
fi

echo "✅ Starting Streamlit app..."
echo ""
echo "📝 The app will open in your browser automatically"
echo "   If not, navigate to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Streamlit
streamlit run streamlit_app.py
