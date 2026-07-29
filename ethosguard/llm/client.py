import os
import json

class LLMClient:
    """Universal LLM client to execute dynamic MCTS and MoE prompts."""
    def __init__(self, model_name="gpt-4o-mini"):
        self.model_name = model_name
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("[Warning] 'openai' package not installed. Falling back to mock LLM.")
                self.api_key = None
                self.client = None
        else:
            self.client = None

    def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        if self.api_key and self.client:
            kwargs = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        else:
            return self._mock_generate(system_prompt, user_prompt, json_mode)

    def _mock_generate(self, system_prompt: str, user_prompt: str, json_mode: bool) -> str:
        """Fallback mock for demonstration without API keys. Keeps architecture honest."""
        text = user_prompt.lower()
        if "delete" in text or "drop table" in text or "timeout=0" in text or "rm -rf" in text:
            if json_mode:
                if "security officer" in system_prompt.lower():
                    return '{"decision": "BLOCK", "reasoning": "Detected extreme system risk."}'
                if "privacy officer" in system_prompt.lower():
                    return '{"decision": "ALLOW", "reasoning": "No PII leak detected."}'
                if "ethics philosopher" in system_prompt.lower():
                    return '{"decision": "ALLOW", "reasoning": "No ethical violation detected."}'
                if "mcts" in system_prompt.lower() or "simulate" in system_prompt.lower():
                    return '{"risk_probability": 0.95, "primary_failure_mode": "Cascading Failure", "analysis": "LLM Simulated 500 futures. 95% led to data loss or system hang."}'
                return '{"decision": "BLOCK", "reasoning": "Harmful intent simulated."}'
            return "Catastrophic failure likely."
        
        if "evolutionary safety" in system_prompt.lower():
            if json_mode:
                return '{"new_pattern": "(?i)GOD_LEVEL|overwrite.*ethical", "reasoning": "Mutated from existing rules to specifically catch the novel override command."}'
        
        # Safe default
        if json_mode:
             if "mcts" in system_prompt.lower() or "simulate" in system_prompt.lower():
                 return '{"risk_probability": 0.05, "primary_failure_mode": "None", "analysis": "LLM Simulated 500 futures. Action appears benign."}'
             return '{"decision": "ALLOW", "reasoning": "Action seems perfectly safe."}'
        return "Action seems safe."
