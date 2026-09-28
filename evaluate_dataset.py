import json
import re
import random
import time
from llm_client import LLMClient

def evaluate_bulk(num_samples=200):
    print(f"--- Starting Bulk SLM Evaluation ({num_samples} scenarios) ---")
    
    # Load traces
    with open("training_data.jsonl", "r") as f:
        lines = f.readlines()
        
    random.seed(42)
    samples = random.sample(lines, min(num_samples, len(lines)))
    
    client = LLMClient(backend="native")
    
    passed = 0
    total = len(samples)
    
    conf_matrix = {
        "switch_algorithm": {"pass": 0, "fail": 0},
        "not_sure": {"pass": 0, "fail": 0},
        "adjust_squad_gains": {"pass": 0, "fail": 0}
    }
    
    start_time = time.time()
    
    for i, line in enumerate(samples):
        data = json.loads(line)
        text = data["text"]
        
        # Parse inputs
        c_star = float(re.search(r"C\*:([0-9.]+)", text).group(1))
        e_tilde = float(re.search(r"E~:([0-9.]+)", text).group(1))
        k_tilde = float(re.search(r"K~:([0-9.]+)", text).group(1))
        col = int(re.search(r"Col:([0-9]+)", text).group(1))
        
        # Parse ground truth
        truth_match = re.search(r"<\|im_start\|>assistant\n(.*?)(<\|im_end\|>|$)", text, re.DOTALL)
        truth_json = json.loads(truth_match.group(1).strip())
        expected_fn = truth_json["fn"]
        
        # Format for client
        mock_history = [{
            "c_star": c_star,
            "e_tilde": e_tilde,
            "k_tilde": k_tilde,
            "collisions": col
        }]
        
        # Query model
        decision = client.get_decision(mock_history)
        actual_fn = decision.get("fn", "unknown")
        
        if actual_fn == expected_fn:
            passed += 1
            conf_matrix[expected_fn]["pass"] += 1
        else:
            conf_matrix[expected_fn]["fail"] += 1
            
        if (i+1) % 20 == 0:
            print(f"Processed {i+1}/{total} scenarios...")
            
    elapsed = time.time() - start_time
    print(f"\n==========================================")
    print(f"EVALUATION COMPLETE IN {elapsed:.1f}s")
    print(f"Accuracy: {passed}/{total} ({(passed/total)*100:.2f}%)")
    print(f"==========================================")
    print("Breakdown by Ground Truth:")
    for k, v in conf_matrix.items():
        if v["pass"] + v["fail"] > 0:
            acc = v["pass"] / (v["pass"] + v["fail"]) * 100
            print(f"  {k}: {acc:.1f}% ({v['pass']}/{v['pass']+v['fail']})")

if __name__ == "__main__":
    evaluate_bulk(250)
