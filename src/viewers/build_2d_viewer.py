import json

def build_2d_html():
    try:
        with open("flight_data.json", "r") as f:
            flight_data = f.read()
    except FileNotFoundError:
        print("Error: flight_data.json not found.")
        return

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Swarm 2D Tactical View</title>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #111; color: white; font-family: sans-serif; }}
        canvas {{ display: block; }}
        #ui {{ position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.8); padding: 10px; border-radius: 5px; border: 1px solid #333; }}
        .stat {{ font-size: 14px; margin-bottom: 5px; }}
        button {{ background: #2196F3; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }}
        button:hover {{ background: #1976D2; }}
    </style>
</head>
<body>
    <div id="ui">
        <h3>Radar (2D)</h3>
        <div class="stat">Frame: <span id="frameCounter">0</span></div>
        <button id="playPause">Pause</button>
    </div>
    <canvas id="radar"></canvas>
    
    <script>
        const flightData = {flight_data};
        const canvas = document.getElementById('radar');
        const ctx = canvas.getContext('2d');
        
        let width, height, scale, offsetX, offsetY;
        
        function resize() {{
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
            // Center the radar [0,0] to the middle of the screen
            offsetX = width / 2;
            offsetY = height / 2;
            scale = Math.min(width, height) / 300; // Zoom factor
        }}
        window.addEventListener('resize', resize);
        resize();

        let currentFrame = 0;
        let isPlaying = true;
        const totalFrames = flightData.frames.length;

        document.getElementById('playPause').addEventListener('click', (e) => {{
            isPlaying = !isPlaying;
            e.target.innerText = isPlaying ? "Play" : "Pause";
        }});

        function drawDrone(x, y, yaw, isLeader) {{
            const px = offsetX + x * scale;
            const py = offsetY - y * scale;
            
            ctx.save();
            ctx.translate(px, py);
            ctx.rotate(-yaw);
            
            ctx.fillStyle = isLeader ? "#FFC107" : "#4CAF50";
            ctx.beginPath();
            ctx.moveTo(6, 0);
            ctx.lineTo(-4, 4);
            ctx.lineTo(-4, -4);
            ctx.closePath();
            ctx.fill();
            ctx.restore();
        }}
        
        function drawObstacle(x, y, r) {{
            const px = offsetX + x * scale;
            const py = offsetY - y * scale;
            
            ctx.beginPath();
            ctx.arc(px, py, r * scale, 0, Math.PI*2);
            ctx.fillStyle = "rgba(255, 51, 51, 0.4)";
            ctx.fill();
            ctx.strokeStyle = "#FF3333";
            ctx.stroke();
        }}
        
        function drawReticle(x, y) {{
            const px = offsetX + x * scale;
            const py = offsetY - y * scale;
            
            ctx.beginPath();
            ctx.arc(px, py, 5, 0, Math.PI*2);
            ctx.strokeStyle = "#FFFF00";
            ctx.stroke();
        }}

        function drawStart() {{
            if (!flightData.start_point) return;
            const px = offsetX + flightData.start_point.x * scale;
            const py = offsetY - flightData.start_point.y * scale;
            
            // Draw green cone
            ctx.fillStyle = "#00FF00";
            ctx.beginPath();
            ctx.moveTo(px, py - 10);
            ctx.lineTo(px - 8, py + 10);
            ctx.lineTo(px + 8, py + 10);
            ctx.closePath();
            ctx.fill();
        }}

        function drawEnd() {{
            if (!flightData.end_point) return;
            const px = offsetX + flightData.end_point.x * scale;
            const py = offsetY - flightData.end_point.y * scale;
            
            // Draw checkered flag
            ctx.fillStyle = "white";
            ctx.fillRect(px, py - 15, 20, 15);
            ctx.fillStyle = "red";
            ctx.fillRect(px, py - 15, 10, 7.5);
            ctx.fillRect(px + 10, py - 7.5, 10, 7.5);
            
            // Flag pole
            ctx.fillStyle = "#888";
            ctx.fillRect(px - 2, py - 15, 2, 25);
        }}

        function animate() {{
            requestAnimationFrame(animate);

            if (isPlaying && currentFrame < totalFrames) {{
                ctx.clearRect(0, 0, width, height);
                
                // Draw grid
                ctx.strokeStyle = "#333";
                ctx.lineWidth = 1;
                for(let i=-200; i<=200; i+=20) {{
                    ctx.beginPath();
                    ctx.moveTo(offsetX + i*scale, 0); ctx.lineTo(offsetX + i*scale, height);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(0, offsetY + i*scale); ctx.lineTo(width, offsetY + i*scale);
                    ctx.stroke();
                }}

                // Draw Start Cone and End Flag
                drawStart();
                drawEnd();
                
                // Draw Obstacles
                flightData.obstacles.forEach(obs => {{
                    drawObstacle(obs.x, obs.y, obs.radius);
                }});
                
                const frameObj = flightData.frames[currentFrame];
                
                // Draw Reticle
                if (frameObj.target_x !== undefined) {{
                    drawReticle(frameObj.target_x, frameObj.target_y);
                }}
                
                // Draw Drones
                frameObj.drones.forEach(d => {{
                    drawDrone(d.x, d.y, d.yaw, d.is_leader);
                }});

                currentFrame++;
                document.getElementById('frameCounter').innerText = currentFrame;
            }} else if (currentFrame >= totalFrames) {{
                currentFrame = 0;
            }}
        }}

        animate();
    </script>
</body>
</html>
"""
    with open("flight_viewer_2d.html", "w") as f:
        f.write(html)
        
    print("Successfully built flight_viewer_2d.html!")

if __name__ == "__main__":
    build_2d_html()
