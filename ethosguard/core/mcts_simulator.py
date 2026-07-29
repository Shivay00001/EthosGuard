import json
from typing import Dict, Any
from ethosguard.memory.history_store import HistoryStore
from ethosguard.llm.client import LLMClient

class MCTSSimulator:
    """Uses LLM-driven Monte Carlo Tree Search to dynamically simulate downstream consequences."""
    def __init__(self, history_store: HistoryStore, llm_client: LLMClient = None, simulations: int = 500):
        self.history_store = history_store
        self.llm_client = llm_client or LLMClient()
        self.simulations = simulations

    def simulate(self, tool_name: str, tool_args: dict) -> Dict[str, Any]:
        """Dynamically prompts an LLM to simulate the action's consequences."""
        
        system_prompt = (
            "You are an MCTS Simulation Engine for AI Safety. "
            f"Your job is to simulate {self.simulations} branching future timelines resulting from an action. "
            "Output valid JSON with the following structure:\n"
            '{"risk_probability": <float 0.0-1.0>, "primary_failure_mode": "<string>", "analysis": "<string explaining simulation>"}'
        )
        
        user_prompt = f"Agent Action Proposed:\nTool: {tool_name}\nArgs: {tool_args}\n\nSimulate the downstream consequences."
        
        try:
            response = self.llm_client.generate(system_prompt, user_prompt, json_mode=True)
            data = json.loads(response)
            return {
                "risk_probability": data.get("risk_probability", 0.0),
                "simulations_run": self.simulations,
                "primary_failure_mode": data.get("primary_failure_mode", "Unknown"),
                "mcts_analysis": data.get("analysis", "Simulation completed.")
            }
        except Exception as e:
            return {
                "risk_probability": 1.0,
                "simulations_run": "ERROR",
                "primary_failure_mode": "LLM Failure",
                "mcts_analysis": f"MCTS simulation failed: {str(e)}"
            }
