# agent/orchestrator_streamlit.py
"""
Enhanced orchestrator with Streamlit callback support
Allows real-time display of agent activity
"""

from agent.orchestrator import ClinicalTrialAgent as BaseAgent
import json


class ClinicalTrialAgentStreamlit(BaseAgent):
    """
    Streamlit-enhanced version of the agent with callback support
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", callback=None):
        super().__init__(api_key, model)
        self.callback = callback  # Function to call with updates

    def _emit_update(self, update_type: str, data: dict):
        """Send updates to Streamlit UI"""
        if self.callback:
            self.callback({
                'type': update_type,
                'data': data
            })

    def run_autonomous_search(self, patient_criteria: dict) -> dict:
        """
        Enhanced version with Streamlit callbacks
        """
        self._emit_update('start', {'criteria': patient_criteria})

        # Run the base search
        result = super().run_autonomous_search(patient_criteria)

        self._emit_update('complete', {'result': result})

        return result