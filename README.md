# UAV Swarm Supervisory Controller

A hierarchical UAV swarm agent simulation based on the Olfati-Saber flocking laws and Reynolds' boids rules. This project isolates the hard real-time kinematic swarm stabilization from the high-level, AI-driven reasoning using a dual-loop concurrency boundary.

## Architecture

1. **Inner Kinematic Loop (33Hz - 100Hz):** Executes closed-form double-integrator dynamics for cohesive flocking, obstacle avoidance, and navigational tracking.
2. **Outer Supervisory Loop (1Hz Async):** Formats telemetry and polls a Small Language Model (SLM) or Frontier Model (Gemini API) to diagnose the swarm's state and adjust tuning parameters to prevent fragmentation or enforce failsafe holds.

## Components

- `simulator.py`: Kinematic physics engine (supports 2D and 3D).
- `metrics.py`: Computes formal verification metrics (Semi-Connectivity $C^*$, Deviation Energy $\tilde{E}$, Velocity Mismatch $\tilde{K}$).
- `agent.py`: The SLM endpoint using strict JSON enforcement.
- `harness.py`: The multi-threaded dual-loop execution environment.
- `visualize.py`: Matplotlib animation generator.
- `test_flock.py`: Test-Driven Development (TDD) baseline suite.

## Setup

1. Make sure you have python installed. Use `uv` or `venv` to create a virtual environment.
2. Install the dependencies:
   ```bash
   pip install numpy matplotlib requests google-genai python-dotenv
   ```
3. Copy the example environment file and add your Gemini API key:
   ```bash
   cp .env.example .env
   # Edit .env to include your GEMINI_API_KEY
   ```

## Usage

### Run the Simulation

You can run the simulation and generate an animated `.gif` of the flocking behavior:
```bash
python visualize.py
```

### Run the Dual-Loop Harness

To run the harness directly and record training traces (useful for LoRA fine-tuning a small local model):
```bash
python harness.py
```
This will append the state metrics and the SLM decisions to `training_traces.jsonl`.

### Run Tests

To verify the agent correctly identifies fragmentation (Algorithm 1 Refusal) and triggers safety holds (Honest Failure):
```bash
python test_flock.py
```

## SLM Stand-In

The `SupervisoryAgent` currently supports three backends:
- `"mock"`: Deterministic rule-based engine for stable testing.
- `"gemini"`: Uses the `google.genai` SDK acting as the frontier "teacher" model.
- `"ollama"`: Queries `http://localhost:11434` for a locally deployed model like `qwen3.5:0.8b`.

Toggle the backend inside `harness.py` or `test_flock.py` as needed.
