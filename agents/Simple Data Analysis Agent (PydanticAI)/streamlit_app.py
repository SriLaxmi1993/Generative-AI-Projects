"""
Streamlit Web Application for Data Analysis Agent

Interactive web interface for the Simple Data Analysis Agent.
Allows users to upload data and ask questions in natural language.

Author: [Your Name]
Built with: Streamlit + PydanticAI
"""

from __future__ import annotations

import os
from io import StringIO

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load environment variables FIRST before importing agent
load_dotenv()
os.environ.setdefault("LOGFIRE_IGNORE_NO_CONFIG", "1")

# Now import agent components
from src.agent import Deps, build_agent
from src.data import make_car_sales_df

# Page config
st.set_page_config(
    page_title="Simple Data Analysis Agent (PydanticAI)",
    page_icon="📊",
    layout="wide",
)

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "data_source" not in st.session_state:
    st.session_state.data_source = None
if "agent" not in st.session_state:
    st.session_state.agent = None


def get_agent():
    """Get or create the agent instance."""
    if st.session_state.agent is None:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        st.session_state.agent = build_agent()
    return st.session_state.agent


def ask_agent(question: str, df: pd.DataFrame) -> str:
    """Ask the agent a question about the dataframe."""
    agent = get_agent()
    if agent is None:
        return "❌ Error: OpenAI API key not set. Please set it in the sidebar."
    deps = Deps(df=df)
    result = agent.run_sync(question, deps=deps)
    # Access the response data - try different methods
    try:
        # Try .data first (common in PydanticAI)
        return str(result.data)
    except AttributeError:
        try:
            # Try new_messages() approach
            return result.new_messages()[-1].content
        except (AttributeError, IndexError):
            # Fallback to string representation
            return str(result)


def main():
    st.title("📊 Simple Data Analysis Agent")
    st.markdown("**Built with PydanticAI** | Ask questions about your data in natural language!")

    # Sidebar for data upload
    with st.sidebar:
        # API Key Configuration
        st.header("🔑 Configuration")
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key. You can also set it via OPENAI_API_KEY environment variable.",
            key="api_key_input"
        )
        
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            # Reset agent if API key changed
            if st.session_state.agent is not None:
                st.session_state.agent = None
            st.session_state.agent = build_agent()
            st.success("✅ API key set!")
        elif not os.getenv("OPENAI_API_KEY"):
            st.warning("⚠️ Please enter your OpenAI API key to use the agent.")
        
        st.divider()
        st.header("📁 Data Source")
        
        data_option = st.radio(
            "Choose data source:",
            ["Use Sample Data", "Upload CSV"],
            key="data_option"
        )

        if data_option == "Use Sample Data":
            if st.button("Generate Sample Data", type="primary"):
                with st.spinner("Generating sample car sales data..."):
                    st.session_state.df = make_car_sales_df()
                    st.session_state.data_source = "Sample Data"
                    st.session_state.messages = []  # Clear chat history
                    st.success("Sample data loaded!")
                    st.rerun()

        else:  # Upload CSV
            uploaded_file = st.file_uploader(
                "Upload a CSV file",
                type=["csv"],
                help="Upload your CSV file to analyze"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.session_state.df = df
                    st.session_state.data_source = uploaded_file.name
                    st.session_state.messages = []  # Clear chat history
                    st.success(f"✅ Loaded {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error loading file: {e}")

        # Display data info
        if st.session_state.df is not None:
            st.divider()
            st.subheader("📋 Dataset Info")
            st.write(f"**Rows:** {len(st.session_state.df):,}")
            st.write(f"**Columns:** {len(st.session_state.df.columns)}")
            st.write(f"**Source:** {st.session_state.data_source}")

    # Main content area
    if st.session_state.df is None:
        st.info("👈 Please load data from the sidebar to get started!")
        st.markdown("""
        ### Example Questions:
        - "What are the column names?"
        - "How many rows are in this dataset?"
        - "What is the average price?"
        - "Which salesperson sold the most cars?"
        - "Show me the most common car color"
        """)
    else:
        # Display dataframe preview
        with st.expander("📊 View Dataset", expanded=False):
            st.dataframe(st.session_state.df, use_container_width=True)
            st.download_button(
                label="Download CSV",
                data=st.session_state.df.to_csv(index=False),
                file_name="dataset.csv",
                mime="text/csv"
            )

        # Chat interface
        st.subheader("💬 Ask Questions")

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about your data..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data..."):
                    try:
                        response = ask_agent(prompt, st.session_state.df)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

        # Clear chat button
        if st.session_state.messages:
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()


if __name__ == "__main__":
    main()
