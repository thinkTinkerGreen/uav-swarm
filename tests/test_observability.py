import pytest
import json
import time
import logging
from swarm_logger import BlackboxRecorder, log_event

def test_blackbox_rolling_buffer():
    # 1 second buffer at 10hz = 10 frames max
    box = BlackboxRecorder(drone_id=7, buffer_seconds=1, hz=10)
    for i in range(15):
        box.record_state(x=float(i), y=0.0, yaw=0.0, algo_state=1, battery=100.0)
    
    assert len(box.buffer) == 10
    assert box.buffer[0]["x"] == 5.0
    assert box.buffer[-1]["x"] == 14.0

def test_json_logging(caplog):
    caplog.set_level(logging.INFO)
    log_event("TEST_EVENT", status="success", val=42)
    assert "TEST_EVENT" in caplog.text
    assert '"val": 42' in caplog.text
