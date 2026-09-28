import os
import json
from harness import Harness
from simulator_patch import apply_scenario
from generate_epic_showcases import apply_the_gauntlet, apply_failure_and_recovery, CinematicHarness

EVAL_FILE = "eval_run_records.jsonl"

def main():
    if os.path.exists(EVAL_FILE):
        os.remove(EVAL_FILE)
        
    print(f"--- Starting Evaluation Runner ---")
    print(f"Executing 10 scenarios and writing raw output to {EVAL_FILE}...")
    
    scenarios = [
        (1, "nominal_flight"),
        (2, "dense_obstacle_field"),
        (3, "corridor_squeeze"),
        (4, "dynamic_target"),
        (5, "agent_loss"),
        (6, "flash_expansion"),
        (7, "predator_evasion"),
        (8, "deadlocked_geometry")
    ]
    
    # Run 1-8
    for sc_id, sc_name in scenarios:
        print(f"Running Scenario {sc_id}: {sc_name}")
        h = Harness(num_agents=15, backend="native", max_duration=2.5, record_traces=True, run_id=sc_name, trajectory_file=f"{sc_name}.json", trace_file=EVAL_FILE)
        apply_scenario(h.sim, sc_id)
        h.run()

    # Run 9: Gauntlet
    print("Running Scenario 9: the_gauntlet")
    h9 = Harness(num_agents=15, backend="native", max_duration=4.0, record_traces=True, run_id="the_gauntlet", trajectory_file="the_gauntlet.json", trace_file=EVAL_FILE)
    apply_the_gauntlet(h9.sim)
    h9.run()
    
    # Run 10: Failure & Recovery (Requires CinematicHarness to mock the collision)
    print("Running Scenario 10: honest_failure")
    events = [
        (1.5, "force_collision"),
        (3.0, "clear_collision")
    ]
    # NOTE: We must monkey-patch CinematicHarness to accept trace_file
    h10 = CinematicHarness(num_agents=15, backend="native", max_duration=4.0, trajectory_file="honest_failure.json", script_events=events)
    h10.controller.trace_file = EVAL_FILE
    h10.controller.run_id = "honest_failure"
    apply_failure_and_recovery(h10.sim)
    h10.run()
    
    print(f"✅ Runner complete. All raw records saved to {EVAL_FILE}.")

if __name__ == "__main__":
    main()
