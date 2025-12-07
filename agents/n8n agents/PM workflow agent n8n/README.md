# **AI Research & PRD Automation Flow — n8n Orchestrated Multi-Agent Pipeline**

This repository contains an **n8n multi-agent automation flow** designed to analyze **market research** or **user research**, route the request to the correct expert agent, and optionally generate a **Product Requirements Document (PRD)** based on a predefined PRD template.

The workflow uses an **Orchestration Agent** to determine intent, specialized research agents, a PRD generator, a user input handler, and automatic file creation.

---

## 🚀 **Overview**

This n8n flow automates the following steps:

1. **Receive Incoming User Message**
2. **Identify Query Intent** → *Market Research*, *User Research*, or *PRD Generation*
3. **Route to the Appropriate Expert Agent**
4. **Retrieve Additional Insights** using external search (Tavily)
5. **Store & Use Memory** across research steps
6. **Return a Consolidated Response to the User**
7. **Ask the User Whether They Want a PRD**
8. **If Yes → Generate a PRD Using a Template**
9. **Convert PRD to a Downloadable File**
10. **Send Final Output Back to the User**

This creates a fully automated **Research → Insights → PRD** pipeline.

---

## 🧠 **Architecture Diagram**

*(Generated from the workflow screenshot)*

```
When Chat Message Received
        ↓
┌──────────────────┐
│ Orchestration    │  → Decides intent (Market Research / User Research / PRD Generation)
│ Agent            │
└──────────────────┘
        ↓
    [Routes to]
        ├─► Market Research Agent
        ├─► User Research Analyst
        └─► PRD Generator (when explicitly requested)
        ↓
Edit Fields → Respond to Chat
        ↓
      [IF User Says "Yes" to save?]
        ├─► YES → Edit Fields → Convert to File → Respond to Chat
        └─► NO → Respond to Chat Only
```

### **Agents Under the Orchestration Layer**

* **Market Research Agent**

  * Competitor analysis
  * Market sizing
  * Pricing insights
  * Trends & opportunities

* **User Research Analyst**

  * User behavior, pain points
  * Interview-style analysis
  * Usability insights

* **PRD Generator**

  * Uses PRD template
  * Generates sections based on research output

Each agent uses:

* **OpenAI Chat Models**
* **Simple Memory**
* **Tavily Search Tool** (optional external research)

---

## 🔧 **Components Explained**

### 1. **Trigger: When Chat Message Received**

Entry point receiving user input.

---

### 2. **Orchestration Agent**

A centralized LLM that:

* Interprets intent
* Routes messages to:

  * Market Research Agent, or
  * User Research Analyst, or
  * PRD Generator (when explicitly requested)
* Determines which downstream actions are required

**Example prompt logic**:

```text
If message relates to market, competitors, pricing, or industry → Market Research Agent  
If message relates to users, interviews, pain points → User Research Analyst
If message explicitly requests PRD generation → PRD Generator
```

---

### 3. **Market Research Agent**

**Functions:**

* Competitor breakdown
* Market landscape
* Strategic recommendations

Uses:

* OpenAI Chat Model
* Memory
* Tavily Search

---

### 4. **User Research Analyst**

**Functions:**

* Synthesizes user feedback
* Identifies pain points
* Maps user journeys
* Suggests UX improvements

Uses:

* OpenAI Chat Model
* Memory
* Tavily Search

---

### 5. **Response Handling**

After an expert agent completes its analysis:

* The response flows into **Respond to Chat**
* The system asks:

> "Would you like me to generate a PRD based on this research?"

---

### 6. **User Input Handler (IF Node)**

* If user answers **"yes"**, the workflow continues to PRD generation
* If **no**, reply immediately and exit

---

### 7. **PRD Generator Agent**

This agent:

* Takes research output
* Applies the predefined PRD template
* Generates:

  * Problem Statement
  * Goals & Success Metrics
  * Target Users
  * Product Requirements
  * Competitive Landscape
  * Feature List
  * Risks & Open Questions

Uses:

* OpenAI Chat Model
* Memory

---

### 8. **Convert to File Node**

* Wraps PRD text into a `.txt` (or PDF, Markdown) file
* Makes it downloadable for the user

---

### 9. **Final Response Node**

Outputs:

* Research insights
* PRD file (if requested)

---

## 📁 **Repository Structure**

```
├── README.md
├── PM workflow.json                   # n8n workflow export file
└── /templates/                        # (Optional) PRD templates directory
    └── prd_template.md                # PRD template used by PRD generator
```

---

## 💡 **Key Features**

### ✔ Multi-Agent LLM Architecture

Intelligently routes tasks to specialized models.

### ✔ Automated PRD Writing

No manual heavy lifting—PRD is created fully from research context.

### ✔ Memory-Aware Agents

Agents remember intermediate insights to ensure consistency.

### ✔ Human-in-the-Loop

User chooses whether to generate a PRD.

### ✔ External Research Integration (Tavily Search)

Ensures up-to-date data and deeper insights.

---

## 📦 **How to Use**

1. Import the `PM workflow.json` file into your n8n instance.
2. Configure your API keys:

   * **OpenAI API** - Required for all agents (Orchestration, Market Research, User Research, PRD Generator)
   * **Tavily API** - Required for external research capabilities
3. The PRD template is already embedded in the PRD Generator's system message.
4. Activate the workflow in n8n.
5. Start chatting — the system intelligently routes your queries to the appropriate agent.

**Note:** The PRD Generator is only triggered when you explicitly request PRD generation (e.g., "generate a PRD", "create a product requirements document").

---

## 🔮 **Future Enhancements**

* Add Jira/Trello integration to auto-create tickets
* Export PRD as PDF or Google Doc
* Add additional agents:

  * Competitive Intelligence Agent
  * UX Design Agent
* Embed analytics & reporting dashboards

---

## 📝 **License**

MIT License

---

