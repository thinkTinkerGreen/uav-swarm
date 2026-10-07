#!/bin/bash

# Ensure Python can find the src modules from the root directory
export PYTHONPATH=$(pwd)

PYTHON_CMD="python"
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

SCENARIOS=("hero_tour" "adv_a" "adv_b" "rtl" "armada")

echo "🚁 SwarmAI Batch Runner"
echo "Generating all 5 scenarios (3-minute flight each)..."
echo "NOTE: This will take significant time as each simulation computes ~2,400 AI inferences and dense physics!"

mkdir -p data

for SCENARIO in "${SCENARIOS[@]}"; do
    echo "----------------------------------------"
    echo "⏳ Running Scenario: $SCENARIO"
    $PYTHON_CMD -m src.tools.export_3d_flight --scenario $SCENARIO --duration 180.0
    
    if [ -f "flight_data_${SCENARIO}.json" ]; then
        mv flight_data_${SCENARIO}.json data/
        echo "✅ Generated data/flight_data_${SCENARIO}.json"
	cp ./data/flight_data_${SCENARIO}.json flight_data.json
	$PYTHON_CMD -m src.viewers.build_3d_viewer
	$PYTHON_CMD -m src.viewers.build_2d_viewer
	mv flight_viewer.html ./data/${SCENARIO}_flight_viewer.html
	mv flight_viewer_2d.html ./data/${SCENARIO}_flight_viewer_2d.html
	echo "✅ Generated data/${SCENARIO}_flight_viewer.html and 2D"
    else
        echo "❌ Error: Simulation failed to generate flight_data_${SCENARIO}.json!"
    fi
done



echo "✅ All scenarios complete! You can view in data/scenario_flight_viewer.html and scenario_flight_viewer_2d.html"
