# 🚁 SwarmAI: Decentralized Edge Command

SwarmAI is a Military-Grade, fault-tolerant autonomous drone swarm engine. It operates a 200-drone swarm using a highly optimized, locally-hosted Small Language Model (SLM) AI running entirely off-the-grid on edge devices (like Android smartphones). 

By utilizing **xVAL Integer Scaling**, **Micro-Key Anchoring**, and a custom **Hierarchical Gossip Protocol**, SwarmAI achieves sub-200ms decision latency on mobile ARM processors without any reliance on 5G, Wi-Fi, or centralized cloud compute.

---

## 📚 Key Documentation

If you are new to this repository, start by reviewing the following core documents:
1. **[Executive Showcase Report](docs/Executive_Showcase.md)** - Explains the business value, the architecture, and the benchmarking matrix. *(Perfect for C-Suite presentations).*
2. **[Product Backlog](ProductBacklog.md)** - Outlines upcoming features, including the **Tri-Tier Fault-Tolerant Consensus Mesh** (HQ -> Phone -> Drone handover).
3. **[Final Benchmark Report](docs/Final_Benchmark_Report.md)** - The raw AI evaluation output logging 100% tactical accuracy at 162ms latency on mobile hardware.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.9+ 
* `llama-cpp-python` (Compiled for your target hardware. For Termux/Android, ensure you install natively without OpenBLAS if required).
* The 135M Model: You must download `SmolLM2-135M-Instruct.Q4_K_M.gguf` into the `models/` directory.

### 1. Running the Benchmark Stress Test
To test the AI engine's latency and accuracy against the adversarial fuzzy dataset:
```bash
python evaluate_dataset.py
```
*Note: On Termux/Android, memory tracking (`psutil`) is automatically bypassed to prevent sandbox crashes.*

### 2. Generating & Viewing Scenarios
To run the full 2-minute physics engine and see the AI navigate the swarm through adversarial obstacles, use the runner scripts:

```bash
# Example: Run the Sniper & Jammer Scenario
bash scripts/run_demo.sh adv_b

# Or run ALL scenarios at once across any environment
bash scripts/run_all.sh
```
**Available Scenarios:**
* `hero_tour` - Standard obstacle course.
* `adv_a` - Split-Brain Gauntlet (Massive wall splitting the swarm).
* `adv_b` - Sniper & Jammer (The Leader drone is destroyed mid-flight).
* `armada` - Massive 200+ drone scale test.
* `rtl` - Kobayashi Maru (The swarm is completely boxed in).

Once the simulation finishes crunching the math, it will automatically generate JSON data and two viewers in the `data/` folder:
1. `data/flight_viewer.html` - A cinematic 3D WebGL renderer.
2. `data/flight_viewer_2d.html` - A top-down HTML5 Canvas tactical radar.
Simply open these files in separate browser tabs to view the demo!

---

## 🛠️ System Architecture Highlights
* **The Physics Engine:** 2D Euler Integration utilizing Olfati-Saber flocking algorithms (`src/engine/simulator.py`).
* **The AI Inference:** `llama.cpp` wrapper (`src/ai/llm_client.py`) heavily patched to spoof OS signatures on Android Termux.
* **The Data Pipeline:** Floating point telemetry is multiplied by 1,000 (xVAL) and anchored with micro-keys (e.g., `C:860|E:5`) to prevent SLM hallucination at extreme quantizations.

