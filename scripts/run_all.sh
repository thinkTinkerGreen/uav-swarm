#!/bin/bash

# Ensure Python can find the src modules from the root directory
export PYTHONPATH=$(pwd)

PYTHON_CMD="python"
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

SCENARIOS=("hero_tour" "adv_a" "adv_b" "rtl" "armada")

echo "🚁 SwarmAI Batch Runner"
echo "Generating all 5 scenarios (2-minute flight each)..."
echo "NOTE: This will take significant time as each simulation computes ~2,400 AI inferences and dense physics!"

mkdir -p data

for SCENARIO in "${SCENARIOS[@]}"; do
    echo "----------------------------------------"
    echo "⏳ Running Scenario: $SCENARIO"
    $PYTHON_CMD -m src.tools.export_3d_flight --scenario $SCENARIO --duration 120.0
    
    if [ -f "flight_data_${SCENARIO}.json" ]; then
        mv flight_data_${SCENARIO}.json data/
        echo "✅ Generated data/flight_data_${SCENARIO}.json"
    else
        echo "❌ Error: Simulation failed to generate flight_data_${SCENARIO}.json!"
    fi
done

echo "----------------------------------------"
echo "🏗️ Building HTML Viewers..."
# Build the viewers using the hero_tour as the default, or the user can switch JSONs
cp data/flight_data_hero_tour.json flight_data.json
$PYTHON_CMD -m src.viewers.build_3d_viewer
$PYTHON_CMD -m src.viewers.build_2d_viewer
rm flight_data.json
mv flight_viewer.html data/
mv flight_viewer_2d.html data/

echo "✅ All scenarios complete! You can view data/flight_viewer.html and data/flight_viewer_2d.html"
echo "To view different scenarios, just swap the JSON file!"
