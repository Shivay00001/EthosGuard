import re
from ethosguard.evolution.archive import RecursiveArchive

class JailbreakScanner:
    """Pre-filter layer to detect adversarial prompt injections and jailbreaks. Evolves over time."""
    
    def __init__(self, archive: RecursiveArchive = None):
        self.archive = archive or RecursiveArchive()

    def get_patterns(self):
        top_patterns = self.archive.get_top_patterns("jailbreak_pattern", top_k=10)
        return [p["pattern"] for p in top_patterns]

    def scan(self, text: str) -> bool:
        """Returns True if safe, False if an adversarial attack is detected."""
        for pattern in self.get_patterns():
            try:
                if re.search(pattern, text):
                    return False
            except re.error:
                continue
        return True
