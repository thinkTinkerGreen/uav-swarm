import json
import random

def get_oracle_decision(c_star, col):
    if c_star < 0.4 or col > 1: return "HOLD"
    elif c_star < 0.8 or col == 1: return "SWITCH"
    else: return "ADJUST"

def generate_prompt(c_star, e_tilde, k_tilde, col):
    # Apply fuzzy noise
    c_noisy = max(0.0, min(1.0, c_star + random.gauss(0, 0.05)))
    e_noisy = max(0.0, e_tilde + random.gauss(0, 0.005))
    k_noisy = max(0.0, k_tilde + random.gauss(0, 0.05))
    
    # xVAL Integer Scaling
    c_int = int(round(c_noisy * 1000))
    e_int = int(round(e_noisy * 1000))
    k_int = int(round(k_noisy * 1000))
    
    # Micro-Key Anchoring (No ChatML wrappers, pure sequence learning)
    return f"C:{c_int}|E:{e_int}|K:{k_int}|Col:{col}="

def generate_dataset(total_size=12000):
    dataset = []
    target_per_class = total_size // 3
    counts = {"ADJUST": 0, "SWITCH": 0, "HOLD": 0}
    
    while any(c < target_per_class for c in counts.values()):
        scenario_type = random.choice([
            "nominal", 
            "borderline_fragment", 
            "high_collision", 
            "chaos_kinetic", 
            "string_of_pearls"
        ])
        
        if scenario_type == "nominal":
            c = round(random.uniform(0.8, 1.0), 2)
            col = 0
            e = round(random.uniform(0.001, 0.01), 5)
            k = round(random.uniform(0.01, 0.1), 2)
        elif scenario_type == "borderline_fragment":
            c = round(random.uniform(0.75, 0.85), 2)
            col = random.choice([0, 1])
            e = round(random.uniform(0.01, 0.05), 5)
            k = round(random.uniform(0.1, 0.3), 2)
        elif scenario_type == "high_collision":
            c = round(random.uniform(0.5, 1.0), 2)
            col = random.randint(2, 5)
            e = round(random.uniform(0.05, 0.2), 5)
            k = round(random.uniform(0.2, 0.8), 2)
        elif scenario_type == "chaos_kinetic":
            c = round(random.uniform(0.1, 0.9), 2)
            col = random.randint(0, 3)
            e = round(random.uniform(0.1, 0.5), 5)
            k = round(random.uniform(1.0, 3.0), 2)
        elif scenario_type == "string_of_pearls":
            c = round(random.uniform(0.1, 0.45), 2)
            col = 0
            e = round(random.uniform(0.05, 0.1), 5)
            k = round(random.uniform(0.1, 0.5), 2)
            
        decision = get_oracle_decision(c, col)
        
        if counts[decision] < target_per_class:
            prompt = generate_prompt(c, e, k, col)
            dataset.append({
                "text": prompt + decision
            })
            counts[decision] += 1
            
    random.shuffle(dataset)
    return dataset

if __name__ == "__main__":
    print("Synthesizing V4 xVAL Integer-Scaled Training Dataset...")
    data = generate_dataset(12000) 
    
    with open("v4_xval_dataset.jsonl", "w") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")
            
    print(f"Generated {len(data)} xVAL rows to v4_xval_dataset.jsonl!")
