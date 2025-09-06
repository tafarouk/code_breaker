#!/usr/bin/env python3
import ast, io, json, os, re, sys, tempfile, textwrap, time, subprocess
from typing import Any, Dict, List, Tuple

try:
    import resource
    def _preexec_resource_limits(cpu_seconds: int = 2, memory_mb: int = 128):
        def _apply():
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            bytes_cap = memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (bytes_cap, bytes_cap))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))
        return _apply
except Exception:
    resource = None
    def _preexec_resource_limits(*args, **kwargs):
        return None

FORBIDDEN_TOKENS = {"import", "__", "exec", "eval", "open"}
FORBIDDEN_NODES = (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal, ast.With)

class SafeAstVisitor(ast.NodeVisitor):
    def __init__(self): self.errors = []
    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.attr, str) and node.attr.startswith("__"):
            self.errors.append(f"Forbidden dunder attribute: {node.attr}")
        self.generic_visit(node)
    def visit_Name(self, node: ast.Name):
        if node.id.startswith("__"): self.errors.append(f"Forbidden dunder name: {node.id}")
    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "__import__":
            self.errors.append("Forbidden call: __import__")
        self.generic_visit(node)
    def generic_visit(self, node):
        if isinstance(node, FORBIDDEN_NODES):
            self.errors.append(f"Forbidden node: {type(node).__name__}")
        super().generic_visit(node)

def check_ast_safe(code: str):
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as e:
        return False, [f"SyntaxError: {e}"]
    v = SafeAstVisitor(); v.visit(tree)
    for tok in FORBIDDEN_TOKENS:
        if tok in code: v.errors.append(f"Forbidden token in source: '{tok}'")
    return (len(v.errors) == 0), v.errors

def _write_temp_py(source: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".py", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(source)
    return path

def run_python_source(code: str, timeout_ms: int = 2000, mem_mb: int = 128):
    temp = _write_temp_py(code)
    cmd = [sys.executable, temp]
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout_ms/1000.0, text=True,
            preexec_fn=_preexec_resource_limits(cpu_seconds=max(1, timeout_ms//1000), memory_mb=mem_mb) if resource is not None else None
        )
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", "Timeout: code exceeded time limit"
    finally:
        try: os.remove(temp)
        except Exception: pass
    return rc, out, err, time.time()-start

def eval_stdout_includes(stdout: str, needle: str) -> bool:
    return needle in stdout

def eval_forbidden_tokens(code: str, tokens):
    return not any(t in code for t in tokens)

def eval_function_contract(code: str, fn_name: str, cases, timeout_ms=2000, mem_mb=128):
    harness = f"""
    import json, sys
    PLAYER_CODE = r"{code}"
    NS = {{}}
    try:
        exec(PLAYER_CODE, NS, NS)
    except Exception as e:
        print("HARNESS: player exec failed:", e, file=sys.stderr)
        print(json.dumps({{"ok": False, "cases": []}})); sys.exit(0)
    fn = NS.get("{fn_name}")
    if not callable(fn):
        print("HARNESS: function '{fn_name}' not found", file=sys.stderr)
        print(json.dumps({{"ok": False, "cases": []}})); sys.exit(0)
    results = []
    CASES = {json.dumps(cases)}
    for args, expected in CASES:
        try:
            got = fn(*args)
            results.append(bool(got == expected))
        except Exception:
            results.append(False)
    print(json.dumps({{"ok": all(results), "cases": results}}))
    """
    rc, out, err, _ = run_python_source(harness, timeout_ms=timeout_ms, mem_mb=mem_mb)
    if rc != 0: return False, [], err
    try:
        payload = json.loads(out.strip().splitlines()[-1])
        return bool(payload.get("ok")), list(payload.get("cases", [])), err
    except Exception:
        return False, [], "HARNESS: invalid JSON output"

def eval_custom(name: str, code: str, stdout: str, args):
    return True  # hook point

def evaluate_goals(puzzle, code, stdout, limits):
    assertions = []; all_pass = True
    for goal in puzzle.get("goals", []):
        gtype = goal.get("type"); passed = False; details = {}
        if gtype == "stdout_includes":
            needle = goal.get("value", ""); passed = eval_stdout_includes(stdout, needle); details = {"needle": needle}
        elif gtype == "forbidden_tokens":
            tokens = goal.get("value", []); passed = eval_forbidden_tokens(code, tokens); details = {"tokens": tokens}
        elif gtype == "function_contract":
            fn_name = goal.get("name"); cases = goal.get("cases", [])
            ok, per_case, herr = eval_function_contract(code, fn_name, cases, timeout_ms=limits.get("cpu_ms",2000), mem_mb=limits.get("mem_mb",128))
            passed = ok; details = {"cases": per_case, "harness_err": herr}
        elif gtype == "custom_eval":
            name = goal.get("name"); args = goal.get("args", {}); passed = eval_custom(name, code, stdout, args); details = {"hook": name}
        else:
            passed = False; details = {"error": f"Unknown goal type '{gtype}'"}
        assertions.append({"name": gtype, "pass": bool(passed), **details})
        if not passed: all_pass = False
    return all_pass, assertions

def load_puzzle(puzzle_id: str):
    path = os.path.join(os.getcwd(), "content", "puzzles", f"{puzzle_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "id": puzzle_id,
        "title_key": "puzzle.fallback.title",
        "intro_key": "puzzle.fallback.intro",
        "starter_code": "print('Door unlocked')\n",
        "goals": [
            {"type":"stdout_includes","value":"Door unlocked"},
            {"type":"forbidden_tokens","value":["import","__","open"]}
        ],
        "world_actions_on_pass": [{"type":"open_door","params":{"id":"D-01"}}]
    }

def main():
    try:
        req = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"ok": False, "stderr": "Bad JSON request"})); return

    puzzle_id = req.get("puzzle_id", "unknown")
    code = req.get("code", "")
    limits = req.get("limits", {"cpu_ms": 2000, "mem_mb": 128})

    safe, errors = check_ast_safe(code)
    if not safe:
        resp = {"ok": False, "stdout": "", "stderr": "\n".join(errors),
                "assertions": [{"name":"ast_safety","pass": False, "errors": errors}],
                "score": 0, "world_actions": [],
                "telemetry": {"exec_ms": 0, "lines": len(code.splitlines())}}
        print(json.dumps(resp)); return

    rc, stdout, stderr, elapsed = run_python_source(code, timeout_ms=limits.get("cpu_ms",2000), mem_mb=limits.get("mem_mb",128))
    puzzle = load_puzzle(puzzle_id)
    all_pass, assertions = evaluate_goals(puzzle, code, stdout, limits)

    resp = {
        "ok": bool(all_pass and rc == 0 and not stderr),
        "stdout": stdout, "stderr": stderr, "assertions": assertions,
        "score": sum(1 for a in assertions if a.get("pass")),
        "world_actions": puzzle.get("world_actions_on_pass", []) if all_pass else [],
        "telemetry": {"exec_ms": int(elapsed*1000), "lines": len(code.splitlines())}
    }
    print(json.dumps(resp))

if __name__ == "__main__": main()
