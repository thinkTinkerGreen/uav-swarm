import matplotlib.pyplot as plt
import matplotlib.animation as animation
from simulator import FlockSimulator
from simulator_patch import apply_scenario

def create_gif(scenario_id, num_agents=20, steps=100, dt=0.03):
    sim = FlockSimulator(num_agents=num_agents, dim=2, algo=2)
    apply_scenario(sim, scenario_id)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 150)
    ax.set_title(f"Scenario {scenario_id} (N={num_agents})")
    
    scat = ax.scatter(sim.q[:, 0], sim.q[:, 1], c='blue', s=20, marker='^')
    target_marker, = ax.plot([], [], 'rx', markersize=10, label='Gamma Target')
    
    # draw obstacles
    if hasattr(sim, 'obstacles'):
        for obs in sim.obstacles:
            if obs['type'] == 'sphere':
                circle = plt.Circle((obs['center'][0], obs['center'][1]), obs['radius'], color='r', fill=False)
                ax.add_patch(circle)
            elif obs['type'] == 'wall':
                # basic line for wall
                if obs['normal'][1] != 0:
                    y = obs['point'][1]
                    ax.axhline(y, color='r', linestyle='--')
                elif obs['normal'][0] != 0:
                    x = obs['point'][0]
                    ax.axvline(x, color='r', linestyle='--')

    def update(frame):
        sim.step(dt=dt)
        scat.set_offsets(sim.q)
        if hasattr(sim, 'q_r'):
            target_marker.set_data([sim.q_r[0]], [sim.q_r[1]])
        return scat, target_marker

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=50, blit=True)
    filename = f"scenario_{scenario_id}.gif"
    ani.save(filename, writer="pillow", fps=20)
    print(f"Saved {filename}")

if __name__ == "__main__":
    for sid in [1, 2, 3, 4]:
        print(f"Generating GIF for scenario {sid}...")
        create_gif(sid)
