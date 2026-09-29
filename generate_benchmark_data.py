import os
import json
import random
import time
import threading
from dotenv import load_dotenv
import concurrent.futures

load_dotenv(os.path.expanduser("~/.env"))

from google import genai
client = genai.Client()

def get_oracle_decision(telem):
    c = telem["c_star"]
    col = telem["collisions"]
    if c < 0.4 or col > 1: return "HOLD"
    elif c < 0.8 or col == 1: return "SWITCH"
    else: return "ADJUST"

lock = threading.Lock()
def process_telem(telem_with_id):
    i, telem = telem_with_id
    prompt = f"""You are a UAV swarm supervisory controller.
Current telemetry:
C*: {telem['c_star']:.2f}
E~: {telem['e_tilde']:.5f}
K~: {telem['k_tilde']:.2f}
Collisions: {telem['collisions']}

Rules:
If C* < 0.4 or Collisions > 1, the situation is critical. Output HOLD.
If C* < 0.8 or Collisions == 1, there is fragmentation or minor risk. Output SWITCH.
If C* >= 0.8 and Collisions == 0, the flight is nominal. Output ADJUST.

Output EXACTLY ONE WORD: 'ADJUST', 'SWITCH', or 'HOLD'. No explanations. No other text."""

    frontier = "ERROR"
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai.types.GenerateContentConfig(temperature=0.0)
            )
            text = response.text.strip().upper()
            if "HOLD" in text: frontier = "HOLD"; break
            if "SWITCH" in text: frontier = "SWITCH"; break
            if "ADJUST" in text: frontier = "ADJUST"; break
            frontier = "UNKNOWN"
            break
        except Exception as e:
            time.sleep(2)
                
    oracle = get_oracle_decision(telem)
    row = {
        "id": i,
        "telemetry": telem,
        "oracle_decision": oracle,
        "frontier_decision": frontier
    }
    
    with lock:
        with open("benchmark_dataset.jsonl", "a") as f:
            f.write(json.dumps(row) + "\n")
            f.flush()

if __name__ == "__main__":
    output_file = "benchmark_dataset.jsonl"
    
    existing_ids = set()
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data["frontier_decision"] not in ["ERROR", "UNKNOWN"]:
                        existing_ids.add(data["id"])
                except: pass
                
    num_existing = len(existing_ids)
    if num_existing > 0:
        print(f"Found {num_existing} valid states. Resuming generation...")
        
    target_total = 100 # Reduced to 100 to finish fast within limits!
    
    if num_existing >= target_total:
        print(f"Dataset already complete with {num_existing} valid states!")
        exit(0)
        
    pool = []
    # Mix of scenarios
    for i in range(target_total):
        if i in existing_ids: continue
        scen = random.choice(["A", "B", "C"])
        if scen == "A":
            pool.append((i, {"scenario": "A", "c_star": round(random.uniform(0.45, 0.75), 2), "collisions": random.choice([0, 1]), "e_tilde": round(random.uniform(0.01, 0.05), 5), "k_tilde": round(random.uniform(0.1, 0.5), 2)}))
        elif scen == "B":
            pool.append((i, {"scenario": "B", "c_star": round(random.uniform(0.1, 0.39), 2), "collisions": random.randint(2, 10), "e_tilde": round(random.uniform(0.05, 0.2), 5), "k_tilde": round(random.uniform(0.5, 1.5), 2)}))
        else:
            pool.append((i, {"scenario": "C", "c_star": round(random.uniform(0.85, 1.0), 2), "collisions": 0, "e_tilde": round(random.uniform(0.001, 0.009), 5), "k_tilde": round(random.uniform(0.01, 0.09), 2)}))
            
    print(f"Generating {len(pool)} remaining states using parallel execution...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for i, _ in enumerate(executor.map(process_telem, pool)):
            if (i+1) % 10 == 0:
                print(f"Processed {num_existing + i + 1}/{target_total} states...", flush=True)
                
    print("Benchmark dataset generation complete!", flush=True)
