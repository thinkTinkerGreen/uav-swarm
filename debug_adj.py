import sys
sys.path.append('.')
from src.tools.export_3d_flight import ExportHarness

h = ExportHarness(num_agents=5, scenario="adv_b", duration=3.0)
h.env.start()
import time
time.sleep(1)
h.env.join()
