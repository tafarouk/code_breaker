# Codebreaker Architecture Sketch

```
┌───────────────┐      HTTPS/IPC      ┌────────────────┐
│  Game Client  │  <----------------> │  Puzzle Engine │
│ (Unity/Godot) │                     │  & Sandbox     │
└──────┬────────┘                     └───────┬────────┘
       │                                      │
       ▼                                      ▼
┌───────────────┐                      ┌───────────────┐
│  Code Editor  │── submit(code) ────▶ │  Python VM    │
│ + HUD/Dialogs │◀── results JSON ──── │ (Sandboxed)   │
└───────────────┘                      └───────────────┘
       ▲                                      │
       │ world actions                         │ stdout/stderr, asserts
       ▼                                      ▼
┌───────────────┐                      ┌───────────────┐
│ WorldActionBus│◀── world_actions ─── │ Test Runner   │
└───────────────┘                      └───────────────┘
```

Key modules:
- AST safety → sandboxed subprocess
- Goal evaluators: stdout, function contracts, custom hooks
- Content pipeline: JSON puzzles + solutions + i18n packs
- CI: validation, i18n key coverage, smoke tests
