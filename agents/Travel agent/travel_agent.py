from textwrap import dedent
from agno.agent import Agent
import streamlit as st
import re
from agno.models.openai import OpenAIChat
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import requests
import json
import time
import os
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# #region debug logging
LOG_PATH = "/Users/srilaxmich/Desktop/Generative-AI-Projects/.cursor/debug.log"
# Function: debug_log
# Description: Writes structured debug information to a local log file (`debug.log`). 
#              It captures timestamps, execution location, messages, and associated data payloads in JSON format.
# Parameters:
#   - location (str): Identifier for where the log is triggered (e.g., "travel_agent.py:duckduckgo_search").
#   - message (str): A human-readable description of the event.
#   - data (dict, optional): Additional context or data payload to log. Defaults to None.
#   - hypothesis_id (str, optional): Identifier for hypothesis tracking. Defaults to None.
#   - session_id (str, optional): Identifier for the user session. Defaults to "debug-session".
#   - run_id (str, optional): Identifier for the specific execution run. Defaults to "run1".
def debug_log(location, message, data=None, hypothesis_id=None, session_id="debug-session", run_id="run1"):
    try:
        log_entry = {
            "id": f"log_{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),
            "location": location,
            "message": message,
            "data": data or {},
            "sessionId": session_id,
            "runId": run_id,
            "hypothesisId": hypothesis_id
        }
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass
# #endregion

