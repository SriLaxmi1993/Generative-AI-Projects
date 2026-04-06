# CrewAI Research Findings

## Key Concepts

### Agents
- Autonomous units that can perform specific tasks
- Make decisions based on their role and goal
- Can be equipped with tools for extended capabilities
- Have a backstory, role, and goal

### Tasks
- Provide details for execution (description, agent responsible, tools, etc.)
- Can have expected output format
- Can write output to files
- Assigned to specific agents

### Crews
- Teams of autonomous agents that collaborate
- Execute tasks in a defined process (sequential, hierarchical, etc.)
- Return results after completion
- Can be triggered by a Flow

### Flows
- The backbone of AI applications
- Define steps, logic, and data flow
- Manage state across executions
- Delegate complex work to Crews

## Basic Structure

```python
from crewai import Agent, Crew, Process, Task

# 1. Create Agents
agent1 = Agent(
    role="Role Name",
    goal="Agent Goal",
    backstory="Agent Backstory",
    tools=[tool1, tool2]
)

# 2. Create Tasks
task1 = Task(
    description="Task Description",
    expected_output="Expected Output Format",
    agent=agent1
)

# 3. Create Crew
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.sequential,
    verbose=True
)

# 4. Run Crew
result = crew.kickoff(inputs={'key': 'value'})
```

## For Study Planning Agent

Multi-agent setup should include:
1. **Study Planner Agent** - Creates study schedules and plans
2. **Content Analyzer Agent** - Breaks down topics into learning chunks
3. **Progress Tracker Agent** - Monitors and adjusts study plans

All agents work together in a crew to create comprehensive study plans.
