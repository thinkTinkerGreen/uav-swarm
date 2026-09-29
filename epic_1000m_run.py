import time
import os
import numpy as np
from harness import Harness
from llm_client import LLMClient

class EpicHarness(Harness):
    def __init__(self):
        super().__init__(num_agents=15, backend="native", max_duration=150.0, record_traces=False, trajectory_file="epic_flight.json")
        self.client = LLMClient(backend="native")
        
        self.sim.q = np.zeros((15, 2))
        for i in range(15):
            self.sim.q[i] = [-50 + (i%5)*15, (i//5)*15 - 15]
            
        self.sim.p = np.zeros((15, 2))
        self.sim.q_r = np.ones(2) * 0.0
        self.sim.q_r[0] = 1000.0
        
        self.sim.obstacles = [{'type': 'sphere', 'center': np.array([500.0, 0.0]), 'radius': 150.0}]
        self.sim.algo = 2 
        
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
                
            metrics = telem[-1]
            avg_x = np.mean([q[0] for q in self.env.sim.q])
            
            if avg_x > 950:
                print(f"Swarm successfully reached destination! Ending simulation.")
                self.env.running = False
                break
                
            decision = self.client.get_decision(telem)
            fn = decision.get("fn", "not_sure")
            
            with self.env.lock:
                if fn == "switch_algorithm" and not self.split_triggered and avg_x > 250:
                    print(f"[T={metrics['time']:.1f}] AI TRIGGERED SPLIT! Splitting around obstacle...")
                    self.split_triggered = True
                    targets = np.zeros((15, 2))
                    for i in range(15):
                        if i < 7:
                            targets[i] = [600.0, 250.0]
                        else:
                            targets[i] = [600.0, -250.0]
                    self.env.sim.q_r = targets
                    
                elif fn == "adjust_squad_gains" and self.split_triggered and not self.regroup_triggered and avg_x > 550:
                    print(f"[T={metrics['time']:.1f}] AI TRIGGERED REGROUP! Bringing swarm back together...")
                    self.regroup_triggered = True
                    self.env.sim.q_r = np.array([1000.0, 0.0])
                    
            time.sleep(0.5)
            
        self.env.join()
        print("Plotting epic cinematic flight...")
        os.system(".venv/bin/python plot_epic.py")
        print("Plotting complete!")

if __name__ == "__main__":
    h = EpicHarness()
    h.run_epic()