# Function: duckduckgo_search
# Description: Performs a web search using the `duckduckgo_search` library. Enriches top results by fetching 
#              page content where possible.
# Parameters:
#   - query (str): The search query string.
#   - max_results (int, optional): Maximum number of search results to retrieve. Defaults to 6.
#   - per_site_timeout (float, optional): Timeout in seconds for fetching individual webpages. Defaults to 8.0.
# Returns:
#   - list[dict]: A list of dictionaries containing title, url, and snippet.
def duckduckgo_search(query: str, max_results: int = 6, per_site_timeout: float = 8.0):
    """Lightweight DuckDuckGo search with optional snippet enrichment."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title"),
                    "url": r.get("href"),
                    "snippet": r.get("body"),
                })
    except Exception as e:
        debug_log("travel_agent.py:duckduckgo_search", "ddg error", {"error": str(e)}, "A")
        return [{"title": "Search error", "url": None, "snippet": str(e)}]

    enriched = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for r in results[:3]:
        url = r.get("url")
        snippet = r.get("snippet") or ""
        if not url:
            enriched.append(r)
            continue
        try:
            resp = requests.get(url, timeout=per_site_timeout, headers=headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                text = " ".join(soup.get_text(" ", strip=True).split()[:120])
                snippet = snippet or text[:400]
        except Exception:
            pass
        enriched.append({**r, "snippet": snippet})
    enriched += results[3:]
    return enriched


# Function: build_research_summary
# Description: Orchestrates the research phase by generating specific search queries based on user inputs 
#              and compiling results.
# Parameters:
#   - destination (str): The target travel location.
#   - num_days (int): Duration of the trip.
#   - travel_style (str): User's preferred style.
#   - budget_range (str): Financial constraint description.
#   - interests (list): List of user interests.
# Returns:
#   - str: A formatted string of research results or 'No results found.'.
def build_research_summary(destination: str, num_days: int, travel_style: str, budget_range: str, interests):
    """Generate a concise research summary using DuckDuckGo (no API key)."""
    queries = [
        f"{destination} {travel_style} travel {num_days} days {budget_range}",
        f"{destination} top things to do {budget_range}",
    ]
    if interests:
        queries.append(f"{destination} {', '.join(interests)} best spots")

    summaries = []
    for q in queries[:2]:
        hits = duckduckgo_search(q, max_results=6)
        for h in hits[:6]:
            title = h.get("title") or "Result"
            url = h.get("url") or ""
            snippet = h.get("snippet") or ""
            summaries.append(f"- {title} — {snippet} ({url})")
    return "\n".join(summaries) if summaries else "No results found."

class TimeoutException(Exception):
    pass

# Function: _timeout_handler
# Description: A signal handler function intended to raise a TimeoutException.
# Parameters:
#   - signum: The signal number.
#   - frame: The current stack frame.
def _timeout_handler(signum, frame):
    raise TimeoutException("Operation timed out")

# Function: run_agent_with_timeout
# Description: Executes an AI agent's `run` method strictly within a specified time limit using a ThreadPoolExecutor.
# Parameters:
#   - agent (Agent): The agent instance to execute.
#   - prompt (str): The input prompt for the agent.
#   - timeout_seconds (int, optional): Maximum allowed execution time. Defaults to 120.
#   - agent_name (str, optional): Name used for logging. Defaults to "agent".
# Returns:
#   - Any: The result object from agent.run().
# Raises:
#   - TimeoutError: If execution time exceeds timeout_seconds.
def run_agent_with_timeout(agent, prompt, timeout_seconds=120, agent_name="agent"):
    """
    Run an agent with timeout protection to prevent hanging.
    Uses ThreadPoolExecutor with timeout, and falls back to direct call with shorter timeout.
    
    Args:
        agent: The agent instance to run
        prompt: The prompt to pass to the agent
        timeout_seconds: Maximum time to wait (default 2 minutes for faster feedback)
        agent_name: Name of agent for error messages
    
    Returns:
        The agent run result
    
    Raises:
        TimeoutError: If the agent call exceeds timeout_seconds
        Exception: Any other exception from the agent
    """
    # #region agent log
    debug_log("travel_agent.py:run_agent_with_timeout", f"Starting {agent_name} with timeout", {"timeout_seconds": timeout_seconds}, "A")
    start_time = time.time()
    # #endregion
    
    def _run():
        # #region agent log
        debug_log("travel_agent.py:_run", f"Inside _run for {agent_name}", {}, "A")
        run_start = time.time()
        # #endregion
        try:
            result = agent.run(prompt, stream=False)
            # #region agent log
            run_elapsed = time.time() - run_start
            debug_log("travel_agent.py:_run", f"{agent_name} _run completed", {"elapsed_seconds": run_elapsed}, "A")
            # #endregion
            return result
        except Exception as e:
            # #region agent log
            run_elapsed = time.time() - run_start
            debug_log("travel_agent.py:_run", f"{agent_name} _run exception", {"error": str(e), "error_type": type(e).__name__, "elapsed_seconds": run_elapsed}, "A")
            # #endregion
            raise
    
    try:
        # #region agent log
        debug_log("travel_agent.py:run_agent_with_timeout", f"Creating ThreadPoolExecutor for {agent_name}", {}, "A")
        # #endregion
        with ThreadPoolExecutor(max_workers=1) as executor:
            # #region agent log
            debug_log("travel_agent.py:run_agent_with_timeout", f"Submitting {agent_name} task to executor", {}, "A")
            submit_start = time.time()
            # #endregion
            future = executor.submit(_run)
            # #region agent log
            submit_elapsed = time.time() - submit_start
            debug_log("travel_agent.py:run_agent_with_timeout", f"Task submitted, waiting for {agent_name} result", {"submit_elapsed": submit_elapsed, "timeout_seconds": timeout_seconds}, "A")
            # #endregion

            last_heartbeat = time.time()
            while True:
                if future.done():
                    result = future.result()
                    # #region agent log
                    total_elapsed = time.time() - start_time
                    debug_log("travel_agent.py:run_agent_with_timeout", f"{agent_name} completed successfully", {"total_elapsed_seconds": total_elapsed}, "A")
                    # #endregion
                    return result

                elapsed = time.time() - start_time
                if elapsed >= timeout_seconds:
                    # #region agent log
                    debug_log("travel_agent.py:run_agent_with_timeout", f"{agent_name} timeout reached", {"timeout_seconds": timeout_seconds, "actual_elapsed": elapsed}, "A")
                    # #endregion
                    raise TimeoutError(f"{agent_name} execution exceeded {timeout_seconds} seconds. This usually means:\n- API keys may be invalid or expired\n- Network connection issues\n- API service is slow or unavailable\n\nPlease check your API keys and try again.")

                if time.time() - last_heartbeat >= 15:
                    # #region agent log
                    debug_log("travel_agent.py:run_agent_with_timeout", f"{agent_name} still running", {"elapsed_seconds": elapsed}, "A")
                    # #endregion
                    last_heartbeat = time.time()
                time.sleep(2)
    except FutureTimeoutError as e:
        # #region agent log
        total_elapsed = time.time() - start_time
        debug_log("travel_agent.py:run_agent_with_timeout", f"{agent_name} ThreadPoolExecutor timeout", {"timeout_seconds": timeout_seconds, "actual_elapsed": total_elapsed, "error": str(e)}, "A")
        # #endregion
        raise TimeoutError(f"{agent_name} execution exceeded {timeout_seconds} seconds. This usually means:\n- API keys may be invalid or expired\n- Network connection issues\n- API service is slow or unavailable\n\nPlease check your API keys and try again.")
    except Exception as e:
        # #region agent log
        total_elapsed = time.time() - start_time
        debug_log("travel_agent.py:run_agent_with_timeout", f"{agent_name} error", {"error": str(e), "error_type": type(e).__name__, "elapsed_seconds": total_elapsed}, "A")
        # #endregion
        raise

# Function: truncate_content
# Description: Shortens text content to a safe length to prevent exceeding token limits.
# Parameters:
#   - content (str): The text string to truncate.
#   - max_length (int, optional): The character limit. Defaults to 2500.
# Returns:
#   - str: The truncated string.
def truncate_content(content: str, max_length: int = 2500) -> str:
    """Truncate content to avoid token limit issues"""
    if not content or len(content) <= max_length:
        return content
    return content[:max_length] + "\n\n[Content truncated due to length...]"


# Function: get_weather_info
# Description: Fetches weather forecasts for a specific destination and date range using the Open-Meteo API.
#              Includes geocoding and mapping WMO codes to descriptions.
# Parameters:
#   - destination (str): Name of the place (used for geocoding).
#   - start_date (datetime): The starting date of the trip.
#   - num_days (int): Duration of the trip.
# Returns:
#   - list[dict] | None: List of daily weather details or None if failed.
def get_weather_info(destination: str, start_date: datetime, num_days: int):
    """Get weather forecast for destination using Open-Meteo (free, no API key required)"""
    # #region agent log
    debug_log("travel_agent.py:19", "get_weather_info called", {"destination": destination, "num_days": num_days}, "B")
    # #endregion
    try:
        # First, get coordinates for the destination using geocoding
        # #region agent log
        debug_log("travel_agent.py:25", "Before geocoding API call", {}, "B")
        # #endregion
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        geocode_params = {
            "name": destination,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        geocode_response = requests.get(geocode_url, params=geocode_params, timeout=10)
        # #region agent log
        debug_log("travel_agent.py:35", "After geocoding API call", {"status_code": geocode_response.status_code}, "B")
        # #endregion
        if geocode_response.status_code != 200:
            # #region agent log
            debug_log("travel_agent.py:37", "Geocoding failed", {"status_code": geocode_response.status_code}, "B")
            # #endregion
            return None
        
        geocode_data = geocode_response.json()
        if not geocode_data.get("results"):
            # #region agent log
            debug_log("travel_agent.py:42", "No geocoding results", {}, "B")
            # #endregion
            return None
        
        location = geocode_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        
        # Get weather forecast
        # #region agent log
        debug_log("travel_agent.py:50", "Before weather API call", {"lat": latitude, "lon": longitude}, "B")
        # #endregion
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
        # #region agent log
        debug_log("travel_agent.py:58", "After weather API call", {"status_code": weather_response.status_code}, "B")
        # #endregion
        if weather_response.status_code != 200:
            # #region agent log
            debug_log("travel_agent.py:60", "Weather API failed", {"status_code": weather_response.status_code}, "B")
            # #endregion
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
        
        # #region agent log
        debug_log("travel_agent.py:97", "get_weather_info completed", {"num_days": len(weather_info)}, "B")
        # #endregion
        return weather_info
    except Exception as e:
        # #region agent log
        debug_log("travel_agent.py:100", "get_weather_info exception", {"error": str(e)}, "B")
        # #endregion
        st.warning(f"Weather API error: {str(e)}")
        return None


# Function: generate_ics_content
# Description: Parses the generated plain-text itinerary to create a downloadable iCalendar (.ics) file.
# Parameters:
#   - plan_text (str): The full text of the generated itinerary.
#   - start_date (datetime, optional): The start date of the trip. Defaults to datetime.today().
# Returns:
#   - bytes: The binary content of the .ics file.
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

if openai_api_key:
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
            "Use the provided DuckDuckGo research summary plus your knowledge.",
            "Organize results by: Attractions, Restaurants, Accommodations, Activities, Tips.",
            "Include approximate costs when mentioned.",
            "Prioritize recent and highly-rated options.",
            "Keep your response concise - summarize key information, don't include full article text.",
            "Focus on top 3-5 results per category to avoid overwhelming responses.",
        ],
        tools=[],
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
            from itineraries and suggest where to book (official sites or major platforms).
        """),
        instructions=[
            "Extract 3-5 key activities and attractions mentioned in the itinerary.",
            "Suggest likely booking platforms or official sites; include plausible URLs if known, otherwise name the platform.",
            "Organize results by: Attractions, Restaurants, Accommodations, Activities, Tips.",
            "Include approximate costs when mentioned.",
            "Prioritize recent and highly-rated options.",
            "Keep your response concise - summarize key information, don't include full article text.",
            "Focus on top 3-5 results per category to avoid overwhelming responses.",
        ],
        tools=[],
    )
    
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
            "Suggest optimal routes and transportation modes (walking, public transit, taxi, rental car).",
            "Estimate travel times between activities.",
            "Recommend efficient day plans to minimize travel time.",
            "Provide practical transportation tips.",
            "Format logistics info clearly with routes and times.",
        ],
        tools=[],
    )

    # Main Input Section
    st.header("🎯 Plan Your Trip")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        destination = st.text_input("📍 Where do you want to go?", placeholder="e.g., Paris, France")
    with col2:
        num_days = st.number_input("📅 Number of Days", min_value=1, max_value=30, value=7)

    if st.button("🚀 Generate Complete Itinerary", type="primary", use_container_width=True):
        # #region agent log
        debug_log("travel_agent.py:292", "Button clicked", {"destination": destination, "num_days": num_days}, "A")
        # #endregion
        if not destination:
            st.error("Please enter a destination!")
        else:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Research (15%)
                # #region agent log
                debug_log("travel_agent.py:303", "Starting Step 1: Research", {}, "A")
                # #endregion
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
                # #region agent log
                debug_log("travel_agent.py:314", "Before duckduckgo research", {"prompt_length": len(research_prompt)}, "A")
                start_time = time.time()
                # #endregion
                with st.spinner("🔍 Searching for travel information... This may take ~30 seconds."):
                    research_text = build_research_summary(destination, num_days, travel_style, budget_range, interests)
                # #region agent log
                elapsed = time.time() - start_time
                debug_log("travel_agent.py:315", "After duckduckgo research", {"elapsed_seconds": elapsed, "has_content": bool(research_text)}, "A")
                # #endregion
                
                # Step 2: Weather Analysis (30%)
                # #region agent log
                debug_log("travel_agent.py:320", "Starting Step 2: Weather Analysis", {"use_weather": use_weather}, "B")
                # #endregion
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
                        # #region agent log
                        debug_log("travel_agent.py:331", "Before weather_agent.run()", {}, "B")
                        start_time = time.time()
                        # #endregion
                        weather_analysis = run_agent_with_timeout(weather_agent, weather_prompt, timeout_seconds=120, agent_name="WeatherAgent")
                        # #region agent log
                        elapsed = time.time() - start_time
                        debug_log("travel_agent.py:332", "After weather_agent.run()", {"elapsed_seconds": elapsed}, "B")
                        # #endregion
                
                # Step 3: Logistics Planning (45%)
                # #region agent log
                debug_log("travel_agent.py:340", "Starting Step 3: Logistics Planning", {}, "C")
                # #endregion
                status_text.text("🗺️ Planning routes and transportation...")
                progress_bar.progress(45)
                logistics_research = truncate_content(research_text, max_length=2000)
                logistics_prompt = f"""
                Destination: {destination}
                Duration: {num_days} days
                
                Research Summary:
                {logistics_research}
                
                Focus on planning transportation and optimal routes between activities mentioned above.
                Keep your response concise and practical.
                """
                # #region agent log
                debug_log("travel_agent.py:353", "Before logistics_agent.run()", {"prompt_length": len(logistics_prompt)}, "C")
                start_time = time.time()
                # #endregion
                logistics_results = run_agent_with_timeout(logistics_agent, logistics_prompt, timeout_seconds=120, agent_name="LogisticsAgent")
                # #region agent log
                elapsed = time.time() - start_time
                debug_log("travel_agent.py:354", "After logistics_agent.run()", {"elapsed_seconds": elapsed}, "C")
                # #endregion
                
                # Step 4: Create Itinerary (60%)
                # #region agent log
                debug_log("travel_agent.py:360", "Starting Step 4: Create Itinerary", {}, "D")
                # #endregion
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
                research_content = truncate_content(research_text, max_length=3000)
                
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
                # #region agent log
                debug_log("travel_agent.py:404", "Before planner.run()", {"prompt_length": len(planning_prompt)}, "D")
                start_time = time.time()
                # #endregion
                response = run_agent_with_timeout(planner, planning_prompt, timeout_seconds=120, agent_name="Planner")
                # #region agent log
                elapsed = time.time() - start_time
                debug_log("travel_agent.py:405", "After planner.run()", {"elapsed_seconds": elapsed}, "D")
                # #endregion
                progress_bar.progress(75)
                
                # Step 5: Find Activity Booking Links (90%)
                # #region agent log
                debug_log("travel_agent.py:410", "Starting Step 5: Activity Booking Links", {"use_activities": use_activities}, "E")
                # #endregion
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
                    # #region agent log
                    debug_log("travel_agent.py:433", "Before activities_agent.run()", {"prompt_length": len(activities_prompt)}, "E")
                    start_time = time.time()
                    # #endregion
                    activities_info = run_agent_with_timeout(activities_agent, activities_prompt, timeout_seconds=120, agent_name="ActivitiesAgent")
                    # #region agent log
                    elapsed = time.time() - start_time
                    debug_log("travel_agent.py:434", "After activities_agent.run()", {"elapsed_seconds": elapsed}, "E")
                    # #endregion
                
                progress_bar.progress(100)
                status_text.text("✅ Itinerary complete!")
                
                # #region agent log
                debug_log("travel_agent.py:440", "All steps completed successfully", {}, "A")
                # #endregion
                
                # Store results
                st.session_state.itinerary = response.content
                st.session_state.weather_info = weather_analysis.content if weather_analysis else None
                st.session_state.activities_info = activities_info.content if activities_info else None
                st.session_state.start_date = start_date
                st.session_state.destination = destination
                
                # Display Results
                st.success("🎉 Your itinerary is ready!")
                
            except TimeoutError as e:
                # #region agent log
                debug_log("travel_agent.py:451", "TimeoutError caught", {"error": str(e)}, "A")
                # #endregion
                st.error(f"⏱️ {str(e)}")
                st.warning("💡 **Tips to resolve:**\n- Check your internet connection\n- Verify your API keys are correct and have available credits\n- Try again with a shorter trip duration\n- Disable optional features (weather/activities) to reduce processing time")
            except Exception as e:
                # #region agent log
                debug_log("travel_agent.py:456", "Exception caught", {"error": str(e), "error_type": type(e).__name__}, "A")
                # #endregion
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
    - **Search**: Uses DuckDuckGo (no API key needed)
    - **Weather**: ✅ No API key needed! Using free [Open-Meteo API](https://open-meteo.com)
    """)
