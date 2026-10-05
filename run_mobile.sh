#!/bin/bash
SCENARIO=${1:-hero_tour}

PYTHON_CMD="python"
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

echo "🚁 Generating Scenario: $SCENARIO (Full 2-Minute Simulation)..."
echo "⏳ NOTE: A 2-minute flight requires 2,400 AI inferences! This will take several minutes to generate. Please wait..."
$PYTHON_CMD export_3d_flight.py --scenario $SCENARIO --duration 120.0

if [ -f "flight_data_${SCENARIO}.json" ]; then
    cp flight_data_${SCENARIO}.json flight_data.json
else
    echo "❌ Error: Simulation failed to generate flight_data_${SCENARIO}.json!"
    exit 1
fi

echo "🏗️ Building 3D HTML Viewer (flight_viewer.html)..."
$PYTHON_CMD build_3d_viewer.py

echo "📡 Building 2D Radar Viewer (flight_viewer_2d.html)..."
$PYTHON_CMD build_2d_viewer.py

echo "✅ Done! You can now manually open flight_viewer.html and flight_viewer_2d.html in separate browser tabs."
