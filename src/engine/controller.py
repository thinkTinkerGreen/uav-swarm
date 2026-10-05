import threading
import time
import json
from src.ai.llm_client import LLMClient
from src.ai.tool_wrapper import SwarmToolWrapper

class SwarmController:
    """
    The asynchronous controller. Acts as the reasoning agent that issues
    formal tool calls to the SwarmToolWrapper.
    """
    def __init__(self, env, backend="mock", record_traces=True, run_id="unknown", trace_file="training_traces.jsonl"):
        self.tools = SwarmToolWrapper(env)
        self.env = env # Keep reference to check is_running()
        self.client = LLMClient(backend=backend)
        self.record_traces = record_traces
        self.run_id = run_id
        self.trace_file = trace_file
        
    def start(self):
        self._thread = threading.Thread(target=self._supervisory_loop)
        self._thread.start()
        
    def join(self):
        if self._thread:
            self._thread.join()

    def _supervisory_loop(self):
        while self.env.is_running():
            time.sleep(1.0) # Poll every 1 second
            
            # 1. Tool Call: Read Result
            telemetry_result = self.tools.read_result()
            if not telemetry_result.success:
                continue
                
            latest_metrics = telemetry_result.data
            
            # Since the client currently expects a list for history, wrap it
            history = [latest_metrics] 
                
            start_poll = time.time()
            decision = self.client.get_decision(history)
            latency = time.time() - start_poll
            
            if self.record_traces:
                trace = {
                    "run_id": self.run_id,
                    "metrics": latest_metrics,
                    "decision": decision,
                    "latency_sec": latency
                }
                with open(self.trace_file, "a") as f:
                    f.write(json.dumps(trace) + "\n")
            
            if latency > 0.4:
                print(f"[Warning] SLM latency {latency*1000:.1f}ms exceeds 400ms constraint.")
            print(f"[SLM] Decision: {decision}")
            
            # 2. Tool Call: Execute Command
            fn = decision.get("fn", "unknown")
            args = decision.get("args", {})
            cmd_result = self.tools.execute_command(fn, args)
            
            if not cmd_result.success:
                print(f"[Error] Tool execution failed: {cmd_result.error}")
