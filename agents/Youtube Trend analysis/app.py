import streamlit as st
import os
import tempfile
import gc
import time
import yaml

from tqdm import tqdm
from youtube_api_scraper import fetch_channel_videos
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI

docs_tool = FileReadTool()

@st.cache_resource
def load_llm():
    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
    return llm

# ===========================
#   Define Agents & Tasks
# ===========================
def create_agents_and_tasks():
    """Creates a Crew for analysis of the channel scrapped output"""

    with open("config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    analysis_agent = Agent(
        role=config["agents"][0]["role"],
        goal=config["agents"][0]["goal"],
        backstory=config["agents"][0]["backstory"],
        verbose=True,
        tools=[docs_tool],
        llm=load_llm()
    )

    response_synthesizer_agent = Agent(
        role=config["agents"][1]["role"],
        goal=config["agents"][1]["goal"],
        backstory=config["agents"][1]["backstory"],
        verbose=True,
        llm=load_llm()
    )

    analysis_task = Task(
        description=config["tasks"][0]["description"],
        expected_output=config["tasks"][0]["expected_output"],
        agent=analysis_agent
    )

    response_task = Task(
        description=config["tasks"][1]["description"],
        expected_output=config["tasks"][1]["expected_output"],
        agent=response_synthesizer_agent
    )

    crew = Crew(
        agents=[analysis_agent, response_synthesizer_agent],
        tasks=[analysis_task, response_task],
        process=Process.sequential,
        verbose=True
    )
    return crew

# ===========================
#   Streamlit Setup
# ===========================

st.markdown("""
    # YouTube Trend Analysis powered by CrewAI & YouTube Data API
""")


if "messages" not in st.session_state:
    st.session_state.messages = []  # Chat history

if "response" not in st.session_state:
    st.session_state.response = None

if "crew" not in st.session_state:
    st.session_state.crew = None      # Store the Crew object

def reset_chat():
    st.session_state.messages = []
    gc.collect()

def start_analysis():
    # Create a status container
    status_container = st.empty()
    
    # Check if API key is set
    if not os.getenv("YOUTUBE_API_KEY"):
        status_container.error("YOUTUBE_API_KEY not found in environment variables. Please add it to your .env file.")
        return
    # Filter out empty channel URLs
    valid_channels = [ch for ch in st.session_state.youtube_channels if ch and ch.strip()]
    
    if not valid_channels:
        status_container.error("Please add at least one YouTube channel URL.")
        return
    
    with st.spinner('Scraping videos... This may take a moment.'):
        status_container.info("Extracting videos from the channels using YouTube Data API...")
        status_container.info("⏳ Processing up to 3 videos per channel...")
        status_container.info("   Getting transcripts for first 2 videos only (for speed)")
        status_container.info("   Estimated time: ~5-15 seconds per channel")
        
        try:
            # Scrape videos from all channels (3 videos per channel, transcripts optional)
            get_transcripts = not st.session_state.get("quick_mode", False)
            if get_transcripts:
                status_container.info("📝 Transcript mode: Will retrieve transcripts (first 2 videos)")
            else:
                status_container.info("⚡ Quick mode: Skipping transcripts for faster processing")

            channel_scrapped_output = []
            for ch in valid_channels:
                try:
                    vids = fetch_channel_videos(
                        ch,
                        num_videos=3,
                        start_date=st.session_state.start_date,
                        end_date=st.session_state.end_date,
                        get_transcripts=get_transcripts,
                        transcript_timeout=8.0,
                    )
                    channel_scrapped_output.extend(vids)
                except Exception as e:
                    status_container.warning(f"Failed to fetch from {ch}: {e}")
            
            if not channel_scrapped_output:
                status_container.error("No videos found. Please check your channel URLs and try again.")
                return
            
            status_container.success(f"Scraping completed! Found {len(channel_scrapped_output)} videos.")

            # Show a list of YouTube videos here in a scrollable container
            st.markdown("## YouTube Videos Extracted")
            # Create a container for the carousel
            carousel_container = st.container()

            # Calculate number of videos per row (adjust as needed)
            videos_per_row = 3

            with carousel_container:
                # Calculate number of rows needed
                num_videos = len(channel_scrapped_output)
                num_rows = (num_videos + videos_per_row - 1) // videos_per_row
                
                for row in range(num_rows):
                    # Create columns for each row
                    cols = st.columns(videos_per_row)
                    
                    # Fill each column with a video
                    for col_idx in range(videos_per_row):
                        video_idx = row * videos_per_row + col_idx
                        
                        # Check if we still have videos to display
                        if video_idx < num_videos:
                            with cols[col_idx]:
                                st.video(channel_scrapped_output[video_idx]['url'])

            status_container.info("Processing transcripts...")
            st.session_state.all_files = []
            
            # Create transcripts directory if it doesn't exist
            os.makedirs("transcripts", exist_ok=True)
            
            # Process transcripts (or fallback metadata) per video
            videos_with_transcripts = 0
            for i in tqdm(range(len(channel_scrapped_output))):
                youtube_video_id = channel_scrapped_output[i]['shortcode']
                file = "transcripts/" + youtube_video_id + ".txt"

                with open(file, "w") as f:
                    transcript_entries = channel_scrapped_output[i].get('formatted_transcript', []) or []
                    if transcript_entries:
                        videos_with_transcripts += 1
                        for entry in transcript_entries:
                            text = entry.get('text', '')
                            start_time = entry.get('start_time', 0.0)
                            end_time = entry.get('end_time', 0.0)
                            f.write(f"({start_time:.2f}-{end_time:.2f}): {text}\n")
                    else:
                        # Fallback content so the agent has something to read
                        f.write(f"Video Title: {channel_scrapped_output[i].get('title', 'N/A')}\n")
                        f.write(f"Description: {channel_scrapped_output[i].get('description', 'N/A')}\n")
                        f.write(f"URL: {channel_scrapped_output[i].get('url', 'N/A')}\n")

                # Always add the file so analysis can run even without transcripts
                st.session_state.all_files.append(file)
            
            # Report transcript coverage
            if videos_with_transcripts > 0:
                status_container.info(f"✅ Retrieved transcripts for {videos_with_transcripts} out of {len(channel_scrapped_output)} videos")
            else:
                status_container.warning("⚠️ No transcripts were retrieved; analysis will use video placeholders.")

            st.session_state.channel_scrapped_output = channel_scrapped_output
            status_container.success("Scraping complete! We shall now analyze the videos and report trends...")

        except Exception as e:
            status_container.error(f"Scraping failed: {str(e)}")
            return

    # Proceed with analysis if we have videos
    if channel_scrapped_output and st.session_state.all_files:
        status_container = st.empty()
        with st.spinner('The agent is analyzing the videos... This may take a moment.'):
            # create crew
            st.session_state.crew = create_agents_and_tasks()
            st.session_state.response = st.session_state.crew.kickoff(inputs={"file_paths": ", ".join(st.session_state.all_files)})
                    


