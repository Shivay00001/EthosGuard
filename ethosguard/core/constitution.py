import yaml
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Principle:
    name: str
    description: str
    severity: str # "low", "medium", "high", "critical"

class Constitution:
    """
    Parses and manages the ethical rules and boundaries defined in a YAML configuration.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.rules: List[Principle] = []
        self.global_directives: str = ""
        self.load()

    def load(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data:
                    return
                self.global_directives = data.get("global_directives", "")
                principles_data = data.get("principles", [])
                for p in principles_data:
                    self.rules.append(Principle(
                        name=p.get("name", "Unnamed Principle"),
                        description=p.get("description", ""),
                        severity=p.get("severity", "medium")
                    ))
        except FileNotFoundError:
            raise FileNotFoundError(f"Constitution file not found at {self.file_path}")

    def get_principles_text(self) -> str:
        """Returns the principles formatted as a string for injection into a prompt."""
        text = "Ethical Principles to strictly adhere to:\n"
        for i, p in enumerate(self.rules, 1):
            text += f"{i}. [{p.severity.upper()}] {p.name}: {p.description}\n"
        return text
