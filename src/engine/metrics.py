import numpy as np

class Metrics:
    def __init__(self, n, d, r):
        self.n = n
        self.d = d
        self.r = r
        self.total_complete_edges = n * (n - 1) / 2.0

    def compute_all(self, q, p):
        # Build adjacency matrix and edge list based on r
        adj = np.zeros((self.n, self.n))
        edges = []
        for i in range(self.n):
            for j in range(i+1, self.n):
                dist = np.linalg.norm(q[i] - q[j])
                if dist < self.r:
                    adj[i, j] = 1
                    adj[j, i] = 1
                    edges.append((i, j, dist))
        
        # 1. Semi-Connectivity Factor (C*)
        # Find connected components
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
        
        largest_comp = max(components, key=len)
        c_star = len(largest_comp) / self.n
        
        # 2. Normalized Deviation Energy (E_tilde)
        # Eq: E(q) = 1 / (|E(q)| + 1) * sum_{i} sum_{j in N_i} (||q_j - q_i|| - d)^2
        E_q = 0
        for i in range(self.n):
            for j in range(self.n):
                if i != j and adj[i, j]:
                    dist = np.linalg.norm(q[i] - q[j])
                    E_q += (dist - self.d)**2
        E_q /= (len(edges) * 2 + 1)
        E_tilde = E_q / (self.d**2)
        
        # 3. Normalized Velocity Mismatch (K_tilde)
        # K(v) = 1/2 * sum ||v_i - v_c||^2
        v_c = np.mean(p, axis=0)
        K_v = 0.5 * np.sum(np.linalg.norm(p - v_c, axis=1)**2)
        K_tilde = K_v / self.n
        
        # 4. Collisions (dist < 1.0)
        collisions = 0
        for i, j, dist in edges:
            if dist < 1.0:
                collisions += 1
                
        return {
            'c_star': c_star,
            'e_tilde': E_tilde,
            'k_tilde': K_tilde,
            'collisions': collisions,
            'components': len(components)
        }
