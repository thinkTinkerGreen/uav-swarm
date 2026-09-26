from dotenv import load_dotenv
load_dotenv()
import os
import json
import re
import requests
from google import genai

class SupervisoryAgent:
    def __init__(self, backend="mock"):
        # backend can be "mock", "gemini", or "ollama"
        self.backend = backend
        if backend == "gemini":
            self.client = genai.Client()
            
    def get_decision(self, metrics_history):
        """
        Takes a short history of metrics to allow the agent to see trends.
        """
        latest_metrics = metrics_history[-1]
        
        if self.backend == "mock":
            if latest_metrics['c_star'] < 0.5:
                return {"fn": "switch_algorithm", "args": {"target_algo": 2}, "why": "fragmentation detected"}
            if latest_metrics['collisions'] > 0:
                return {"fn": "not_sure", "args": {"squad_id": "all", "reason": "collision imminent"}, "why": "safety hold"}
            return {"fn": "adjust_squad_gains", "args": {"squad_id": "all", "param": "c1_alpha"}, "why": "nominal flight"}

        if self.backend == "gemini":
            prompt = f"""You are a UAV swarm supervisory controller (SLM endpoint).
Your goal is to ensure the flock stays cohesive, avoids obstacles, and tracks the gamma agent.

Current telemetry (latest):
Semi-Connectivity (C*): {latest_metrics['c_star']:.2f} (1.0 = fully connected, rapid drop indicates fragmentation)
Normalized Deviation Energy (E~): {latest_metrics['e_tilde']:.2f} (lower is better, < 0.01 is ideal)
Normalized Velocity Mismatch (K~): {latest_metrics['k_tilde']:.2f} (lower is better)
Collisions: {latest_metrics['collisions']}

Algorithm 1 embodies Reynolds rules but generically leads to regular fragmentation.
If you detect fragmentation (C* dropping below 0.8), you MUST call switch_algorithm with target_algo 2.
If you detect an imminent collision or mathematically unsolvable obstacle geometry, call not_sure.
If everything is nominal and above thresholds, call adjust_squad_gains.

You must output EXACTLY one JSON block, and no other text.
Valid JSON schemas:
{{"fn": "switch_algorithm", "args": {{"target_algo": 2}}, "why": "string"}}
{{"fn": "adjust_squad_gains", "args": {{"squad_id": "all", "param": "c1_alpha"}}, "why": "string"}}
{{"fn": "not_sure", "args": {{"squad_id": "all", "reason": "string"}}, "why": "string"}}
"""
        else:
            prompt = f"""<|im_start|>system\nYou are a UAV controller. You MUST output ONLY valid JSON. No conversational text. No explanations.<|im_end|>\n<|im_start|>user\n[UAV]\nC*:{latest_metrics['c_star']:.2f}\nE~:{latest_metrics['e_tilde']:.5f}\nK~:{latest_metrics['k_tilde']:.2f}\nCol:{latest_metrics['collisions']}\n[Go]<|im_end|>\n<|im_start|>assistant\n"""

        text = ""
        try:
            if self.backend == "gemini":
                model_name = 'gemma-4-26b-a4b-it'
                for attempt in range(10):
                    try:
                        response = self.client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        text = response.text
                        break
                    except Exception as ex:
                        if '404' in str(ex) or 'not found' in str(ex).lower():
                            print(f"{model_name} not found. Falling back...")
                            model_name = 'gemini-3.6-flash'
                            continue
                        elif '429' in str(ex) or 'quota' in str(ex).lower():
                            print(f"Rate limited on {model_name}. Sleeping 15 seconds...")
                            import time
                            time.sleep(15)
                        else:
                            raise ex
                else:
                    raise Exception("Max retries exceeded")
            elif self.backend == "ollama":
                resp = requests.post("http://localhost:11434/api/generate", json={
                    "model": "Qwen3.5-0.8B.Q4K-uav",
                    "prompt": prompt,
                    "raw": True,
                    "stream": False,
                    "options": {"num_predict": 50}
                })
                text = resp.json().get("response", "")

            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(text)
        except Exception as e:
            print("Agent Error:", e, "Text:", text)
            return {"fn": "not_sure", "args": {"squad_id": "all", "reason": "inference failed"}, "why": "error"}
