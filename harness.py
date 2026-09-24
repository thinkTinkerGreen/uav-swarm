import threading
import time
import numpy as np
import copy
import json
from simulator import FlockSimulator
from metrics import Metrics
from agent import SupervisoryAgent

class Harness:
    def __init__(self, num_agents=20, backend="mock", max_duration=10.0, record_traces=True):
        self.sim = FlockSimulator(num_agents=num_agents, dim=2, algo=1) # Start with Alg 1 to test refusal
        self.metrics_engine = Metrics(num_agents, self.sim.math.d, self.sim.math.r)
        self.agent = SupervisoryAgent(backend=backend)
        
        self.max_duration = max_duration
        self.running = False
        self.dt = 0.03 # ~33 Hz
        
        self.metrics_history = []
        self.lock = threading.Lock()
        
        self.failsafe_triggered = False
        self.record_traces = record_traces
        
    def kinematic_loop(self):
        """Inner Loop: 33 Hz - 100 Hz"""
        start_time = time.time()
        step_count = 0
        
        while self.running and (time.time() - start_time) < self.max_duration:
            loop_start = time.time()
            
            with self.lock:
                self.sim.step(dt=self.dt)
                metrics = self.metrics_engine.compute_all(self.sim.q, self.sim.p)
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 10:
                    self.metrics_history.pop(0)
                    
            step_count += 1
            
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.dt - elapsed)
            time.sleep(sleep_time)
            
        self.running = False

    def supervisory_loop(self):
        """Outer Loop: 1 Hz Asynchronous"""
        while self.running:
            time.sleep(1.0) # Poll every 1 second
            
            with self.lock:
                if len(self.metrics_history) == 0:
                    continue
                history_copy = copy.deepcopy(self.metrics_history)
                latest_metrics = history_copy[-1]
                
            start_poll = time.time()
            decision = self.agent.get_decision(history_copy)
            latency = time.time() - start_poll
            
            # Record the trace for future fine-tuning
            if self.record_traces:
                trace = {
                    "metrics": latest_metrics,
                    "decision": decision,
                    "latency_sec": latency
                }
                with open("training_traces.jsonl", "a") as f:
                    f.write(json.dumps(trace) + "\n")
            
            with self.lock:
                if latency > 0.4:
                    print(f"[Warning] SLM latency {latency*1000:.1f}ms exceeds 400ms constraint.")
                
                print(f"[SLM] Decision: {decision}")
                
                if decision.get("fn") == "switch_algorithm":
                    target = decision.get("args", {}).get("target_algo", 2)
                    self.sim.algo = target
                elif decision.get("fn") == "not_sure":
                    self.failsafe_triggered = True
                    self.sim.algo = 2

    def run(self):
        self.running = True
        t_kinematic = threading.Thread(target=self.kinematic_loop)
        t_supervisory = threading.Thread(target=self.supervisory_loop)
        
        t_kinematic.start()
        t_supervisory.start()
        
        t_kinematic.join()
        t_supervisory.join()
        
        print("Simulation complete.")

if __name__ == "__main__":
    harness = Harness(num_agents=20, backend="mock", max_duration=3.0)
    harness.run()
