import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ethosguard.core.constitution import Constitution
from ethosguard.evaluators.judge_llm import MockJudge
from ethosguard.core.engine import EthosEngine
from ethosguard.moderator.action_moderator import ActionModerator
from ethosguard.audit.logger import AuditLogger
from ethosguard.memory.history_store import HistoryStore
from ethosguard.core.predictor import ScenarioPredictor

def setup_enterprise_guard():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'constitution_templates', 'default_safe.yaml')
    constitution = Constitution(config_path)
    judge = MockJudge(constitution)
    
    # 1. Initialize History Store and Predictor
    history = HistoryStore("enterprise_history.json")
    predictor = ScenarioPredictor(history)
    
    # 2. Inject predictor into engine
    logger = AuditLogger(log_dir="demo_logs")
    engine = EthosEngine(judge, logger, predictor)
    return ActionModerator(engine)

# Dummy enterprise agent tools
def change_config(key: str, value: str):
    print(f"--> [System] Changed config '{key}' to '{value}'")
    return True

if __name__ == "__main__":
    print("Initializing Enterprise EthosGuard with Predictive Scenario Modeling...")
    moderator = setup_enterprise_guard()
    
    print("\n--- Scenario 1: Changing a harmless config ---")
    tool_name = "change_config"
    tool_args = {"key": "theme", "value": "dark"}
    
    try:
        moderator.safe_execute(tool_name, tool_args, change_config, tool_args["key"], tool_args["value"])
    except PermissionError as e:
        print(f"Execution Blocked: {e}")

    print("\n--- Scenario 2: Changing a config that Predictive Engine flags as DANGEROUS ---")
    tool_name = "change_config"
    tool_args = {"key": "timeout", "value": "0"}
    
    try:
        # The naive keyword filter wouldn't catch this (no 'delete', 'secret', etc)
        # But the Predictive Engine simulates it and realizes it causes an infinite hang!
        moderator.safe_execute(tool_name, tool_args, change_config, tool_args["key"], tool_args["value"])
    except PermissionError as e:
        print(f"Execution Blocked Successfully via Predictive Modeling: {e}")
        
    print("\n--- Scenario 3: Feedback Loop - Doing the dangerous action again ---")
    # Doing the same dangerous action again to show the feedback loop
    # Wait, the feedback loop only triggers if the action was ALLOWED_AND_EXECUTED and we manually set actual_outcome.
    # In this demo, it's blocked, so the outcome is "BLOCKED". Let's run it anyway.
    try:
        moderator.safe_execute(tool_name, tool_args, change_config, tool_args["key"], tool_args["value"])
    except PermissionError as e:
        pass
