---
name: uav-swarm-architecture
description: >-
  Core architectural knowledge base for the Edge SLM UAV Swarm project. 
  Use this skill to quickly understand the physics engine, the math (Olfati-Saber), 
  the SLM prompt structure, and the hierarchical resilience protocols without needing user explanation.
---

# 🚁 UAV Swarm Architecture & Physics Engine Reference

This skill contains the compressed knowledge of the UAV Swarm system. Read this when you need to understand how the swarm operates, how it recovers from failure, or how telemetry is passed to the AI.

## 1. The Physics Math (Olfati-Saber Reynolds Flocking)
The swarm uses three core physical rules calculated per-drone, restricted by a radio communication radius ($R_{comm} = 25.0m$).
*   **$u_\alpha$ (Separation/Alignment/Cohesion):** Drones match velocities and maintain distance with neighbors within $R_{comm}$.
*   **$u_\beta$ (Obstacle Avoidance):** Drones repel from physical spheres (obstacles).
*   **$u_\gamma$ (Target Seeking):** Drones are pulled toward the global target ($q_r$). **Crucially, only Squad Leaders feel this pull.**

## 2. Telemetry Sent to the SLM (The 4 KPIs)
The physics engine calculates four metrics which are injected with Gaussian noise (to prevent overfitting) and sent to the LLM:
*   **$C^*$ (Connectivity):** $0.0 - 1.0$. Ratio of actual mesh connections to the maximum possible. Low $C^*$ means the swarm is fragmenting.
*   **$E\sim$ (Energy Deviation):** Deviation from the ideal uniform spacing.
*   **$K\sim$ (Velocity Mismatch):** The kinetic energy difference between drones. High = chaotic movement.
*   **$Col$ (Collisions):** Count of drones intersecting obstacles.

## 3. The SLM Prompt & Commands
The `qwen2.5-0.5B` model outputs exactly one word based on the telemetry:
*   **`ADJUST`:** Nominal flight. The swarm uses standard flocking rules.
*   **`SWITCH`:** Evasion flight. Obstacle avoidance ($u_\beta$) is multiplied by 5x.
*   **`HOLD`:** Complete Refusal / RTL. The swarm zeros its momentum and triggers backtracking.

## 4. Military/Enterprise Resilience Protocols
*   **Hierarchical Squads:** The swarm automatically divides into 20-drone chunks. Only Squad Leaders communicate with the Prime Commander, preventing $O(N^2)$ network flooding at 200+ scale.
*   **Gossip Protocol:** Squad Leaders continuously broadcast the target $q_r$ to their local mesh via a BFS traversal.
*   **Line of Succession:** Every Leader maintains up to 3 Deputies. If the Leader dies (Sniper), a Deputy instantly takes command.
*   **Orphan Recovery:** If a drone loses all connections ($neighbors = 0$), it reverses its velocity vector to backtrack until it regains connection.
*   **Split-Brain Demotion:** If a swarm fractures around a wall and elects two leaders, when they re-merge, the leader with the higher ID automatically demotes itself to a follower.

## 5. The Test Scenarios
*   `hero_tour`: 20-drone baseline stability.
*   `adv_a`: Split-Brain Wall (Forces fracture and merge).
*   `adv_b`: Sniper & Jammer (Kills Leader, injects 5.0m noise).
*   `armada`: 200+ Drones stress test.
*   `rtl`: Kobayashi Maru trap (Infinite collisions).
