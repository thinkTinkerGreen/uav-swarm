import re
with open("generate_benchmark_data.py", "r") as f:
    content = f.read()

content = content.replace("model='gemini-1.5-pro'", "model='gemini-2.5-pro'")
with open("generate_benchmark_data.py", "w") as f:
    f.write(content)
