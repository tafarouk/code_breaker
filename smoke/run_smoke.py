import os, json, subprocess, sys

PUZZLE_DIR = "content/puzzles"
SOL_DIR = "content/solutions"
ENGINE_CMD = [sys.executable, "engine/src/run.py"]

def run_solution(puzzle_id, solution_path):
    code = open(solution_path, "r", encoding="utf-8").read()
    req = {"puzzle_id": puzzle_id, "code": code, "limits": {"cpu_ms": 2000, "mem_mb": 128}}
    proc = subprocess.run(
        ENGINE_CMD, input=json.dumps(req).encode(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
    )
    if proc.returncode != 0:
        print(f"❌ Engine crashed for {puzzle_id}\n{proc.stderr.decode()}")
        return None
    try:
        return json.loads(proc.stdout.decode())
    except Exception as e:
        print(f"❌ Bad JSON from engine for {puzzle_id}: {e}")
        return None

def main():
    failures = []
    for fn in sorted(os.listdir(PUZZLE_DIR)):
        if not fn.endswith('.json'): continue
        path = os.path.join(PUZZLE_DIR, fn)
        data = json.load(open(path, 'r', encoding='utf-8'))
        puzzle_id = data["id"]
        sol_path = os.path.join(SOL_DIR, puzzle_id + ".py")
        if not os.path.exists(sol_path):
            print(f"⚠️  No solution found for {puzzle_id}, skipping"); continue
        print(f"▶ Running solution for {puzzle_id}...")
        result = run_solution(puzzle_id, sol_path)
        if not result or not result.get("ok", False):
            failures.append(puzzle_id); print(f"❌ FAILED {puzzle_id}")
        else:
            print(f"✅ PASSED {puzzle_id}")
    print("\n--- Smoke Summary ---")
    if failures:
        print("❌ Some puzzles failed:", failures); sys.exit(1)
    else:
        print("✅ All reference solutions passed")

if __name__ == "__main__": main()
