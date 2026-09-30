import json

def build_html():
    with open("flight_data.json", "r") as f:
        flight_data = f.read()

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>3D UAV Swarm Flight Viewer</title>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #87CEEB; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        #ui {{ position: absolute; top: 15px; left: 15px; background: rgba(0,0,0,0.8); color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 250px; }}
        h3 {{ margin: 0 0 15px 0; color: #4CAF50; border-bottom: 1px solid #555; padding-bottom: 10px; }}
        .stat {{ font-size: 14px; margin-bottom: 8px; display: flex; justify-content: space-between; }}
        .stat span {{ font-weight: bold; }}
        button {{ margin-top: 15px; padding: 10px; cursor: pointer; background: #2196F3; color: white; border: none; border-radius: 4px; font-weight: bold; width: 100%; transition: background 0.2s; }}
        button:hover {{ background: #1976D2; }}
        
        #ai-status {{ position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 30px; font-size: 24px; font-weight: bold; border: 2px solid #4CAF50; text-align: center; box-shadow: 0 0 20px rgba(0,0,0,0.5); }}
    </style>
</head>
<body>
    <div id="ui">
        <h3>🚁 Swarm Telemetry</h3>
        <div class="stat">Frame: <span id="frameCounter">0</span></div>
        <div class="stat">Total: <span id="totalFrames">0</span></div>
        <button id="camToggle">Enable Free Cam</button>
        <button id="playPause">Pause</button>
    </div>
    
    <div id="ai-status">SLM DECISION: <span id="decisionText" style="color: #4CAF50;">ADJUST</span></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        const flightData = {flight_data};
        
        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog(0x87CEEB, 20, 200);
        
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.enabled = false;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
        dirLight.position.set(100, 200, 50);
        dirLight.castShadow = true;
        dirLight.shadow.camera.top = 100;
        dirLight.shadow.camera.bottom = -100;
        dirLight.shadow.camera.left = -100;
        dirLight.shadow.camera.right = 100;
        scene.add(dirLight);

        // Ground Grid
        const gridHelper = new THREE.GridHelper(400, 80, 0x000000, 0x000000);
        gridHelper.material.opacity = 0.1;
        gridHelper.material.transparent = true;
        scene.add(gridHelper);
        
        const groundGeo = new THREE.PlaneGeometry(400, 400);
        const groundMat = new THREE.MeshLambertMaterial({{ color: 0x90EE90 }});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        // Obstacles (The Wall)
        const obsGeo = new THREE.CylinderGeometry(10, 10, 30, 32);
        const obsMat = new THREE.MeshLambertMaterial({{ color: 0xFF3333, transparent: true, opacity: 0.8 }});
        flightData.obstacles.forEach(obs => {{
            const mesh = new THREE.Mesh(obsGeo, obsMat);
            mesh.position.set(obs.x, 15, -obs.y);
            mesh.castShadow = true;
            scene.add(mesh);
        }});

        // Drones
        const drones = [];
        const createDrone = () => {{
            const group = new THREE.Group();
            
            // Body
            const bodyGeo = new THREE.BoxGeometry(2.0, 0.6, 2.0);
            const bodyMat = new THREE.MeshLambertMaterial({{ color: 0x424242 }});
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            body.name = "body"; // Tag it so we can change color later
            group.add(body);
            
            // Propeller arms
            const armGeo = new THREE.CylinderGeometry(0.15, 0.15, 3.5);
            const armMat = new THREE.MeshLambertMaterial({{ color: 0x212121 }});
            const arm1 = new THREE.Mesh(armGeo, armMat);
            arm1.rotation.x = Math.PI / 2;
            arm1.rotation.y = Math.PI / 4;
            const arm2 = new THREE.Mesh(armGeo, armMat);
            arm2.rotation.x = Math.PI / 2;
            arm2.rotation.y = -Math.PI / 4;
            group.add(arm1);
            group.add(arm2);

            scene.add(group);
            return group;
        }};

        for(let i=0; i<8; i++) {{
            drones.push(createDrone());
        }}

        let currentFrame = 0;
        let isPlaying = true;
        let isFollowCam = true;
        const totalFrames = flightData.frames.length;
        document.getElementById('totalFrames').innerText = totalFrames;

        document.getElementById('playPause').addEventListener('click', (e) => {{
            isPlaying = !isPlaying;
            e.target.innerText = isPlaying ? "Play" : "Pause";
        }});
        
        document.getElementById('camToggle').addEventListener('click', (e) => {{
            isFollowCam = !isFollowCam;
            controls.enabled = !isFollowCam;
            e.target.innerText = isFollowCam ? "Enable Follow Cam (Leader)" : "Enable Free Cam";
        }});

        const decisionText = document.getElementById('decisionText');
        const aiStatusBox = document.getElementById('ai-status');

        function animate() {{
            requestAnimationFrame(animate);

            if (isPlaying && currentFrame < totalFrames) {{
                const frameObj = flightData.frames[currentFrame];
                const frameData = frameObj.drones;
                
                // Update AI UI
                decisionText.innerText = frameObj.decision;
                decisionText.style.color = frameObj.color;
                aiStatusBox.style.borderColor = frameObj.color;
                
                let currentLeader = null;
                
                frameData.forEach((dData, idx) => {{
                    const drone = drones[idx];
                    drone.position.set(dData.x, 10, -dData.y); // Height 10m
                    drone.rotation.y = -dData.yaw; 
                    
                    // Dynamic Leader Coloring
                    const bodyMesh = drone.getObjectByName("body");
                    if (dData.is_leader) {{
                        bodyMesh.material.color.setHex(0xFFC107); // Gold Leader
                        currentLeader = dData;
                    }} else {{
                        bodyMesh.material.color.setHex(0x424242); // Grey Follower
                    }}
                }});

                if (isFollowCam && currentLeader) {{
                    const distance = 25;
                    const height = 15;
                    const camX = currentLeader.x - Math.cos(currentLeader.yaw) * distance;
                    const camZ = -currentLeader.y + Math.sin(currentLeader.yaw) * distance;
                    
                    camera.position.lerp(new THREE.Vector3(camX, 10 + height, camZ), 0.1);
                    const target = new THREE.Vector3(currentLeader.x, 10, -currentLeader.y);
                    camera.lookAt(target);
                    controls.target.copy(target);
                }} else if (!isFollowCam) {{
                    controls.update();
                }}

                currentFrame++;
                document.getElementById('frameCounter').innerText = currentFrame;
            }} else if (currentFrame >= totalFrames) {{
                currentFrame = 0;
            }}

            renderer.render(scene, camera);
        }}

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        animate();
    </script>
</body>
</html>
"""
    with open("flight_viewer.html", "w") as f:
        f.write(html)
        
    print("Successfully built flight_viewer.html with Dynamic Leader Election!")

if __name__ == "__main__":
    build_html()
