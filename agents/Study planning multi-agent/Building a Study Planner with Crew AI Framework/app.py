#!/usr/bin/env python3
"""
Study Planning Multi-Agent System using CrewAI
-----------------------------------------------
This app uses a crew of three specialized AI agents to create a
comprehensive, personalized study plan for any subject or exam.

Agents:
  1. Curriculum Analyst   - Breaks down the subject into key topics
  2. Study Planner        - Creates a time-boxed study schedule
  3. Study Coach          - Adds tips, resources, and motivational advice

Usage:
  python app.py
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI

# ---------------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. "
        "Please add it to a .env file or export it as an environment variable."
    )

# Use GPT-4o-mini by default for cost efficiency; change as needed.
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def build_tasks(subject: str, available_hours_per_day: float, days_until_exam: int):
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


# ---------------------------------------------------------------------------
# Crew
# ---------------------------------------------------------------------------

def run_study_planner(subject: str, hours_per_day: float, days: int) -> str:
    """Assemble the crew and kick off the study planning workflow."""

    tasks = build_tasks(subject, hours_per_day, days)

    crew = Crew(
        agents=[curriculum_analyst, study_planner, study_coach],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("  Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("  Please enter a positive integer.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a whole number.")


def main():
    print("=" * 60)
    print("       Study Planning Multi-Agent System (CrewAI)")
    print("=" * 60)
    print()

    subject = input("Enter the subject or exam you want to study for:\n> ").strip()
    if not subject:
        subject = "General Knowledge"

    hours_per_day = get_positive_float(
        "\nHow many hours can you study per day? (e.g., 2.5)\n> "
    )

    days = get_positive_int(
        "\nHow many days do you have until your exam/deadline?\n> "
    )

    print()
    print("-" * 60)
    print(f"  Subject        : {subject}")
    print(f"  Hours per day  : {hours_per_day}")
    print(f"  Days available : {days}")
    print("-" * 60)
    print("\nLaunching your study planning crew... (this may take a minute)\n")

    result = run_study_planner(subject, hours_per_day, days)

    # Save output to a file for easy reference
    output_file = "study_plan.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Study Plan: {subject}\n\n")
        f.write(result)

    print("\n" + "=" * 60)
    print("  Your study plan is ready!")
    print(f"  Saved to: {output_file}")
    print("=" * 60)
    print("\n--- STUDY PLAN PREVIEW ---\n")
    print(result[:2000] + ("\n\n[...truncated — see study_plan.md for full plan]"
                           if len(result) > 2000 else ""))


if __name__ == "__main__":
    main()
