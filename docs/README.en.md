> Current 0.9 alpha documentation / Актуальная документация: [Quick Start](QUICKSTART.md), [Language reference / Справочник](LANGUAGE_0_9.md), [Build / Сборка](BUILD.md), [FAQ](FAQ.md), [Limitations / Ограничения](KNOWN_LIMITATIONS.md), [Audit / Аудит](ALPHA_AUDIT.md). Older prototype commands below are historical.

# Sedrava documentation (English)

**Status:** experimental language; not production-ready.

Sedrava describes application state, actions, invariants and executable tests. Its restricted, typed AST is interpreted in Python or compiled to Android (Kotlin/Compose) and the web (standalone HTML/JavaScript).

## Quick start

Python 3.10+ (CI uses Python 3.12/3.13):

```sh
python -m unittest discover -s tests -v
python web_codegen.py examples/workflow.sdr --output build/web/index.html
```

Open `build/web/index.html` in a browser. Android generation:

```sh
python android_codegen_v03.py examples/workflow.sdr --output build/generated-android
```

## Language elements

- `app "Name"`: application name.
- `state name = value`: integer or boolean state.
- `action name:`: assignments and `if` / `else` blocks.
- `rule expression`: invariant, checked after an action.
- `test name: action, action -> expression`: independent test starting from initial state.
- `screen main:`: basic `text`, `value` and `button` widgets.

Expressions support integer arithmetic, comparisons and boolean operators. Each action runs on a private candidate state; invariants either commit the whole action or reject it without changes.

See [Russian guide](README.ru.md) and [example](../examples/workflow.sdr).

## Current limitations

No user-defined functions, collections, modules, IO, async, standard library or production-level diagnostics. The web backend is experimental; equivalence across runtimes still needs end-to-end verification.

## Install from source

```sh
python -m pip install .
sedrava --version
sedrava check examples/workflow.sdr
sedrava test examples/workflow.sdr
sedrava build web examples/workflow.sdr
```

The `sedrava` distribution is not published on PyPI.

> Sedrava is not yet published on PyPI. Install from this source checkout using `python -m pip install .`; the CLI is `sedrava`, and source files end in `.sdr`. The GitHub repository is now `VasiliiBabkin/sedrava`. The domain sedrava.com is prospective only.
