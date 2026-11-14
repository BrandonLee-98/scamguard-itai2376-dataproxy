<div align="center">

# 🛡️ ScamGuard AI
### Interactive Scam Detection Companion & Security Trainer for Seniors

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Senior_UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-Tool_Calling_Agent-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Course](https://img.shields.io/badge/Course-ITAI_2376--14562-0F2942?style=for-the-badge)](#team--rubric-contributions)

**Team Data Proxy** • Houston City College — Deep Learning Final AI Agent Project

</div>

---

## 📖 Project Overview

**ScamGuard AI** is an adaptive, senior-friendly digital safety companion designed to help older adults recognize, verify, and protect themselves against financial fraud and social engineering. Built with accessibility and emotional reassurance at its core, the system operates in two seamless modes:

1. **🔍 Real-World Verification Mode:** Inspects suspicious texts, emails, URLs, and phone numbers in plain English using regex threat detection and live FTC/AARP fraud advisories.
2. **🎯 Interactive Simulation Mode:** Provides a safe, zero-risk practice environment where seniors build confidence spotting common scams while an adaptive reinforcement loop scales difficulty over time.

---

## ✨ Key Features & Capabilities

* **👵 Senior-First Accessible Interface (`app.py`):** High-contrast WCAG AAA layout featuring a one-click **Reading Comfort** toggle (`18px` Standard vs. `21px` Extra Large), enlarged tactile buttons, and icon-paired alert banners.
* **🧭 Intelligent Intent Routing (`src/core.py`):** Automatically classifies user prompts into **Practice Mode** or **Real-World Lookup** and dispatches tasks through a LangChain tool-calling `AgentExecutor`.
* **📈 Adaptive Reinforcement Learning (`src/memory.py` & `src/simulation.py`):** Uses a Pydantic-backed `UserSessionState` tracker to monitor accuracy, attempt history, and hint usage—automatically advancing learners from **Beginner $\rightarrow$ Intermediate $\rightarrow$ Advanced**.
* **🌐 Live Threat Intelligence + Offline Fallback (`src/tools/scam_lookup.py`):** Queries verified FTC and AARP scam alerts via the Tavily Search API, with automatic `try/except` failover to a curated local JSON database (`scam_database.json`) if offline or rate-limited.
* **🛑 Privacy & Safety Guardrails (`src/tools/safety_analyzer.py` & `app.py`):** Automatically blocks accidental submissions containing Social Security Numbers (`XXX-XX-XXXX`) or 16-digit payment card numbers, refuses unsafe prompts, and explains every risk decision transparently.

---

## 🏗️ System Architecture

```text
┌────────────────────┐      ┌──────────────────────┐      ┌───────────────────────────┐
│   Senior User UI   │─────▶│  PII & Safety Guard  │─────▶│     Intent Classifier     │
│  (Streamlit App)   │      │  (SSN / Card Block)  │      │  Practice vs. Lookup      │
└────────────────────┘      └──────────────────────┘      └─────────────┬─────────────┘
                                                                        │
                       ┌────────────────────────────────────────────────┴────────────────┐
                       ▼                                                                 ▼
        ┌─────────────────────────────┐                                   ┌─────────────────────────────┐
        │   Real-World Lookup Loop    │                                   │   Adaptive Simulation Loop  │
        │  • SafetyAnalyzer (Regex)   │                                   │  • Tiered Scam Scenarios    │
        │  • ScamDatabaseLookup (API) │                                   │  • UserSessionState (RL)    │
        │  • JSON Offline Fallback    │                                   │  • Dynamic Difficulty Scale │
        └──────────────┬──────────────┘                                   └──────────────┬──────────────┘
                       └────────────────────────────────┬────────────────────────────────┘
                                                        ▼
                                       ┌─────────────────────────────────┐
                                       │  gpt-4o-mini + Buffer Memory    │
                                       │  Plain-English Senior Guidance  │
                                       └─────────────────────────────────┘
```

| Architectural Stage | Module | Responsibility |
| :--- | :--- | :--- |
| **1. Input Processing** | `app.py`, `src/core.py` | Screens out sensitive PII patterns and routes queries via `classify_user_intent()`. |
| **2. Memory System** | `src/memory.py`, `src/core.py` | Tracks short-term chat history (`ConversationBufferMemory`) and long-term learner metrics (`UserSessionState`). |
| **3. Reasoning & Tools** | `src/core.py`, `src/tools/` | Executes `create_tool_calling_agent` with `gpt-4o-mini` (`temperature=0.3`) to select tools and evaluate threats. |
| **4. Output Generation** | `app.py`, `src/simulation.py` | Delivers calm, jargon-free guidance, red-flag badges, and transparent AI reasoning notes. |

---

## 🧰 External Tool Integration

| Tool Name | Source File | Purpose & Trigger | Error Handling & Fallback |
| :--- | :--- | :--- | :--- |
| **`ScamDatabaseLookup`** | `src/tools/scam_lookup.py` | Queries live **FTC & AARP** advisories via `tavily-python` when verifying real-world scam claims. | Intercepts network timeouts, rate limits, or missing keys and falls back to `src/tools/scam_database.json`. |
| **`SafetyAnalyzer`** | `src/tools/safety_analyzer.py` | Scans pasted messages for URLs, phone numbers, and urgency keywords (*IRS, arrest, gift card, suspended*). | Catches malformed or empty inputs and returns a safe generic warning without crashing. |

---

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/BrandonLee-98/scamguard-itai2376-dataproxy.git](https://github.com/BrandonLee-98/scamguard-itai2376-dataproxy.git)
cd scamguard-itai2376-dataproxy
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root (or add keys to `.streamlit/secrets.toml` for Streamlit Community Cloud):
```env
OPENAI_API_KEY=your_openai_api_key_here
SEARCH_API_KEY=your_tavily_api_key_here
```

### 4. Launch the Application
* **Run the Interactive Web App (Recommended):**
  ```bash
  streamlit run app.py
  ```
* **Run the CLI Simulation Runner:**
  ```bash
  python -m src.simulation
  ```
* **Verify Core Agent Initialization:**
  ```bash
  python -m src.core
  ```

---

## 📂 Repository Structure

```text
scamguard-itai2376-dataproxy/
├── app.py                        # Senior-accessible Streamlit web interface & PII guardrails
├── requirements.txt              # Project dependencies
├── .env.example                  # Environment variable template
├── README.md                     # Project documentation & team contributions
└── src/
    ├── __init__.py
    ├── core.py                   # gpt-4o-mini tool-calling agent, memory & intent router
    ├── memory.py                 # Pydantic UserSessionState & adaptive difficulty scaling
    ├── simulation.py             # Multi-scenario interactive training runner
    ├── tools/
    │   ├── __init__.py
    │   ├── scam_lookup.py        # Tavily FTC/AARP search tool with JSON fallback
    │   ├── scam_database.json    # Offline structured senior scam knowledge base
    │   └── safety_analyzer.py    # Regex URL, phone & urgency keyword scanner
    ├── safety/
    │   └── __init__.py
    └── tests/                    # Unit & integration validation scripts
```

---

## 👥 Team & Rubric Contributions

**Course:** ITAI 2376-14562 • **Team Name:** Data Proxy

| Team Member | Design Contribution | Coding Implementation | Reflection & Testing |
| :--- | :--- | :--- | :--- |
| **Brandon Matias** | Designed end-to-end agent architecture, intent routing workflow, and senior-accessible Streamlit UX/UI layout. | Implemented `src/core.py`, `src/memory.py`, `src/simulation.py`, and the full `app.py` web interface with PII guardrails. | Conducted end-to-end integration testing, dependency optimization, and project reflection analysis. |
| **Elijah Raines** | Co-designed conversational intent flows and senior-friendly prompt tone guidelines. | Contributed to core agent configuration, prompt templates, and intent classification test cases. | Evaluated prompt routing accuracy and documented lessons learned on model temperature tuning. |
| **Jonah Joseph** | Designed external threat intelligence retrieval schema and offline fallback strategy. | Built and validated `src/tools/scam_lookup.py` and structured scam vectors in `src/tools/scam_database.json`. | Tested live Tavily API queries and simulated network failures to verify seamless JSON failover. |
| **Fifehanmi Ogedengbe** | Designed adaptive reinforcement learning progression tiers and senior training scenarios. | Contributed to adaptive difficulty thresholds, scenario libraries, and session scoring validation. | Assessed learner progression curves and documented insights on adaptive feedback design. |
| **Justin Davis** | Designed input sanitization rules, regex threat detection patterns, and AI transparency standards. | Built and tested `src/tools/safety_analyzer.py` and boundary validation error handling. | Verified malformed input handling and reflected on safety-first guardrails for vulnerable users. |
