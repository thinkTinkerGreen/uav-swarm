import time
import os
from harness import Harness
from simulator_patch import apply_scenario

def run_mobile_test():
    print("==============================================")
    print("📱 UAV Swarm Mobile CPU Benchmark (Termux)")
    print("==============================================")
    print("Initializing LLM and allocating RAM...")
    
    # We use a short 5.0 second simulation to quickly test latency
    harness = Harness(
        num_agents=15, 
        backend="native", 
        max_duration=5.0, 
        record_traces=False, 
        trajectory_file="mobile_flight.json"
    )
    
    # Setup a challenging scenario to force the model to think (Dense Obstacle Field)
    apply_scenario(harness.sim, 2)
    
    print("\n🚀 Commencing Headless Flight...")
    print("Executing physics and AI loops (No GUI)...\n")
    
    start_time = time.time()
    
    # Run the simulation
    harness.run()
    
    total_time = time.time() - start_time
    
    print("\n==============================================")
    print("🏁 Flight Complete!")
    print(f"Total Wall-Clock Time: {total_time:.2f} seconds")
    
    if os.path.exists("mobile_flight.json"):
        print(f"Flight Data Saved: mobile_flight.json ({os.path.getsize('mobile_flight.json') / 1024:.2f} KB)")
    
    print("==============================================")
    print("To visualize this flight, transfer 'mobile_flight.json' to a PC")
    print("and run: python plot_scenarios.py --input mobile_flight.json")

if __name__ == "__main__":
    run_mobile_test()
