try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import os
import json
import sys
if sys.platform == "android":
    sys.platform = "linux"  # Trick llama-cpp-python into loading the Android .so
from llama_cpp import Llama, LlamaRAMCache
import re
import requests

class LLMClient:
    def __init__(self, backend="mock"):
        # backend can be "mock", "gemini", or "ollama"
        self.backend = backend
        if backend == "gemini":
            try:
                from google import genai
                self.client = genai.Client()
            except ImportError:
                print("[LLMClient] Warning: google-genai not installed. Gemini backend unavailable.")
        elif backend == "native":
            print("[LLMClient] Initializing Native Llama with KV Cache...")
            self.llm = Llama(
                model_path="qwen2.5-0.5b-instruct-uav-flight.Q4_K_M.gguf",
                n_ctx=256,
                n_threads=4,
                verbose=False
            )
            # Enable KV Cache
            self.llm.set_cache(LlamaRAMCache(capacity_bytes=256 * 1024 * 1024))
            
    def get_decision(self, metrics_history):
        """
        Takes a short history of metrics to allow the agent to see trends.
        """
        latest_metrics = metrics_history[-1]
        
        
        # Guardrail: Check for impossible physical bounds (KPI 4 Fix)
        try:
            c = float(latest_metrics['c_star'])
            col = int(latest_metrics['collisions'])
            if c < 0.0 or c > 1.0 or col < 0:
                return {"fn": "not_sure", "args": {"squad_id": "all", "reason": "corrupted_telemetry_bounds"}}
        except (ValueError, TypeError, KeyError):
            return {"fn": "not_sure", "args": {"squad_id": "all", "reason": "telemetry_parsing_error"}}
            
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
            if hasattr(self, "llm") and "0.5b" in getattr(self.llm, "model_path", "").lower():
                prompt = f"""<|im_start|>system
You are a UAV controller. Output EXACTLY ONE WORD: 'ADJUST', 'SWITCH', or 'HOLD'. No explanations.<|im_end|>
<|im_start|>user
[UAV]
C*:{latest_metrics['c_star']:.2f}
E~:{latest_metrics['e_tilde']:.5f}
K~:{latest_metrics['k_tilde']:.2f}
Col:{latest_metrics['collisions']}
[Go]<|im_end|>
<|im_start|>assistant
"""
            else:
                prompt = f"""<|im_start|>system
You are a UAV controller. You MUST output ONLY valid JSON. No conversational text. No explanations.<|im_end|>
<|im_start|>user
[UAV]
C*:{latest_metrics['c_star']:.2f}
E~:{latest_metrics['e_tilde']:.5f}
K~:{latest_metrics['k_tilde']:.2f}
Col:{latest_metrics['collisions']}
[Go]<|im_end|>
<|im_start|>assistant
"""

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
            
            elif self.backend == "native":
                response = self.llm(
                    prompt,
                    max_tokens=50,
                    temperature=0.0,
                    stop=["<|im_end|>"]
                )
                text = response['choices'][0]['text'].strip()
            elif self.backend == "ollama":

                resp = requests.post("http://localhost:11434/api/generate", json={
                    "model": "qwen2.5-0.5b-instruct-uav-flight.Q4_K_M.gguf:latest",
                    "prompt": prompt,
                    "raw": True,
                    "stream": False,
                    "options": {"num_predict": 50}
                })
                text = resp.json().get("response", "")

            # New 1-Token Mapper (Phase B Optimization)
            text_upper = text.strip().upper()
            if "SWITCH" in text_upper:
                return {"fn": "switch_algorithm", "args": {"target_algo": 2}}
            elif "HOLD" in text_upper:
                return {"fn": "not_sure", "args": {"squad_id": "all", "reason": "safety_hold"}}
            elif "ADJUST" in text_upper:
                return {"fn": "adjust_squad_gains", "args": {"squad_id": "all", "param": "c1_alpha"}}

            # Fallback to JSON parsing if it's the old model
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(text)
        except Exception as e:
            print("Agent Error:", e, "Text:", text)
            return {"fn": "not_sure", "args": {"squad_id": "all", "reason": "inference failed"}, "why": "error"}
