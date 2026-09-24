import time
from harness import Harness
from simulator_patch import apply_scenario

# We define the breakdown
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

def generate_all():
    print("Starting trace generation via Gemini Teacher API...")
    for scenario_id, total_runs, sizes in scenarios_plan:
        runs_per_size = total_runs // len(sizes)
        for size in sizes:
            for i in range(runs_per_size):
                print(f"Running Scenario {scenario_id}, Size {size}, Iteration {i+1}/{runs_per_size}")
                
                # We use gemini as backend for teaching traces
                # max_duration 2.5s allows at least 2 SLM polls per run
                harness = Harness(num_agents=size, backend="gemini", max_duration=2.5, record_traces=True)
                
                # Apply the specific scenario
                apply_scenario(harness.sim, scenario_id)
                
                harness.run()
                time.sleep(0.5) # Slight pause between runs

if __name__ == "__main__":
    generate_all()
