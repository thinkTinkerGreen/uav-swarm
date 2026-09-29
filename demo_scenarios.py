import time
import os
import numpy as np
from harness import Harness
from llm_client import LLMClient

class DemoHarness(Harness):
    def __init__(self, demo_id, output_json, num_agents=15):
        super().__init__(num_agents=num_agents, backend="native", max_duration=60.0, record_traces=False, trajectory_file=output_json)
        self.demo_id = demo_id
        self.client = LLMClient(backend="native")
        self.n = num_agents
        self.setup_demo()

    def setup_demo(self):
        self.sim.q = np.zeros((self.n, 2))
        for i in range(self.n):
            if self.n == 15:
                self.sim.q[i] = [-50 + (i%5)*5, (i//5)*5 - 5]
            else:
                self.sim.q[i] = [-50 + (i%4)*8, (i//4)*8 - 4]
                
        self.sim.p = np.zeros((self.n, 2))
        
        self.sim.q_r = np.array([150.0, 0.0])
        self.sim.p_r = np.array([5.0, 0.0])  
        self.sim.algo = 1
        self.retreat_triggered = False
        
        self.split_state = 0
        
        if self.demo_id == 2:
            self.sim.obstacles = []
            for y in range(-100, 100, 10):
                self.sim.obstacles.append({'type': 'sphere', 'center': np.array([30.0, float(y)]), 'radius': 10.0})

    def run_demo(self):
        print(f"Starting Demo {self.demo_id} Simulation...")
        self.env.start()
        
        while self.env.is_running():
            telem = self.env.read_telemetry()
            if not telem:
                time.sleep(0.1)
                continue
                
            q_all = [q[0] for q in self.env.sim.q if not np.isnan(q[0])]
            if not q_all: break
            avg_x = np.mean(q_all)
            
            with self.env.lock:
                if self.demo_id == 2:
                    if avg_x > 15 and not self.retreat_triggered:
                        print("AI: NOT SURE! Wall detected. Retreating to Base!")
                        self.retreat_triggered = True
                        self.env.sim.algo = 3
                        
                        # Completely freeze all physics forces
                        self.env.sim.c1_a = 0.0
                        self.env.sim.c2_a = 0.0
                        self.env.sim.c1_g = 0.0
                        self.env.sim.c2_g = 0.0
                        self.env.sim.c1_b = 0.0
                        self.env.sim.c2_b = 0.0
                        
                        # Manually force all drones to glide backward perfectly at 5 m/s
                        for i in range(self.n):
                            self.env.sim.p[i] = [-5.0, 0.0]
                        
                    elif not self.retreat_triggered and avg_x > -15:
                        self.env.sim.algo = 2
                        
                    if self.retreat_triggered and avg_x < -40:
                        print("Swarm successfully retreated to base. Ending demo.")
                        self.env.running = False
                        
            time.sleep(0.5)
            
        self.env.join()
        print(f"Demo {self.demo_id} Simulation Complete!")

if __name__ == "__main__":
    h2 = DemoHarness(demo_id=2, output_json="demo_2_refusal.json", num_agents=8)
    h2.run_demo()
