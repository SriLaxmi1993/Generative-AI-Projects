"""
Finance Insights - Streamlit UI for Multi-Agent System
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from smart_processor import SmartBankStatementProcessor
from crew import analyze_finances
import json

# Page configuration
st.set_page_config(
    page_title="Finance Insights - AI-Powered Analysis",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #0f0f23;
    }
    .stApp {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("💰 Finance Insights")
st.markdown("### AI-Powered Spending Analysis with Multi-Agent System")
st.markdown("Upload your bank statement and let our AI agents analyze your spending behavior and provide personalized recommendations.")

# Sidebar
with st.sidebar:
    st.header("📊 About")
    st.markdown("""
    This application uses **CrewAI** with two specialized agents:
    
    🤖 **Spending Analyst Agent**
    - Categorizes transactions
    - Identifies spending patterns
    - Analyzes trends
    
    💡 **Financial Advisor Agent**
    - Provides recommendations
    - Suggests budgets
    - Creates action plans
    """)
    
    st.markdown("---")
    st.markdown("**Supported Formats:**")
    st.markdown("- CSV files")
    st.markdown("- Excel files (.xlsx, .xls)")
    st.markdown("- PDF bank statements")

# Main content
uploaded_file = st.file_uploader(
    "Upload Your Bank Statement",
    type=['csv', 'xlsx', 'xls', 'pdf'],
    help="Upload your monthly bank statement in CSV, Excel, or PDF format"
)

if uploaded_file is not None:
    # Show file details
    st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
    
    # Analyze button
    if st.button("🚀 Analyze My Spending", type="primary", use_container_width=True):
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Process file
            status_text.text("📄 Processing bank statement...")
            progress_bar.progress(20)
            
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process the file
            processor = SmartBankStatementProcessor()
            transaction_data = processor.process_file(temp_path)
            
            # Clean up temp file
            import os
            os.remove(temp_path)
            
            progress_bar.progress(40)
            
            # Step 2: Run AI analysis
            status_text.text("🤖 AI agents analyzing your spending patterns...")
            progress_bar.progress(50)
            
            results = analyze_finances(transaction_data)
            
            # Step 3: Display results
            status_text.text("📊 Displaying insights...")
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Display results
            st.markdown("---")
            st.header("📈 Your Financial Analysis")
            
            # Show analysis from Spending Analyst
            st.subheader("⚡ Spending Analysis")
            st.markdown(results['analysis'])
            
            st.markdown("---")
            
            # Show recommendations from Financial Advisor
            st.subheader("⭐ Personalized Recommendations")
            st.markdown(results['recommendations'])
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.exception(e)
            progress_bar.empty()
            status_text.empty()

else:
    # Show example format
    st.info("👆 Upload a bank statement to get started!")
    
    with st.expander("📝 Example CSV Format"):
        st.code("""Date,Description,Amount
2024-01-01,Grocery Store,-125.50
2024-01-02,Coffee Shop,-4.50
2024-01-03,Gas Station,-45.00
2024-01-04,Restaurant,-67.80
2024-01-05,Online Shopping,-89.99""", language="csv")
        
        st.markdown("**Column Requirements:**")
        st.markdown("- **Date**: Transaction date")
        st.markdown("- **Description**: Merchant or transaction description")
        st.markdown("- **Amount**: Transaction amount (negative for expenses)")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Powered by CrewAI Multi-Agent System | Your data is processed securely and never stored</p>
</div>
""", unsafe_allow_html=True)
