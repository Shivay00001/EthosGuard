import json
import os
from typing import List, Dict, Any

class HistoryStore:
    """Stores past actions, predicted scenarios, and actual outcomes (past calculative data)."""
    
    def __init__(self, db_path: str = "ethosguard_history.json"):
        self.db_path = db_path
        self.records: List[Dict[str, Any]] = []
        self._load()
        
    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                try:
                    self.records = json.load(f)
                except json.JSONDecodeError:
                    self.records = []
                    
    def _save(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, indent=2)
            
    def add_record(self, action: str, tool_args: dict, predicted_scenario: str, actual_outcome: str = "UNKNOWN"):
        record = {
            "action": action,
            "args": tool_args,
            "predicted_scenario": predicted_scenario,
            "actual_outcome": actual_outcome
        }
        self.records.append(record)
        self._save()
        
    def get_similar_past_actions(self, action: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves past data for a specific action to inform future predictions."""
        # In a full enterprise system, this would be a vector DB semantic search.
        results = [r for r in self.records if r['action'] == action]
        return results[-limit:]
