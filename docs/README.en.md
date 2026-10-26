# Intent documentation (English)

**Status:** experimental language; not production-ready.

Intent describes application state, actions, invariants and executable tests. Its restricted, typed AST is interpreted in Python or compiled to Android (Kotlin/Compose) and the web (standalone HTML/JavaScript).

## Quick start

Python 3.12+:

```sh
python -m unittest discover -s tests -v
python web_codegen.py examples/workflow.intent --output build/web/index.html
```

Open `build/web/index.html` in a browser. Android generation:

```sh
python android_codegen_v03.py examples/workflow.intent --output build/generated-android
```

## Language elements

- `app "Name"`: application name.
- `state name = value`: integer or boolean state.
- `action name:`: assignments and `if` / `else` blocks.
- `rule expression`: invariant, checked after an action.
- `test name: action, action -> expression`: independent test starting from initial state.
- `screen main:`: basic `text`, `value` and `button` widgets.

Expressions support integer arithmetic, comparisons and boolean operators. Each action runs on a private candidate state; invariants either commit the whole action or reject it without changes.

See [Russian guide](README.ru.md) and [example](../examples/workflow.intent).

## Current limitations

No user-defined functions, collections, modules, IO, async, standard library or production-level diagnostics. The web backend is experimental; equivalence across runtimes still needs end-to-end verification.
