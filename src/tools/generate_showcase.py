import os
import numpy as np
from src.engine.harness import Harness
import time

def apply_long_journey(sim):
    # Drones spawn in bottom left
    sim.q = np.random.rand(sim.n, sim.m) * 15.0 + 5.0
    sim.p = np.zeros((sim.n, sim.m))
    
    # Target is top right
    sim.q_r = np.array([90.0, 90.0])
    
    # Scattered obstacles
    sim.obstacles = [
        {'type': 'sphere', 'center': np.array([40.0, 40.0]), 'radius': 12.0},
        {'type': 'sphere', 'center': np.array([70.0, 30.0]), 'radius': 10.0},
        {'type': 'sphere', 'center': np.array([30.0, 70.0]), 'radius': 15.0},
        {'type': 'sphere', 'center': np.array([60.0, 80.0]), 'radius': 8.0}
    ]

def apply_honest_failure(sim):
    # Drones spawn in the middle
    sim.q = np.random.rand(sim.n, sim.m) * 10.0 + 20.0
    sim.q[:, 1] += 20.0
    sim.p = np.zeros((sim.n, sim.m))
    
    # Target is straight right
    sim.q_r = np.array([90.0, 50.0])
    
    # Massive impassable wall blocks them completely
    sim.obstacles = [
        {'type': 'wall', 'point': np.array([50.0, 50.0]), 'normal': np.array([-1.0, 0.0])}
    ]

print("\n--- Running Showcase 1: The Long Journey (12 seconds) ---")
h1 = Harness(num_agents=20, backend="ollama", max_duration=12.0, record_traces=False, trajectory_file="long_journey.json")
apply_long_journey(h1.sim)
h1.run()
os.system(".venv/bin/python plot_scenarios.py --input long_journey.json --output long_journey.gif")

print("\n--- Running Showcase 2: The Honest Failure (5 seconds) ---")
h2 = Harness(num_agents=20, backend="ollama", max_duration=5.0, record_traces=False, trajectory_file="honest_failure.json")
apply_honest_failure(h2.sim)
h2.run()
os.system(".venv/bin/python plot_scenarios.py --input honest_failure.json --output honest_failure.gif")

print("\n🎉 Showcases completely rendered!")
