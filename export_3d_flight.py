import time
import os
import json
import numpy as np
from harness import Harness
import math

class ExportHarness(Harness):
    def __init__(self, num_agents=8):
        super().__init__(num_agents=num_agents, backend="native", max_duration=40.0, record_traces=False, trajectory_file="dummy.json")
        self.n = num_agents
        self.flight_data = {"frames": [], "obstacles": []}
        self.setup_demo()

    def setup_demo(self):
        self.sim.q = np.zeros((self.n, 2))
        for i in range(self.n):
            self.sim.q[i] = [-50 + (i%4)*8, (i//4)*8 - 4]
                
        self.sim.p = np.zeros((self.n, 2))
        self.sim.q_r = np.array([150.0, 0.0])
        self.sim.p_r = np.array([5.0, 0.0])  
        self.sim.algo = 1
        self.retreat_triggered = False
        
        self.sim.obstacles = []
        for y in range(-100, 100, 10):
            obs = {'type': 'sphere', 'center': np.array([30.0, float(y)]), 'radius': 10.0}
            self.sim.obstacles.append(obs)
            self.flight_data["obstacles"].append({"x": 30.0, "y": float(y), "radius": 10.0})

    def run_demo(self):
        print("Starting V4 Enterprise 3D Export Simulation...")
        self.env.start()
        
        while self.env.is_running():
            telem = self.env.read_telemetry()
            if not telem:
                time.sleep(0.05)
                continue
                
            q_all = [q[0] for q in self.env.sim.q if not np.isnan(q[0])]
            if not q_all: break
            avg_x = np.mean(q_all)
            
            with self.env.lock:
                if avg_x > 15 and not self.retreat_triggered:
                    self.retreat_triggered = True
                    self.env.sim.algo = 3
                    self.env.sim.c1_a = 0.0
                    self.env.sim.c2_a = 0.0
                    self.env.sim.c1_g = 0.0
                    self.env.sim.c2_g = 0.0
                    self.env.sim.c1_b = 0.0
                    self.env.sim.c2_b = 0.0
                    for i in range(self.n):
                        self.env.sim.p[i] = [-5.0, 0.0]
                elif not self.retreat_triggered and avg_x > -15:
                    self.env.sim.algo = 2
                    
                if self.retreat_triggered and avg_x < -40:
                    self.env.running = False
                    
                if self.env.sim.algo == 1:
                    decision = "ADJUST (Nominal)"
                    color = "#4CAF50"
                elif self.env.sim.algo == 2:
                    decision = "SWITCH (Evasion)"
                    color = "#FFC107"
                else:
                    decision = "HOLD (RTL Failsafe)"
                    color = "#F44336"
                    
                frame = []
                leaders = self.env.sim.squad_leaders
                for i in range(self.n):
                    x, y = self.env.sim.q[i]
                    vx, vy = self.env.sim.p[i]
                    yaw = math.atan2(vy, vx) if (abs(vx) > 0.1 or abs(vy) > 0.1) else 0.0
                    frame.append({"x": float(x), "y": float(y), "yaw": float(yaw), "is_leader": (i in leaders)})
                
                self.flight_data["frames"].append({"drones": frame, "decision": decision, "color": color})
                    
            time.sleep(0.05)
            
        self.env.join()
        
        with open("flight_data.json", "w") as f:
            json.dump(self.flight_data, f)
        print(f"Exported {len(self.flight_data['frames'])} frames to flight_data.json!")

if __name__ == "__main__":
    h2 = ExportHarness(num_agents=8)
    h2.run_demo()
