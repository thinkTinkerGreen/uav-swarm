import time
import os
import numpy as np
from harness import Harness
from llm_client import LLMClient

class EpicHarness(Harness):
    def __init__(self):
        super().__init__(num_agents=15, backend="native", max_duration=200.0, record_traces=False, trajectory_file="epic_flight.json")
        self.client = LLMClient(backend="native")
        
        self.sim.q = np.zeros((15, 2))
        for i in range(15):
            self.sim.q[i] = [-50 + (i%5)*15, (i//5)*15 - 15]
            
        self.sim.p = np.zeros((15, 2))
        self.sim.q_r = np.zeros((15, 2))
        for i in range(15):
            self.sim.q_r[i] = [1050.0, self.sim.q[i][1]]
        self.sim.p_r = np.array([7.0, 0.0]) # Fast speed for the 1km run!
        
        # Massive 300m wide obstacle in the middle
        self.sim.obstacles = [{'type': 'sphere', 'center': np.array([500.0, 0.0]), 'radius': 150.0}]
        self.sim.algo = 1 
        
        self.split_triggered = False
        self.regroup_triggered = False

    def run_epic(self):
        print("Starting Epic 1000m Flight...")
        self.env.start()
        
        while self.env.is_running():
            telem = self.env.read_telemetry()
            if not telem:
                time.sleep(0.1)
                continue
                
            q_all = [q[0] for q in self.env.sim.q if not np.isnan(q[0])]
            if not q_all: break
            avg_x = np.mean(q_all)
            
            if avg_x > 1000:
                print("Swarm successfully reached 1000m destination! Ending simulation.")
                self.env.running = False
                break
                
            decision = self.client.get_decision(telem)
            fn = decision.get("fn", "not_sure")
            
            with self.env.lock:
                if fn == "switch_algorithm" and not self.split_triggered and avg_x > 250:
                    print(f"AI TRIGGERED SPLIT! Splitting around massive 300m obstacle...")
                    self.split_triggered = True
                    self.env.sim.algo = 2
                    targets = np.zeros((15, 2))
                    for i in range(15):
                        targets[i] = [600.0, 200.0] if self.env.sim.q[i][1] >= 0 else [600.0, -200.0]
                    self.env.sim.q_r = targets
                    self.env.sim.p_r = np.array([6.0, 0.0])
                    
                elif fn == "adjust_squad_gains" and self.split_triggered and not self.regroup_triggered and avg_x > 600:
                    print(f"AI TRIGGERED REGROUP! Bringing swarm back together for final approach...")
                    self.regroup_triggered = True
                    self.env.sim.algo = 1
                    targets = np.zeros((15, 2))
                    for i in range(15):
                        targets[i] = [1050.0, self.env.sim.q[i][1]]
                    self.env.sim.q_r = targets
                    self.env.sim.p_r = np.array([7.0, 0.0])
                    
            time.sleep(0.5)
            
        self.env.join()
        print("Simulation complete! You can now plot epic_flight.json")

if __name__ == "__main__":
    h = EpicHarness()
    h.run_epic()
