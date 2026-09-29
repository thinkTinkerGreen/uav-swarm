import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

with open("epic_flight.json", "r") as f:
    data = json.load(f)

# Decimate frames by 10 to speed up rendering and prevent OOM
frames = data["frames"][::10]
obstacles = data.get("obstacles", [])

fig, ax = plt.subplots(figsize=(12, 6))

def animate(i):
    ax.clear()
    f = frames[i]
    q = np.array(f["q"])
    
    avg_x = np.mean(q[:, 0])
    
    # Track camera with swarm
    ax.set_xlim(avg_x - 150, avg_x + 150)
    ax.set_ylim(-300, 300)
    ax.set_aspect('equal')
    
    ax.scatter(q[:, 0], q[:, 1], c='blue', s=30, label="Drones")
    
    for obs in obstacles:
        circle = plt.Circle(obs["center"], obs["radius"], color='red', alpha=0.3)
        ax.add_patch(circle)
        
    ax.set_title(f"Epic 1000m Flight - T={f['time']:.2f}s | Swarm Pos: {avg_x:.0f}m")
    
anim = animation.FuncAnimation(fig, animate, frames=len(frames), interval=30)
anim.save("epic_flight.gif", writer='pillow', fps=30)
