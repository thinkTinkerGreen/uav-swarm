 cp ./data/flight_data_adv_a.json  flight_data.json
 .venv/bin/python ./src/viewers/build_3d_viewer.py 
 .venv/bin/python ./src/viewers/build_2d_viewer.py 
 mv flight_viewer.html ./data/adv_a_flight_viewer.html
 mv flight_viewer_2d.html ./data/adv_a_flight_viewer_2d.html
 cp ./data/flight_data_adv_b.json  flight_data.json
 .venv/bin/python ./src/viewers/build_3d_viewer.py 
 .venv/bin/python ./src/viewers/build_2d_viewer.py 
 mv flight_viewer_2d.html ./data/adv_b_flight_viewer_2d.html
 mv flight_viewer.html ./data/adv_b_flight_viewer.html
 cp ./data/flight_data_rtl.json flight_data.json
 .venv/bin/python ./src/viewers/build_3d_viewer.py 
 .venv/bin/python ./src/viewers/build_2d_viewer.py 
 mv flight_viewer.html ./data/rtl_flight_viewer.html
 mv flight_viewer_2d.html ./data/rtl_flight_viewer_2d.html
 cp ./data/flight_data_hero_tour.json flight_data.json
 .venv/bin/python ./src/viewers/build_3d_viewer.py 
 .venv/bin/python ./src/viewers/build_2d_viewer.py 
 mv flight_viewer.html ./data/hero_tour_flight_viewer.html
 mv flight_viewer_2d.html ./data/hero_tour_flight_viewer_2d.html
 cp ./data/flight_data_armada.json flight_data.json
 .venv/bin/python ./src/viewers/build_3d_viewer.py 
 .venv/bin/python ./src/viewers/build_2d_viewer.py 
 mv flight_viewer.html ./data/armada_flight_viewer.html
 mv flight_viewer_2d.html ./data/armada_flight_viewer_2d.html
