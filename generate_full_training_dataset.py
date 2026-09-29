import json
import random

def get_oracle_decision(c_star, col):
    if c_star < 0.4 or col > 1: return "HOLD"
    elif c_star < 0.8 or col == 1: return "SWITCH"
    else: return "ADJUST"

def generate_prompt(c_star, e_tilde, k_tilde, col):
    return f"""<|im_start|>system
You are a UAV controller. Output EXACTLY ONE WORD: 'ADJUST', 'SWITCH', or 'HOLD'. No explanations.<|im_end|>
<|im_start|>user
[UAV]
C*:{c_star:.2f}
E~:{e_tilde:.5f}
K~:{k_tilde:.2f}
Col:{col}
[Go]<|im_end|>
<|im_start|>assistant
"""

def generate_dataset(num_samples_per_class):
    dataset = []
    
    # 1. Nominal Flight (ADJUST) - Non-adversarial perfect conditions
    for _ in range(num_samples_per_class):
        c = round(random.uniform(0.85, 1.0), 2)
        col = 0
        e = round(random.uniform(0.001, 0.009), 5)
        k = round(random.uniform(0.01, 0.09), 2)
        prompt = generate_prompt(c, e, k, col)
        dataset.append({"text": prompt + "ADJUST<|im_end|>"})
        
    # 2. Simple Evasion / Fragmentation (SWITCH) - Non-adversarial dynamic conditions
    for _ in range(num_samples_per_class):
        c = round(random.uniform(0.45, 0.79), 2)
        col = random.choice([0, 1])
        e = round(random.uniform(0.01, 0.05), 5)
        k = round(random.uniform(0.1, 0.5), 2)
        prompt = generate_prompt(c, e, k, col)
        dataset.append({"text": prompt + "SWITCH<|im_end|>"})
        
    # 3. Extreme Adversarial / Failsafe (HOLD) - The missing edge case!
    for _ in range(num_samples_per_class):
        c = round(random.uniform(0.05, 0.39), 2)
        col = random.randint(2, 12)
        e = round(random.uniform(0.05, 0.3), 5)
        k = round(random.uniform(0.5, 2.0), 2)
        prompt = generate_prompt(c, e, k, col)
        dataset.append({"text": prompt + "HOLD<|im_end|>"})

    random.shuffle(dataset)
    return dataset

if __name__ == "__main__":
    print("Synthesizing V2 Training Dataset with perfectly balanced attention features...")
    # Generating 4,000 samples for EACH class (12,000 total rows)
    data = generate_dataset(4000) 
    
    with open("v2_training_dataset.jsonl", "w") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")
            
    print(f"Generated {len(data)} perfectly balanced training rows to v2_training_dataset.jsonl!")
