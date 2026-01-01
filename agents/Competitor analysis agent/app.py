"""
Main Streamlit Application for Competitor Analysis System
Multi-agent system powered by CrewAI for automated competitor analysis
"""

import streamlit as st
import logging
from datetime import datetime
from crewai import Crew, Process
import config
from agents import create_all_agents
from tasks import create_all_tasks
from utils import (
    PDFReportGenerator,
    format_report_for_display,
    extract_key_metrics,
    generate_filename
)

# Configure page
st.set_page_config(
    page_title="Competitor Analysis System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'report_content' not in st.session_state:
        st.session_state.report_content = None
    if 'company_name' not in st.session_state:
        st.session_state.company_name = ""
    if 'industry' not in st.session_state:
        st.session_state.industry = ""
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False


def validate_api_keys():
    """Validate that required API keys are configured"""
    is_valid, message = config.validate_config()
    
    if not is_valid:
        st.error(f"⚠️ Configuration Error: {message}")
        st.info("""
        **Setup Instructions:**
        1. Create a `.env` file in the project directory
        2. Add your API keys:
           ```
           OPENAI_API_KEY=your_openai_key_here
           SERPAPI_API_KEY=your_serpapi_key_here
           ```
        3. Restart the application
        
        **Get API Keys:**
        - OpenAI: https://platform.openai.com/api-keys
        - SerpAPI: https://serpapi.com/manage-api-key
        """)
        return False
    
    return True


def render_sidebar():
    """Render sidebar with input form"""
    with st.sidebar:
        st.title("🔍 Competitor Analysis")
        st.markdown("---")
        
        # Company Information
        st.subheader("Company Information")
        
        company_name = st.text_input(
            "Company Name *",
            placeholder="e.g., Slack, Shopify, Tesla",
            help="Enter the name of your company or the company you want to analyze"
        )
        
        industry = st.selectbox(
            "Industry *",
            options=config.INDUSTRIES,
            help="Select the industry sector"
        )
        
        st.markdown("---")
        
        # Analysis Settings
        st.subheader("Analysis Settings")
        
        num_competitors = st.slider(
            "Number of Competitors",
            min_value=1,
            max_value=config.MAX_COMPETITORS,
            value=config.DEFAULT_COMPETITORS,
            help="How many competitors to analyze"
        )
        
        analysis_depth = st.selectbox(
            "Analysis Depth",
            options=list(config.ANALYSIS_DEPTH_CONFIG.keys()),
            format_func=lambda x: f"{x.title()} - {config.ANALYSIS_DEPTH_CONFIG[x]['description']}",
            help="Choose the depth of analysis"
        )
        
        st.markdown("---")
        
        # Action Button
        start_analysis = st.button(
            "🚀 Start Analysis",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.analysis_running
        )
        
        # Validation
        if start_analysis:
            if not company_name or not industry:
                st.error("Please fill in all required fields (*)")
                return None, None, None, None
            
            return company_name, industry, num_competitors, analysis_depth
        
        # Info section
        if st.session_state.analysis_running:
            st.info("⏳ Analysis in progress...")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This AI-powered system uses multiple specialized agents to:
        - 🔎 Research competitors
        - 📊 Analyze market positioning
        - 📝 Generate strategic insights
        """)
        
        return None, None, None, None


def render_welcome_screen():
    """Render welcome screen before analysis"""
    st.title("🔍 AI-Powered Competitor Analysis System")
    
    st.markdown("""
    ### Welcome to the Competitor Analysis Platform
    
    This system uses advanced AI agents to conduct comprehensive competitor research and analysis.
    
    #### How It Works:
    
    1. **Research Agent** 🔎
       - Discovers and gathers data on your competitors
       - Collects pricing, features, and customer feedback
       - Identifies market positioning
    
    2. **Analysis Agent** 📊
       - Performs SWOT analysis on each competitor
       - Creates competitive comparison matrices
       - Analyzes market dynamics and trends
    
    3. **Report Agent** 📝
       - Synthesizes insights into strategic recommendations
       - Generates executive-ready reports
       - Identifies opportunities and threats
    
    #### Get Started:
    
    👈 Fill in the form in the sidebar to begin your competitor analysis.
    
    ---
    """)
    
    # Features grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Accurate")
        st.write("Real-time data from reliable sources")
    
    with col2:
        st.markdown("### ⚡ Fast")
        st.write("Complete analysis in minutes")
    
    with col3:
        st.markdown("### 💡 Actionable")
        st.write("Strategic recommendations you can use")


def run_competitor_analysis(company_name: str, industry: str, num_competitors: int, analysis_depth: str):
    """
    Execute the competitor analysis using CrewAI
    
    Args:
        company_name: Name of the company to analyze
        industry: Industry sector
        num_competitors: Number of competitors to analyze
        analysis_depth: Depth of analysis (quick/standard/deep)
    """
    try:
        st.session_state.analysis_running = True
        st.session_state.company_name = company_name
        st.session_state.industry = industry
        
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔄 Analysis in Progress")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Initialize Agents
            status_text.text("🤖 Initializing AI agents...")
            progress_bar.progress(10)
            
            agents = create_all_agents(company_name, industry)
            logger.info("Agents created successfully")
            
            # Step 2: Create Tasks
            status_text.text("📋 Creating analysis tasks...")
            progress_bar.progress(20)
            
            tasks = create_all_tasks(agents, company_name, industry, num_competitors)
            logger.info("Tasks created successfully")
            
            # Step 3: Create Crew
            status_text.text("👥 Assembling crew...")
            progress_bar.progress(30)
            
            crew = Crew(
                agents=list(agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            logger.info("Crew assembled successfully")
            
            # Step 4: Execute Analysis
            status_text.text("🔎 Research Agent: Discovering competitors...")
            progress_bar.progress(40)
            
            # Execute the crew
            with st.spinner("Analysis in progress... This may take several minutes."):
                result = crew.kickoff()
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store results
            st.session_state.report_content = str(result)
            st.session_state.analysis_complete = True
            st.session_state.analysis_running = False
            
            logger.info("Analysis completed successfully")
            
            # Success message
            st.success("🎉 Competitor analysis completed successfully!")
            st.balloons()
            
            # Rerun to show results
            st.rerun()
            
    except Exception as e:
        st.session_state.analysis_running = False
        logger.error(f"Error during analysis: {str(e)}")
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        st.info("Please check your API keys and try again.")


def render_results():
    """Render analysis results in tabs"""
    if not st.session_state.analysis_complete or not st.session_state.report_content:
        return
    
    st.title(f"📊 Competitor Analysis: {st.session_state.company_name}")
    st.markdown(f"**Industry:** {st.session_state.industry} | **Date:** {datetime.now().strftime('%B %d, %Y')}")
    st.markdown("---")
    
    # Extract metrics for summary
    metrics = extract_key_metrics(st.session_state.report_content)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Competitors Analyzed", metrics.get('num_competitors', 'N/A'))
    
    with col2:
        st.metric("Key Findings", len(metrics.get('key_findings', [])))
    
    with col3:
        st.metric("Opportunities", metrics.get('opportunities', 'N/A'))
    
    with col4:
        st.metric("Threat Level", metrics.get('threat_level', 'Medium'))
    
    st.markdown("---")
    
    # Parse report into sections
    sections = format_report_for_display(st.session_state.report_content)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Overview",
        "🔍 Detailed Analysis",
        "📊 Competitor Matrix",
        "💡 Recommendations"
    ])
    
    with tab1:
        st.markdown("### Executive Summary")
        if sections['overview']:
            st.markdown(sections['overview'])
        else:
            st.info("Overview section not available")
    
    with tab2:
        st.markdown("### Detailed Competitor Analysis")
        if sections['detailed_analysis']:
            st.markdown(sections['detailed_analysis'])
        else:
            st.info("Detailed analysis section not available")
    
    with tab3:
        st.markdown("### Competitive Comparison Matrix")
        if sections['competitor_matrix']:
            st.markdown(sections['competitor_matrix'])
        else:
            st.info("Comparison matrix not available")
    
    with tab4:
        st.markdown("### Strategic Recommendations")
        if sections['recommendations']:
            st.markdown(sections['recommendations'])
        else:
            st.info("Recommendations section not available")
    
    # Export section
    st.markdown("---")
    st.markdown("### 📥 Export Report")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # PDF Export
        if st.button("📄 Download PDF", use_container_width=True):
            try:
                with st.spinner("Generating PDF..."):
                    pdf_generator = PDFReportGenerator(
                        st.session_state.company_name,
                        st.session_state.industry
                    )
                    pdf_buffer = pdf_generator.generate_pdf(st.session_state.report_content)
                    
                    filename = generate_filename(st.session_state.company_name, "pdf")
                    
                    st.download_button(
                        label="💾 Save PDF",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf"
                    )
                    st.success("PDF generated successfully!")
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        # Text Export
        filename = generate_filename(st.session_state.company_name, "txt")
        st.download_button(
            label="📝 Download Text",
            data=st.session_state.report_content,
            file_name=filename,
            mime="text/plain",
            use_container_width=True
        )
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Analysis", use_container_width=False):
        st.session_state.analysis_complete = False
        st.session_state.report_content = None
        st.rerun()


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Validate API keys
    if not validate_api_keys():
        return
    
    # Render sidebar and get inputs
    company_name, industry, num_competitors, analysis_depth = render_sidebar()
    
    # Main content area
    if st.session_state.analysis_complete:
        # Show results
        render_results()
    elif company_name and industry:
        # Run analysis
        run_competitor_analysis(company_name, industry, num_competitors, analysis_depth)
    else:
        # Show welcome screen
        render_welcome_screen()


if __name__ == "__main__":
    main()

