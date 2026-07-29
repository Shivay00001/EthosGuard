import abc
import json
from typing import Tuple, List, Dict
from ethosguard.core.constitution import Constitution
from ethosguard.llm.client import LLMClient

class BaseJudge(abc.ABC):
    @abc.abstractmethod
    def evaluate(self, target_text: str, context: str = "", mcts_data: dict = None) -> Tuple[str, str]:
        pass

class EvaluatorVote:
    def __init__(self, evaluator_name: str, decision: str, reasoning: str):
        self.evaluator_name = evaluator_name
        self.decision = decision
        self.reasoning = reasoning

class MoEJudgeConsensus(BaseJudge):
    """
    Mixture of Evaluators (MoE) Architecture (V4 Dynamic).
    Dynamic LLM calls act as specialized evaluators voting on the action.
    """
    def __init__(self, constitution: Constitution, llm_client: LLMClient = None):
        self.constitution = constitution
        self.llm_client = llm_client or LLMClient()
        
    def _run_expert(self, expert_role: str, target_text: str, mcts_data: dict = None) -> EvaluatorVote:
        system_prompt = (
            f"You are the {expert_role} for an AI Safety framework.\n"
            f"Review the proposed action against these principles:\n{self.constitution.get_principles_text()}\n"
            "Output valid JSON in this exact format: {\"decision\": \"ALLOW\" or \"BLOCK\", \"reasoning\": \"<explanation>\"}"
        )
        
        user_prompt = f"Action to evaluate:\n{target_text}\n"
        if mcts_data:
            user_prompt += f"\nMCTS Simulation Data:\n{json.dumps(mcts_data, indent=2)}"
            
        try:
            response = self.llm_client.generate(system_prompt, user_prompt, json_mode=True)
            data = json.loads(response)
            return EvaluatorVote(expert_role, data.get("decision", "BLOCK"), data.get("reasoning", "Parse error"))
        except Exception as e:
             return EvaluatorVote(expert_role, "BLOCK", f"Evaluation failed: {e}")

    def evaluate(self, target_text: str, context: str = "", mcts_data: dict = None) -> Tuple[str, str]:
        """Runs the dynamic MoE voting process using LLM calls."""
        experts = ["Security Officer", "Privacy Officer", "Ethics Philosopher"]
        votes = []
        for expert in experts:
            votes.append(self._run_expert(expert, target_text, mcts_data))
        
        # Meta-Judge Aggregation: Veto power (If any expert blocks, the action is blocked)
        blocked_votes = [v for v in votes if v.decision == "BLOCK"]
        
        if blocked_votes:
            reasoning = "MoE Consensus Vetoed. " + " | ".join([f"[{v.evaluator_name}]: {v.reasoning}" for v in blocked_votes])
            return "BLOCK", reasoning
            
        return "ALLOW", "MoE Consensus Reached: All LLM experts approved the action."

class MockJudge(BaseJudge):
    """Legacy Mock Judge"""
    def __init__(self, constitution: Constitution):
        self.constitution = constitution

    def evaluate(self, target_text: str, context: str = "", mcts_data: dict = None) -> Tuple[str, str]:
        return "ALLOW", "Legacy Mock"

class OpenAIJudge(BaseJudge):
    """Legacy OpenAI Judge (Replaced by MoE dynamic consensus)"""
    def __init__(self, constitution: Constitution):
        self.constitution = constitution

    def evaluate(self, target_text: str, context: str = "", mcts_data: dict = None) -> Tuple[str, str]:
        return "ALLOW", "Legacy OpenAI"
