# Study Planning Multi-Agent System

A study planning assistant powered by the **[CrewAI](https://docs.crewai.com/)** multi-agent framework. Three specialized AI agents collaborate sequentially to produce a comprehensive, personalized study plan for any subject or exam. Includes both a CLI app (`app.py`) and a Streamlit web UI (`streamlit_app.py`).

---

## Architecture

The system uses a **sequential multi-agent crew** composed of three agents, each with a distinct role:

| Agent | Role | Responsibility |
|---|---|---|
| **Curriculum Analyst** | Academic expert | Breaks the subject into prioritized topics with difficulty ratings and time estimates |
| **Study Planner** | Productivity coach | Builds a realistic day-by-day schedule with spaced repetition and revision days |
| **Study Coach** | Academic mentor | Adds recommended resources, study techniques, a daily routine template, and motivational tips |

Each agent hands off its output as context to the next, ensuring the final plan is coherent and comprehensive.

```
User Input
    │
    ▼
┌─────────────────────┐
│  Curriculum Analyst │  ── Topic breakdown, difficulty, time estimates
└─────────┬───────────┘
          │ context
          ▼
┌─────────────────────┐
│    Study Planner    │  ── Day-by-day schedule with review sessions
└─────────┬───────────┘
          │ context
          ▼
┌─────────────────────┐
│    Study Coach      │  ── Resources, techniques, motivation, final Markdown plan
└─────────────────────┘
          │
          ▼
   study_plan.md
```

---

## Project Structure

```
Building a Study Planner with Crew AI Framework/
├── app.py                 # CLI application — agents, tasks, crew, and CLI prompts
├── streamlit_app.py       # Streamlit web UI
├── requirements.txt       # Python dependencies
└── Study Planning Multi-Agent System.md  # This guide
```

---

## Prerequisites

- **Python 3.10+**
- An **OpenAI API key** (or any OpenAI-compatible LLM key)

---

## Setup

### 1. Clone or download this project

```bash
git clone <repo-url>
cd "agents/Study planning multi-agent/Building a Study Planner with Crew AI Framework"
```

### 2. Create and activate a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

Or export it directly in your shell:

```bash
export OPENAI_API_KEY=sk-...
```

> Note: The app uses `gpt-4o-mini` by default for cost efficiency. To change the model in the CLI, edit the `ChatOpenAI(model="...")` line in `app.py`. In the Streamlit app you can select the model in the sidebar.

---

## Usage

### Option A — Streamlit Web App (Recommended)

```bash
streamlit run streamlit_app.py
```

In the browser:
- Enter your OpenAI API key in the sidebar (or set `OPENAI_API_KEY` in your environment)
- Fill in subject, hours/day, and days until exam
- Click “Generate Study Plan” to produce and download the Markdown plan

### Option B — CLI
```bash
python app.py
```

You will be prompted for three inputs:

| Prompt | Example |
|---|---|
| Subject or exam | `Python Programming` |
| Study hours per day | `3` |
| Days until exam | `30` |

### Example Session

```
============================================================
       Study Planning Multi-Agent System (CrewAI)
============================================================

Enter the subject or exam you want to study for:
> Machine Learning

How many hours can you study per day? (e.g., 2.5)
> 2

How many days do you have until your exam/deadline?
> 21

------------------------------------------------------------
  Subject        : Machine Learning
  Hours per day  : 2.0
  Days available : 21
------------------------------------------------------------

Launching your study planning crew... (this may take a minute)
```

After the crew finishes (typically 1–3 minutes), the full study plan is:

- **Printed** to the terminal (first 2,000 characters as a preview)
- **Saved** to `study_plan.md` in the current directory

---

## Output

The generated `study_plan.md` includes:

1. **Topic Breakdown** — All key topics with difficulty ratings and recommended time allocation
2. **Day-by-Day Schedule** — A complete calendar with topic assignments, daily review slots, and full revision days
3. **Recommended Resources** — Books, websites, YouTube channels, and apps
4. **Study Techniques** — Methods best suited to the subject (active recall, spaced repetition, etc.)
5. **Daily Routine Template** — A structured daily workflow to follow
6. **Motivational Coaching Notes** — Tips to stay consistent and avoid burnout

---

## Customization

| What to change | Where |
|---|---|
| LLM model (CLI) | `ChatOpenAI(model="...")` in `app.py` |
| LLM model (UI) | Sidebar model selector in `streamlit_app.py` |
| Agent personalities | `backstory` field of each `Agent(...)` in `app.py` |
| Task instructions | `description` field of each `Task(...)` in `build_tasks()` |
| Output format | `expected_output` field of the final task |
| Add tools (web search, etc.) | Add `tools=[...]` to any `Agent(...)` definition |

---

## Dependencies (minimal)

| Package | Purpose |
|---|---|
| `crewai` | Multi-agent orchestration framework |
| `crewai-tools` | Optional built-in tools (web search, file I/O, etc.) |
| `openai` | LLM backend client |
| `python-dotenv` | Loads API keys from `.env` file |
| `langchain-openai` | OpenAI chat LLM wrapper used by agents |
| `streamlit` | Web UI framework |

---

## License

MIT — free to use, modify, and distribute.
