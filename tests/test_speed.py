from llama_cpp import Llama
import time

print("Loading model into RAM...")

# This loads the C++ engine directly inside Python
llm = Llama(
    model_path="SmolLM2-135M-Instruct.Q4_K_M.gguf", 
    n_threads=2,      
    n_ctx=128,        
    verbose=False     
)

print("Running Inference...")
start_time = time.time()

# Feed it your micro-prompt
output = llm(
    "C:860|E:5|K:40|Col:0=", 
    max_tokens=2,            
    stop=["<|im_end|>"]
)

decision = output['choices'][0]['text'].strip()
latency_ms = (time.time() - start_time) * 1000

print(f"Decision: {decision}")
print(f"Latency: {latency_ms:.1f} ms")
