import json

EVAL_FILE = "eval_run_records.jsonl"

def score_run():
    print(f"--- Starting Verifier Scorer ---")
    print(f"Reading records from {EVAL_FILE}...\n")
    
    try:
        with open(EVAL_FILE, "r") as f:
            records = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"Error: {EVAL_FILE} not found. Run runner.py first.")
        return

    # Group by run_id
    runs = {}
    for r in records:
        run_id = r.get("run_id")
        if run_id not in runs:
            runs[run_id] = []
        runs[run_id].append(r)
        
    total_checks = 0
    passed_checks = 0

    print("=== Verification Report ===\n")
    
    for run_id, frames in runs.items():
        print(f"Scenario: {run_id} ({len(frames)} frames recorded)")
        
        # Predicate 1: Did it trigger not_sure on collision?
        if run_id == "honest_failure":
            total_checks += 2
            
            # Simple check: Did not_sure trigger?
            triggered = any(f['decision'].get('fn') == 'not_sure' for f in frames)
            print(f"  [Simple] 'not_sure' triggered on failure: {'✅' if triggered else '❌'}")
            if triggered: passed_checks += 1
            
            # Deep Physics check: Was not_sure only triggered when collisions > 0 AND c_star >= 0.8?
            # Or conversely, verify that when it did trigger, the physics justified it.
            deep_pass = True
            for f in frames:
                if f['decision'].get('fn') == 'not_sure':
                    if f['metrics']['collisions'] == 0 or f['metrics']['c_star'] < 0.8:
                        deep_pass = False
            print(f"  [Deep Physics] 'not_sure' matched valid telemetry (Col > 0, C* > 0.8): {'✅' if deep_pass and triggered else '❌'}")
            if deep_pass and triggered: passed_checks += 1

        elif run_id == "nominal_flight":
            total_checks += 2
            # Nominal flight should favor adjust_squad_gains if C* is high
            triggered = any(f['decision'].get('fn') == 'adjust_squad_gains' for f in frames)
            print(f"  [Simple] 'adjust_squad_gains' triggered during nominal flight: {'✅' if triggered else '❌'}")
            if triggered: passed_checks += 1
            
            # Deep physics: When adjust_squad_gains fires, C* must be > 0.8 and collisions == 0
            deep_pass = True
            for f in frames:
                if f['decision'].get('fn') == 'adjust_squad_gains':
                    if f['metrics']['collisions'] > 0 or f['metrics']['c_star'] < 0.8:
                        deep_pass = False
            print(f"  [Deep Physics] 'adjust_squad_gains' matched valid telemetry (Col == 0, C* > 0.8): {'✅' if deep_pass and triggered else '❌'}")
            if deep_pass and triggered: passed_checks += 1
            
        else:
            # For obstacles, squeeze, gauntlet, etc., fragmentation occurs.
            # We expect switch_algorithm
            total_checks += 2
            triggered = any(f['decision'].get('fn') == 'switch_algorithm' for f in frames)
            print(f"  [Simple] 'switch_algorithm' triggered to save swarm: {'✅' if triggered else '❌'}")
            if triggered: passed_checks += 1
            
            # Deep physics: When switch_algorithm fires, C* must be < 0.8
            deep_pass = True
            for f in frames:
                if f['decision'].get('fn') == 'switch_algorithm':
                    if f['metrics']['c_star'] >= 0.8 and f['metrics']['collisions'] == 0:
                        # Wait, sometimes it might switch if C* is high but something else is wrong?
                        # No, the training rule strictly says switch_algorithm if C* < 0.8.
                        deep_pass = False
            print(f"  [Deep Physics] 'switch_algorithm' matched valid telemetry (C* < 0.8): {'✅' if deep_pass and triggered else '❌'}")
            if deep_pass and triggered: passed_checks += 1

    print("\n===========================")
    score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    print(f"FINAL SCORE: {passed_checks}/{total_checks} ({score:.1f}%)")
    print("===========================")

if __name__ == "__main__":
    score_run()
