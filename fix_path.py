with open("benchmark_suite.py", "r") as f:
    content = f.read()

# Replace the hardcoded absolute path with a simple local filename
content = content.replace(
    '"/home/opc/.gemini/antigravity-cli/brain/666ea37a-f32d-4909-be4a-33f8a87665f1/Final_Benchmark_Report.md"',
    '"Final_Benchmark_Report.md"'
)

with open("benchmark_suite.py", "w") as f:
    f.write(content)
