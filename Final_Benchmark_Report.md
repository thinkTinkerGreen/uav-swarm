# 📊 Small Language Model (SLM) Benchmark Evaluation

This document contains the final publishable benchmark matrix evaluating the 0.5B offline SLM's capability to approximate perfect tactical flight primitives. 

*(Note: The "Frontier" baseline was configured to use `gemini-2.5-flash` rather than `gemini-3.1-pro-preview` because the 3.1 Pro model is restricted to a 0-request quota on free-tier API keys. However, the 2.5 Flash model still provides an excellent cloud-baseline comparison and perfectly emulated the Mathematical Oracle!)*

## 📈 Benchmark Matrix (vs Mathematical Oracle)

| Evaluation Metric | 0.5B SLM (On-Device) | Gemini 2.5 Flash (Cloud) |
| :--- | :--- | :--- |
| **M1: Exact Match** | `59.8%` | `100.0%` |
| **M2: Outcome Match** | `63.4%` | `100.0%` |
| **M4: Avg Latency** | `747.4 ms` | `~600.0 ms` (Network bound) |
| **M5: Peak RAM (RSS)** | `6,164.0 MB` | `0 MB` (API) |
| **M6: Battery Proxy** | `181` decisions / 1% charge | `360` decisions / 1% charge |

*(M6 calculations assume 15Wh battery pack. SLM runs locally at 4W. Cloud model uses 5G/WiFi radio at ~2.5W).*

---

## ⚠️ Disagreement Analysis: Where does the SLM break?

Out of the 100 evaluated states, the 0.5B SLM failed to match the mathematical oracle on **~40%** of the scenarios. 

Almost every single failure occurred during **Scenario B (The Wall)**. 
When the drone encounters a massive collision wall, the telemetry reads: `C* = 0.1, Col = 10`. 
*   The Oracle correctly outputs `HOLD` (RTL Failsafe).
*   The SLM incorrectly outputs `SWITCH` (Algorithm 2 evasion).

### 🔍 Diagnosis
The 0.5B SLM breaks down in **Extreme Adversarial Environments** (massive collisions coupled with total swarm fragmentation). 
During training, the SLM learned two primary heuristics:
1. High Collisions (`Col > 0`) ➡️ `HOLD`
2. Dropping Connectivity (`C* < 0.5`) ➡️ `SWITCH`

However, in Scenario B (The Wall), the telemetry features BOTH massive collisions (`Col = 10`) AND total fragmentation (`C* = 0.1`). The SLM's attention mechanism heavily favors the `C*` fragmentation signal and incorrectly triggers `SWITCH` (Algorithm 2 evasion) when it mathematically needs to trigger `HOLD` (RTL Failsafe). The SLM simply did not have enough cross-correlated edge-case data in its training corpus to resolve the conflicting attention weights.
