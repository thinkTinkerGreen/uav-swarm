import os
import numpy as np
from src.engine.harness import Harness
import time

def apply_instant_crash(sim):
    # Spawn all drones at EXACTLY the same point (0, 0)
    # This guarantees drone-to-drone distance is 0.0, which is < 1.0, 
    # spiking the collisions metric immediately.
    sim.q = np.zeros((sim.n, sim.m)) 
    sim.p = np.zeros((sim.n, sim.m))
    
    sim.q_r = np.array([90.0, 50.0])
    sim.obstacles = []

print("\n--- Running True Crash (3 seconds) ---")
h2 = Harness(num_agents=20, backend="ollama", max_duration=3.0, record_traces=False, trajectory_file="honest_failure.json")
apply_instant_crash(h2.sim)
h2.run()
os.system(".venv/bin/python plot_scenarios.py --input honest_failure.json --output honest_failure.gif")

print("\n🎉 Crash rendered!")
