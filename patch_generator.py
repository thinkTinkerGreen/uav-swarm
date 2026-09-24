import re

with open("generate_traces.py", "r") as f:
    content = f.read()

batch_logic = """
    new_traces_count = 0
    max_new_traces = 10

    for scenario_id, total_runs, sizes in scenarios_plan:
        if new_traces_count >= max_new_traces:
            break
        runs_per_size = total_runs // len(sizes)
        for size in sizes:
            if new_traces_count >= max_new_traces:
                break
            for i in range(runs_per_size):
                if new_traces_count >= max_new_traces:
                    break
                run_id = f"s{scenario_id}_n{size}_i{i}"
                
                if run_id in successful_runs:
                    continue
                    
                print(f"Running {run_id}...")
                harness = Harness(num_agents=size, backend="gemini", max_duration=2.5, record_traces=True, run_id=run_id)
                apply_scenario(harness.sim, scenario_id)
                harness.run()
                new_traces_count += 1
                time.sleep(0.5)
    
    print(f"Finished batch of {new_traces_count} traces.")
"""

# Replace the loop starting from "for scenario_id..."
content = re.sub(r'    for scenario_id, total_runs, sizes in scenarios_plan:.*', batch_logic.strip('\n'), content, flags=re.DOTALL)

with open("generate_traces.py", "w") as f:
    f.write(content)
