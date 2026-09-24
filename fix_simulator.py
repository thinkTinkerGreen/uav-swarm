import re

with open("simulator.py", "r") as f:
    content = f.read()

# Extract compute_u_beta block
match = re.search(r'(    def compute_u_beta\(self\):.*)', content, re.DOTALL)
if match:
    u_beta_code = match.group(1)
    content = content.replace(u_beta_code, "")
    
    # insert before if __name__
    content = content.replace('if __name__ == "__main__":', u_beta_code + '\nif __name__ == "__main__":')

with open("simulator.py", "w") as f:
    f.write(content)
