import numpy as np
import time

class OlfatiSaberMath:
    def __init__(self, d=7.0, r=8.4, epsilon=0.1, a=5.0, b=5.0, h=0.2):
        self.d = d
        self.r = r  # This acts as R_comm (Communication Radius)
        self.epsilon = epsilon
        self.a = a
        self.b = b
        self.c = np.abs(a - b) / np.sqrt(4 * a * b) if a != b else 0.0
        self.h = h
        
        self.d_alpha = self.sigma_norm(self.d)
        self.r_alpha = self.sigma_norm(self.r)

    def sigma_norm(self, z):
        if np.isscalar(z):
            norm_sq = z**2
        else:
            norm_sq = np.sum(z**2, axis=-1)
        return (1.0 / self.epsilon) * (np.sqrt(1.0 + self.epsilon * norm_sq) - 1.0)

    def sigma_1(self, z):
        return z / np.sqrt(1.0 + z**2)

    def rho_h(self, z):
        res = np.zeros_like(z)
        mask1 = (z >= 0) & (z < self.h)
        res[mask1] = 1.0
        mask2 = (z >= self.h) & (z <= 1)
        res[mask2] = 0.5 * (1.0 + np.cos(np.pi * (z[mask2] - self.h) / (1.0 - self.h)))
        return res

    def phi(self, z):
        return 0.5 * ((self.a + self.b) * self.sigma_1(z + self.c) + (self.a - self.b))

    def phi_alpha(self, z):
        return self.rho_h(z / self.r_alpha) * self.phi(z - self.d_alpha)

    def a_ij(self, q_i, q_j):
        dist = self.sigma_norm(q_j - q_i)
        return self.rho_h(dist / self.r_alpha)

    def n_ij(self, q_i, q_j):
        diff = q_j - q_i
        norm_sq = np.sum(diff**2, axis=-1, keepdims=True)
        return diff / np.sqrt(1.0 + self.epsilon * norm_sq)

class FlockSimulator:
    def __init__(self, num_agents, dim=2, algo=2):
        self.n = num_agents
        self.m = dim
        self.algo = algo
        
        self.math = OlfatiSaberMath()
        
        # Invariants & Gains
        self.c1_a = 1.0
        self.c2_a = 2.0 * np.sqrt(self.c1_a)
        
        # Gamma gain (Leader tracking) - Boosted so leader moves fast enough
        self.c1_g = 0.2
        self.c2_g = 2.0 * np.sqrt(self.c1_g)
        
        self.c1_b = 2.0
        self.c2_b = 2.0 * np.sqrt(self.c1_b)
        
        # State
        self.q = np.random.rand(self.n, self.m) * 50.0
        self.p = np.zeros((self.n, self.m))
        
        # Gamma target
        self.q_r = np.ones(self.m) * 100.0
        self.p_r = np.zeros(self.m)
        
        self.obstacles = [] 
        
        # Robustness Phase 2.5 Features
        self.leader_id = 0
        self.wind_strength = 0.5 # Actuator Noise (Wind Gusts)

    def compute_u_alpha(self):
        u_alpha = np.zeros((self.n, self.m))
        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    continue
                q_ij = self.q[j] - self.q[i]
                norm_q_ij = np.linalg.norm(q_ij)
                
                # R_comm restriction
                if norm_q_ij < self.math.r:
                    sigma_norm_qij = self.math.sigma_norm(norm_q_ij)
                    n_ij = self.math.n_ij(self.q[i], self.q[j])
                    a_ij = self.math.rho_h(sigma_norm_qij / self.math.r_alpha)
                    
                    term1 = self.math.phi_alpha(sigma_norm_qij) * n_ij
                    term2 = a_ij * (self.p[j] - self.p[i])
                    
                    u_alpha[i] += self.c1_a * term1 + self.c2_a * term2
        return u_alpha

    def update_leadership(self):
        # Build adjacency matrix based on R_comm
        adj = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i+1, self.n):
                if np.linalg.norm(self.q[i] - self.q[j]) < self.math.r:
                    adj[i, j] = 1
                    adj[j, i] = 1
                    
        # Find components
        visited = [False] * self.n
        components = []
        for i in range(self.n):
            if not visited[i]:
                comp_nodes = []
                queue = [i]
                visited[i] = True
                while queue:
                    node = queue.pop(0)
                    comp_nodes.append(node)
                    for neighbor in range(self.n):
                        if adj[node, neighbor] and not visited[neighbor]:
                            visited[neighbor] = True
                            queue.append(neighbor)
                components.append(comp_nodes)
                
        # Find the largest component (Main Swarm)
        largest_comp = max(components, key=len)
        
        # If leader is not in the main swarm, re-elect!
        if self.leader_id not in largest_comp:
            # Elect the drone in the largest component closest to the target
            best_drone = -1
            min_dist = float('inf')
            for drone in largest_comp:
                dist = np.linalg.norm(self.q[drone] - self.q_r)
                if dist < min_dist:
                    min_dist = dist
                    best_drone = drone
            if best_drone != -1:
                print(f"[SWARM CONSENSUS] Leader {self.leader_id} lost! Electing Drone {best_drone} as new Leader.")
                self.leader_id = best_drone

    def compute_u_gamma(self):
        u_gamma = np.zeros((self.n, self.m))
        if self.algo >= 1:
            # ONLY the Leader knows the global target!
            u_gamma[self.leader_id] = -self.c1_g * self.math.sigma_1(self.q[self.leader_id] - self.q_r) - self.c2_g * (self.p[self.leader_id] - self.p_r)
        return u_gamma

    def step(self, dt=0.03):
        self.update_leadership()
        
        u_a = self.compute_u_alpha()
        u_g = self.compute_u_gamma()
        u_b = self.compute_u_beta()
        
        # Actuator Noise (Wind Shear)
        u_wind = np.random.normal(0, self.wind_strength, (self.n, self.m))
        
        u = u_a + u_g + u_b + u_wind
        
        self.p += u * dt
        self.q += self.p * dt
        
        if hasattr(self, 'p_r'):
            self.q_r += self.p_r * dt
        
        if hasattr(self, 'obstacles'):
            for obs in self.obstacles:
                if 'velocity' in obs:
                    obs['center'] += obs['velocity'] * dt

    def compute_u_beta(self):
        u_beta = np.zeros((self.n, self.m))
        if self.algo >= 2 and hasattr(self, 'obstacles'):
            for i in range(self.n):
                for obs in self.obstacles:
                    if obs['type'] == 'sphere':
                        dist = np.linalg.norm(self.q[i] - obs['center'])
                        if dist < obs['radius'] + self.math.r:
                            n_ik = (self.q[i] - obs['center']) / dist
                            u_beta[i] += self.c1_b * n_ik * (1.0 / (dist - obs['radius'] + 0.1))
        return u_beta
