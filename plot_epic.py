import json
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import sys
import gc

def plot_memory_safe(json_file, output_file):
    if not os.path.exists(json_file): 
        print(f"Error: {json_file} not found!")
        return
        
    with open(json_file, "r") as f: data = json.load(f)

    # Decimate by 5 for a very smooth but memory-safe framerate
    frames = data["frames"][::5]
    obstacles = data.get("obstacles", [])
    tmp_dir = f"tmp_frames_epic"
    os.makedirs(tmp_dir, exist_ok=True)
    frame_paths = []
    
    total_frames = len(frames)
    print(f"Rendering {total_frames} frames to {output_file}...")
    
    try:
        for i, f in enumerate(frames):
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1}/{total_frames} frames...")
                
            fig, ax = plt.subplots(figsize=(14, 7))
            q = np.array(f["q"])
            avg_x = np.mean(q[:, 0])
            
            ax.set_xlim(avg_x - 100, avg_x + 300)
            ax.set_ylim(-300, 300)
            ax.set_aspect('equal')
            
            # Start and Finish Markers
            ax.scatter([-50], [0], c='green', marker='^', s=400, label="Start Point", zorder=2)
            ax.scatter([1000], [0], c='black', marker='*', s=600, label="1000m Destination", zorder=2)
            
            # Drone colors
            algo = f.get('algo', 1)
            d_color = "gold" if algo == 1 else ("dodgerblue" if algo == 2 else "limegreen")
            
            ax.scatter(q[:, 0], q[:, 1], c=d_color, s=50, edgecolors='black', label="Drones", zorder=3)
            
            for obs in obstacles:
                circle = plt.Circle(obs["center"], obs["radius"], color='red', alpha=0.3, zorder=2)
                ax.add_patch(circle)
                
            ai_state = "NOMINAL CRUISE" if algo == 1 else ("OBSTACLE AVOIDANCE (SPLIT)" if algo == 2 else "FAILSAFE (HOLD)")
            hud_color = "darkgoldenrod" if algo == 1 else ("dodgerblue" if algo == 2 else "forestgreen")
                
            ax.text(0.02, 0.95, f"AI Decision: {ai_state}\nDistance: {avg_x:.0f} / 1000m", transform=ax.transAxes, fontsize=14, color=hud_color, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
            
            ax.set_title(f"Epic 1000m Simulation - Time: {f['time']:.1f}s")
            ax.grid(True, linestyle='--', alpha=0.5)
            
            frame_path = os.path.join(tmp_dir, f"frame_{i:04d}.png")
            plt.savefig(frame_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            gc.collect()
            frame_paths.append(frame_path)
            
    except KeyboardInterrupt:
        print("Rendering cancelled. Cleaning up...")
        shutil.rmtree(tmp_dir)
        sys.exit(0)
        
    print("Stitching frames into GIF using imageio...")
    import imageio.v2 as imageio
    with imageio.get_writer(output_file, mode='I', duration=0.1) as writer:
        for p in frame_paths: writer.append_data(imageio.imread(p))
        
    shutil.rmtree(tmp_dir)
    print(f"Successfully created {output_file}!")

if __name__ == "__main__":
    plot_memory_safe("epic_flight.json", "epic_flight.gif")
