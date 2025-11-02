from textwrap import dedent
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
import streamlit as st
import re
from agno.models.openai import OpenAIChat
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import requests


def truncate_content(content: str, max_length: int = 2500) -> str:
    """Truncate content to avoid token limit issues"""
    if not content or len(content) <= max_length:
        return content
    return content[:max_length] + "\n\n[Content truncated due to length...]"


def get_weather_info(destination: str, start_date: datetime, num_days: int):
    """Get weather forecast for destination using Open-Meteo (free, no API key required)"""
    try:
        # First, get coordinates for the destination using geocoding
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        geocode_params = {
            "name": destination,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        geocode_response = requests.get(geocode_url, params=geocode_params, timeout=10)
        if geocode_response.status_code != 200:
            return None
        
        geocode_data = geocode_response.json()
        if not geocode_data.get("results"):
            return None
        
        location = geocode_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        
        # Get weather forecast
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability",
            "timezone": "auto",
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": (start_date + timedelta(days=num_days - 1)).strftime('%Y-%m-%d')
        }
        
        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        if weather_response.status_code != 200:
            return None
        
        weather_data = weather_response.json()
        daily_data = weather_data.get("daily", {})
        
        # Map weather codes to descriptions
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
            55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
            77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
            82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        
        weather_info = []
        dates = daily_data.get("time", [])
        temps_max = daily_data.get("temperature_2m_max", [])
        temps_min = daily_data.get("temperature_2m_min", [])
        codes = daily_data.get("weathercode", [])
        precipitation = daily_data.get("precipitation_probability", [])
        
        for i in range(min(len(dates), num_days)):
            code = codes[i] if i < len(codes) else 0
            status = weather_codes.get(code, "Unknown")
            
            weather_info.append({
                'date': dates[i],
                'temp_max': temps_max[i] if i < len(temps_max) else None,
                'temp_min': temps_min[i] if i < len(temps_min) else None,
                'status': status,
                'precipitation_prob': precipitation[i] if i < len(precipitation) else None,
                'location': f"{destination} ({latitude:.2f}°, {longitude:.2f}°)"
            })
        
        return weather_info
    except Exception as e:
        st.warning(f"Weather API error: {str(e)}")
        return None


def generate_ics_content(plan_text: str, start_date: datetime = None) -> bytes:
    """Generate an ICS calendar file from a travel itinerary text."""
    cal = Calendar()
    cal.add('prodid', '-//AI Travel Planner//github.com//')
    cal.add('version', '2.0')

    if start_date is None:
        start_date = datetime.today()
    
    # Convert to date if it's a datetime object
    if isinstance(start_date, datetime):
        start_date_obj = start_date
        start_date = start_date.date()
    else:
        start_date_obj = datetime.combine(start_date, datetime.min.time())

    day_pattern = re.compile(r'Day (\d+)[:\s]+(.*?)(?=Day \d+|$)', re.DOTALL)
    days = day_pattern.findall(plan_text)

    if not days:
        event = Event()
        event.add('summary', "Travel Itinerary")
        event.add('description', plan_text)
        event.add('dtstart', start_date)
        event.add('dtend', start_date)
        event.add("dtstamp", datetime.now())
        cal.add_component(event)
    else:
        for day_num, day_content in days:
            day_num = int(day_num)
            current_date = start_date + timedelta(days=day_num - 1)
            
            event = Event()
            event.add('summary', f"Day {day_num} Itinerary")
            event.add('description', day_content.strip())
            event.add('dtstart', current_date)
            event.add('dtend', current_date)
            event.add("dtstamp", datetime.now())
            cal.add_component(event)

    return cal.to_ical()


# Streamlit App
st.title("🌍 AI Travel Planner Plus")
st.caption("Plan your next adventure with AI-powered weather forecasts, activity booking links, and personalized itineraries")

# Initialize session state
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None
if 'weather_info' not in st.session_state:
    st.session_state.weather_info = None
if 'activities_info' not in st.session_state:
    st.session_state.activities_info = None
if 'destination' not in st.session_state:
    st.session_state.destination = None

# Sidebar for API Keys and Preferences
st.sidebar.header("🔑 API Configuration")

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Required for AI agents")
serp_api_key = st.sidebar.text_input("SerpAPI Key", type="password", help="Required for web search")
use_weather = st.sidebar.checkbox("Enable Weather Forecast", value=True, 
                                   help="Free weather data using Open-Meteo API (no key required)")
use_activities = st.sidebar.checkbox("Enable Activity Booking Links", value=True)

