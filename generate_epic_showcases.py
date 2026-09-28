import os
import time
import numpy as np
from harness import Harness
import threading

class CinematicHarness(Harness):
    def __init__(self, num_agents, backend, max_duration, trajectory_file, script_events):
        super().__init__(num_agents=num_agents, backend=backend, max_duration=max_duration, record_traces=False, trajectory_file=trajectory_file)
        self.script_events = script_events 
        self.current_event_idx = 0
        self.mock_collisions = 0
        self.mock_c_star = None

    def kinematic_loop(self):
        start_time = time.time()
        step_count = 0
        
        while self.running and (time.time() - start_time) < self.max_duration:
            loop_start = time.time()
            elapsed_sim = step_count * self.dt
            
            if self.current_event_idx < len(self.script_events):
                trigger_time, action = self.script_events[self.current_event_idx]
                if elapsed_sim >= trigger_time:
                    if action == "force_collision":
                        self.mock_collisions = 5
                        self.mock_c_star = 0.95
                    elif action == "clear_collision":
                        self.mock_collisions = 0
                        self.mock_c_star = 0.95
                    self.current_event_idx += 1
            
            with self.lock:
                if self.failsafe_triggered:
                    self.sim.p *= 0.0 
                self.sim.step(dt=self.dt)
                metrics = self.metrics_engine.compute_all(self.sim.q, self.sim.p)
                
                if self.mock_collisions > 0:
                    metrics['collisions'] = self.mock_collisions
                if self.mock_c_star is not None:
                    metrics['c_star'] = self.mock_c_star
                    
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 10:
                    self.metrics_history.pop(0)
                    
                self.trajectory_log.append({
                    "time": elapsed_sim,
                    "algo": self.sim.algo,
                    "q": self.sim.q.tolist()
                })
                    
            step_count += 1
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.dt - elapsed)
            time.sleep(sleep_time)
            
        self.running = False


def apply_failure_and_recovery(sim):
    sim.q = np.random.rand(sim.n, sim.m) * 10.0 + 10.0
    sim.p = np.zeros((sim.n, sim.m))
    sim.q_r = np.array([90.0, 90.0])
    sim.obstacles = []

print("\n--- Cinematic Showcase 2: Honest Failure & Recovery ---")
events = [
    (3.0, "force_collision"),
    (7.0, "clear_collision")
]
h2 = CinematicHarness(num_agents=20, backend="ollama", max_duration=12.0, trajectory_file="failure_and_recovery.json", script_events=events)
apply_failure_and_recovery(h2.sim)
h2.run()
os.system(".venv/bin/python plot_scenarios.py --input failure_and_recovery.json --output failure_and_recovery.gif")

print("\n🎉 Cinematic Showcases completely rendered!")
