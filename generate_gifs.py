import os
from harness import Harness
from simulator_patch import apply_scenario

scenarios = [
    (1, "nominal_flight"),
    (2, "dense_obstacle_field"),
    (3, "corridor_squeeze"),
    (4, "dynamic_target"),
    (5, "agent_loss"),
    (6, "flash_expansion"),
    (7, "predator_evasion"),
    (8, "deadlocked_geometry"),
]

for scenario_id, name in scenarios:
    json_file = f"{name}.json"
    gif_file = f"{name}.gif"
    
    print(f"\n--- Running Scenario {scenario_id}: {name} ---")
    # Run the live simulation with Qwen SLM
    harness = Harness(num_agents=15, backend="ollama", max_duration=3.0, record_traces=False, trajectory_file=json_file)
    apply_scenario(harness.sim, scenario_id)
    harness.run()
    
    # Render the GIF
    os.system(f".venv/bin/python plot_scenarios.py --input {json_file} --output {gif_file}")

print("\n🎉 All scenarios rendered into GIFs!")
