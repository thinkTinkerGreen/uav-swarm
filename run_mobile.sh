#!/bin/bash
SCENARIO=${1:-hero_tour}

echo "🚁 Generating Scenario: $SCENARIO..."
.venv/bin/python export_3d_flight.py --scenario $SCENARIO

# Copy the generated JSON to the default filename expected by the HTML builder
cp flight_data_${SCENARIO}.json flight_data.json

echo "🏗️ Building 3D HTML Viewer..."
.venv/bin/python build_3d_viewer.py

echo "📱 Launching 3D Viewer in Android Browser..."
termux-open flight_viewer.html
