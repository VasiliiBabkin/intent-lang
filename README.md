# Intent

Experimental declarative language for specifying application state, actions, invariants and tests.

## Quick start

```bash
python -m unittest discover -s tests -v
python intent.py examples/timer.intent
```

The initial prototype is a deterministic interpreter, not yet an Android compiler. Android/Compose generation is the next experimental milestone.

## Design principles

- Explicit state and transitions
- Executable assertions
- No arbitrary evaluation of source code
- Deterministic compilation and verification
- Platform-independent core
