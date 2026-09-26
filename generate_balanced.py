import time
import json
import os
import sys
import numpy as np
from harness import Harness

def apply_balanced_scenario(sim, scenario_type):
    if scenario_type == "nominal":
        # Start agents in a very tight, perfectly connected lattice so C* = 1.0
        sim.q = np.random.rand(sim.n, sim.m) * (7.0 * 0.8) # Pack them within interaction range
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.ones(sim.m) * 100.0
        sim.obstacles = []
    elif scenario_type == "collision":
        # Force a collision by spawning them literally on top of an obstacle
        sim.q = np.random.rand(sim.n, sim.m) * 10.0
        sim.q[:, 0] += 50.0
        sim.q[:, 1] += 50.0
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.array([100.0, 100.0])
        sim.obstacles = [{'type': 'sphere', 'center': np.array([55.0, 55.0]), 'radius': 20.0}]

def generate_balanced_dataset():
    print("Generating balanced dataset using Gemma 4...")
    
    # 150 Nominal Runs
    for i in range(150):
        run_id = f"nominal_i{i}"
        print(f"Running {run_id}...")
        harness = Harness(num_agents=20, backend="gemini", max_duration=1.0, record_traces=True, run_id=run_id)
        apply_balanced_scenario(harness.sim, "nominal")
        harness.run()
        time.sleep(0.5)

    # 100 Collision Runs
    for i in range(100):
        run_id = f"collision_i{i}"
        print(f"Running {run_id}...")
        harness = Harness(num_agents=20, backend="gemini", max_duration=1.0, record_traces=True, run_id=run_id)
        apply_balanced_scenario(harness.sim, "collision")
        harness.run()
        time.sleep(0.5)
        
    print("Balanced dataset generation complete!")

if __name__ == "__main__":
    generate_balanced_dataset()
