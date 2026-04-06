"""
Streamlit App for Study Planning Multi-Agent System
---------------------------------------------------
A web interface for the CrewAI-based study planning system.
Allows users to input their OpenAI API key and create personalized study plans.
"""

import os

# Disable telemetry that pulls in opentelemetry/chroma to avoid version conflicts
os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")
os.environ.setdefault("CHROMA_TELEMETRY_IMPLEMENTATION", "none")

import streamlit as st
from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI


def create_agents(api_key: str, model: str = "gpt-4o-mini"):
    """Create the three specialized agents with the provided API key."""
    llm = ChatOpenAI(model=model, api_key=api_key)
    
    curriculum_analyst = Agent(
        role="Curriculum Analyst",
        goal=(
            "Analyse the given subject or exam and identify all key topics, "
            "subtopics, and their relative importance and difficulty levels."
        ),
        backstory=(
            "You are an expert academic curriculum designer with 15 years of "
            "experience building syllabi for universities and professional "
            "certification programs. You excel at decomposing complex subjects "
            "into clear, prioritised learning objectives."
        ),
        llm=llm,
        verbose=True,
    )

    study_planner = Agent(
        role="Study Planner",
        goal=(
            "Create a realistic, day-by-day study schedule that fits the "
            "learner's available time and covers all topics identified by the "
            "Curriculum Analyst, with appropriate review sessions built in."
        ),
        backstory=(
            "You are a productivity coach and certified learning strategist. "
            "You specialise in spaced-repetition scheduling, Pomodoro techniques, "
            "and building study plans that prevent burnout while maximising "
            "retention. You always account for rest days and revision cycles."
        ),
        llm=llm,
        verbose=True,
    )

    study_coach = Agent(
        role="Study Coach",
        goal=(
            "Enrich the study plan with actionable learning tips, recommended "
            "resources (books, videos, practice tests), and motivational "
            "strategies tailored to the subject and timeline."
        ),
        backstory=(
            "You are a seasoned academic mentor who has guided thousands of "
            "students through challenging exams and self-study journeys. You "
            "know the best free and paid resources for virtually every subject "
            "and understand how to keep learners motivated over long periods."
        ),
        llm=llm,
        verbose=True,
    )
    
    return curriculum_analyst, study_planner, study_coach


def build_tasks(subject: str, available_hours_per_day: float, days_until_exam: int,
                curriculum_analyst: Agent, study_planner: Agent, study_coach: Agent):
    """Construct the three tasks dynamically based on user inputs."""
    
    analyse_curriculum = Task(
        description=(
            f"Analyse the subject: '{subject}'.\n"
            f"The learner has {days_until_exam} days until their exam/deadline "
            f"and can study {available_hours_per_day} hours per day.\n\n"
            "Your output must include:\n"
            "1. A prioritised list of all major topics and subtopics.\n"
            "2. An estimated difficulty rating (Easy / Medium / Hard) for each topic.\n"
            "3. A suggested time allocation (in hours) for each topic based on "
            "   its importance and difficulty.\n"
            "4. Any prerequisites or recommended study order."
        ),
        expected_output=(
            "A structured breakdown of topics with difficulty ratings, "
            "time estimates, and a recommended study order."
        ),
        agent=curriculum_analyst,
    )

    create_schedule = Task(
        description=(
            f"Using the curriculum breakdown provided, create a day-by-day "
            f"study schedule for {days_until_exam} days, assuming "
            f"{available_hours_per_day} study hours per day.\n\n"
            "Requirements:\n"
            "- Assign specific topics to each day.\n"
            "- Include at least one full review/revision day per week.\n"
            "- Add short daily review slots (15–20 min) for previously covered material.\n"
            "- Mark the final 2–3 days as mock-test / full-revision days.\n"
            "- Format the schedule as a clear table or numbered list."
        ),
        expected_output=(
            "A complete day-by-day study schedule in a clear, readable format "
            "with topic assignments, review sessions, and revision days."
        ),
        agent=study_planner,
        context=[analyse_curriculum],
    )

    add_coaching = Task(
        description=(
            f"Review the study schedule for '{subject}' and enrich it with:\n"
            "1. Top 3–5 recommended resources (books, YouTube channels, "
            "   websites, or apps) for this subject.\n"
            "2. Specific study techniques best suited to this subject "
            "   (e.g., active recall, mind maps, practice problems).\n"
            "3. A short motivational message and tips to avoid burnout.\n"
            "4. A daily routine template (e.g., warm-up → deep work → review → break).\n\n"
            "Combine the schedule and coaching notes into one final, polished "
            "study plan document formatted in Markdown."
        ),
        expected_output=(
            "A complete, polished Markdown study plan document that includes "
            "the day-by-day schedule, recommended resources, study techniques, "
            "a daily routine template, and motivational coaching notes."
        ),
        agent=study_coach,
        context=[analyse_curriculum, create_schedule],
    )

    return [analyse_curriculum, create_schedule, add_coaching]


