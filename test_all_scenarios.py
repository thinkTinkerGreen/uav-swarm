import sys
import json
import time

# Mock time.sleep to run instantly
original_sleep = time.sleep
time.sleep = lambda x: None

sys.path.append('.')
from src.tools.export_3d_flight import ExportHarness

scenarios = ["hero_tour", "adv_a", "adv_b", "rtl", "armada"]
issues = []

for sc in scenarios:
    print(f"\n--- Testing Scenario: {sc} (180s) ---")
    agents = 200 if sc == "armada" else 20
    h = ExportHarness(num_agents=agents, scenario=sc, duration=180.0)
    
    # We don't need SLM inference for physics testing
    h.controller.backend = "mock"
    
    start_t = original_sleep(0) # just to get a tick if needed, wait, let's use time.time
    real_start = time.time()
    
    h.run_demo()
    
    real_end = time.time()
    print(f"Scenario {sc} completed in {real_end - real_start:.2f} real seconds.")
    
    frames = h.flight_data["frames"]
    obstacles = h.flight_data["obstacles"]
    
    if len(frames) == 0:
        issues.append(f"[{sc}] CRITICAL: Generated 0 frames.")
        continue
        
    print(f"Generated {len(frames)} frames. Checking physics invariants...")
    
    has_nan = False
    for frame in frames:
        for d in frame["drones"]:
            if d["x"] != d["x"] or d["y"] != d["y"]:
                has_nan = True
                break
        if has_nan: break
        
    if has_nan:
        issues.append(f"[{sc}] MATH ERROR: NaN detected in drone coordinates.")
        
    first_frame = frames[0]["drones"]
    last_frame = frames[-1]["drones"]
    
    dist_moved = sum(((f["x"] - l["x"])**2 + (f["y"] - l["y"])**2)**0.5 for f, l in zip(first_frame, last_frame)) / len(first_frame)
    if dist_moved < 5.0 and not has_nan:
        issues.append(f"[{sc}] LOGIC ERROR: Swarm moved less than 5 meters ({dist_moved:.2f}m) over 180s. Drones are stuck.")
        
    if sc == "rtl" and dist_moved > 50.0 and not has_nan:
         issues.append(f"[{sc}] LOGIC ERROR: RTL Kobayashi Maru failed. Swarm was supposed to be trapped but escaped ({dist_moved:.2f}m).")

print("\n\n=== FINAL ISSUES LIST ===")
for issue in issues:
    print(issue)
