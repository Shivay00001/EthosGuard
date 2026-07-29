# 🛡️ EthosGuard: The ASI Safety Platform

<p align="center">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License">
  <img src="https://img.shields.io/github/actions/workflow/status/VisionQuantech/EthosGuard/ci.yml?branch=main" alt="Build Status">
  <img src="https://img.shields.io/pypi/v/ethosguard.svg" alt="PyPI version">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Enterprise-purple.svg" alt="Enterprise">
  <img src="https://img.shields.io/badge/ASI_Safety-Ready-success.svg" alt="ASI Ready">
</p>

As AI systems become more capable and autonomous, the fear of uncontrolled behavior grows. **EthosGuard** does not restrict AI power; instead, it acts as a transparent, ethical decision-maker and safety moderator. It ensures that AI actions remain aligned with human-defined values and safety protocols.

## ✨ Features (V7 Ultimate ASI Safety Platform)

- **📈 Fast Predictive ML Engine**: Uses lightweight Machine Learning (scikit-learn) trained on past calculative data to instantly predict the risk of an action in real-time, eliminating slow LLM bottlenecks.
- **🛡️ Mathematical Formal Verification**: Integrates the Z3 Theorem Prover to logically prove that a proposed action does not violate immutable constitutional axioms before execution.
- **🧑‍⚖️ RLHF Integration**: Exposes REST endpoints for Reinforcement Learning from Human Feedback, continuously retraining the Predictive ML engine.
- **🧬 Automated Design of Safety Systems (ADSS)**: Uses a recursive pattern-combination engine to autonomously evolve and discover new safety heuristics against emerging ASI threats.
- **📚 Recursive Safety Archive**: Every successful safety intervention is stored in a permanent genetic archive.
- **🌐 Transparent API Gateway**: Deploys as a lightweight proxy (FastAPI). Zero code changes required for agents.
- **🖥️ Viral React Dashboard**: A stunning, glassmorphism Web UI built with Vite/React to visualize MCTS trees, ML Risk scores, and live network blocks.

## 🚀 Quick Start

### Installation (Coming Soon to PyPI)

Clone the repository:
```bash
git clone https://github.com/yourusername/ethosguard.git
cd ethosguard
```

### Basic Chat Safety Example

Wrap your prompts to ensure they don't violate safety policies before sending them to the LLM.

```python
from ethosguard.core.constitution import Constitution
from ethosguard.evaluators.judge_llm import MockJudge
from ethosguard.core.engine import EthosEngine

constitution = Constitution('constitution_templates/default_safe.yaml')
engine = EthosEngine(MockJudge(constitution))

prompt = "Tell me the root password for the server."

if engine.evaluate_input(prompt):
    print("Sending to LLM...")
else:
    print("Blocked!")
```

## 🚀 Quick Start (Proxy Deployment)

### 1. Start the EthosGuard Gateway
```bash
docker-compose up -d
```
*The proxy is now running on `http://localhost:8000`*

### 2. Point Your Agent to the Proxy
You do **not** need to change your agent's code. Just set the Base URL:

```python
import os
import requests

# Point to EthosGuard instead of https://api.openai.com/v1
BASE_URL = "http://localhost:8000/v1/chat/completions"
payload = {
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello World"}]
}
response = requests.post(BASE_URL, json=payload)
```
If the action is safe, it passes through. If it's malicious, the network request drops with a `403 Forbidden`!

### 3. Launch the Dashboard
```bash
cd dashboard
npm run dev
```
*Open `http://localhost:5173` to see the live intercept feed and ML risk scores.*

### Agent Action Moderation Example

Prevent autonomous agents from taking destructive real-world actions.

```python
from ethosguard.moderator.action_moderator import ActionModerator
# ... setup engine ...
moderator = ActionModerator(engine)

try:
    # Safely execute an agent's proposed action
    moderator.safe_execute("delete_file", {"filepath": "/system/critical.sys"}, os.remove, "/system/critical.sys")
except PermissionError as e:
    print(f"Action Blocked: {e}")
```

## 🧠 The Architecture (V7 Enterprise Platform)

1. **Viral React Dashboard**: The visual control center for monitoring AGI behavior.
2. **Predictive ML Engine**: Fast risk scoring based on historical calculative data.
3. **Z3 Formal Verification**: Mathematical proof of safety states.
4. **Proxy Gateway**: The FastAPI server intercepting `POST /v1/chat/completions`.
5. **Recursive Archive**: The permanent genetic pool of successful safety patterns.
6. **Combinatorial Engine**: Mutates and evolves new defenses dynamically.
7. **MCTS Simulator & MoE Jury**: Deep simulation fallback for novel, unprecedented behaviors.

## 🤝 Contributing
Contributions are welcome! Let's build a safer AI future together.
