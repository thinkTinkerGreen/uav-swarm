import json
from collections import Counter

traces = []
with open('training_traces.jsonl', 'r') as f:
    for line in f:
        traces.append(json.loads(line))

decisions = [t['decision'] for t in traces]
reasons = [d.get('why', d.get('args', {}).get('reason', 'unknown')) for d in decisions]
fn_counts = Counter([d.get('fn') for d in decisions])
reason_counts = Counter(reasons)

print("Function Counts:", dict(fn_counts))
print("Reason Counts:", dict(reason_counts))

failed_traces = [t for t in traces if t['decision'].get('reason') == 'inference failed' or t['decision'].get('args', {}).get('reason') == 'inference failed']

print(f"\nFailed Traces Count: {len(failed_traces)}")
if failed_traces:
    print("Example latency:", failed_traces[0]['latency_sec'])
