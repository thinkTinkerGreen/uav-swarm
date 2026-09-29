import json
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import sys
import gc

def plot_memory_safe(json_file, output_file):
    if not os.path.exists(json_file): return
    with open(json_file, "r") as f: data = json.load(f)

    frames = data["frames"][::3]
    obstacles = data.get("obstacles", [])
    tmp_dir = f"tmp_frames_{json_file.replace('.json', '')}"
    os.makedirs(tmp_dir, exist_ok=True)
    frame_paths = []
    
    total_frames = len(frames)
    print(f"Rendering {total_frames} frames to {output_file}...")
    
    try:
        for i, f in enumerate(frames):
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1}/{total_frames} frames...")
                
            fig, ax = plt.subplots(figsize=(12, 6))
            q = np.array(f["q"])
            avg_x = np.mean(q[:, 0])
            
            ax.set_xlim(avg_x - 40, avg_x + 100)
            ax.set_ylim(-60, 60)
            ax.set_aspect('equal')
            
            # Start and Finish Markers
            ax.scatter([-50], [0], c='green', marker='^', s=200, label="Start Point", zorder=2)
            ax.scatter([120], [0], c='black', marker='*', s=300, label="Destination", zorder=2)
            
            # Drone colors
            algo = f.get('algo', 1)
            d_color = "gold" if algo == 1 else ("dodgerblue" if algo == 2 else "limegreen")
            
            ax.scatter(q[:, 0], q[:, 1], c=d_color, s=50, edgecolors='black', label="Drones", zorder=3)
            
            for obs in obstacles:
                circle = plt.Circle(obs["center"], obs["radius"], color='red', alpha=0.3, zorder=2)
                ax.add_patch(circle)
                
            ai_state = "NOMINAL FLIGHT (ADJUST)" if algo == 1 else ("AVOIDANCE / SPLIT (SWITCH)" if algo == 2 else "FAILSAFE (HOLD)")
            hud_color = "darkgoldenrod" if algo == 1 else ("dodgerblue" if algo == 2 else "forestgreen")
                
            ax.text(0.02, 0.95, f"AI Decision: {ai_state}", transform=ax.transAxes, fontsize=14, color=hud_color, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
            
            ax.set_title(f"Simulation Time: {f['time']:.1f}s")
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    plot_memory_safe(args.input, args.output)
