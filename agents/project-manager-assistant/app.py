import argparse
import uuid
from typing import List, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field


# Load environment variables from .env if present.
load_dotenv(override=True)


class Task(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the task")
    task_name: str = Field(description="Name of the task")
    task_description: str = Field(description="Description of the task")
    estimated_day: int = Field(description="Estimated number of days to complete the task")


class TaskList(BaseModel):
    tasks: List[Task] = Field(description="List of tasks")


class TaskDependency(BaseModel):
    task: Task = Field(description="Task")
    dependent_tasks: List[Task] = Field(description="List of dependent tasks")


class TeamMember(BaseModel):
    name: str = Field(description="Name of the team member")
    profile: str = Field(description="Profile of the team member")


class Team(BaseModel):
    team_members: List[TeamMember] = Field(description="List of team members")


class TaskAllocation(BaseModel):
    task: Task = Field(description="Task")
    team_member: TeamMember = Field(description="Team member assigned to the task")


class TaskSchedule(BaseModel):
    task: Task = Field(description="Task")
    start_day: int = Field(description="Start day of the task")
    end_day: int = Field(description="End day of the task")


class DependencyList(BaseModel):
    dependencies: List[TaskDependency] = Field(description="List of task dependencies")


class Schedule(BaseModel):
    schedule: List[TaskSchedule] = Field(description="List of task schedules")


class TaskAllocationList(BaseModel):
    task_allocations: List[TaskAllocation] = Field(description="List of task allocations")


class Risk(BaseModel):
    task: Task = Field(description="Task")
    score: int = Field(description="Risk score associated with the task from 0 to 10")


class RiskList(BaseModel):
    risks: List[Risk] = Field(description="List of task risks")


class AgentState(TypedDict):
    project_description: str
    team: Team
    tasks: TaskList
    dependencies: DependencyList
    schedule: Schedule
    task_allocations: TaskAllocationList
    risks: RiskList
    project_risk_score: int
    iteration_number: int
    max_iteration: int
    insights: str
    schedule_iteration: List[Schedule]
    task_allocations_iteration: List[TaskAllocationList]
    risks_iteration: List[RiskList]
    project_risk_score_iterations: List[int]


def load_llm(model_provider: str):
    if model_provider.lower() == "azure":
        return AzureChatOpenAI(deployment_name="gpt-4o-mini")
    if model_provider.lower() == "openai":
        return ChatOpenAI(model="gpt-4o-mini")
    raise ValueError("model_provider must be either 'Azure' or 'OpenAI'")


def task_generation_node(state: AgentState, llm):
    prompt = f"""
You are an expert project manager tasked with analyzing the following project description:
{state["project_description"]}

Objectives:
1) Extract actionable and realistic tasks with estimated duration in days.
2) If a task takes longer than 5 days, split it into smaller independent tasks.
3) Keep tasks clearly defined and execution-friendly.
"""
    tasks = llm.with_structured_output(TaskList).invoke(prompt)
    return {"tasks": tasks}


def task_dependency_node(state: AgentState, llm):
    prompt = f"""
You are a project scheduler mapping dependencies.
Given tasks: {state["tasks"]}

For each task:
- Identify tasks that depend on it.
- Keep dependencies realistic and minimal.
"""
    dependencies = llm.with_structured_output(DependencyList).invoke(prompt)
    return {"dependencies": dependencies}


def task_scheduler_node(state: AgentState, llm):
    prompt = f"""
Create an optimized task schedule.

Tasks: {state["tasks"]}
Dependencies: {state["dependencies"]}
Previous insights: {state["insights"]}
Previous schedules: {state["schedule_iteration"]}

Rules:
- Respect dependencies.
- Parallelize where possible.
- Reduce total duration without harming feasibility.
"""
    schedule = llm.with_structured_output(Schedule).invoke(prompt)
    schedule_iteration = list(state["schedule_iteration"])
    schedule_iteration.append(schedule)
    return {"schedule": schedule, "schedule_iteration": schedule_iteration}


def task_allocation_node(state: AgentState, llm):
    prompt = f"""
Allocate tasks to team members.

Tasks: {state["tasks"]}
Schedule: {state["schedule"]}
Team: {state["team"]}
Previous insights: {state["insights"]}
Previous allocations: {state["task_allocations_iteration"]}

Constraints:
- One person can handle only one overlapping task at a time.
- Match tasks to skill profiles.
- Balance workload across the team.
"""
    task_allocations = llm.with_structured_output(TaskAllocationList).invoke(prompt)
    task_allocations_iteration = list(state["task_allocations_iteration"])
    task_allocations_iteration.append(task_allocations)
    return {
        "task_allocations": task_allocations,
        "task_allocations_iteration": task_allocations_iteration,
    }


def risk_assessment_node(state: AgentState, llm):
    prompt = f"""
Assess risks for this project plan.

Task allocations: {state["task_allocations"]}
Schedule: {state["schedule"]}
Previous risks: {state["risks_iteration"]}

Output risk score per task from 0 (low) to 10 (high), considering:
- task complexity
- resource constraints
- dependency pressure
- if assignments are unchanged from prior iteration, keep scores consistent
"""
    risks = llm.with_structured_output(RiskList).invoke(prompt)
    project_risk_score = sum(risk.score for risk in risks.risks)

    risk_iterations = list(state["risks_iteration"])
    risk_iterations.append(risks)

    risk_scores_history = list(state["project_risk_score_iterations"])
    risk_scores_history.append(project_risk_score)

    return {
        "risks": risks,
        "project_risk_score": project_risk_score,
        "iteration_number": state["iteration_number"] + 1,
        "risks_iteration": risk_iterations,
        "project_risk_score_iterations": risk_scores_history,
    }


def insight_generation_node(state: AgentState, llm):
    prompt = f"""
Generate short actionable insights to reduce project risk in the next iteration.

Task allocations: {state["task_allocations"]}
Schedule: {state["schedule"]}
Risks: {state["risks"]}
"""
    insights = llm.invoke(prompt).content
    return {"insights": insights}


def router(state: AgentState):
    if state["iteration_number"] >= state["max_iteration"]:
        return END

    history = state["project_risk_score_iterations"]
    if len(history) > 1 and history[-1] < history[0]:
        return END
    return "insight_generator"


def build_graph(llm):
    workflow = StateGraph(AgentState)

    workflow.add_node("task_generation", lambda state: task_generation_node(state, llm))
    workflow.add_node("task_dependencies", lambda state: task_dependency_node(state, llm))
    workflow.add_node("task_scheduler", lambda state: task_scheduler_node(state, llm))
    workflow.add_node("task_allocator", lambda state: task_allocation_node(state, llm))
    workflow.add_node("risk_assessor", lambda state: risk_assessment_node(state, llm))
    workflow.add_node("insight_generator", lambda state: insight_generation_node(state, llm))

    workflow.set_entry_point("task_generation")
    workflow.add_edge("task_generation", "task_dependencies")
    workflow.add_edge("task_dependencies", "task_scheduler")
    workflow.add_edge("task_scheduler", "task_allocator")
    workflow.add_edge("task_allocator", "risk_assessor")
    workflow.add_conditional_edges("risk_assessor", router, ["insight_generator", END])
    workflow.add_edge("insight_generator", "task_scheduler")

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def get_project_description(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def get_team(file_path: str) -> Team:
    team_df = pd.read_csv(file_path)
    team_members = [
        TeamMember(name=row["Name"], profile=row["Profile Description"])
        for _, row in team_df.iterrows()
    ]
    return Team(team_members=team_members)


def main():
    parser = argparse.ArgumentParser(description="Project Manager Assistant Agent")
    parser.add_argument("--project-file", required=True, help="Path to project description .txt file")
    parser.add_argument("--team-csv", required=True, help="Path to team .csv file with Name and Profile Description columns")
    parser.add_argument("--model-provider", default="Azure", choices=["Azure", "OpenAI"], help="Model provider to use")
    parser.add_argument("--max-iteration", default=3, type=int, help="Maximum reflection iterations")
    args = parser.parse_args()

    llm = load_llm(args.model_provider)
    graph_plan = build_graph(llm)

    state_input = {
        "project_description": get_project_description(args.project_file),
        "team": get_team(args.team_csv),
        "insights": "",
        "iteration_number": 0,
        "max_iteration": args.max_iteration,
        "schedule_iteration": [],
        "task_allocations_iteration": [],
        "risks_iteration": [],
        "project_risk_score_iterations": [],
    }

    config = {"configurable": {"thread_id": "project-manager-assistant"}}
    for event in graph_plan.stream(state_input, config, stream_mode=["updates"]):
        print(f"Current node: {next(iter(event[1]))}")

    final_state = graph_plan.get_state(config).values
    print("\nFinal iteration count:", final_state["iteration_number"])
    print("Project risk scores per iteration:", final_state["project_risk_score_iterations"])


if __name__ == "__main__":
    main()
