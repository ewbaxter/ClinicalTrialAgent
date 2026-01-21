# test_agent.py
"""
Quick test to see the agent in action
Run with: python test_agent.py
"""

import os
from agent.orchestrator import ClinicalTrialAgent


def main():
    # Pull from OS environment variable (no .env file needed)
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables")
        print("Set it in your OS or PyCharm run configuration")
        return

    print("✅ API key found in environment")
    print("Initializing Clinical Trial Agent...\n")

    agent = ClinicalTrialAgent(api_key=api_key)

    # Test case matching your actual medical situation
    patient_criteria = {
        "age": 57,
        "gender": "male",
        "conditions": ["severe fatty liver disease", "NAFLD", "CAP score 374"],
        "location": "Denver, CO",
        "patient_id": "ERIC_001"
    }

    print("This demonstrates AGENTIC behavior:")
    print("- Claude autonomously decides which tools to call")
    print("- Multi-step planning without human intervention")
    print("- Adaptive reasoning based on results\n")

    result = agent.run_autonomous_search(patient_criteria)

    if result["success"]:
        print("\n" + "=" * 70)
        print("✅ AUTONOMOUS SEARCH COMPLETE")
        print("=" * 70)


if __name__ == "__main__":
    main()