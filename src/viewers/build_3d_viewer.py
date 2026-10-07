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
        scene.add(dirLight);

        // Ground Grid
        const gridHelper = new THREE.GridHelper(400, 80, 0x000000, 0x000000);
        gridHelper.material.opacity = 0.1;
        gridHelper.material.transparent = true;
        scene.add(gridHelper);
        

        // START POINT (Green Cone)
        const startGeo = new THREE.ConeGeometry(3, 10, 16);
        const startMat = new THREE.MeshLambertMaterial({{ color: 0x00FF00 }});
        const startCone = new THREE.Mesh(startGeo, startMat);
        if (flightData.start_point) {{
            startCone.position.set(flightData.start_point.x, 5, -flightData.start_point.y);
        }} else {{
            startCone.position.set(-50, 5, 0);
        }}
        scene.add(startCone);

        // TARGET RETICLE / FLAG (Red Checkered/Blob)
        const reticleGeo = new THREE.CylinderGeometry(2, 2, 8, 16);
        const reticleMat = new THREE.MeshLambertMaterial({{ color: 0xFF0000 }});
        const targetReticle = new THREE.Mesh(reticleGeo, reticleMat);
        scene.add(targetReticle);
        
        // END POINT FLAG (Checkered Box)
        if (flightData.end_point) {{
            const endGeo = new THREE.BoxGeometry(10, 10, 10);
            const endMat = new THREE.MeshLambertMaterial({{ color: 0xFFFFFF }});
            const endBox = new THREE.Mesh(endGeo, endMat);
            endBox.position.set(flightData.end_point.x, 5, -flightData.end_point.y);
            scene.add(endBox);
        }}
        
        // Ground Geo (Keep as is)

        
        const groundGeo = new THREE.PlaneGeometry(400, 400);
        const groundMat = new THREE.MeshLambertMaterial({{ color: 0x90EE90 }});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        // Obstacles
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
            
            const bodyGeo = new THREE.BoxGeometry(2.0, 0.6, 2.0);
            const bodyMat = new THREE.MeshLambertMaterial({{ color: 0x424242 }});
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            body.name = "body";
            group.add(body);
            
            scene.add(group);
            return group;
        }};

        const numDrones = (flightData.frames && flightData.frames.length > 0 && flightData.frames[0].drones) ? flightData.frames[0].drones.length : 20;
        for(let i=0; i<numDrones; i++) {{
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
                
                decisionText.innerText = frameObj.decision;
                decisionText.style.color = frameObj.color;
                aiStatusBox.style.borderColor = frameObj.color;
                
                if (frameObj.target_x !== undefined) {{
                    targetReticle.position.set(frameObj.target_x, 0.5, -frameObj.target_y);
                    targetReticle.visible = true;
                }} else {{
                    targetReticle.visible = false;
                }}
                
                let currentLeader = null;
                
                frameData.forEach((dData, idx) => {{
                    if(idx < drones.length) {{
                        const drone = drones[idx];
                        if (dData.x > 9000) {{
                            drone.visible = false;
                        }} else {{
                            drone.visible = true;
                            drone.position.set(dData.x, 10, -dData.y); 
                            drone.rotation.y = -dData.yaw; 
                            
                            const bodyMesh = drone.getObjectByName("body");
                            if (dData.is_leader) {{
                                bodyMesh.material.color.setHex(0xFFC107);
                                currentLeader = dData;
                            }} else {{
                                bodyMesh.material.color.setHex(0x424242);
                            }}
                        }}
                    }}
                }});

                if (isFollowCam && currentLeader) {{
                    const distance = 40;
                    const height = 25;
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
        
    print("Successfully built flight_viewer.html!")

if __name__ == "__main__":
    build_html()
