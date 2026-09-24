import time
import json
import os
import sys
from harness import Harness
from simulator_patch import apply_scenario

scenarios_plan = [
    (1, 40, [10, 20, 50]),
    (2, 40, [10, 20, 50]),
    (3, 30, [10, 20, 50]),
    (4, 30, [10, 20, 50]),
    (5, 30, [20, 50]),
    (6, 20, [20, 50]),
    (7, 30, [20, 50]),
    (8, 30, [10, 20])
]

def load_successful_runs(filepath):
    successful_runs = set()
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    decision = data.get("decision", {})
                    reason = decision.get("why", decision.get("args", {}).get("reason", ""))
                    if reason != "error" and reason != "inference failed":
                        run_id = data.get("run_id")
                        if run_id:
                            successful_runs.add(run_id)
                except:
                    pass
    return successful_runs

def generate_all():
    print("Starting incremental trace generation...")
    successful_runs = load_successful_runs("training_traces.jsonl")
    print(f"Found {len(successful_runs)} previously successful runs.")
    
    for scenario_id, total_runs, sizes in scenarios_plan:
        runs_per_size = total_runs // len(sizes)
        for size in sizes:
            for i in range(runs_per_size):
                run_id = f"s{scenario_id}_n{size}_i{i}"
                
                if run_id in successful_runs:
                    print(f"Skipping {run_id}, already successful.")
                    continue
                    
                print(f"Running {run_id}...")
                harness = Harness(num_agents=size, backend="gemini", max_duration=2.5, record_traces=True, run_id=run_id)
                apply_scenario(harness.sim, scenario_id)
                harness.run()
                
                # Check for inference failure to safety halt
                try:
                    with open("training_traces.jsonl", "r") as tr:
                        lines = tr.readlines()
                        if lines:
                            last_line = lines[-1]
                            data = json.loads(last_line)
                            dec = data.get("decision", {})
                            reason = dec.get("why", dec.get("args", {}).get("reason", ""))
                            if reason == "error" or reason == "inference failed":
                                print("Encountered inference failure. Stopping.")
                                sys.exit(1)
                except Exception:
                    pass

                time.sleep(0.5)
    
    print("Finished generating all traces.")

if __name__ == "__main__":
    generate_all()
