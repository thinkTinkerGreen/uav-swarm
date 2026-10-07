import time
import os
import json
import numpy as np
from src.engine.harness import Harness
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
        self.sim.p = np.array([[2.0, 0.0] for _ in range(self.n)])
        self.sim.obstacles.clear()
        self.env.obstacles = self.sim.obstacles
        
        # Default target
        self.sim.q_r = np.array([-10.0, 0.0])
        self.sim.p_r = np.array([3.0, 0.0])  
        self.sim.algo = 1
        
        # We record the starting center of the swarm for the viewers
        self.flight_data["start_point"] = {"x": -50.0, "y": 0.0}
        self.flight_data["end_point"] = {"x": 200.0, "y": 0.0}
        
        if self.scenario == "hero_tour":
            print("[SCENARIO] 1: The Grand Tour (Hero)")
            for i in range(self.n):
                self.sim.q[i] = [-50 + (i%5)*8, (i//5)*8 - 12]
            self.flight_data["start_point"] = {"x": -34.0, "y": 0.0}
            self.sim.gamma_all = True
            self.sim.max_speed = 6.0
            self.sim.c1_g = 1.0
            self.sim.c2_g = 2.0 * np.sqrt(self.sim.c1_g)
            for x in range(0, 150, 40):
                self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), (x%80)-40.0]), 'radius': 10.0})
                self.flight_data["obstacles"].append({"x": float(x), "y": (x%80)-40.0, "radius": 10.0})
                
        elif self.scenario == "adv_a":
            print("[SCENARIO] 11: Split-Brain Gauntlet (Corridor)")
            for i in range(self.n):
                self.sim.q[i] = [-50 + (i%5)*8, (i//5)*8 - 12]
            self.flight_data["start_point"] = {"x": -34.0, "y": 0.0}
            # Corridor walls
            for x in range(-20, 150, 15):
                # Top wall
                self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), 30.0]), 'radius': 12.0})
                self.flight_data["obstacles"].append({"x": float(x), "y": 30.0, "radius": 12.0})
                # Bottom wall
                self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), -30.0]), 'radius': 12.0})
                self.flight_data["obstacles"].append({"x": float(x), "y": -30.0, "radius": 12.0})
                
        elif self.scenario == "adv_b":
            print("[SCENARIO] 12: Sniper & Jammer (The Perfect Demo)")
            # 20 drones perfectly spaced to prevent overlap stuck
            for i in range(self.n):
                self.sim.q[i] = [-50 + (i%5)*8, (i//5)*8 - 15]
            self.flight_data["start_point"] = {"x": -34.0, "y": -3.0}
            self.flight_data["end_point"] = {"x": 200.0, "y": 0.0}
            
            # Create a striking, scattered obstacle field for evasion
            # Sparse field: staggered so every row has >=1 clear lane wider than the swarm
            # (obstacle radius 10 + sensing buffer 8.4 on each side).
            obstacles = [(30, 0), (75, -25), (75, 25), (120, 0), (165, -25), (165, 25)]
            self.sim.gamma_all = True   # every drone navigates to the reference (Olfati-Saber Alg. 2)
            self.sim.max_speed = 6.0
            self.sim.c1_g = 1.0
            self.sim.c2_g = 2.0 * np.sqrt(self.sim.c1_g)
            for x, y in obstacles:
                self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), float(y)]), 'radius': 10.0})
                self.flight_data["obstacles"].append({"x": float(x), "y": float(y), "radius": 10.0})
                
        elif self.scenario == "armada":
            print("[SCENARIO] 13: The Armada (200 Drones)")
            # 20 columns x 10 rows at 8 m spacing (> lattice distance d=7) so nothing starts overlapped
            for i in range(self.n):
                self.sim.q[i] = [-150 + (i % 20) * 8, (i // 20) * 8 - 36]
            self.flight_data["start_point"] = {"x": -74.0, "y": 0.0}
            self.flight_data["end_point"] = {"x": 200.0, "y": 0.0}
            self.sim.q_r = np.array([-40.0, 0.0])
            self.sim.gamma_all = True   # every drone navigates to the reference (Olfati-Saber Alg. 2)
            self.sim.max_speed = 6.0
            self.sim.sep_radius = 4.0   # dense swarm: hard short-range separation guard
            self.sim.c1_g = 1.0
            self.sim.c2_g = 2.0 * np.sqrt(self.sim.c1_g)
            # Sparse staggered field with lanes wider than the sensing buffer
            for x, y in [(40, 0), (95, -50), (95, 50), (150, 0)]:
                self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), float(y)]), 'radius': 12.0})
                self.flight_data["obstacles"].append({"x": float(x), "y": float(y), "radius": 12.0})

        elif self.scenario == "rtl":
            print("[SCENARIO] 14: Complete Refusal (RTL Kobayashi Maru)")
            for i in range(self.n):
                self.sim.q[i] = [-15 + (i%5)*8, -15 + (i//5)*8]
            self.flight_data["start_point"] = {"x": 0.0, "y": 0.0}
            # Enclose them in a massive box
            for x in [-50, 50]:
                for y in range(-50, 60, 10):
                    self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), float(y)]), 'radius': 10.0})
                    self.flight_data["obstacles"].append({"x": float(x), "y": float(y), "radius": 10.0})
            for y in [-50, 50]:
                for x in range(-40, 50, 10):
                    self.sim.obstacles.append({'type': 'sphere', 'center': np.array([float(x), float(y)]), 'radius': 10.0})
                    self.flight_data["obstacles"].append({"x": float(x), "y": float(y), "radius": 10.0})

    def run_demo(self):
        self.env.start()
        self.controller.start()
        
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
                if self.scenario == "adv_b" and len(self.flight_data["frames"]) == 200:
                    print("[JAMMER] Jamming Resolved!")
                    self.env.sensor_noise_std = 0.5

                    
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
                
                # Dynamic target logic to stop AT the flag
                avg_x = np.mean([x for x, y in self.env.sim.q if x < 9000])
                
                # Cap the virtual target position at 200
                if self.env.sim.q_r[0] > 200.0:
                    self.env.sim.q_r[0] = 200.0
                
                # Smoothly decelerate the target velocity (cruise control) based on distance
                # Target settles smoothly at the staging point just short of the flag
                desired_v = min(3.0, max(0.0, (190.0 - self.env.sim.q_r[0]) * 0.3))
                    
                self.env.sim.p_r = np.array([desired_v, 0.0])

                # Render Target Reticle for Viewer
                target_q = self.env.sim.q_r.tolist()
                vis_target_x = target_q[0]
                
                self.flight_data["frames"].append({
                    "drones": frame, 
                    "decision": decision, 
                    "color": color,
                    "target_x": vis_target_x,
                    "target_y": target_q[1]
                })
                
                # Progress bar
                if len(self.flight_data["frames"]) % 50 == 0:
                    print(f"\r[Exporter] Rendered {len(self.flight_data['frames'])} frames...", end='', flush=True)
                    
            time.sleep(0.05)
            
        self.env.join()
        self.controller.join()
        
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
