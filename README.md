# 🚁 Autonomous UAV Swarm Controller (Edge SLM)

## 📖 Overview
This project implements a decentralized, fault-tolerant, aerospace-grade UAV swarm architecture driven entirely by a local, edge-deployed Small Language Model (SLM) (`qwen2.5-0.5B`). The system replaces rigid, hardcoded tactical controllers with a fine-tuned, natively inferencing AI capable of issuing dynamic swarm maneuvers (`ADJUST`, `SWITCH`, `HOLD`) based on chaotic, noisy telemetry data.

## ✨ Features
- **Decentralized Mesh Networking:** Implements Olfati-Saber Reynolds flocking math restricted by a local communication radius ($R_{comm}$).
- **Hierarchical Sub-Squads:** Dynamically scales to 200+ drones by fracturing the swarm into autonomous 20-drone squads, preventing latency and "rubber-banding".
- **Dynamic Leader Election:** Fully decentralized consensus. If a leader is destroyed, the orphaned swarm mathematically elects a new leader instantly.
- **Line of Succession (Deputies):** Active leaders maintain a weighted fitness score of deputies to seamlessly hand off command without pausing the mesh.
- **Gossip Protocol:** Target waypoints are broadcast across the mesh via timestamped heartbeats, ensuring split swarms don't fly backwards when they re-merge.
- **Failsafe Resiliency:** Built-in defenses against RF Jamming (Orphan Backtracking), Adversarial Spoofing (Quorum Validation), and GPS noise injection.
- **Edge AI Execution:** Runs the tactical AI strictly locally on CPU via `llama.cpp` using a highly compressed Q4 quantized model.

## 🏛️ Architecture
The architecture strictly decouples the physics engine from the AI and the visualization layer.
1. **The Physics Engine (Euler Integration):** Computes $C^*$ (Connectivity), $E\sim$ (Energy Deviation), $K\sim$ (Velocity Mismatch), and Collisions.
2. **The LLM Client:** Takes the noisy telemetry, formats it into an AI prompt, and executes local inference.
3. **The Simulation Harness:** Bridges the physics engine and the AI, injecting adversarial events (Snipers, Jammers, Walls).
4. **The 3D WebGL Engine:** An entirely decoupled Three.js HTML renderer that visualizes the JSON flight paths locally in the browser.

## 📂 Core Components
- `simulator.py`: The absolute crux of the physics. Contains the flocking math, Hierarchy generation, Gossip protocol, and Leader Election logic.
- `swarm_env.py`: The decoupled physical environment. Feeds fuzzy, Gaussian-noisy telemetry to the AI engine.
- `llm_client.py`: The native LLaMA binding interface. Connects the system to the `.gguf` SLM model.
- `export_3d_flight.py`: The Multi-Scenario Harness. Sets up the 3D world, runs the simulation, and dumps `flight_data_*.json`.
- `build_3d_viewer.py`: Reads the exported JSON and dynamically generates a standalone `flight_viewer.html` WebGL experience.
- `generate_full_training_dataset.py`: The AI data synthesizer. Generates 12,000 perfectly balanced, fuzzy/noisy rows to fine-tune the SLM.

## 🚀 How to Run Scenarios
You can run the full multi-scenario testing suite from the command line. This simulates the flight and exports the physics data to JSON.

```bash
# Example: Run the Split-Brain scenario
.venv/bin/python export_3d_flight.py --scenario adv_a

# Render the HTML Viewer
.venv/bin/python build_3d_viewer.py
```
*Note: Make sure you copy/rename the resulting `flight_data_{scenario}.json` to `flight_data.json` before building the viewer!*

## 🎬 Scenario Guide
- **`--scenario hero_tour` (The Grand Tour):** A 20-drone nominal flight path through sparse pillars. Proves baseline stability against GPS noise.
- **`--scenario adv_a` (Split-Brain Gauntlet):** A tight corridor leading into a massive wall. Forces the swarm to fracture, elect two leaders, and merge back together (triggering demotion).
- **`--scenario adv_b` (Sniper & Jammer):** Midway through the flight, the Prime Commander is deleted and a 5.0m noise spike is injected. Proves the Line of Succession and Orphan Backtracking.
- **`--scenario armada` (The Scale Test):** 200+ drones in open airspace. A pure stress test of the Hierarchical Squad Topology.
- **`--scenario rtl` (Complete Refusal Trap):** The swarm is boxed in on all sides (Kobayashi Maru), forcing infinite collisions to trigger a complete `HOLD` / Return to Launch maneuver.

## 📊 Benchmarks
The repository includes a rigorous computational benchmark evaluating the local 0.5B SLM against the Gemini 2.5 Flash API (Oracle). 
When tested against 200 unseen, noisy telemetry frames, the fine-tuned model achieved **100% Exact Match Accuracy** while operating entirely offline.

The full results matrix and telemetry breakdown is stored in:
👉 `Final_Benchmark_Report.md` (located in the artifacts directory).
