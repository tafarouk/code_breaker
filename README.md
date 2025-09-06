# Codebreaker: Python Protocols

[![CI: Validate Content & Tests](https://github.com/OWNER/REPO/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/OWNER/REPO/actions/workflows/validate.yml)

A graphical, puzzle-driven adventure that teaches Python through a cyberpunk hacking narrative.

## Quickstart
```bash
python tools/validate_content.py content/puzzles
python tools/i18n_check.py --puzzles content/puzzles --i18n i18n
python smoke/run_smoke.py
```

## Localization Guide (excerpt)
See `LOCALIZATION.md` for full details.

- Use i18n keys in puzzles (`title_key`, `intro_key`, `hints_keys`)
- Add keys first to `i18n/en.json`, then translate in `ru.json`, `fr.json`, `ar.json`
- Validate with:
```bash
python tools/i18n_check.py --puzzles content/puzzles --i18n i18n
```
