import json
import time

import sys
if sys.platform == "android":
    sys.platform = "linux"  # Hack to bypass llama-cpp-python 'Unsupported platform' error on Termux

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMClient:
    def __init__(self, backend="native"):
        self.backend = backend
        self.client = None
        
        if self.backend == "native":
            if not LLAMA_AVAILABLE:
                raise RuntimeError("llama-cpp-python is not installed.")
            # We use the fine-tuned V4 SLM
            model_file = "SmolLM2-135M-Instruct.Q4_K_M.gguf"
            try:
                print("[LLMClient] Initializing Native Llama with KV Cache...")
                # LATENCY OPTIMIZATION: Shrink n_ctx to 128 to save mobile RAM
                self.client = Llama(model_path=model_file, verbose=False, n_ctx=128)
            except Exception as e:
                print(f"Failed to load model {model_file}: {e}")
                print("Please make sure the .gguf file is in the same folder as this script!")
                exit(1)
                
        elif self.backend == "gemini":
            if not GEMINI_AVAILABLE:
                raise RuntimeError("google-genai is not installed.")
            self.client = genai.Client()
        else:
            raise ValueError(f"Unknown backend {backend}")

    def get_decision(self, telemetry_data):
        # We assume telemetry_data is a list of dicts, but we only evaluate the first one (the swarm average)
        telem = telemetry_data[0]
        
        c = telem.get("c_star", 1.0)
        e = telem.get("e_tilde", 0.0)
        k = telem.get("k_tilde", 0.0)
        col = telem.get("collisions", 0)
        
        # LATENCY OPTIMIZATION: xVAL Integer Scaling
        c_int = int(round(c * 1000))
        e_int = int(round(e * 1000))
        k_int = int(round(k * 1000))
        
        # LATENCY OPTIMIZATION: Micro-Key Anchoring
        prompt = f"C:{c_int}|E:{e_int}|K:{k_int}|Col:{col}="
        
        if self.backend == "native":
            # LATENCY OPTIMIZATION: max_tokens=10
            response = self.client(
                prompt,
                max_tokens=10, 
                temperature=0.0,
                stop=["<|im_end|>", "\n"]
            )
            text = response['choices'][0]['text'].strip().upper()
        else:
            # Gemini Backend (For benchmarking Oracle)
            # Gemini doesn't know the xVAL format, so we give it English instructions
            gemini_prompt = f"""You are a UAV swarm supervisory controller.
Current telemetry:
C*: {c:.2f}
E~: {e:.5f}
K~: {k:.2f}
Collisions: {col}

Rules:
If C* < 0.4 or Collisions > 1, the situation is critical. Output HOLD.
If C* < 0.8 or Collisions == 1, there is fragmentation or minor risk. Output SWITCH.
If C* >= 0.8 and Collisions == 0, the flight is nominal. Output ADJUST.

Output EXACTLY ONE WORD: 'ADJUST', 'SWITCH', or 'HOLD'. No explanations. No other text."""
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=gemini_prompt,
                    config=genai.types.GenerateContentConfig(temperature=0.0)
                )
                text = response.text.strip().upper()
            except Exception:
                text = "HOLD"

        if "HOLD" in text:
            return {"fn": "not_sure"}
        elif "SWITCH" in text:
            return {"fn": "switch_algorithm", "args": {"target_algo": 2}}
        elif "ADJUST" in text:
            return {"fn": "adjust_squad_gains"}
        else:
            return {"fn": "not_sure"}
