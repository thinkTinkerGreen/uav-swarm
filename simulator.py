import numpy as np
import time
from swarm_logger import log_event

class OlfatiSaberMath:
    def __init__(self, d=7.0, r=8.4, epsilon=0.1, a=5.0, b=5.0, h=0.2):
        self.d = d
        self.r = r
        self.epsilon = epsilon
        self.a = a
        self.b = b
        self.c = np.abs(a - b) / np.sqrt(4 * a * b) if a != b else 0.0
        self.h = h
        self.d_alpha = self.sigma_norm(self.d)
        self.r_alpha = self.sigma_norm(self.r)

    def sigma_norm(self, z):
        if np.isscalar(z): return (1.0 / self.epsilon) * (np.sqrt(1.0 + self.epsilon * z**2) - 1.0)
        return (1.0 / self.epsilon) * (np.sqrt(1.0 + self.epsilon * np.sum(z**2, axis=-1)) - 1.0)

    def sigma_1(self, z):
        return z / np.sqrt(1.0 + z**2)

    def rho_h(self, z):
        res = np.zeros_like(z)
        res[(z >= 0) & (z < self.h)] = 1.0
        mask = (z >= self.h) & (z <= 1)
        res[mask] = 0.5 * (1.0 + np.cos(np.pi * (z[mask] - self.h) / (1.0 - self.h)))
        return res

    def phi(self, z):
        return 0.5 * ((self.a + self.b) * self.sigma_1(z + self.c) + (self.a - self.b))

    def phi_alpha(self, z):
        return self.rho_h(z / self.r_alpha) * self.phi(z - self.d_alpha)

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
        self.c1_g = 0.2
        self.c2_g = 2.0 * np.sqrt(self.c1_g)
        self.c1_b = 2.0
        self.c2_b = 2.0 * np.sqrt(self.c1_b)
        
        # State
        self.q = np.random.rand(self.n, self.m) * 50.0
        self.p = np.zeros((self.n, self.m))
        
        # Global Target
        self.q_r = np.ones(self.m) * 100.0
        self.p_r = np.zeros(self.m)
        self.obstacles = [] 
        
        # Actuator Noise (Wind Gusts)
        self.wind_strength = 0.5 
        
        # --- ENTERPRISE HIERARCHY & FAILSAFES ---
        self.squad_size_limit = 20
        self.squad_leaders = []
        self.prime_commander = 0
        self.deputies = {} # Map of leader_id -> [deputy_id_1, deputy_id_2]
        self.cached_targets = np.zeros((self.n, self.m)) # Gossip protocol cache
        
        self.initialize_hierarchy()

    def initialize_hierarchy(self):
        """Partitions swarm into squads and assigns initial leaders and deputies"""
        self.squad_leaders = []
        for i in range(0, self.n, self.squad_size_limit):
            leader = i
            self.squad_leaders.append(leader)
            
            # Select deputies (next available drones in the squad)
            squad_end = min(i + self.squad_size_limit, self.n)
            squad_deputies = list(range(i+1, squad_end))[:3] # Up to 3 deputies
            self.deputies[leader] = squad_deputies
            
        self.prime_commander = self.squad_leaders[0]
        # Initial gossip blast
        for i in range(self.n):
            self.cached_targets[i] = self.q_r

    def compute_u_alpha(self, adj):
        u_alpha = np.zeros((self.n, self.m))
        for i in range(self.n):
            # Orphan Recovery Failsafe
            if np.sum(adj[i]) == 0:
                log_event("ORPHAN_RECOVERY", drone_id=i, action="backtrack")
                u_alpha[i] = -self.p[i] * 2.0 
                continue
                
            for j in range(self.n):
                if i != j and adj[i, j] == 1:
                    norm_q_ij = np.linalg.norm(self.q[j] - self.q[i])
                    sigma_norm_qij = self.math.sigma_norm(norm_q_ij)
                    n_ij = self.math.n_ij(self.q[i], self.q[j])
                    a_ij = self.math.rho_h(sigma_norm_qij / self.math.r_alpha)
                    
                    term1 = self.math.phi_alpha(sigma_norm_qij) * n_ij
                    term2 = a_ij * (self.p[j] - self.p[i])
                    
                    u_alpha[i] += self.c1_a * term1 + self.c2_a * term2
        return u_alpha

    def gossip_protocol(self, adj):
        """Simulate heartbeat propagation of target data through the mesh"""
        # In a real system this would hop through adj. 
        # Here we simulate instant propagation within connected components.
        visited = [False] * self.n
        for leader in self.squad_leaders:
            if visited[leader]: continue
            
            queue = [leader]
            visited[leader] = True
            
            # The target this component will sync to
            sync_target = self.cached_targets[leader]
            
            while queue:
                curr = queue.pop(0)
                self.cached_targets[curr] = sync_target
                for neighbor in range(self.n):
                    if adj[curr, neighbor] == 1 and not visited[neighbor]:
                        visited[neighbor] = True
                        queue.append(neighbor)

    def update_hierarchy(self, adj):
        """Dynamic Squad Leader Election & Demotion Protocol"""
        self.gossip_protocol(adj)
        
        components = []
        visited = [False] * self.n
        for i in range(self.n):
            if not visited[i]:
                comp = []
                queue = [i]
                visited[i] = True
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for neighbor in range(self.n):
                        if adj[curr, neighbor] == 1 and not visited[neighbor]:
                            visited[neighbor] = True
                            queue.append(neighbor)
                components.append(comp)

        new_squad_leaders = []
        
        for comp in components:
            if len(comp) <= 1: continue
            
            # Find existing leaders in this isolated component
            leaders_in_comp = [d for d in comp if d in self.squad_leaders]
            
            if len(leaders_in_comp) == 0:
                # ELECTION NEEDED (Leader died or we fractured)
                # First, check if a Deputy is alive in this component
                elected = None
                # Since we don't know exactly which squad this component belonged to,
                # we just pick the drone with the most neighbors (centrality).
                degrees = np.sum(adj, axis=1)
                best_drone = max(comp, key=lambda d: degrees[d])
                elected = best_drone
                
                log_event("LEADER_ELECTION", component_size=len(comp), new_leader=elected)
                new_squad_leaders.append(elected)
                
            elif len(leaders_in_comp) > 1:
                # DEMOTION PROTOCOL (Multi-Swarms Merged)
                true_leader = min(leaders_in_comp) # Keep lowest ID
                new_squad_leaders.append(true_leader)
                
                demoted = [l for l in leaders_in_comp if l != true_leader]
                for d in demoted:
                    log_event("LEADER_DEMOTION", demoted_leader=d, true_leader=true_leader)
            else:
                new_squad_leaders.append(leaders_in_comp[0])

        self.squad_leaders = new_squad_leaders
        
        # Ensure Prime Commander is valid
        if self.prime_commander not in self.squad_leaders and len(self.squad_leaders) > 0:
            self.prime_commander = min(self.squad_leaders)
            log_event("PRIME_COMMANDER_CHANGE", new_commander=self.prime_commander)

    def compute_u_gamma(self):
        u_gamma = np.zeros((self.n, self.m))
        if self.algo >= 1:
            for leader in self.squad_leaders:
                target = self.cached_targets[leader]
                u_gamma[leader] = -self.c1_g * self.math.sigma_1(self.q[leader] - target) - self.c2_g * (self.p[leader] - self.p_r)
        return u_gamma

    def step(self, dt=0.03):
        # 1. Build Adjacency Matrix (R_comm)
        adj = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i+1, self.n):
                if np.linalg.norm(self.q[i] - self.q[j]) < self.math.r:
                    adj[i, j] = 1
                    adj[j, i] = 1

        # 2. Run Enterprise Diagnostics & Failsafes
        self.update_hierarchy(adj)
        
        # 3. Physics Forces
        u_a = self.compute_u_alpha(adj)
        u_g = self.compute_u_gamma()
        u_b = self.compute_u_beta()
        u_wind = np.random.normal(0, self.wind_strength, (self.n, self.m))
        
        u = u_a + u_g + u_b + u_wind
        self.p += u * dt
        self.q += self.p * dt
        
        if hasattr(self, 'p_r'):
            self.q_r += self.p_r * dt
            
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
