import time
import json
import urllib.request

def test_inference(c_star, e_tilde, k_tilde, col):
    # Constructing the exact string we trained on
    raw_prompt = f"<|im_start|>system\nYou are a UAV controller. You MUST output ONLY valid JSON. No conversational text. No explanations.<|im_end|>\n<|im_start|>user\n[UAV]\nC*:{c_star:.2f}\nE~:{e_tilde:.5f}\nK~:{k_tilde:.2f}\nCol:{col}\n[Go]<|im_end|>\n<|im_start|>assistant\n"
    
    data = json.dumps({
        "model": "Qwen3.5-0.8B.Q4K-uav",
        "prompt": raw_prompt,
        "raw": True, # Bypass Ollama's ChatML templater!
        "stream": False,
        "options": {
            "num_predict": 50
        }
    }).encode("utf-8")
    
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data, headers={"Content-Type": "application/json"})
    
    start = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            latency_ms = (time.time() - start) * 1000
            raw_text = resp_data.get("response", "")
            
            try:
                decision = json.loads(raw_text)
                print(f"✅ Success ({latency_ms:.1f}ms): {decision}")
            except Exception as e:
                print(f"❌ Failed ({latency_ms:.1f}ms): Model hallucinated or returned bad JSON.")
                print(f"Raw output: {raw_text}")
    except Exception as err:
        print(f"❌ HTTP Error: {err}")

print("Test 1: Severe Fragmentation (Expect target_algo: 2)")
test_inference(c_star=0.04, e_tilde=0.01, k_tilde=0.9, col=0)
