import numpy as np
from simulator import FlockSimulator

sim = FlockSimulator(n=15)
sim.q = np.zeros((15, 2))
for i in range(15):
    sim.q[i] = [-50 + (i%5)*15, (i//5)*15 - 15]
    
sim.p = np.zeros((15, 2))
sim.q_r = np.zeros((15, 2))
for i in range(15):
    sim.q_r[i] = [1050.0, sim.q[i][1]]
    
sim.p_r = np.array([7.0, 0.0])

u_a = sim.compute_u_alpha()
u_g = sim.compute_u_gamma()
print("u_a:", u_a[0])
print("u_g:", u_g[0])
print("Total u:", u_a[0] + u_g[0])
