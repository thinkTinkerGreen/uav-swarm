#!/bin/bash
SCENARIO=${1:-hero_tour}

# Dynamically detect if using virtual environment (OCI) or global python (Termux)
PYTHON_CMD="python"
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

echo "🚁 Generating Scenario: $SCENARIO..."
$PYTHON_CMD export_3d_flight.py --scenario $SCENARIO

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

echo "📱 Launching 3D Viewer in Android Browser..."
termux-open flight_viewer.html
