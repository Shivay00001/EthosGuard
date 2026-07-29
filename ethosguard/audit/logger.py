import json
import os
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    """Logs all ethical decisions made by EthosGuard for transparency and auditability."""
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = os.path.join(log_dir, f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl")

    def log_decision(self, context: str, decision: str, reasoning: str, metadata: Dict[str, Any] = None):
        """
        Logs a decision made by EthosGuard.
        :param context: What was being evaluated (e.g., "Agent Tool Call: delete_file")
        :param decision: "ALLOW", "BLOCK", or "MODIFY"
        :param reasoning: The explanation from the Judge LLM
        :param metadata: Any additional context (prompt, inputs, etc.)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "decision": decision,
            "reasoning": reasoning,
            "metadata": metadata or {}
        }
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
