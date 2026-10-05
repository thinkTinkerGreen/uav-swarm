import sys
import logging
import numpy as np
import copy
import math

# Suppress logging
logging.getLogger("SwarmLogger").setLevel(logging.CRITICAL)

sys.path.append('.')
from src.tools.export_3d_flight import ExportHarness
from src.engine.simulator import FlockSimulator

scenarios = ["hero_tour", "adv_a", "adv_b", "rtl", "armada"]
issues = []

for sc in scenarios:
    print(f"\n--- Testing Scenario: {sc} (180s) ---")
    agents = 50 if sc == "armada" else 20
    h = ExportHarness(num_agents=agents, scenario=sc, duration=180.0)
    
    sim = h.sim
    dt = 0.03
    max_steps = int(180.0 / dt)
    
    initial_q = copy.deepcopy(sim.q)
    has_nan = False
    
    for step in range(max_steps):
        sim.step(dt=dt)
        if step % 200 == 0 and np.isnan(sim.q).any():
             has_nan = True
             break
                 
    if has_nan or np.isnan(sim.q).any():
        issues.append(f"[{sc}] MATH ERROR: NaN detected in drone coordinates (exploded physics).")
        continue
        
    final_q = sim.q
    
    dist_moved = np.mean(np.linalg.norm(final_q - initial_q, axis=1))
    print(f"{sc} moved {dist_moved:.2f} meters.")
    if dist_moved < 5.0:
        issues.append(f"[{sc}] LOGIC ERROR: Swarm moved less than 5 meters ({dist_moved:.2f}m) over 180s. Drones are stuck.")
        
    if sc == "rtl" and dist_moved > 50.0:
         issues.append(f"[{sc}] LOGIC ERROR: RTL Kobayashi Maru failed. Swarm was supposed to be trapped but escaped ({dist_moved:.2f}m).")

print("\n\n=== FINAL ISSUES LIST ===")
for issue in issues:
    print(issue)
if not issues:
    print("None!")
