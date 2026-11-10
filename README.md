# ScamGuard AI: Interactive Scam Detection Companion for Seniors

**Course:** ITAI 2376: Deep Learning – Final AI Agent Project  
**Team Name:** Data Proxy  
**Team Members:** Elijah Raines, Brandon Matias, Jonah Joseph, Osemudia Ogedengbe, & Justin Davis  

---


### Project Overview
ScamGuard AI is an adaptive, patient learning companion designed to help elderly individuals recognize, avoid, and protect themselves against financial fraud and social engineering. The system functions in two core modes: an **Interactive Simulation Mode** that safely trains seniors to spot red flags through practice scenarios, and a **Real-Time Verification Mode** that analyzes suspicious messages, links, and phone numbers.

---
  
### Key Features & Capabilities
* **Interactive Scenario Simulations:** Role-plays realistic phishing texts, fake tech support alerts, and imposter scams with gentle, jargon-free feedback.
* **Adaptive Reinforcement Learning:** Tracks user performance (pass/fail rates and hint counts) to dynamically adjust scenario difficulty and target weak spots.
* **Real-Time Scam Lookup:** Parses user-submitted messages and checks links/phone numbers against threat intelligence sources.
* **Robust Safety Guardrails:** Automatically redacts accidental PII (like Social Security Numbers) and triggers immediate emergency helpline routing if a user reports an active financial loss.

---

### System Architecture
The agent implements a **ReAct (Reasoning and Acting)** framework combined with a reflection loop:
1. **Input Processing:** Sanitizes inputs and checks for emergency keywords or intent classification.
2. **Memory System:** Maintains session state and tracks historical learner progress.
3. **Reasoning Component:** Evaluates responses, determines hint frequency, and adjusts scenario difficulty.
4. **Output Generation:** Delivers clear, high-contrast, bulleted guidance tailored for senior accessibility.


---

### Tool Integration
* **Scam Database Lookup (Web Search API):** Queries live FTC and AARP fraud data feeds, with an automated fallback to a local backup JSON list if rate-limited or offline.
* **Safety Analyzer Utility:** Parses text strings and URLs to detect spoofed domains and suspicious indicators.

---

### Setup & Installation Instructions
```bash
1. Clone the Repository

git clone [https://github.com/BrandonLee-98/scamguard-itai2376.git]
cd scamguard-ai-itai2376

2. Install Dependencies
pip install -r requirements.txt

3. Configure Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
SEARCH_API_KEY=your_search_api_key_here

4. Run the Agent
python src/core.py
```

---

### Folder Structure
```bash
scamguard-itai2376-dataproxy/
├── README.md
├── requirements.txt
├── .env.example
└── src/
    ├── __init__.py
    ├── core.py
    ├── memory.py
    ├── reasoning.py
    ├── tools/
    │   ├── __init__.py
    │   ├── scam_lookup.py
    │   └── safety_analyzer.py
    ├── safety/
    │   ├── __init__.py
    │   └── guardrails.py
    ├── tests/
    │   ├── test_agent.py
    │   └── test_tools.py
    └── examples/
