# Clinical Trial Matching Agent 🔬

An autonomous AI agent that searches, filters, and ranks clinical trials from ClinicalTrials.gov based on patient criteria. Demonstrates production-ready agentic AI architecture with real-time decision-making, tool orchestration, and transparent reasoning.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Project Purpose

Built to demonstrate modern agentic AI patterns and healthcare domain expertise. This system autonomously plans and executes multi-step workflows without human intervention - a key capability in production AI systems.

## ✨ Key Features

### Agentic AI Capabilities
- **Autonomous Planning**: Agent decides which tools to use and when
- **Multi-Step Execution**: Search → Filter → Rank → Save (no human in loop)
- **Adaptive Reasoning**: Adjusts strategy based on results
- **Tool Orchestration**: Manages multiple APIs and services independently
- **Transparent Decision-Making**: Real-time activity logging and reasoning display

### Technical Features
- Real-time ClinicalTrials.gov API integration
- Streamlit web interface with live agent activity streaming
- Production logging with audit trails
- Search history and session management
- Professional error handling and timeout management
## 📊 Current Status - Version 0.1

**✅ Implemented:**
- Real ClinicalTrials.gov API integration
- Autonomous agent orchestration
- Real-time UI with activity streaming
- Production logging system
- Search history management
- Deterministic temperature setting (0.0) for clinical consistency
- Direct ClinicalTrials.gov links in final results (clickable links to each recommended trial)
- Graceful fallback when max iterations reached (agent summarizes partial results instead of failing)

**🔜 v0.2 Planned Features:**
- Temperature control UI (Deterministic/Creative dropdown)
- MongoDB persistence for search results
- Email alerts for new trial matches
- Automated monitoring for trial updates
- Enhanced eligibility parsing from trial criteria

## 🏗️ Architecture
```
┌─────────────────────┐
│   Streamlit UI      │ ← User inputs patient criteria
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  Agent Orchestrator         │
│  (Claude Sonnet 4)          │ ← Autonomous decision-making
│  - Tool selection           │
│  - Multi-step planning      │
│  - Adaptive reasoning       │
└─────┬──────────────────────┘
      │
      ├─→ [Tool: search_trials] ────→ ClinicalTrials.gov API
      ├─→ [Tool: check_eligibility] → Eligibility Logic
      ├─→ [Tool: rank_trials] ──────→ Relevance Scoring
      ├─→ [Tool: save_results] ─────→ MongoDB (planned)
      └─→ [Tool: get_details] ──────→ Trial Details
           │
           ▼
      ┌──────────────┐
      │ Logger       │ ← Audit trails, debugging
      └──────────────┘
```

## 🛠️ Tech Stack

- **AI/LLM**: Anthropic Claude Sonnet 4 (with function calling/tool use)
- **Backend**: Python 3.10+
- **Web Framework**: Streamlit
- **APIs**: ClinicalTrials.gov API v2
- **Database**: MongoDB (planned for persistence)
- **Logging**: Python logging with custom audit trails

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ewbaxter/ClinicalTrialAgent.git
cd ClinicalTrialAgent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variable**
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Linux/Mac
export ANTHROPIC_API_KEY="your-api-key-here"

# Or set in your system environment variables
```

5. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Enter Patient Information**
   - Patient ID
   - Age
   - Gender
   - Medical conditions (one per line)
   - Location (city, state)

2. **Run Agent Search**
   - Click "Run Agent Search"
   - Watch the agent autonomously plan and execute the search
   - See real-time reasoning and tool calls

3. **Review Results**
   - Matched clinical trials with relevance scores
   - Direct links to each trial on ClinicalTrials.gov (e.g., `https://clinicaltrials.gov/study/NCT03995238`)
   - Agent's decision-making process
   - Search history

4. **Check Logs**
   - Detailed logs saved to `logs/` directory
   - Timestamped audit trails for each search

## 🎬 Demo Workflow

The agent autonomously executes this workflow:

1. **Initial Search**: Searches ClinicalTrials.gov with patient condition
2. **Broadening Strategy**: If needed, tries alternative search terms
3. **Eligibility Filtering**: Checks age, gender, condition criteria
4. **Relevance Ranking**: Ranks by proximity, phase, enrollment status
5. **Result Persistence**: Saves search for future monitoring

## 📁 Project Structure
```
clinical_trial_agent/
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py      # Core agent logic with tool orchestration
│   └── logger.py            # Production logging system
├── services/
│   └── clinicaltrials_api.py # ClinicalTrials.gov API client
├── logs/                     # Generated log files
├── app.py                    # Streamlit web interface
├── test_agent.py            # CLI testing script
├── requirements.txt
└── README.md
```

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for Claude |

## 🧪 Testing

**Test the API integration directly:**
```bash
python services/clinicaltrials_api.py
```

**Test the agent via CLI:**
```bash
python test_agent.py
```

## 📊 Current Status

**✅ Implemented:**
- Real ClinicalTrials.gov API integration
- Autonomous agent orchestration
- Real-time UI with activity streaming
- Production logging system
- Search history management
- Direct ClinicalTrials.gov links in final results
- Graceful fallback on max iterations (partial results instead of hard failure)

**🚧 Planned:**
- MongoDB persistence for search results
- Email alerts for new trial matches
- Automated monitoring for trial updates
- Enhanced eligibility parsing from trial criteria

## 🏥 Healthcare Domain Context

This project leverages 20+ years of healthcare technology experience to build a practical tool for clinical trial discovery. Key healthcare considerations:

- Patient privacy (no PHI stored)
- Accurate eligibility matching
- Location-based accessibility
- Trial phase understanding
- Regulatory awareness

## 🤝 Contributing

This is a portfolio/demonstration project. Feedback and suggestions welcome via issues.

## 📝 License

MIT License - see LICENSE file for details

## 👤 Author

**Eric Baxter**
- Healthcare Technology Leader with 20+ years experience
- Platform Engineering & AI Integration Specialist
- LinkedIn: [Your LinkedIn]
- GitHub: [@ewbaxter](https://github.com/ewbaxter)

## 🙏 Acknowledgments

- ClinicalTrials.gov for providing free public API access
- Anthropic for Claude API and agentic AI capabilities
- Streamlit for rapid web app development

## 📌 Notes

This is a demonstration project showing agentic AI architecture. While it uses real clinical trial data, it should not be used as medical advice. Always consult healthcare professionals for medical decisions.

---

**Built with ❤️ to demonstrate modern AI agent architecture and healthcare technology expertise**
