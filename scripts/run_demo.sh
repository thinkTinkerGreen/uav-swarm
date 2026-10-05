#!/bin/bash
SCENARIO=${1:-hero_tour}

PYTHON_CMD="python"
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

# Ensure Python can find the src modules from the root directory
export PYTHONPATH=$(pwd)

echo "🚁 Generating Scenario: $SCENARIO (Full 2-Minute Simulation)..."
echo "⏳ NOTE: A 2-minute flight requires 2,400 AI inferences! This will take several minutes to generate. Please wait..."
$PYTHON_CMD -m src.tools.export_3d_flight --scenario $SCENARIO --duration 120.0

if [ -f "flight_data_${SCENARIO}.json" ]; then
    # Move the raw JSON to the data directory, but also keep a copy in the root for the viewer builders
    mv flight_data_${SCENARIO}.json data/
    cp data/flight_data_${SCENARIO}.json flight_data.json
else
    echo "❌ Error: Simulation failed to generate flight_data_${SCENARIO}.json!"
    exit 1
fi

echo "🏗️ Building 3D HTML Viewer (flight_viewer.html)..."
$PYTHON_CMD -m src.viewers.build_3d_viewer

echo "📡 Building 2D Radar Viewer (flight_viewer_2d.html)..."
$PYTHON_CMD -m src.viewers.build_2d_viewer

# Cleanup the root data file now that HTMLs are built
rm flight_data.json

# Move the HTML outputs into the data directory to keep the root clean
mv flight_viewer.html data/
mv flight_viewer_2d.html data/

echo "✅ Done! You can now manually open data/flight_viewer.html and data/flight_viewer_2d.html in separate browser tabs."