def run_study_planner(subject: str, hours_per_day: float, days: int, api_key: str, model: str = "gpt-4o-mini") -> str:
    """Assemble the crew and kick off the study planning workflow."""
    curriculum_analyst, study_planner, study_coach = create_agents(api_key, model)
    tasks = build_tasks(subject, hours_per_day, days, curriculum_analyst, study_planner, study_coach)

    crew = Crew(
        agents=[curriculum_analyst, study_planner, study_coach],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


def main():
    st.set_page_config(
        page_title="Study Planning Multi-Agent System",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Study Planning Multi-Agent System")
    st.markdown("Create a comprehensive, personalized study plan using AI agents powered by CrewAI")
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check for API key in environment first
        env_api_key = os.getenv("OPENAI_API_KEY", "")
        
        if env_api_key:
            st.success("✅ API key found in environment")
            api_key = env_api_key
            use_env_key = True
        else:
            use_env_key = False
            api_key_input = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key. It will not be saved.",
                value=st.session_state.get("api_key", "")
            )
            api_key = api_key_input
            if api_key:
                st.session_state.api_key = api_key
        
        st.divider()
        
        model = st.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
            help="Choose the OpenAI model to use. gpt-4o-mini is cost-effective."
        )
        
        st.info("💡 **Tip:** You can also set `OPENAI_API_KEY` in your environment or `.env` file to skip entering it each time.")
    
    # Main form
    st.header("📝 Study Plan Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input(
            "Subject or Exam",
            placeholder="e.g., Python Programming, Machine Learning, AWS Certification",
            help="Enter the subject or exam you want to study for"
        )
        
        hours_per_day = st.number_input(
            "Hours per day",
            min_value=0.5,
            max_value=12.0,
            value=2.5,
            step=0.5,
            help="How many hours can you dedicate to studying each day?"
        )
    
    with col2:
        days_until_exam = st.number_input(
            "Days until exam/deadline",
            min_value=1,
            max_value=365,
            value=30,
            step=1,
            help="How many days do you have until your exam or deadline?"
        )
        
        total_hours = hours_per_day * days_until_exam
        st.metric("Total Study Hours", f"{total_hours:.1f} hours")
    
    st.divider()
    
    # Generate button
    generate_button = st.button("🚀 Generate Study Plan", type="primary", use_container_width=True)
    
    # Validation
    if generate_button:
        if not api_key:
            st.error("❌ Please enter your OpenAI API key in the sidebar.")
            st.stop()
        
        if not subject or not subject.strip():
            st.error("❌ Please enter a subject or exam name.")
            st.stop()
        
        if hours_per_day <= 0:
            st.error("❌ Hours per day must be greater than 0.")
            st.stop()
        
        if days_until_exam <= 0:
            st.error("❌ Days until exam must be greater than 0.")
            st.stop()
        
        # Show summary
        with st.expander("📋 Plan Summary", expanded=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("Subject", subject)
            col2.metric("Hours/Day", f"{hours_per_day:.1f}")
            col3.metric("Days", days_until_exam)
        
        # Run the crew
        with st.spinner("🤖 Your AI agents are working... This may take a few minutes."):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.info("👨‍🏫 Curriculum Analyst is analyzing the subject...")
                progress_bar.progress(20)
                
                result = run_study_planner(subject, hours_per_day, days_until_exam, api_key, model)
                
                progress_bar.progress(100)
                status_text.empty()
                
                # Store result in session state
                st.session_state.last_result = result
                st.session_state.last_subject = subject
                
                st.success("✅ Study plan generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating study plan: {str(e)}")
                st.exception(e)
                st.stop()
    
    # Display results
    if "last_result" in st.session_state:
        st.divider()
        st.header(f"📖 Study Plan: {st.session_state.get('last_subject', 'Your Subject')}")
        
        # Download button
        study_plan_text = f"# Study Plan: {st.session_state.get('last_subject', 'Your Subject')}\n\n{st.session_state.last_result}"
        st.download_button(
            label="📥 Download Study Plan (Markdown)",
            data=study_plan_text,
            file_name=f"study_plan_{st.session_state.get('last_subject', 'subject').replace(' ', '_').lower()}.md",
            mime="text/markdown"
        )
        
        # Display the result
        st.markdown(st.session_state.last_result)


if __name__ == "__main__":
    main()
