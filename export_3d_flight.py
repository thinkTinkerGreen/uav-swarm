import time
import os
import json
import numpy as np
from harness import Harness
import math
import argparse

class ExportHarness(Harness):
    def __init__(self, num_agents=20, scenario="hero_tour", duration=120.0):
        super().__init__(num_agents=num_agents, backend="native", max_duration=duration, record_traces=False, trajectory_file="dummy.json")
        self.n = num_agents
        self.scenario = scenario
        self.flight_data = {"frames": [], "obstacles": []}
        self.setup_scenario()

    def setup_scenario(self):
        self.sim.q = np.zeros((self.n, 2))
        self.sim.p = np.zeros((self.n, 2))
        self.sim.obstacles = []
        
        # Default target
        self.sim.q_r = np.array([200.0, 0.0])
        self.sim.p_r = np.array([3.0, 0.0])  
        self.sim.algo = 1
        
        if self.scenario == "hero_tour":
            print("[SCENARIO] 1: The Grand Tour (Hero)")
            # 20 Drones, Sparse Pillars
            for i in range(self.n):
                self.sim.q[i] = [-50 + (i%5)*5, (i//5)*5 - 10]
            for x in range(0, 150, 40):
                self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), (x%80)-40.0]), 'radius': 10.0})
                self.flight_data["obstacles"].append({"x": float(x), "y": (x%80)-40.0, "radius": 10.0})
                
        elif self.scenario == "adv_a":
            print("[SCENARIO] 11: Split-Brain Gauntlet (Adversarial A)")
            # Massive wall in the center
            for i in range(self.n):
                self.sim.q[i] = [-50 + (i%5)*5, (i//5)*5]
            for y in range(-100, 100, 10):
                self.sim.obstacles.append({'type': 'sphere', 'center': np.array([50.0, float(y)]), 'radius': 12.0})
                self.flight_data["obstacles"].append({"x": 50.0, "y": float(y), "radius": 12.0})
                
        elif self.scenario == "adv_b":
            print("[SCENARIO] 12: Sniper & Jammer (Adversarial B)")
            for i in range(self.n):
                self.sim.q[i] = [-50 + (i%5)*5, (i//5)*5]
                
        elif self.scenario == "armada":
            print("[SCENARIO] 13: The Armada (200+ Drones)")
            # Need to adjust number of agents dynamically if the arg wasn't passed right, 
            # but we assume the harness was initialized with 200.
            for i in range(self.n):
                self.sim.q[i] = [-100 + (i%20)*5, (i//20)*5 - 25]
                
        elif self.scenario == "rtl":
            print("[SCENARIO] 14: Complete Refusal (RTL Kobayashi Maru)")
            # Boxed in
            for i in range(self.n):
                self.sim.q[i] = [0, (i%5)*5]
            # Form a box around them
            for x in [-20, 20]:
                for y in range(-20, 30, 10):
                    self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), float(y)]), 'radius': 10.0})
                    self.flight_data["obstacles"].append({"x": float(x), "y": float(y), "radius": 10.0})
            for y in [-20, 30]:
                for x in range(-10, 20, 10):
                    self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), float(y)]), 'radius': 10.0})
                    self.flight_data["obstacles"].append({"x": float(x), "y": float(y), "radius": 10.0})

    def run_demo(self):
        self.env.start()
        
        while self.env.is_running():
            telem = self.env.read_telemetry()
            if not telem:
                time.sleep(0.05)
                continue
                
            q_all = [q[0] for q in self.env.sim.q if not np.isnan(q[0])]
            if not q_all: break
            
            with self.env.lock:
                # Dynamic Scenario Triggers
                if self.scenario == "adv_b" and len(self.flight_data["frames"]) == 50:
                    print("[SNIPER] Killing Prime Commander (Drone 0)!")
                    self.env.sim.q[0] = [9999, 9999] # Teleport away to break R_comm
                if self.scenario == "adv_b" and len(self.flight_data["frames"]) == 150:
                    print("[JAMMER] Injecting Massive RF Jamming (Noise)!")
                    self.env.sensor_noise_std = 5.0
                    
                if self.env.sim.algo == 1: decision = "ADJUST"; color = "#4CAF50"
                elif self.env.sim.algo == 2: decision = "SWITCH"; color = "#FFC107"
                else: decision = "HOLD"; color = "#F44336"
                    
                frame = []
                leaders = self.env.sim.squad_leaders
                for i in range(self.n):
                    x, y = self.env.sim.q[i]
                    vx, vy = self.env.sim.p[i]
                    yaw = math.atan2(vy, vx) if (abs(vx) > 0.1 or abs(vy) > 0.1) else 0.0
                    frame.append({"x": float(x), "y": float(y), "yaw": float(yaw), "is_leader": (i in leaders)})
                
                # Render Target Reticle for Viewer
                target_q = self.env.sim.q_r.tolist()
                
                self.flight_data["frames"].append({
                    "drones": frame, 
                    "decision": decision, 
                    "color": color,
                    "target_x": target_q[0],
                    "target_y": target_q[1]
                })
                
                # Progress bar
                if len(self.flight_data["frames"]) % 50 == 0:
                    print(f"\r[Exporter] Rendered {len(self.flight_data['frames'])} frames...", end='', flush=True)
                    
            time.sleep(0.05)
            
        self.env.join()
        
        with open(f"flight_data_{self.scenario}.json", "w") as f:
            json.dump(self.flight_data, f)
        print(f"Exported {self.scenario} to JSON!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=str, default="hero_tour")
    parser.add_argument("--duration", type=float, default=120.0, help="Simulation duration in seconds")
    args = parser.parse_args()
    
    agents = 200 if args.scenario == "armada" else 20
    h2 = ExportHarness(num_agents=agents, scenario=args.scenario, duration=args.duration)
    h2.run_demo()
