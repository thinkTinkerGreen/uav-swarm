import re

with open("generate_traces.py", "r") as f:
    content = f.read()

batch_logic = """
    for scenario_id, total_runs, sizes in scenarios_plan:
        runs_per_size = total_runs // len(sizes)
        for size in sizes:
            for i in range(runs_per_size):
                run_id = f"s{scenario_id}_n{size}_i{i}"
                
                if run_id in successful_runs:
                    continue
                    
                print(f"Running {run_id}...")
                harness = Harness(num_agents=size, backend="gemini", max_duration=2.5, record_traces=True, run_id=run_id)
                apply_scenario(harness.sim, scenario_id)
                harness.run()
                
                # Check if it was inference failed by opening the last line of the traces
                try:
                    with open("training_traces.jsonl", "r") as tr:
                        last_line = tr.readlines()[-1]
                        data = json.loads(last_line)
                        dec = data.get("decision", {})
                        if dec.get("why") == "error" or dec.get("args", {}).get("reason") == "inference failed":
                            print("Encountered inference failure. Stopping.")
                            import sys
                            sys.exit(1)
                except Exception as e:
                    pass

                time.sleep(0.5)
    
    print("Finished generating all traces.")
"""

# Replace the loop starting from "for scenario_id..."
content = re.sub(r'    for scenario_id, total_runs, sizes in scenarios_plan:.*?(?=\n\nif __name__)', batch_logic.strip('\n'), content, flags=re.DOTALL)

with open("generate_traces.py", "w") as f:
    f.write(content)
