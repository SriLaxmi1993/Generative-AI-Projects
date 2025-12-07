# **ATS Resume Reviewer & Writer – n8n Workflow**

This repository contains an **end-to-end automated ATS Resume Optimization workflow** built in **n8n**.
The workflow analyzes a candidate's resume against a job description, scores the match using AI, rewrites the resume to achieve a higher ATS match, and finally exports the tailored resume into a formatted **Google Doc**.

---

## 📌 **Purpose**

This automation helps job seekers create **ATS-friendly resumes** by:

* Evaluating resume alignment vs job description
* Identifying strengths, weaknesses, and missing keywords
* Tailoring the resume to maximize ATS match score
* Exporting the improved resume into a Google Doc

---

## 🧩 **Workflow Overview**

The workflow is composed of **4 main steps**, each represented by a modular node group in n8n.

---

## **🟦 Step 1: Input Validation**

**Nodes:**
`Edit Fields → Code in JavaScript → If`

**What this step does:**

* Normalizes resume and JD text:

  * Removes special characters
  * Standardizes bullet formats
  * Trims whitespace
* Calculates text lengths
* Validates minimum requirements:

  * **Resume ≥ 500 characters**
  * **Job Description ≥ 300 characters**
* Routes to an error handler if validation fails

This ensures the AI receives clean, usable input for scoring.

---

## **🟥 Step 2: ATS Evaluation**

**Nodes:**
`Message a Model → Parse ATS JSON`

**What this step does:**

Uses an OpenAI model (e.g., GPT-4o-mini or similar) to evaluate the resume vs the job description.

The model returns a JSON object containing:

* **Overall ATS Match Score (0–100%)**
* **Dimension-level scores**:

  * Title match
  * Skills alignment
  * Experience relevance
  * Formatting clarity
* **Strengths & Gaps** (keyword presence, missing responsibilities, etc.)

The JSON is then parsed for the next step.

---

## **💛 Step 3: Resume Tailoring**

**Node:**
`Tailor Resume (Message Model)`

**What this step does:**

* Rewrites the resume to target **99–100% ATS match**
* Incorporates relevant keywords from the JD
* Uses gaps identified in Step 2 to guide improvements
* Optimizes structure & wording specifically for ATS scanning
* Maintains truthfulness (no fabrication of achievements)
* Preserves clean, ATS-friendly formatting (no tables, no graphics)

This results in a polished, optimized resume aligned with the target role.

---

## **🟫 Step 4: Google Docs Export**

**Nodes:**
`HTTP Request → HTTP Request1 → Code in JavaScript2`

**What this step does:**

* Creates a **new Google Doc** titled:
  **`{candidate_name} – {target_role} (ATS Resume)`**
* Inserts:

  * Tailored resume
  * ATS match score
  * Dimension scores
  * Strengths & gaps report
* Produces final output containing:

  * **Google Doc URL**
  * Summary of improvements

This gives users a clean downloadable document ready for job applications.

---

## 🎯 **Inputs Required**

| Field             | Description                        |
| ----------------- | ---------------------------------- |
| `resume_text`     | Raw resume text (≥ 500 characters) |
| `job_description` | JD text (≥ 300 characters)         |
| `candidate_name`  | Candidate's full name              |
| `target_role`     | The role being applied for         |

---

## 📤 **Output**

A **Google Doc** containing:

* Tailored ATS-optimized resume
* Overall ATS score
* Keyword & relevance analysis
* Strengths and gaps
* Final polished formatting

---

## 🔐 **Security & Credentials**

This repository **does not include** any API keys.

In n8n:

* The OpenAI and Google credentials are stored securely in **n8n Credentials**, not inside the workflow.
* When exporting, n8n only outputs credential **IDs**, not secrets.

Your workflow JSON is safe to commit as long as:

* You do **not** export credentials
* You do **not** paste API keys directly into nodes

**Recommended `.gitignore`:**

```gitignore
.env
.env.*
.n8n/
```

---

## 📂 **Suggested Repository Structure**

```
.
├── ats_resume_workflow.json      # Exported n8n workflow (no secrets)
└── README.md                     # Documentation
```

---

## 🚀 **How to Use**

1. Import the workflow in n8n:
   **Workflows → Import from File**

2. Connect credentials:

   * **OpenAI API**
   * **Google Docs / Google OAuth**

3. Run the workflow with:

   * Resume text
   * Job description text
   * Candidate name
   * Target role

4. Receive:

   * ATS evaluation
   * Tailored resume
   * Google Doc link

---

## 📌 Future Enhancements (Optional)

* Add PDF export
* Add multiple resume versions for A/B testing
* Add a recruiter-style review summary
* Auto-apply to job boards (LinkedIn, Indeed, etc.)



