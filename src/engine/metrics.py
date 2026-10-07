import numpy as np

class Metrics:
    def __init__(self, n, d, r):
        self.n = n
        self.d = d
        self.r = r
        self.total_complete_edges = n * (n - 1) / 2.0

    def compute_all(self, q, p, obstacles=None):
        # Build adjacency matrix and edge list based on r
        D = np.linalg.norm(q[:, None, :] - q[None, :, :], axis=-1)
        adj = (D < self.r + 6.0)
        np.fill_diagonal(adj, False)
        iu, ju = np.nonzero(np.triu(adj, 1))
        edges = list(zip(iu, ju, D[iu, ju]))
        
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
                    for neighbor in np.nonzero(adj[node])[0]:
                        if not visited[neighbor]:
                            visited[neighbor] = True
                            queue.append(neighbor)
                components.append(comp_nodes)
        
        largest_comp = max(components, key=len)
        c_star = len(largest_comp) / self.n
        
        # 2. Normalized Deviation Energy (E_tilde)
        E_q = float(np.sum(np.where(adj, (D - self.d)**2, 0.0)))
        E_q /= (len(edges) * 2 + 1)
        E_tilde = E_q / (self.d**2)
        
        # 3. Normalized Velocity Mismatch (K_tilde)
        v_c = np.mean(p, axis=0)
        K_v = 0.5 * np.sum(np.linalg.norm(p - v_c, axis=1)**2)
        K_tilde = K_v / self.n
        
        # 4. Collisions
        collisions = 0
        # Drone-to-Drone
        for i, j, dist in edges:
            if dist < 1.0:
                collisions += 1
                
        # Drone-to-Obstacle
        if obstacles:
            for obs in obstacles:
                if obs.get('type') == 'sphere':
                    dist = np.linalg.norm(q - obs['center'], axis=1)
                    # if distance is less than the radius plus a buffer
                    collisions += int(np.sum(dist < obs['radius'] + 0.5))
                
        return {
            'c_star': c_star,
            'e_tilde': E_tilde,
            'k_tilde': K_tilde,
            'collisions': collisions,
            'components': len(components)
        }
