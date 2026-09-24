# UAV Swarm Agent - Data Generation Test Plan (V2)

**Objective:** Run the dual-loop simulation using Gemini as the frontier "Teacher" model to generate 250 high-quality `(metrics -> SLM decision)` traces. These traces will be used to LoRA fine-tune the local Qwen-0.8B student model.

## Phase 1: Scenario Definition & Edge Cases
We will systematically run batches of the following 8 scenarios to capture a wide variance of edge cases.

1. **Nominal Flight (Open Space)**
   - *Setup*: Random sparse initialization in empty space.
   - *Goal*: Swarm must consolidate, avoid fragmentation, and track a static $\gamma$-target.

2. **Dense Obstacle Field**
   - *Setup*: Swarm navigates through a field of 3-5 randomly placed spherical obstacles.
   - *Goal*: Tests the SLM's ability to switch to Algorithm 3 ($\beta$-agent tracking) and safely bypass obstacles.

3. **Corridor Squeeze**
   - *Setup*: Swarm navigates a narrow pathway between two parallel infinite walls.
   - *Goal*: Tests tight formation flying, tuning separation distances, and avoiding structural collapse.

4. **Dynamic $\gamma$-Target Tracking**
   - *Setup*: The mission objective point moves erratically during the flight.
   - *Goal*: Tests the swarm's velocity matching and the SLM's ability to hold the lattice together during high-speed turns.

5. **Agent Loss / Fault Injection**
   - *Setup*: 10% to 20% of the drones are abruptly removed mid-flight.
   - *Goal*: Tests dynamic graph reconfiguration and the SLM's recovery commands when Semi-Connectivity ($C^*$) drops instantly.

6. **Extreme Velocity Mismatch (Flash Expansion) [EDGE CASE]**
   - *Setup*: Agents are initialized extremely close together in a tight cluster.
   - *Goal*: The physical separation forces will cause a violent "flash expansion" radially outward. The SLM must rapidly adjust damping gains to prevent the swarm from exploding into regular fragmentation.

7. **Predator Evasion / Split-Rejoin Maneuver [EDGE CASE]**
   - *Setup*: A fast-moving dynamic obstacle actively intersects the swarm's path.
   - *Goal*: The swarm must split into smaller quasi-flocks to evade, and the SLM must guide them to rejoin into a single flock post-evasion.

8. **Deadlocked Geometry / Concave Traps [EDGE CASE]**
   - *Setup*: The swarm flies into a U-shaped concave obstacle while tracking a $\gamma$-target placed behind it.
   - *Goal*: This creates a mathematical conflict of tasks. The SLM must recognize the deadlock and correctly issue a `not_sure` safety hold instead of guessing.

*Note: All scenarios will be iterated across varying swarm scales ($N=10$, $N=20$, and $N=50$) to ensure the tuning rules learned are scale-invariant.*

## Phase 2: Overall Break-up (250 Total Runs)

To achieve the target of 200+ high-quality traces, we will execute 250 initial runs. Runs resulting in unrecoverable physical crashes (where the teacher fails) will be filtered out.

| Scenario | Run Count | Swarm Sizes |
| :--- | :--- | :--- |
| 1. Nominal Flight | 40 | 10, 20, 50 |
| 2. Dense Obstacle Field | 40 | 10, 20, 50 |
| 3. Corridor Squeeze | 30 | 10, 20, 50 |
| 4. Dynamic Target Tracking | 30 | 10, 20, 50 |
| 5. Agent Loss | 30 | 20, 50 |
| 6. Flash Expansion | 20 | 20, 50 |
| 7. Predator Evasion | 30 | 20, 50 |
| 8. Deadlocked Geometry | 30 | 10, 20 |
| **Total Target Runs** | **250** | |

## Phase 3: Execution & Delivery
- We will write a batch script `generate_traces.py` that loops through these scenarios.
- **Trace Capture**: The harness will save every step to `training_traces.jsonl`.
- **Filtering**: Any simulation run that ends in total unrecoverable fragmentation or severe collisions (where the frontier model failed) will be discarded.
- A clean, vetted `training_traces.jsonl` file will be produced, ready for upload to Google Colab for the Qwen-0.8B fine-tuning.
