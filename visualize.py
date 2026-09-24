import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from simulator import FlockSimulator

def visualize_flock(num_agents=20, steps=200, dt=0.03, algo=2):
    sim = FlockSimulator(num_agents=num_agents, dim=2, algo=algo)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 150)
    ax.set_title(f"UAV Swarm Flight (N={num_agents}, Algo={algo})")
    
    scat = ax.scatter(sim.q[:, 0], sim.q[:, 1], c='blue', s=20, marker='^')
    
    target_marker, = ax.plot([], [], 'rx', markersize=10, label='Gamma Target')
    ax.legend(loc='upper right')
    
    def update(frame):
        sim.step(dt=dt)
        scat.set_offsets(sim.q)
        if sim.algo >= 2:
            target_marker.set_data([sim.q_r[0]], [sim.q_r[1]])
        else:
            target_marker.set_data([], [])
        return scat, target_marker

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=50, blit=True)
    ani.save("flock_simulation.gif", writer="pillow", fps=20)
    print("Saved flock_simulation.gif")

if __name__ == "__main__":
    print("Generating simulation animation...")
    visualize_flock()
