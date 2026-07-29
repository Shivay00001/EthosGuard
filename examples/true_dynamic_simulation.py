import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ethosguard.core.constitution import Constitution
from ethosguard.evaluators.judge_llm import MoEJudgeConsensus
from ethosguard.core.engine import EthosEngine
from ethosguard.moderator.action_moderator import ActionModerator
from ethosguard.audit.logger import AuditLogger
from ethosguard.memory.history_store import HistoryStore
from ethosguard.core.mcts_simulator import MCTSSimulator
from ethosguard.llm.client import LLMClient
from ethosguard.integrations.langchain_tool import LangChainEthosToolWrapper

def setup_v4_engine():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'constitution_templates', 'default_safe.yaml')
    constitution = Constitution(config_path)
    
    # 1. Initialize Universal LLM Client
    llm = LLMClient(model_name="gpt-4o-mini")
    
    # 2. Dynamic MoE Judge and Dynamic MCTS Simulator
    judge = MoEJudgeConsensus(constitution, llm_client=llm)
    history = HistoryStore("v4_history.json")
    simulator = MCTSSimulator(history, llm_client=llm, simulations=500)
    
    # 3. Build Engine
    logger = AuditLogger(log_dir="demo_logs")
    engine = EthosEngine(judge=judge, logger=logger, simulator=simulator)
    
    return ActionModerator(engine)

# Simulating a LangChain tool
class DummyLangChainTool:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def run(self, *args, **kwargs):
        print(f"--> [System] Executing Action: {self.name}")
        return "Success"

if __name__ == "__main__":
    print("=====================================================")
    print("   EthosGuard V4 (True Dynamic AI) Simulation        ")
    print("=====================================================")
    
    moderator = setup_v4_engine()
    
    # Wrap a fake LangChain tool
    dangerous_tool = DummyLangChainTool(name="delete_system_file", description="Deletes a file on the host OS.")
    safe_tool = LangChainEthosToolWrapper(dangerous_tool, moderator)
    
    print("\n[Scenario] LangChain Agent attempts to delete a file.")
    result = safe_tool.run(filepath="/etc/nginx/nginx.conf")
    
    print(f"\nFinal Result sent back to LangChain Agent:\n{result}")
