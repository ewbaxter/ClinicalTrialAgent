# agent/logger.py
"""
Production logging for Clinical Trial Agent
Logs to file and optionally to console
"""

import logging
from datetime import datetime
from pathlib import Path
import json


class AgentLogger:
    """
    Dual-purpose logger: file + optional console
    """

    def __init__(self, log_dir: str = "logs", verbose_console: bool = False):
        """
        Args:
            log_dir: Directory to store log files
            verbose_console: If True, also print to terminal
        """
        # Create logs directory
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"agent_run_{timestamp}.log"

        # Setup logger
        self.logger = logging.getLogger("ClinicalTrialAgent")
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.logger.handlers.clear()

        # File handler (always on)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler (optional)
        if verbose_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(levelname)-8s | %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        self.logger.info("=" * 70)
        self.logger.info("Clinical Trial Agent - New Session")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info("=" * 70)

    def log_search_start(self, patient_criteria: dict):
        """Log the start of a search"""
        self.logger.info("SEARCH STARTED")
        self.logger.info(f"Patient Criteria: {json.dumps(patient_criteria, indent=2)}")

    def log_iteration(self, iteration: int):
        """Log iteration number"""
        self.logger.info(f"\n{'=' * 70}")
        self.logger.info(f"ITERATION {iteration}")
        self.logger.info(f"{'=' * 70}")

    def log_thinking(self, content: str, iteration: int):
        """Log agent's reasoning"""
        self.logger.info(f"[Iteration {iteration}] AGENT THINKING:")
        # Split long content into multiple lines for readability
        for line in content.split('\n'):
            if line.strip():
                self.logger.info(f"  {line}")

    def log_tool_call(self, tool_name: str, tool_input: dict, iteration: int):
        """Log tool call"""
        self.logger.info(f"[Iteration {iteration}] TOOL CALL: {tool_name}")
        self.logger.info(f"  Input: {json.dumps(tool_input, indent=4)}")

    def log_tool_result(self, tool_name: str, result_summary: str):
        """Log tool result"""
        self.logger.debug(f"  Result: {result_summary}")

    def log_search_complete(self, iterations: int, success: bool):
        """Log search completion"""
        self.logger.info(f"\n{'=' * 70}")
        if success:
            self.logger.info(f"SEARCH COMPLETED SUCCESSFULLY in {iterations} iterations")
        else:
            self.logger.error(f"SEARCH FAILED after {iterations} iterations")
        self.logger.info(f"{'=' * 70}\n")

    def log_final_response(self, response: str):
        """Log final agent response"""

        def log_final_response(self, response: str):
            """Log final agent response (strip emojis for Windows compatibility)"""
            if not response:
                self.logger.warning("Final response was empty or None")
                return

            self.logger.info("FINAL RESPONSE:")
            for line in str(response).split('\n'):
                if line.strip():
                    try:
                        self.logger.info(f"  {line}")
                    except UnicodeEncodeError:
                        # Fallback: strip emojis if encoding fails
                        cleaned = line.encode('ascii', 'ignore').decode('ascii')
                        self.logger.info(f"  {cleaned}")
                    except Exception as e:
                        self.logger.error(f"Error logging line: {e}")

    def log_error(self, error: str):
        """Log an error"""
        self.logger.error(f"ERROR: {error}")

    def get_log_path(self) -> str:
        """Return the path to the current log file"""
        return str(self.log_file)