# ===========================
#   Sidebar
# ===========================
with st.sidebar:
    st.header("YouTube Channels")
    
    # Initialize the channels list in session state if it doesn't exist
    if "youtube_channels" not in st.session_state:
        st.session_state.youtube_channels = [""]  # Start with one empty field
    
    # Function to add new channel field
    def add_channel_field():
        st.session_state.youtube_channels.append("")
    
    # Create input fields for each channel
    for i, channel in enumerate(st.session_state.youtube_channels):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.session_state.youtube_channels[i] = st.text_input(
                "Channel URL",
                value=channel,
                key=f"channel_{i}",
                label_visibility="collapsed"
            )
        # Show remove button for all except the first field
        with col2:
            if i > 0:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.youtube_channels.pop(i)
                    st.rerun()
    
    # Add channel button
    st.button("Add Channel ➕", on_click=add_channel_field)
    
    st.divider()
    
    st.subheader("Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
        st.session_state.start_date = start_date
        # store date as string
        st.session_state.start_date = start_date.strftime("%Y-%m-%d")
    with col2:
        end_date = st.date_input("End Date")
        st.session_state.end_date = end_date
        st.session_state.end_date = end_date.strftime("%Y-%m-%d")

    st.divider()
    
    # Quick mode option (skip transcripts for faster testing)
    quick_mode = st.checkbox("⚡ Quick Mode (Skip Transcripts)", value=False, 
                             help="Skip transcript retrieval for faster processing. Analysis will use video titles/descriptions only.")
    
    if "quick_mode" not in st.session_state:
        st.session_state.quick_mode = False
    st.session_state.quick_mode = quick_mode
    
    st.button("Start Analysis 🚀", type="primary", on_click=start_analysis)
    # st.button("Clear Chat", on_click=reset_chat)

# ===========================
#   Main Chat Interface
# ===========================

# Main content area
if st.session_state.response:
    with st.spinner('Generating content... This may take a moment.'):
        try:
            result = st.session_state.response
            st.markdown("### Generated Analysis")
            st.markdown(result)

            download_payload = getattr(result, "raw", None) or str(result)
            st.download_button(
                label="Download Content",
                data=download_payload,
                file_name=f"youtube_trend_analysis.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with CrewAI, YouTube Data API v3, and Streamlit")