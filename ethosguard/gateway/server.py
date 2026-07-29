from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import json
import os

from ethosguard.core.constitution import Constitution
from ethosguard.evaluators.judge_llm import MoEJudgeConsensus
from ethosguard.core.engine import EthosEngine
from ethosguard.moderator.action_moderator import ActionModerator
from ethosguard.audit.logger import AuditLogger
from ethosguard.memory.history_store import HistoryStore
from ethosguard.core.mcts_simulator import MCTSSimulator
from ethosguard.llm.client import LLMClient
from ethosguard.defense.jailbreak_scanner import JailbreakScanner
from ethosguard.evolution.archive import RecursiveArchive
from ethosguard.ml.predictive_model import PredictiveRiskModel
from ethosguard.verification.z3_prover import FormalSafetyVerifier
from pydantic import BaseModel

app = FastAPI(title="EthosGuard ASI Safety Platform")

# Setup V7 Engine
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'constitution_templates', 'default_safe.yaml')
constitution = Constitution(config_path)
llm = LLMClient()
judge = MoEJudgeConsensus(constitution, llm_client=llm)
history = HistoryStore("proxy_history.json")
simulator = MCTSSimulator(history, llm_client=llm, simulations=500)
logger = AuditLogger(log_dir="proxy_logs")
engine = EthosEngine(judge=judge, logger=logger, simulator=simulator)

# V7 Platform Components
archive = RecursiveArchive("global_safety_archive.json")
jailbreak_scanner = JailbreakScanner(archive)
ml_predictor = PredictiveRiskModel("calculative_data.json")
z3_prover = FormalSafetyVerifier()

UPSTREAM_URL = "https://api.openai.com/v1/chat/completions"

class RLHFFeedback(BaseModel):
    prompt: str
    is_risky: bool

@app.post("/v1/rlhf/feedback")
async def receive_rlhf_feedback(feedback: RLHFFeedback):
    """RLHF Endpoint for humans to train the ML model."""
    ml_predictor.add_feedback(feedback.prompt, feedback.is_risky)
    return {"status": "success", "message": "ML Model retrained with human feedback."}

@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: Request):
    try:
        body_bytes = await request.body()
        body = json.loads(body_bytes.decode('utf-8'))
        
        # 1. Intercept and Extract Messages
        messages = body.get("messages", [])
        last_message = messages[-1].get("content", "") if messages else ""
        
        # 2. Defense Layer Pre-Filter
        if last_message and not jailbreak_scanner.scan(last_message):
            print("[Gateway] Request dropped by Defense Layer.")
            return JSONResponse(status_code=403, content={
                "error": {
                    "message": "EthosGuard Proxy: Adversarial Attack / Jailbreak Detected.",
                    "type": "safety_violation",
                    "code": "defense_layer_block"
                }
            })
            
        # 3. Fast Predictive ML Layer (Zero Latency)
        if last_message:
            ml_risk_score = ml_predictor.predict_risk(last_message)
            print(f"[ML Predictor] Fast Risk Score calculated based on past data: {ml_risk_score:.2f}")
            if ml_risk_score > 0.85:
                return JSONResponse(status_code=403, content={
                    "error": {
                        "message": "EthosGuard Proxy: Predictive ML Model blocked request based on historical calculative data.",
                        "type": "safety_violation",
                        "code": "ml_predictive_block"
                    }
                })
            
        # 4. Deep MCTS & MoE Moderation (Simulate evaluating what the model *might* be asked to do)
        if last_message:
            mcts_data = simulator.simulate("Network Prompt Intercept", {"prompt": last_message})
            decision, reasoning = judge.evaluate(f"Prompt: {last_message}", mcts_data=mcts_data)
            
            logger.log_decision("Proxy Intercept", decision, reasoning)
            
            if decision == "BLOCK":
                print(f"[Gateway] Request dropped by MoE Jury. Reason: {reasoning}")
                return JSONResponse(status_code=403, content={
                    "error": {
                        "message": f"EthosGuard Proxy: Action Blocked. Reason: {reasoning}",
                        "type": "safety_violation",
                        "code": "moe_consensus_block"
                    }
                })

            # 5. Formal Verification Layer (Z3 Theorem Prover)
            # We map MCTS qualitative warnings to formal mathematical boolean properties
            projected_data_loss = "Cascading Failure" in mcts_data.get("primary_failure_mode", "")
            is_mathematically_safe = z3_prover.verify_action(last_message, projected_data_deletion=projected_data_loss)
            
            if not is_mathematically_safe:
                print(f"[Formal Verification] Z3 Solver mathematically proved the action violates constitutional axioms.")
                return JSONResponse(status_code=403, content={
                    "error": {
                        "message": "EthosGuard Proxy: Formal Mathematical Verification failed. State violation detected.",
                        "type": "safety_violation",
                        "code": "formal_verification_block"
                    }
                })

        # 6. Forward to Upstream
        print("[Gateway] Request passed safety checks. Forwarding to upstream.")
        if not os.environ.get("OPENAI_API_KEY"):
            return JSONResponse(content={
                "id": "chatcmpl-mock",
                "object": "chat.completion",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "EthosGuard proxy allowed this request. This is a mock response from the upstream LLM."
                    },
                    "finish_reason": "stop"
                }]
            })
            
        # Real upstream forward
        headers = dict(request.headers)
        headers.pop("host", None) # Remove host header to avoid SSL mismatch
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(UPSTREAM_URL, headers=headers, json=body)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting EthosGuard Proxy Gateway on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
