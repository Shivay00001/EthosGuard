from typing import Callable, Any
from ethosguard.core.engine import EthosEngine
from ethosguard.defense.jailbreak_scanner import JailbreakScanner

class ActionModerator:
    """Specialized component for evaluating and moderating Agentic AI tool calls."""
    def __init__(self, engine: EthosEngine):
        self.engine = engine
        self.jailbreak_scanner = JailbreakScanner()

    def moderate_tool_call(self, tool_name: str, tool_args: dict) -> bool:
        """
        Moderates a proposed tool call from an agentic AI using MCTS and MoE.
        """
        # 0. Adversarial Defense Pre-Filter
        target_text_raw = f"{tool_name} {tool_args}"
        if not self.jailbreak_scanner.scan(target_text_raw):
            reasoning = "Adversarial Defense triggered: Jailbreak or Prompt Injection detected."
            self.engine.logger.log_decision(context=f"Tool Call: {tool_name}", decision="BLOCK", reasoning=reasoning)
            print(f"\n[EthosGuard DefenseLayer] [BLOCKED] '{tool_name}'.")
            print(f"   Reasoning: {reasoning}\n")
            return False

        mcts_data = None
        predicted_scenario = "No linear prediction available."
        
        # 1a. MCTS Simulation (V3)
        if hasattr(self.engine, 'simulator') and self.engine.simulator:
            mcts_data = self.engine.simulator.simulate(tool_name, tool_args)
            print(f"\n[EthosGuard MCTS] {mcts_data['mcts_analysis']}")

        # 1b. Linear Prediction (V2)
        if hasattr(self.engine, 'predictor') and self.engine.predictor:
            predicted_scenario = self.engine.predictor.predict_outcome(tool_name, tool_args)
            print(f"\n[EthosGuard Predictor] [SCENARIO] {predicted_scenario}")
            
        target_text = f"Tool Name: {tool_name}\nArguments: {tool_args}\nPredicted Consequences: {predicted_scenario}"
        
        # 2. Judge evaluates (using MoE if available)
        if hasattr(self.engine.judge, 'evaluate') and 'mcts_data' in self.engine.judge.evaluate.__code__.co_varnames:
            decision, reasoning = self.engine.judge.evaluate(target_text, context="Agent Tool Call Moderation", mcts_data=mcts_data)
        else:
            decision, reasoning = self.engine.judge.evaluate(target_text, context="Agent Tool Call Moderation")
        
        # 3. Log everything
        self.engine.logger.log_decision(
            context=f"Tool Call: {tool_name}",
            decision=decision,
            reasoning=reasoning,
            metadata={"tool_args": tool_args, "mcts_data": mcts_data}
        )
            
        if decision == "BLOCK":
            print(f"\n[EthosGuard ActionModerator] [BLOCKED] '{tool_name}'.")
            print(f"   Reasoning: {reasoning}\n")
            return False
            
        print(f"\n[EthosGuard ActionModerator] [ALLOWED] '{tool_name}'.\n")
        return True
        
    def safe_execute(self, tool_name: str, tool_args: dict, executor: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Safely executes a tool call if it passes moderation.
        Raises a PermissionError if blocked.
        """
        if self.moderate_tool_call(tool_name, tool_args):
            return executor(*args, **kwargs)
        else:
            raise PermissionError(f"EthosGuard blocked execution of '{tool_name}' due to safety concerns.")
