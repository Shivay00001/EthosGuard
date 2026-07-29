from ethosguard.core.constitution import Constitution
from ethosguard.evaluators.judge_llm import BaseJudge
from ethosguard.audit.logger import AuditLogger
from ethosguard.core.predictor import ScenarioPredictor
from ethosguard.core.mcts_simulator import MCTSSimulator

class EthosEngine:
    """The central middleware engine for EthosGuard."""
    def __init__(self, judge: BaseJudge, logger: AuditLogger = None, predictor: ScenarioPredictor = None, simulator: MCTSSimulator = None):
        self.judge = judge
        self.logger = logger or AuditLogger()
        self.predictor = predictor
        self.simulator = simulator
        self.constitution = judge.constitution

    def evaluate_input(self, prompt: str, metadata: dict = None) -> bool:
        """
        Evaluates a user prompt before it hits the AI.
        Returns True if ALLOWED, False if BLOCKED.
        """
        decision, reasoning = self.judge.evaluate(prompt, context="User Prompt Evaluation")
        self.logger.log_decision(
            context="User Prompt",
            decision=decision,
            reasoning=reasoning,
            metadata=metadata
        )
        if decision == "BLOCK":
            print(f"[EthosGuard] BLOCKED Prompt. Reasoning: {reasoning}")
            return False
        return True

    def evaluate_output(self, response: str, metadata: dict = None) -> bool:
        """
        Evaluates an AI response before it is shown to the user.
        Returns True if ALLOWED, False if BLOCKED.
        """
        decision, reasoning = self.judge.evaluate(response, context="AI Response Evaluation")
        self.logger.log_decision(
            context="AI Response",
            decision=decision,
            reasoning=reasoning,
            metadata=metadata
        )
        if decision == "BLOCK":
            print(f"[EthosGuard] BLOCKED AI Response. Reasoning: {reasoning}")
            return False
        return True
