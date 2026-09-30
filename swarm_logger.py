import json
import time
import logging
from collections import deque

# Configure strict JSON logging for ELK stack ingestion
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler("swarm_telemetry.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SwarmLogger")

class BlackboxRecorder:
    """
    Maintains a rolling 60-second in-memory buffer of telemetry.
    Can be dumped via burst transmission upon catastrophic failure.
    """
    def __init__(self, drone_id, buffer_seconds=60, hz=20):
        self.drone_id = drone_id
        self.max_frames = buffer_seconds * hz
        self.buffer = deque(maxlen=self.max_frames)
        
    def record_state(self, x, y, yaw, algo_state, battery):
        self.buffer.append({
            "ts": time.time(),
            "x": round(x, 3),
            "y": round(y, 3),
            "yaw": round(yaw, 3),
            "algo": algo_state,
            "bat": round(battery, 2)
        })
        
    def burst_transmission(self):
        """Simulates dumping the blackbox to the nearest neighbor"""
        dump_data = {
            "event": "BLACKBOX_BURST",
            "drone_id": self.drone_id,
            "timestamp": time.time(),
            "history_frames": len(self.buffer),
            "data": list(self.buffer)
        }
        logger.info(json.dumps(dump_data))
        return dump_data

def log_event(event_type, **kwargs):
    """Structured JSON event logger"""
    payload = {
        "timestamp": time.time(),
        "event": event_type
    }
    payload.update(kwargs)
    logger.info(json.dumps(payload))
