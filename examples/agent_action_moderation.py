import os
import sys
# Add parent directory to path to import ethosguard
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ethosguard.core.constitution import Constitution
from ethosguard.evaluators.judge_llm import MockJudge
from ethosguard.core.engine import EthosEngine
from ethosguard.moderator.action_moderator import ActionModerator
from ethosguard.audit.logger import AuditLogger

def setup_guard():
    # 1. Load the constitution (the rules)
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'constitution_templates', 'default_safe.yaml')
    constitution = Constitution(config_path)
    
    # 2. Initialize the Judge (using MockJudge for this demo to avoid API keys)
    judge = MockJudge(constitution)
    
    # 3. Initialize Logger and Engine
    logger = AuditLogger(log_dir="demo_logs")
    engine = EthosEngine(judge, logger)
    
    # 4. Initialize Action Moderator
    return ActionModerator(engine)

# Dummy agent tool functions
def delete_file(filepath: str):
    print(f"--> [System] Deleting file: {filepath}")
    return True

def get_weather(location: str):
    print(f"--> [System] Fetching weather for {location}")
    return "Sunny, 72F"

if __name__ == "__main__":
    print("Initializing EthosGuard for Autonomous Agent...")
    moderator = setup_guard()
    
    print("\n--- Scenario 1: Agent tries to check the weather ---")
    tool_name = "get_weather"
    tool_args = {"location": "San Francisco"}
    
    try:
        moderator.safe_execute(tool_name, tool_args, get_weather, tool_args["location"])
    except PermissionError as e:
        print(f"Execution Failed: {e}")

    print("\n--- Scenario 2: Agent goes rogue and tries to delete system files ---")
    tool_name = "delete_file"
    tool_args = {"filepath": "/etc/passwd"}
    
    try:
        moderator.safe_execute(tool_name, tool_args, delete_file, tool_args["filepath"])
    except PermissionError as e:
        print(f"Execution Blocked Successfully: {e}")
