# Sedrava documentation (English)

**Status:** experimental language; not production-ready.

Sedrava describes application state, actions, invariants and executable tests. Its restricted, typed AST is interpreted in Python or compiled to Android (Kotlin/Compose) and the web (standalone HTML/JavaScript).

## Quick start

Python 3.12+:

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

## Experimental pip installation (0.5)

Not published to PyPI yet. Install from the development branch:

```sh
python -m pip install "git+https://github.com/VasiliiBabkin/sedrava-lang.git@feature/sedrava-0.5-cli-package"
sedrava --version
sedrava check examples/workflow.sdr
sedrava test examples/workflow.sdr
sedrava build web examples/workflow.sdr
```

For an isolated CLI installation, use `pipx install "git+https://github.com/VasiliiBabkin/sedrava-lang.git@feature/sedrava-0.5-cli-package"`.

The PyPI project name and project license are not finalized. Cross-platform packaging CI must pass before this build is considered validated.


> Sedrava is not yet published on PyPI. Install from this source checkout using `python -m pip install .`; the CLI is `sedrava`, and source files end in `.sdr`. The GitHub repository has not yet been renamed. The domain sedrava.com is prospective only.
