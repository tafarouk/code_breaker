# Localization Guide

## How to add new text
Use i18n keys in puzzles, not literals:
```json
{ "title_key": "puzzle.L1-P3.title", "intro_key": "puzzle.L1-P3.intro" }
```

Add keys to `i18n/en.json`, then mirror into `ru.json`, `fr.json`, `ar.json`.

## Check locally
```bash
python tools/i18n_check.py --puzzles content/puzzles --i18n i18n
```

## Best practices
- English is source of truth
- Namespaces: puzzle.<id>.*, hint.*, fmt.*
- Keep code keywords in English across locales
