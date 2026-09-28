import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import argparse

def replay_scenario(filepath, output_file):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    print(f"Loading {filepath}...")
    with open(filepath, "r") as f:
        data = json.load(f)
    
    obstacles = data.get("obstacles", [])
    frames = data.get("frames", [])
    
    if not frames:
        print("No flight frames found.")
        return

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title(f"UAV Swarm Replay: {output_file}")
    ax.set_xlim(0, 100) 
    ax.set_ylim(0, 100)
    ax.set_facecolor('#1e1e2e') 
    
    for obs in obstacles:
        if obs['type'] == 'sphere':
            circle = plt.Circle(obs['center'], obs['radius'], color='red', alpha=0.3)
            ax.add_patch(circle)
        elif obs['type'] == 'wall':
            p = np.array(obs['point'])
            n = np.array(obs['normal'])
            tangent = np.array([-n[1], n[0]])
            p1 = p + tangent * 50
            p2 = p - tangent * 50
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='red', linewidth=3)
            
    scatter = ax.scatter([], [], s=50, zorder=5)
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=12)
    algo_text = ax.text(0.02, 0.90, '', transform=ax.transAxes, color='white', fontsize=12)
    
    def init():
        scatter.set_offsets(np.empty((0, 2)))
        time_text.set_text('')
        algo_text.set_text('')
        return scatter, time_text, algo_text

    def update(frame_idx):
        frame = frames[frame_idx]
        q = np.array(frame["q"])
        algo = frame["algo"]
        
        scatter.set_offsets(q)
        
        if algo == 1: 
            color = '#F9E076'
            algo_name = "Reynolds"
        elif algo == 2: 
            color = '#4D96FF'
            algo_name = "Alpha-Lattice"
        else: 
            color = '#FF4C4C'
            algo_name = "EMERGENCY HOLD"
            
        scatter.set_color(color)
        time_text.set_text(f'Time: {frame["time"]:.2f}s')
        algo_text.set_text(f'Algorithm: {algo} ({algo_name})')
        
        return scatter, time_text, algo_text

    print(f"Generating animation {output_file}...")
    ani = animation.FuncAnimation(
        fig, update, frames=len(frames),
        init_func=init, blit=True, interval=30 
    )
    
    ani.save(output_file, writer='pillow', fps=30)
    print(f"✅ Animation successfully saved as {output_file}!")
    plt.close(fig)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="flight_path.json")
    parser.add_argument("--output", default="swarm_flight.gif")
    args = parser.parse_args()
    replay_scenario(args.input, args.output)
