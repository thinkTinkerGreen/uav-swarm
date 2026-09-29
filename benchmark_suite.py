import json
import time
import psutil
import os
from llm_client import LLMClient

def evaluate_slm():
    if not os.path.exists("benchmark_dataset.jsonl"):
        print("Waiting for dataset generation to complete...")
        return
        
    with open("benchmark_dataset.jsonl", "r") as f:
        lines = f.readlines()
        
    dataset = [json.loads(line) for line in lines]
    
    print("Initializing local 0.5B SLM...")
    client = LLMClient(backend="native")
    
    # SLM vs Oracle
    exact_matches_slm = 0
    outcome_matches_slm = 0
    
    # Frontier vs Oracle
    exact_matches_frontier = 0
    outcome_matches_frontier = 0
    
    disagreements = []
    
    total_time = 0.0
    process = psutil.Process(os.getpid())
    peak_memory = 0
    
    print("Starting evaluation...")
    for i, row in enumerate(dataset):
        telem = row["telemetry"]
        
        mapped_telem = {
            "c_star": telem["c_star"],
            "e_tilde": telem["e_tilde"],
            "k_tilde": telem["k_tilde"],
            "collisions": telem["collisions"]
        }
        
        mem_before = process.memory_info().rss
        t0 = time.perf_counter()
        decision = client.get_decision([mapped_telem])
        t1 = time.perf_counter()
        mem_after = process.memory_info().rss
        
        total_time += (t1 - t0)
        peak_memory = max(peak_memory, mem_after)
        
        fn = decision.get("fn", "not_sure")
        if fn == "switch_algorithm": slm_action = "SWITCH"
        elif fn == "adjust_squad_gains": slm_action = "ADJUST"
        else: slm_action = "HOLD"
            
        oracle = row["oracle_decision"]
        frontier = row["frontier_decision"]
        
        # Grade SLM vs Oracle
        if slm_action == oracle:
            exact_matches_slm += 1
            outcome_matches_slm += 1
        elif (slm_action == "SWITCH" and oracle == "ADJUST") or (slm_action == "ADJUST" and oracle == "SWITCH"):
            if telem["collisions"] == 0: outcome_matches_slm += 1
            else: disagreements.append(f"[SLM] C*={telem['c_star']}, Col={telem['collisions']}. Expected {oracle}, Got {slm_action}")
        else:
            disagreements.append(f"[SLM] C*={telem['c_star']}, Col={telem['collisions']}. Expected {oracle}, Got {slm_action}")
            
        # Grade Frontier vs Oracle
        if frontier != "ERROR" and frontier != "UNKNOWN":
            if frontier == oracle:
                exact_matches_frontier += 1
                outcome_matches_frontier += 1
            elif (frontier == "SWITCH" and oracle == "ADJUST") or (frontier == "ADJUST" and oracle == "SWITCH"):
                if telem["collisions"] == 0: outcome_matches_frontier += 1
                    
    # Metrics
    n = len(dataset)
    m1_slm = (exact_matches_slm / n) * 100
    m2_slm = (outcome_matches_slm / n) * 100
    
    valid_frontier = len([r for r in dataset if r["frontier_decision"] not in ["ERROR", "UNKNOWN"]])
    m1_front = (exact_matches_frontier / valid_frontier) * 100 if valid_frontier > 0 else 0
    m2_front = (outcome_matches_frontier / valid_frontier) * 100 if valid_frontier > 0 else 0
    
    avg_latency_slm = (total_time / n) * 1000
    peak_mem_slm = peak_memory / (1024 * 1024)
    
    # SLM Battery (4W CPU)
    j_per_dec_slm = 4.0 * (avg_latency_slm / 1000)
    batt_slm = (54000 / j_per_dec_slm) / 100 if j_per_dec_slm > 0 else 0
    
    # Frontier Battery (0.6s latency over 5G radio @ 2.5W)
    avg_latency_front = 600.0
    j_per_dec_front = 2.5 * (avg_latency_front / 1000)
    batt_front = (54000 / j_per_dec_front) / 100
    
    print(f"\nSLM: M1={m1_slm:.1f}%, M2={m2_slm:.1f}%, Lat={avg_latency_slm:.1f}ms, Mem={peak_mem_slm:.1f}MB, Batt={batt_slm:.0f}")
    print(f"FRN: M1={m1_front:.1f}%, M2={m2_front:.1f}%, Lat={avg_latency_front:.1f}ms, Mem=0MB (API), Batt={batt_front:.0f}")

if __name__ == "__main__":
    evaluate_slm()
