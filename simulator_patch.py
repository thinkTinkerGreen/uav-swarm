import numpy as np

def apply_scenario(sim, scenario_id):
    if scenario_id == 1:
        # Nominal Flight
        sim.q = np.random.rand(sim.n, sim.m) * 50.0
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.ones(sim.m) * 100.0
    elif scenario_id == 2:
        # Dense Obstacle Field
        sim.q = np.random.rand(sim.n, sim.m) * 20.0
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.ones(sim.m) * 100.0
        sim.obstacles = [{'type': 'sphere', 'center': np.array([40.0, 40.0]), 'radius': 10.0},
                         {'type': 'sphere', 'center': np.array([60.0, 30.0]), 'radius': 15.0},
                         {'type': 'sphere', 'center': np.array([50.0, 70.0]), 'radius': 12.0}]
    elif scenario_id == 3:
        # Corridor Squeeze
        sim.q = np.random.rand(sim.n, sim.m) * 10.0
        sim.q[:, 1] += 45.0
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.array([100.0, 50.0])
        sim.obstacles = [{'type': 'wall', 'point': np.array([0.0, 35.0]), 'normal': np.array([0.0, 1.0])},
                         {'type': 'wall', 'point': np.array([0.0, 65.0]), 'normal': np.array([0.0, -1.0])}]
    elif scenario_id == 4:
        # Dynamic Target
        sim.q = np.random.rand(sim.n, sim.m) * 30.0
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.array([50.0, 50.0])
        sim.p_r = np.array([10.0, -5.0])
    elif scenario_id == 5:
        # Agent Loss
        sim.q = np.random.rand(sim.n, sim.m) * 40.0
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.ones(sim.m) * 100.0
    elif scenario_id == 6:
        # Flash Expansion
        sim.q = np.random.rand(sim.n, sim.m) * 2.0  # Extremely tight
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.ones(sim.m) * 100.0
    elif scenario_id == 7:
        # Predator Evasion (Dynamic Obstacle)
        sim.q = np.random.rand(sim.n, sim.m) * 30.0
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.ones(sim.m) * 100.0
        sim.obstacles = [{'type': 'sphere', 'center': np.array([50.0, 50.0]), 'radius': 5.0, 'velocity': np.array([-15.0, -15.0])}]
    elif scenario_id == 8:
        # Deadlocked Geometry
        sim.q = np.random.rand(sim.n, sim.m) * 20.0
        sim.p = np.zeros((sim.n, sim.m))
        sim.q_r = np.array([80.0, 50.0])
        # U-shape Trap
        sim.obstacles = [{'type': 'wall', 'point': np.array([60.0, 50.0]), 'normal': np.array([-1.0, 0.0])},
                         {'type': 'wall', 'point': np.array([50.0, 70.0]), 'normal': np.array([0.0, -1.0])},
                         {'type': 'wall', 'point': np.array([50.0, 30.0]), 'normal': np.array([0.0, 1.0])}]
