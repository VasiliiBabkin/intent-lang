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

## Install published version 0.7.0 from PyPI

The published distribution is [`intent-lng`](https://pypi.org/project/intent-lng/); the CLI executable is `intent`. Package metadata requires Python 3.10+.

```sh
python -m pip install --upgrade intent-lng==0.7.0
intent --version
```

CLI usage:

```sh
intent check examples/workflow.intent
intent test examples/workflow.intent
intent build web examples/workflow.intent --output build/web/index.html
intent build android examples/workflow.intent --output build/generated-android
```

Android project compilation additionally requires Java, the Android SDK and Gradle. The 0.7.0 package remains experimental.

### Published release versus development branch

The `derive`, `persist`, `input`, and `show` features belong to the later 0.8/0.9 development work and **are not included in the published 0.7.0 package**. Use the [development branch](https://github.com/VasiliiBabkin/intent-lang/tree/feature/intent-0.9-security-integrated) and CI artifacts to test these features. Development milestones do not imply corresponding PyPI releases.

See [0.7 release history](RELEASE_NOTES_0_7.ru-en.md).