# Travel Preferences
st.sidebar.header("✈️ Travel Preferences")
travel_style = st.sidebar.selectbox("Travel Style", 
    ["Adventure", "Relaxation", "Culture", "Family-Friendly", "Business", "Luxury"])
budget_range = st.sidebar.selectbox("Budget Range", 
    ["Budget-Friendly", "Mid-Range", "Luxury"])
start_date = st.sidebar.date_input("Travel Start Date", value=datetime.today())
interests = st.sidebar.multiselect("Interests",
    ["Food & Dining", "History & Culture", "Nature & Outdoors", 
     "Nightlife", "Shopping", "Art & Museums", "Sports"])

if openai_api_key and serp_api_key:
    # Existing Agents
    researcher = Agent(
        name="Researcher",
        role="Searches for travel destinations, activities, and accommodations",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        description=dedent("""\
            You are a world-class travel researcher. Generate targeted search terms 
            and find relevant travel information, activities, and accommodations.
        """),
        instructions=[
            "Generate 4-5 specific search terms combining destination, duration, style, and budget.",
            "Use `search_google` for each term and analyze results.",
            "Organize results by: Attractions, Restaurants, Accommodations, Activities, Tips.",
            "Include approximate costs when mentioned.",
            "Prioritize recent and highly-rated options.",
            "Keep your response concise - summarize key information, don't include full article text.",
            "Focus on top 3-5 results per category to avoid overwhelming responses.",
        ],
        tools=[SerpApiTools(api_key=serp_api_key)],
    )
    
    planner = Agent(
        name="Planner",
        role="Generates detailed day-by-day itineraries",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        description=dedent("""\
            You are a senior travel planner. Create detailed itineraries with time slots, 
            costs, and practical information.
        """),
        instructions=[
            "Create day-by-day itinerary with time slots (Morning, Afternoon, Evening).",
            "Include estimated costs for each activity when available.",
            "Suggest realistic travel times between locations.",
            "Balance activities - don't overpack days.",
            "Include meal recommendations with cuisine types and price ranges.",
            "Add practical tips: best times to visit, booking requirements.",
            "Format with clear Day X headers and time-based sections.",
            "List specific activity names clearly for booking purposes.",
            "Never make up facts - only use research results.",
        ],
    )
    
    # NEW AGENT 1: Weather Agent
    weather_agent = Agent(
        name="WeatherAnalyst",
        role="Provides weather forecasts and packing suggestions",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        description=dedent("""\
            You are a weather and travel preparation expert. Analyze weather forecasts 
            and provide practical packing and activity recommendations.
        """),
        instructions=[
            "Analyze weather data provided for the destination and dates.",
            "Provide daily weather summaries with temperature and conditions.",
            "Suggest appropriate clothing and packing items.",
            "Recommend indoor alternatives if weather is unfavorable.",
            "Give practical tips based on weather patterns.",
            "Format weather info clearly by day.",
        ],
    ) if use_weather else None
    
    # NEW AGENT 2: Activities Agent (FOCUSED ON BOOKING LINKS)
    activities_agent = Agent(
        name="ActivitiesFinder",
        role="Identifies activities and finds booking links",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        description=dedent("""\
            You are an activities and booking specialist. Identify specific activities 
            from itineraries and find official booking links from platforms like Viator, 
            GetYourGuide, TripAdvisor, Klook, or official attraction websites.
        """),
        instructions=[
            "Extract all specific activities and attractions mentioned in the itinerary.",
            "For each activity, use `search_google` to find booking platforms and official websites.",
            "Search for terms like: '[Activity Name] [Destination] booking', '[Activity Name] tickets', '[Activity Name] official website'.",
            "Prioritize official booking platforms: Viator, GetYourGuide, TripAdvisor, Klook, official attraction sites.",
            "Extract and format booking URLs clearly.",
            "Include activity name, brief description, estimated price if found, and direct booking link.",
            "Format output as a structured list with clear links.",
            "If no booking link is found, suggest where to find more information.",
            "Organize by day if possible.",
        ],
        tools=[SerpApiTools(api_key=serp_api_key)],
    ) if use_activities else None
    
    # NEW AGENT 3: Logistics Agent
    logistics_agent = Agent(
        name="LogisticsPlanner",
        role="Plans transportation and routes between locations",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        description=dedent("""\
            You are a logistics and transportation expert. Plan optimal routes, 
            suggest transportation modes, and estimate travel times.
        """),
        instructions=[
            "Analyze the itinerary and identify locations to visit.",
            "Use `search_google` to find best transportation options between locations.",
            "Suggest optimal routes and transportation modes (walking, public transit, taxi, rental car).",
            "Estimate travel times between activities.",
            "Recommend efficient day plans to minimize travel time.",
            "Provide practical transportation tips.",
            "Format logistics info clearly with routes and times.",
        ],
        tools=[SerpApiTools(api_key=serp_api_key)],
    )

    # Main Input Section
    st.header("🎯 Plan Your Trip")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        destination = st.text_input("📍 Where do you want to go?", placeholder="e.g., Paris, France")
    with col2:
        num_days = st.number_input("📅 Number of Days", min_value=1, max_value=30, value=7)

    if st.button("🚀 Generate Complete Itinerary", type="primary", use_container_width=True):
        if not destination:
            st.error("Please enter a destination!")
        else:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Research (15%)
                status_text.text("🔍 Researching destination...")
                progress_bar.progress(15)
                
                research_prompt = f"""
                Research {destination} for a {num_days} day {travel_style.lower()} trip.
                Budget: {budget_range}
                Date: {start_date.strftime('%B %d, %Y')}
                Interests: {', '.join(interests) if interests else 'General'}
                
                Find top activities, restaurants, accommodations matching these preferences.
                Keep summaries concise - focus on names, locations, prices, and brief descriptions.
                """
                research_results = researcher.run(research_prompt, stream=False)
                
                # Step 2: Weather Analysis (30%)
                weather_data = None
                weather_analysis = None
                if use_weather:
                    status_text.text("🌤️ Getting weather forecast...")
                    progress_bar.progress(30)
                    weather_data = get_weather_info(destination, start_date, num_days)
                    if weather_data and weather_agent:
                        weather_prompt = f"""
                        Destination: {destination}
                        Travel Dates: {start_date.strftime('%Y-%m-%d')} for {num_days} days
                        Weather Data: {weather_data}
                        
                        Provide weather analysis and packing recommendations.
                        """
                        weather_analysis = weather_agent.run(weather_prompt, stream=False)
                
                # Step 3: Logistics Planning (45%)
                status_text.text("🗺️ Planning routes and transportation...")
                progress_bar.progress(45)
                logistics_research = truncate_content(research_results.content, max_length=2000)
                logistics_prompt = f"""
                Destination: {destination}
                Duration: {num_days} days
                
                Research Summary:
                {logistics_research}
                
                Focus on planning transportation and optimal routes between activities mentioned above.
                Keep your response concise and practical.
                """
                logistics_results = logistics_agent.run(logistics_prompt, stream=False)
                
                # Step 4: Create Itinerary (60%)
                status_text.text("📋 Creating your personalized itinerary...")
                progress_bar.progress(60)
                
                # Build weather and logistics info strings separately to avoid f-string backslash issue
                newline = "\n"
                weather_section = ""
                if weather_analysis:
                    weather_content = truncate_content(weather_analysis.content, max_length=800)
                    weather_section = f"Weather Info:{newline}{weather_content}"
                
                logistics_section = ""
                if logistics_results:
                    logistics_content = truncate_content(logistics_results.content, max_length=800)
                    logistics_section = f"Logistics Info:{newline}{logistics_content}"
                
                # Truncate research results to avoid token limit
                research_content = truncate_content(research_results.content, max_length=3000)
                
                planning_prompt = f"""
                Destination: {destination}
                Duration: {num_days} days
                Travel Style: {travel_style}
                Budget Range: {budget_range}
                Interests: {', '.join(interests) if interests else 'General'}
                Start Date: {start_date.strftime('%B %d, %Y')}
                
                Research Results:
                {research_content}
                
                {weather_section}
                {logistics_section}
                
                Create a detailed day-by-day itinerary with:
                - Specific time slots (Morning: 9-12, Afternoon: 12-5, Evening: 5-9)
                - Activity descriptions
                - Approximate costs when available
                - Travel time considerations
                - Meal recommendations
                - Weather-appropriate activities
                - Practical tips
                
                IMPORTANT: List specific activity/attraction names clearly (e.g., 
                "Eiffel Tower", "Louvre Museum", "Seine River Cruise") so they can 
                be used for booking searches.
                
                Format with "Day X:" headers and time-based sections.
                Keep the itinerary focused and concise.
                """
                
                response = planner.run(planning_prompt, stream=False)
                progress_bar.progress(75)
                
                # Step 5: Find Activity Booking Links (90%)
                activities_info = None
                if use_activities and activities_agent:
                    status_text.text("🎫 Finding activity booking links...")
                    progress_bar.progress(75)
                    
                    # Extract just activity names instead of full itinerary to save tokens
                    # Use a simpler approach - extract activity names from itinerary
                    itinerary_content = truncate_content(response.content, max_length=2000)
                    
                    activities_prompt = f"""
                    Extract specific activity and attraction names from this itinerary excerpt:
                    
                    {itinerary_content}
                    
                    For each unique activity/attraction mentioned, search for booking links.
                    Focus on finding official booking platforms:
                    - Viator
                    - GetYourGuide  
                    - TripAdvisor
                    - Klook
                    - Official websites
                    
                    Provide a concise list with activity name and booking link.
                    Search for 3-5 key activities only to avoid token limits.
                    """
                    activities_info = activities_agent.run(activities_prompt, stream=False)
                
                progress_bar.progress(100)
                status_text.text("✅ Itinerary complete!")
                
                # Store results
                st.session_state.itinerary = response.content
                st.session_state.weather_info = weather_analysis.content if weather_analysis else None
                st.session_state.activities_info = activities_info.content if activities_info else None
                st.session_state.start_date = start_date
                st.session_state.destination = destination
                
                # Display Results
                st.success("🎉 Your itinerary is ready!")
                
            except Exception as e:
                st.error(f"Error generating itinerary: {str(e)}")
                st.exception(e)

    # Display Results Section
    if st.session_state.itinerary:
        st.divider()
        st.header("📋 Your Itinerary")
        st.write(st.session_state.itinerary)
        
        # Display Weather Info
        if st.session_state.weather_info:
            with st.expander("🌤️ Weather Forecast & Packing Tips", expanded=False):
                st.markdown(st.session_state.weather_info)
        
        # Display Activities with Booking Links
        if st.session_state.activities_info:
            with st.expander("🎫 Activity Booking Links", expanded=True):
                # Parse and format booking links nicely
                activities_content = st.session_state.activities_info
                
                # Try to extract URLs and format them as clickable links
                url_pattern = re.compile(r'(https?://[^\s]+)')
                activities_formatted = url_pattern.sub(
                    r'[\1](\1)', 
                    activities_content
                )
                st.markdown(activities_formatted)
        
        # Export Options
        st.divider()
        st.header("💾 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ics_content = generate_ics_content(
                st.session_state.itinerary,
                st.session_state.get('start_date', datetime.today())
            )
            dest_name = st.session_state.destination.replace(' ', '_') if st.session_state.destination else 'travel'
            dest_name = ''.join(c for c in dest_name if c.isalnum() or c in ('_', '-'))  # Sanitize filename
            
            st.download_button(
                label="📅 Calendar (.ics)",
                data=ics_content,
                file_name=f"itinerary_{dest_name}.ics",
                mime="text/calendar",
                use_container_width=True
            )
        
        with col2:
            dest_name = st.session_state.destination.replace(' ', '_') if st.session_state.destination else 'travel'
            dest_name = ''.join(c for c in dest_name if c.isalnum() or c in ('_', '-'))  # Sanitize filename
            
            st.download_button(
                label="📄 Text (.txt)",
                data=st.session_state.itinerary,
                file_name=f"itinerary_{dest_name}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col3:
            dest_name = st.session_state.destination.replace(' ', '_') if st.session_state.destination else 'travel'
            dest_name = ''.join(c for c in dest_name if c.isalnum() or c in ('_', '-'))  # Sanitize filename
            
            # Combined export with weather and activities
            combined_content = f"""
{st.session_state.itinerary}

{'='*60}
WEATHER FORECAST & PACKING TIPS
{'='*60}
{st.session_state.weather_info if st.session_state.weather_info else 'Not available'}

{'='*60}
ACTIVITY BOOKING LINKS
{'='*60}
{st.session_state.activities_info if st.session_state.activities_info else 'Not available'}
"""
            st.download_button(
                label="📦 Complete Guide",
                data=combined_content,
                file_name=f"complete_guide_{dest_name}.txt",
                mime="text/plain",
                use_container_width=True
            )

else:
    st.info("👆 Please enter your API keys in the sidebar to get started.")
    st.markdown("""
    ### 🔑 Getting API Keys:
    - **OpenAI**: Get your key at [platform.openai.com](https://platform.openai.com)
    - **SerpAPI**: Sign up at [serpapi.com](https://serpapi.com) (free tier available)
    - **Weather**: ✅ No API key needed! Using free [Open-Meteo API](https://open-meteo.com)
    """)
