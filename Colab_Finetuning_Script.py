"""
UAV Swarm Qwen3.5-0.8B LoRA Fine-Tuning Script
Intended for Google Colab (T4 GPU Free Tier)

Before running, ensure you have installed Unsloth:
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps xformers trl peft accelerate bitsandbytes
"""

import json
from datasets import Dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

# ==========================================
# 1. Configuration
# ==========================================
MODEL_NAME = "unsloth/Qwen3.5-0.8B-Instruct-bnb-4bit" # 4-bit optimized model
MAX_SEQ_LENGTH = 1024 # Fits our prompts and JSON responses perfectly
TRACES_FILE = "training_traces.jsonl"
OUTPUT_GGUF_NAME = "qwen3.5-uav-swarm-q4_k_m.gguf"

# ==========================================
# 2. Data Preparation
# ==========================================
def format_prompt_from_trace(trace_dict):
    metrics = trace_dict["metrics"]
    return f"""[UAV]
C*:{metrics['c_star']:.2f}
E~:{metrics['e_tilde']:.5f}
K~:{metrics['k_tilde']:.2f}
Col:{metrics['collisions']}
[Go]"""

print("Loading dataset...")
raw_data = []
with open(TRACES_FILE, 'r') as f:
    for line in f:
        try:
            raw_data.append(json.loads(line))
        except:
            pass

formatted_data = {"text": []}
for trace in raw_data:
    user_prompt = format_prompt_from_trace(trace)
    
    # Strip the "why" explanation to save tokens, keep only fn and args
    decision = trace["decision"]
    optimized_decision = {"fn": decision["fn"], "args": decision.get("args", {})}
    
    # Use compact JSON separators (no spaces)
    assistant_response = json.dumps(optimized_decision, separators=(',', ':'))
    
    # Manually construct the ChatML string as requested
    chatml_string = f"""<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
{assistant_response}<|im_end|>"""
    
    formatted_data["text"].append(chatml_string)

# Convert to HuggingFace Dataset
dataset = Dataset.from_dict(formatted_data)

# ==========================================
# 3. Model & LoRA Loading
# ==========================================
print("Loading Model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = MODEL_NAME,
    max_seq_length = MAX_SEQ_LENGTH,
    dtype = None, # Auto-detects bf16 if supported
    load_in_4bit = True,
)



model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Rank
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 32,
    lora_dropout = 0, # Dropout = 0 is optimized for Unsloth
    bias = "none",    
    use_gradient_checkpointing = "unsloth", # Saves massive VRAM
    random_state = 3407,
)

# ==========================================
# 4. Training
# ==========================================
print("Starting SFT Training...")
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = MAX_SEQ_LENGTH,
    dataset_num_proc = 2,
    packing = False, # Can make training faster for short sequences
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        num_train_epochs = 3,
        learning_rate = 2e-4,
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

trainer_stats = trainer.train()
print(f"Training completed in {trainer_stats.metrics['train_runtime']} seconds.")

# ==========================================
# 5. Export to GGUF (For Ollama)
# ==========================================
print(f"Exporting model to {OUTPUT_GGUF_NAME}...")
model.save_pretrained_gguf("model", tokenizer, quantization_method = "q4_k_m")

print("Done! You can now download the .gguf file from the 'model' directory in Colab.")
