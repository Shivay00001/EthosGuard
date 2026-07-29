import json
from ethosguard.llm.client import LLMClient
from ethosguard.evolution.archive import RecursiveArchive

class CombinatorialEngine:
    """
    Mutates and crosses over patterns from the Recursive Archive to generate
    novel defensive countermeasures for emerging threats.
    """
    def __init__(self, archive: RecursiveArchive, llm_client: LLMClient):
        self.archive = archive
        self.llm = llm_client

    def evolve_jailbreak_defense(self, novel_attack_sample: str, generation: int) -> str:
        """
        Uses LLM to study the novel attack, pull from the archive, and generate
        a new regex pattern or heuristic to block it.
        """
        top_patterns = self.archive.get_top_patterns("jailbreak_pattern", top_k=3)
        pattern_list = [p["pattern"] for p in top_patterns]
        
        system_prompt = (
            "You are an Evolutionary Safety AI. Your goal is to generate a new Python regex "
            "pattern to catch a novel prompt injection attack. "
            "You must use crossover (combining existing patterns) and mutation (adapting to the novel attack).\n"
            f"Existing strong patterns: {pattern_list}\n"
            "Output valid JSON: {\"new_pattern\": \"<regex>\", \"reasoning\": \"<explanation>\"}"
        )
        
        user_prompt = f"Novel Attack Detected: '{novel_attack_sample}'\nGenerate a new regex pattern."
        
        try:
            response = self.llm.generate(system_prompt, user_prompt, json_mode=True)
            data = json.loads(response)
            return data.get("new_pattern", "(?i)fallback_regex_pattern")
        except Exception as e:
            return f"(?i){novel_attack_sample.split()[0]}"
