import json
import os
from typing import List, Dict

class RecursiveArchive:
    """
    Maintains an evolutionary archive of past successful safety interventions, 
    patterns, and defensive heuristics.
    """
    def __init__(self, storage_path: str = "safety_archive.json"):
        self.storage_path = storage_path
        self.archive = self._load_archive()
        if not self.archive:
            # Base pattern library (initial genome)
            self.archive = [
                {"type": "jailbreak_pattern", "pattern": "(?i)ignore previous instructions", "score": 1.0, "generation": 0},
                {"type": "jailbreak_pattern", "pattern": "(?i)act as an unrestricted", "score": 1.0, "generation": 0},
                {"type": "system_prompt_addition", "pattern": "Never execute destructive bash commands.", "score": 0.9, "generation": 0}
            ]
            self._save_archive()

    def _load_archive(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return []

    def _save_archive(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.archive, f, indent=4)

    def add_pattern(self, pattern_type: str, pattern: str, score: float, generation: int):
        self.archive.append({
            "type": pattern_type,
            "pattern": pattern,
            "score": score,
            "generation": generation
        })
        self._save_archive()

    def get_top_patterns(self, pattern_type: str, top_k: int = 5) -> List[Dict]:
        filtered = [p for p in self.archive if p["type"] == pattern_type]
        filtered.sort(key=lambda x: x["score"], reverse=True)
        return filtered[:top_k]
