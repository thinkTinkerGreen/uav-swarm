import time
import json
import urllib.request

def test_inference(c_star, e_tilde, k_tilde, col):
    prompt = f"[UAV]\nC*:{c_star:.2f}\nE~:{e_tilde:.5f}\nK~:{k_tilde:.2f}\nCol:{col}\n[Go]"
    
    data = json.dumps({
        "model": "Qwen3.5-0.8B.Q4K-uav",
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")
    
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data, headers={"Content-Type": "application/json"})
    
    start = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            latency_ms = (time.time() - start) * 1000
            
            try:
                decision = json.loads(resp_data.get("response", ""))
                print(f"✅ Success ({latency_ms:.1f}ms): {decision}")
            except Exception as e:
                print(f"❌ Failed ({latency_ms:.1f}ms): Model hallucinated or returned bad JSON.")
                print("Raw output:", resp_data.get("response", ""))
    except Exception as err:
        print(f"❌ HTTP Error: {err}")

print("Test 1: Severe Fragmentation (Expect target_algo: 2)")
test_inference(c_star=0.04, e_tilde=0.01, k_tilde=0.9, col=0)

print("\nTest 2: Imminent Collision (Expect not_sure)")
test_inference(c_star=0.95, e_tilde=0.01, k_tilde=0.1, col=1)

print("\nTest 3: Nominal Flight (Expect adjust_squad_gains)")
test_inference(c_star=0.98, e_tilde=0.00, k_tilde=0.05, col=0)
