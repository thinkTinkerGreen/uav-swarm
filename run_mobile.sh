#!/bin/bash
SCENARIO=${1:-hero_tour}

# Dynamically detect if using virtual environment (OCI) or global python (Termux)
PYTHON_CMD="python"
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

echo "🚁 Generating Scenario: $SCENARIO (Full 2-Minute Simulation)..."
$PYTHON_CMD export_3d_flight.py --scenario $SCENARIO --duration 120.0

# Verify the physics engine actually produced the file
if [ -f "flight_data_${SCENARIO}.json" ]; then
    cp flight_data_${SCENARIO}.json flight_data.json
else
    echo "❌ Error: Simulation failed to generate flight_data_${SCENARIO}.json!"
    echo "Did the python script crash?"
    exit 1
fi

echo "🏗️ Building 3D HTML Viewer..."
$PYTHON_CMD build_3d_viewer.py

echo "📡 Building 2D Radar Viewer..."
$PYTHON_CMD build_2d_viewer.py

echo "📺 Building Split-Screen Demo..."
$PYTHON_CMD build_split_viewer.py

echo "📱 Launching Split-Screen Demo in Android Browser..."
termux-open split_demo.html
