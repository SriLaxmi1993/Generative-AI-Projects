# Project Manager Assistant Agent

## Overview
This agent helps with early project planning by turning a project description into:
- actionable tasks
- task dependencies
- an execution schedule
- task assignments based on team expertise
- per-task and overall project risk scores

It uses LangGraph for orchestration and `gpt-4o-mini` (Azure OpenAI or OpenAI) for structured planning outputs.

## Motivation
Project initiation can be complex and time-consuming. This assistant automates the setup process by producing a structured project plan from plain-language input and iteratively refining it based on risk feedback.

## Benefits
- Reduces manual planning effort
- Improves consistency in plan generation
- Surfaces dependencies and risk hotspots early
- Supports iterative improvement via self-reflection

## Key Components
- **LangGraph**: manages stateful workflow execution
- **LLM (`gpt-4o-mini`)**: generates structured tasks, dependencies, schedule, allocations, risks, and insights

## Data Models
- `Task`, `TaskList`
- `TaskDependency`, `DependencyList`
- `TeamMember`, `Team`
- `TaskSchedule`, `Schedule`
- `TaskAllocation`, `TaskAllocationList`
- `Risk`, `RiskList`
- `AgentState` for workflow state

## Workflow Nodes
- `task_generation`: create actionable tasks from description
- `task_dependencies`: map dependency graph
- `task_scheduler`: generate dependency-aware schedule
- `task_allocator`: assign tasks to team members
- `risk_assessor`: score task risks and total risk
- `insight_generator`: produce recommendations for next iteration
- `router`: controls iterative loop based on risk trend and max iterations

## Author and Access
- **Author:** Srilaxmich
- **Access:** Public (GitHub-ready)
- **Repository Visibility Recommendation:** Public

## Repository Readiness (Public GitHub)
- API keys are loaded via environment variables and should never be committed.
- Use a local `.env` file and add it to `.gitignore`.
- Keep sample data non-sensitive (no private customer/team information).

## Installation
```bash
cd "agents/project-manager-assistant"
python -m pip install -r requirements.txt
```

## Environment Variables
Choose one provider:

### Azure OpenAI
- `AZURE_OPENAI_API_KEY`
- `OPENAI_API_VERSION`
- `AZURE_OPENAI_ENDPOINT`

### OpenAI
- `OPENAI_API_KEY`
- `OPENAI_API_BASE` (optional)

### Example `.env`
```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
OPENAI_API_VERSION=your_version_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# OpenAI (if using OpenAI provider)
OPENAI_API_KEY=your_key_here
OPENAI_API_BASE=https://api.openai.com/v1
```

## Expected Input Files
- Project description text file (for example `project_description.txt`)
- Team CSV with columns:
  - `Name`
  - `Profile Description`

## Run
```bash
python app.py \
  --project-file "./sample_data/project_description.txt" \
  --team-csv "./sample_data/team.csv" \
  --model-provider Azure \
  --max-iteration 3
```

## Output
During execution, the script prints visited nodes and finally shows:
- total number of iterations run
- project risk score per iteration

## Notes and Limitations
- LLM-based risk scoring can vary between runs.
- Prompt constraints improve reliability but do not guarantee perfect consistency.
- A future enhancement is human-in-the-loop updates (for example team availability changes).
- Another enhancement is adding a deterministic optimizer for scheduling and assignment after LLM extraction.

## Security and Secrets
- Never commit `.env`, API keys, or credentials.
- Rotate API keys periodically.
- If a key is accidentally exposed, revoke and regenerate immediately.

## License
This project is licensed under the MIT License. See `LICENSE`.

## Contributing
Contributions are welcome. Open an issue for major changes before submitting a PR.

## Public GitHub Checklist
- [x] Author and access details included
- [x] `.env`-based secret handling documented
- [x] Example environment variables provided
- [x] Sample non-sensitive input files added (`sample_data/`)
- [x] License included (`MIT`)
- [ ] Optional: add screenshots/diagram exports for README visuals
- [ ] Optional: add CI checks (lint/tests) for pull requests
