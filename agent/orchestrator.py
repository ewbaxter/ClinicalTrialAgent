# agent/orchestrator.py
"""
Core Agent Orchestrator - Complete version with logging
"""

import anthropic
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from agent.logger import AgentLogger
from services.clinicaltrials_api import ClinicalTrialsAPI


class ClinicalTrialAgent:
    """
    Agentic AI orchestrator with real-time updates and logging
    """

    def __init__(
            self,
            api_key: str,
            model: str = "claude-sonnet-4-20250514",
            activity_callback: Optional[Callable] = None,
            enable_logging: bool = True,
            verbose_console: bool = False

    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.conversation_history = []
        self.activity_callback = activity_callback
        self.ct_api = ClinicalTrialsAPI()

        # Initialize logger
        self.logger = AgentLogger(verbose_console=verbose_console) if enable_logging else None

    def _log_activity(self, activity_type: str, content: Any, **kwargs):
        """
        Send activity updates to UI and log file
        """
        # Send to UI callback
        if self.activity_callback:
            self.activity_callback({
                'type': activity_type,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            })

        # Write to log file
        if self.logger:
            if activity_type == 'start':
                self.logger.log_search_start(kwargs.get('patient_criteria', {}))
            elif activity_type == 'iteration':
                self.logger.log_iteration(kwargs.get('iteration', 0))
            elif activity_type == 'thinking':
                self.logger.log_thinking(content, kwargs.get('iteration', 0))
            elif activity_type == 'tool_call':
                self.logger.log_tool_call(
                    kwargs.get('tool_name', 'unknown'),
                    kwargs.get('tool_input', {}),
                    kwargs.get('iteration', 0)
                )
            elif activity_type == 'tool_result':
                self.logger.log_tool_result(
                    kwargs.get('tool_name', 'unknown'),
                    kwargs.get('result_summary', '')
                )
            elif activity_type == 'complete':
                self.logger.log_search_complete(
                    kwargs.get('iterations', 0),
                    success=True
                )

    def get_tool_definitions(self) -> List[Dict]:
        """
        Define tools that the agent can autonomously call.
        """
        return [
            {
               {
                    "name": "search_clinical_trials",
                    "description": "Search ClinicalTrials.gov for trials matching patient criteria. IMPORTANT: Always include location to find trials near the patient. Returns list of trials with basic info.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "condition": {
                                "type": "string",
                                "description": "Medical condition or disease (e.g., 'liver disease', 'diabetes')"
                            },
                            "location": {
                                "type": "string",
                                "description": "Patient's city and state (e.g., 'Denver, CO', 'Colorado'). REQUIRED to find nearby trials."
                            },
                            "recruiting_status": {
                                "type": "string",
                                "description": "Trial recruitment status",
                                "enum": ["recruiting", "not_yet_recruiting", "active", "all"]
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of trials to return (default 20)"
                            }
                        },
                        "required": ["condition", "location"]  # Add location as required!
                    }
                }
            },
            {
                "name": "check_eligibility",
                "description": "Check if a patient meets eligibility criteria for specific trials. Use after searching to filter candidates.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "trial_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of NCT IDs to check eligibility for"
                        },
                        "patient_age": {
                            "type": "integer",
                            "description": "Patient age in years"
                        },
                        "patient_gender": {
                            "type": "string",
                            "enum": ["male", "female", "all"]
                        },
                        "conditions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of patient's medical conditions"
                        }
                    },
                    "required": ["trial_ids", "patient_age", "patient_gender"]
                }
            },
            {
                "name": "rank_trials",
                "description": "Rank eligible trials by relevance to patient. Consider distance, phase, enrollment status. Use after eligibility filtering.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "eligible_trial_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of NCT IDs that patient is eligible for"
                        },
                        "patient_location": {
                            "type": "string",
                            "description": "Patient's city and state for distance calculation"
                        },
                        "preference_weights": {
                            "type": "object",
                            "description": "Optional weights for ranking factors",
                            "properties": {
                                "distance": {"type": "number"},
                                "phase": {"type": "number"},
                                "enrollment": {"type": "number"}
                            }
                        }
                    },
                    "required": ["eligible_trial_ids"]
                }
            },
            {
                "name": "save_search_results",
                "description": "Save search results to database for future monitoring. Use at end of successful search.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": "Unique patient identifier"
                        },
                        "search_criteria": {
                            "type": "object",
                            "description": "Original search parameters"
                        },
                        "matched_trials": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of NCT IDs that matched"
                        }
                    },
                    "required": ["patient_id", "search_criteria", "matched_trials"]
                }
            },
            {
                "name": "get_trial_details",
                "description": "Get detailed information about specific trials. Use when user wants to learn more about a specific trial.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "nct_id": {
                            "type": "string",
                            "description": "NCT identifier for the trial"
                        }
                    },
                    "required": ["nct_id"]
                }
            }
        ]

    def process_tool_call(self, tool_name: str, tool_input: Dict, iteration: int = 0) -> Dict:
        """
        Execute tool calls. In Phase 1, these are mocks.
        """

        # Log the tool call to UI
        self._log_activity(
            'tool_call',
            f"Calling tool: {tool_name}",
            tool_name=tool_name,
            tool_input=tool_input,
            iteration=iteration
        )

        # Mock implementations for demo purposes
        if tool_name == "search_clinical_trials":
            return self._mock_search_trials(tool_input)

        elif tool_name == "check_eligibility":
            return self._mock_check_eligibility(tool_input)

        elif tool_name == "rank_trials":
            return self._mock_rank_trials(tool_input)

        elif tool_name == "save_search_results":
            return self._mock_save_results(tool_input)

        elif tool_name == "get_trial_details":
            return self._mock_get_details(tool_input)

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _mock_search_trials(self, params: Dict) -> Dict:
        """Mock trial search - returns realistic dummy data"""
        condition = params.get("condition", "").lower()
        # Use real API
        result = self.ct_api.search_studies(
            condition=params.get("condition", ""),
            location=params.get("location"),
            recruiting_status=params.get("recruiting_status", "recruiting"),
            max_results=params.get("max_results", 20)
        )

        return result

    def _mock_check_eligibility(self, params: Dict) -> Dict:
        """Mock eligibility check"""
        trial_ids = params.get("trial_ids", [])
        age = params.get("patient_age")

        # Simulate eligibility logic
        eligible = []
        ineligible = []

        for trial_id in trial_ids:
            if age and age >= 18 and age <= 75:
                eligible.append({
                    "nct_id": trial_id,
                    "eligible": True,
                    "reason": "Meets age criteria (18-75)"
                })
            else:
                ineligible.append({
                    "nct_id": trial_id,
                    "eligible": False,
                    "reason": f"Age {age} outside range (18-75)"
                })

        return {
            "eligible_count": len(eligible),
            "eligible_trials": eligible,
            "ineligible_trials": ineligible
        }

    def _mock_rank_trials(self, params: Dict) -> Dict:
        """Mock trial ranking"""
        trial_ids = params.get("eligible_trial_ids", [])

        # Simple mock ranking
        ranked = [
            {
                "nct_id": tid,
                "rank": idx + 1,
                "relevance_score": 0.95 - (idx * 0.1),
                "distance_miles": 5 + (idx * 3),
                "reason": f"High relevance, close proximity"
            }
            for idx, tid in enumerate(trial_ids)
        ]

        return {
            "ranked_trials": ranked
        }

    def _mock_save_results(self, params: Dict) -> Dict:
        """Mock save to database"""
        return {
            "saved": True,
            "patient_id": params.get("patient_id"),
            "timestamp": datetime.now().isoformat(),
            "trials_saved": len(params.get("matched_trials", []))
        }

    def _mock_get_details(self, params: Dict) -> Dict:
        """Mock trial details retrieval"""
        nct_id = params.get("nct_id")
        return {
            "nct_id": nct_id,
            "title": "Detailed Study Information",
            "description": "This is a Phase 2 clinical trial investigating...",
            "eligibility_criteria": {
                "inclusion": ["Age 18-75", "Confirmed diagnosis", "Adequate organ function"],
                "exclusion": ["Prior similar treatment", "Significant comorbidities"]
            },
            "locations": [
                {"facility": "University of Colorado Hospital", "city": "Aurora", "state": "CO", "status": "Recruiting"}
            ],
            "contacts": {
                "primary": "research@uchealth.org",
                "phone": "303-555-0100"
            }
        }

    def run_autonomous_search(self, patient_criteria: Dict) -> Dict:
        """
        Main agentic workflow - Claude autonomously plans and executes trial matching.
        """

        # Log search start
        self._log_activity('start', 'Agent initialized and starting autonomous search',
                           patient_criteria=patient_criteria)

        system_prompt = """You are an expert clinical trial matching agent. Your goal is to autonomously find, filter, and rank clinical trials for patients.

When given patient criteria, you should:
1. Search for relevant trials using search_clinical_trials
2. Check eligibility using check_eligibility
3. Rank the eligible trials using rank_trials
4. Save the results using save_search_results

Be autonomous - decide which tools to use and in what order. If you get no results, try broadening the search criteria. If you get too many results, try adding more specific filters.

Always explain your reasoning for each step so the user can see your decision-making process."""

        user_message = f"""Find clinical trials for a patient with the following criteria:

{json.dumps(patient_criteria, indent=2)}

Please autonomously search, filter, and rank trials. Show me your step-by-step reasoning."""

        messages = [{"role": "user", "content": user_message}]

        # Agentic loop - Claude continues calling tools until it's done
        iteration = 0
        max_iterations = 10  # Safety limit

        while iteration < max_iterations:
            iteration += 1

            # Log iteration start
            self._log_activity('iteration', f'Starting iteration {iteration}', iteration=iteration)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.0,  # Add this: 0=deterministic, 1=creative
                system=system_prompt,
                tools=self.get_tool_definitions(),
                messages=messages
            )

            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Claude is being agentic - calling tools autonomously
                tool_results = []

                for block in response.content:
                    if block.type == "text":
                        # Log agent's reasoning
                        self._log_activity(
                            'thinking',
                            block.text,
                            iteration=iteration
                        )

                    elif block.type == "tool_use":
                        # Execute the tool Claude chose to use
                        tool_result = self.process_tool_call(
                            block.name,
                            block.input,
                            iteration
                        )

                        # Log tool result
                        self._log_activity(
                            'tool_result',
                            f"Tool {block.name} completed",
                            tool_name=block.name,
                            result_summary=f"Returned {len(str(tool_result))} chars"
                        )

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result)
                        })

                # Add Claude's response and tool results to conversation
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            else:
                # Claude is done - no more tools to call
                self._log_activity('complete', 'Agent completed autonomous search', iterations=iteration)

                # Extract final response
                final_response = ""
                for block in response.content:
                    if block.type == "text":
                        final_response = block.text

                # Log final response
                if self.logger:
                    self.logger.log_final_response(final_response)

                return {
                    "success": True,
                    "final_response": final_response,
                    "iterations": iteration,
                    "conversation": messages,
                    "log_file": self.logger.get_log_path() if self.logger else None
                }

        # If we hit max iterations, something went wrong
        if self.logger:
            self.logger.log_error("Max iterations reached")

        return {
            "success": False,
            "error": "Max iterations reached",
            "iterations": iteration,
            "log_file": self.logger.get_log_path() if self.logger else None
        }
