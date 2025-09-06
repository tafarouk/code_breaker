#!/usr/bin/env python3
import argparse, json, os, sys, glob

def load_pack(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "keys" not in data:
        if "meta" in data and isinstance(data["meta"], dict):
            meta = data["meta"]
            data["meta.lang"] = str(meta.get("lang", ""))
            data["meta.rtl"]  = "true" if meta.get("rtl", False) else "false"
        return data
    if isinstance(data, dict) and "keys" in data and "values" in data:
        out = {}
        ks, vs = data.get("keys") or [], data.get("values") or []
        for i in range(min(len(ks), len(vs))):
            out[str(ks[i])] = str(vs[i])
        meta = data.get("meta") or {}
        out["meta.lang"] = str(meta.get("lang", ""))
        out["meta.rtl"]  = "true" if meta.get("rtl", False) else "false"
        return out
    raise ValueError(f"Unsupported i18n format in {path}")

def collect_required_keys(puzzles_dir):
    keys = set()
    for fn in os.listdir(puzzles_dir):
        if not fn.endswith(".json"): continue
        pz_path = os.path.join(puzzles_dir, fn)
        with open(pz_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for field in ("title_key", "intro_key"):
            k = data.get(field)
            if k: keys.add(k)
        for k in (data.get("hints_keys") or []):
            if k: keys.add(k)
        for act in (data.get("world_actions_on_pass") or []):
            mk = act.get("message_key")
            if mk: keys.add(mk)
    return keys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--puzzles", default="content/puzzles")
    ap.add_argument("--i18n", default="i18n")
    ap.add_argument("--non-strict", action="store_true")
    args = ap.parse_args()

    required = collect_required_keys(args.puzzles)
    if not required:
        print("No i18n keys referenced by puzzles. ✅")
        return

    lang_files = sorted([f for f in os.listdir(args.i18n) if f.endswith('.json')])
    if not lang_files:
        print(f"❌ No language packs found in {args.i18n}")
        sys.exit(1)

    packs = {}
    for lf in lang_files:
        lang = os.path.splitext(lf)[0]
        packs[lang] = load_pack(os.path.join(args.i18n, lf))

    if "en" not in packs:
        print("❌ Missing base pack: i18n/en.json")
        sys.exit(1)

    failures = {}
    langs_to_check = ["en"] if args.non_strict else list(packs.keys())

    for lang in langs_to_check:
        pack = packs[lang]
        missing = sorted([k for k in required if k not in pack])
        if missing:
            failures[lang] = missing

    if failures:
        print("❌ Missing i18n keys:")
        for lang, miss in failures.items():
            sample = ", ".join(miss[:20])
            more = f" (+{len(miss)-20} more)" if len(miss) > 20 else ""
            print(f" - {lang}: {sample}{more}")
        sys.exit(1)

    print(f"✅ All {len(required)} keys found in language packs: {', '.join(langs_to_check)}")

if __name__ == "__main__":
    main()
