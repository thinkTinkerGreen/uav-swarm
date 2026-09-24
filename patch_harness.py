import re

with open("harness.py", "r") as f:
    content = f.read()

# Update init
content = re.sub(r'def __init__\(self, num_agents=20, backend="mock", max_duration=10\.0, record_traces=True\):', 
                 'def __init__(self, num_agents=20, backend="mock", max_duration=10.0, record_traces=True, run_id="unknown"):', 
                 content)

content = re.sub(r'self\.record_traces = record_traces', 
                 'self.record_traces = record_traces\n        self.run_id = run_id', 
                 content)

# Update trace recording
trace_recording = """
            # Record the trace for future fine-tuning
            if self.record_traces:
                trace = {
                    "run_id": self.run_id,
                    "metrics": latest_metrics,
                    "decision": decision,
                    "latency_sec": latency
                }
"""

content = re.sub(r'            # Record the trace for future fine-tuning.*?\"latency_sec\": latency\n                }', trace_recording.strip('\n'), content, flags=re.DOTALL)

with open("harness.py", "w") as f:
    f.write(content)
