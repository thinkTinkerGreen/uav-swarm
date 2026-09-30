import threading
import time
import numpy as np
import copy
import json
from simulator import FlockSimulator
from metrics import Metrics
from swarm_logger import log_event

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        return super().default(obj)

class SwarmEnvironment:
    def __init__(self, num_agents=20, max_duration=10.0, trajectory_file="flight_path.json"):
        self.sim = FlockSimulator(num_agents=num_agents, dim=2, algo=1)
        self.metrics_engine = Metrics(num_agents, self.sim.math.d, self.sim.math.r)
        
        self.max_duration = max_duration
        self.dt = 0.03
        self.running = False
        
        self.metrics_history = []
        self.lock = threading.Lock()
        
        self.failsafe_triggered = False
        self.trajectory_file = trajectory_file
        self.trajectory_log = []
        self.sensor_noise_std = 0.5 
        
    def start(self):
        self.running = True
        self.obstacles = self.sim.obstacles
        self._thread = threading.Thread(target=self._kinematic_loop)
        self._thread.start()
        
    def join(self):
        if self._thread:
            self._thread.join()
        
        if self.trajectory_file:
            with open(self.trajectory_file, "w") as f:
                json.dump({
                    "obstacles": self.obstacles,
                    "frames": self.trajectory_log
                }, f, cls=NumpyEncoder)

    def _kinematic_loop(self):
        start_time = time.time()
        step_count = 0
        
        while self.running and (time.time() - start_time) < self.max_duration:
            loop_start = time.time()
            
            with self.lock:
                if self.failsafe_triggered:
                    self.sim.p *= 0.0 
                    
                self.sim.step(dt=self.dt)
                
                noisy_q = self.sim.q + np.random.normal(0, self.sensor_noise_std, self.sim.q.shape)
                noisy_p = self.sim.p + np.random.normal(0, 0.1, self.sim.p.shape)
                
                metrics = self.metrics_engine.compute_all(noisy_q, noisy_p)
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 10:
                    self.metrics_history.pop(0)
                    
                self.trajectory_log.append({
                    "time": step_count * self.dt,
                    "algo": self.sim.algo,
                    "squad_leaders": copy.deepcopy(self.sim.squad_leaders),
                    "q": self.sim.q.tolist()
                })
                    
            step_count += 1
            elapsed = time.time() - loop_start
            time.sleep(max(0, self.dt - elapsed))
            
        self.running = False

    def is_running(self):
        return self.running

    def read_telemetry(self):
        with self.lock:
            if len(self.metrics_history) == 0:
                return None
            return copy.deepcopy(self.metrics_history)
            
    def apply_command(self, decision):
        with self.lock:
            fn = decision.get("fn")
            if fn == "switch_algorithm":
                target = decision.get("args", {}).get("target_algo", 2)
                self.sim.algo = target
                self.failsafe_triggered = False
                log_event("SLM_DECISION", decision="SWITCH", target=target)
            elif fn == "adjust_squad_gains":
                self.sim.algo = 1
                self.failsafe_triggered = False
                log_event("SLM_DECISION", decision="ADJUST")
            elif fn == "not_sure":
                self.failsafe_triggered = True
                self.sim.algo = 3
                log_event("SLM_DECISION", decision="HOLD")
