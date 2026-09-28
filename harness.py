from swarm_env import SwarmEnvironment
from controller import SwarmController

class Harness:
    """
    Facade class maintaining backward compatibility for older scripts.
    It wraps the decoupled SwarmEnvironment and SwarmController.
    """
    def __init__(self, num_agents=20, backend="mock", max_duration=10.0, record_traces=True, run_id="unknown", trajectory_file="flight_path.json", trace_file="training_traces.jsonl"):
        self.env = SwarmEnvironment(num_agents=num_agents, max_duration=max_duration, trajectory_file=trajectory_file)
        self.controller = SwarmController(self.env, backend=backend, record_traces=record_traces, run_id=run_id, trace_file=trace_file)
        
        # Backward compatibility properties
        self.sim = self.env.sim
        self.metrics_engine = self.env.metrics_engine
        
    @property
    def failsafe_triggered(self):
        return self.env.failsafe_triggered
        
    def run(self):
        self.env.start()
        self.controller.start()
        self.env.join()
        self.controller.join()
        print("Simulation complete.")

if __name__ == "__main__":
    harness = Harness(num_agents=20, backend="mock", max_duration=3.0)
    harness.run()
