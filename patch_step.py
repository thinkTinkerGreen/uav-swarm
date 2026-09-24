import re

with open("simulator.py", "r") as f:
    content = f.read()

new_step = """
    def step(self, dt=0.03):
        u_a = self.compute_u_alpha()
        u_g = self.compute_u_gamma()
        
        u = u_a + u_g + self.compute_u_beta()
        
        self.p += u * dt
        self.q += self.p * dt
        
        # dynamic updates
        if hasattr(self, 'p_r'):
            self.q_r += self.p_r * dt
        
        if hasattr(self, 'obstacles'):
            for obs in self.obstacles:
                if 'velocity' in obs:
                    obs['center'] += obs['velocity'] * dt
"""

content = re.sub(r'    def step\(self, dt=0\.03\):.*?(?=\n\n|\Z)', new_step.strip('\n'), content, flags=re.DOTALL)

with open("simulator.py", "w") as f:
    f.write(content)
