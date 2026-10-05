import sys
sys.path.append('.')
from src.tools.export_3d_flight import ExportHarness

h = ExportHarness(num_agents=20, scenario="adv_b", duration=3.0)
h.run_demo()

frames = h.flight_data["frames"]
print(f"Total Frames: {len(frames)}")
if len(frames) > 0:
    for i, f in enumerate(frames[:5]):
        print(f"Frame {i} Drone 0: {f['drones'][0]}")
