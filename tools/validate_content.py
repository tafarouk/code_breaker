import json, sys, os, re

FORBIDDEN = ["import", "exec", "eval", "open", "__"]

def validate_puzzle(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for field in ["id", "starter_code", "goals"]:
        if field not in data:
            return f"❌ Missing field `{field}`"

    # ID should match filename (without .json)
    fn_id = os.path.splitext(os.path.basename(path))[0]
    if data["id"] != fn_id:
        return f"❌ id '{data['id']}' must match filename '{fn_id}'"

    # ID format
    if not re.match(r"^L\d+-P\d+", data["id"]):
        return f"❌ Invalid id format: {data['id']}"

    code = data.get("starter_code", "")
    for token in FORBIDDEN:
        if token in code:
            return f"❌ Forbidden token `{token}` in starter_code"

    if not isinstance(data["goals"], list) or not data["goals"]:
        return "❌ Goals must be non-empty list"

    # Warn if no hints keys provided
    if "hints" not in data and "hints_keys" not in data:
        print(f"⚠️  Warning: no hints in {data['id']}")

    return f"✅ {data['id']} valid"


def walk_dir(puzzles_dir):
    errors = []
    for fn in os.listdir(puzzles_dir):
        if fn.endswith(".json"):
            result = validate_puzzle(os.path.join(puzzles_dir, fn))
            print(result)
            if result.startswith("❌"):
                errors.append(result)
    return errors


if __name__ == "__main__":
    puzzles_dir = sys.argv[1] if len(sys.argv) > 1 else "content/puzzles"
    errors = walk_dir(puzzles_dir)
    if errors:
        print("\nValidation failed:")
        for e in errors: print(" -", e)
        sys.exit(1)
    else:
        print("\nAll puzzles passed ✅")
