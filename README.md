# Intent

Experimental declarative programming language for application state, transitions, invariants and executable tests.

**Documentation:** [Русский](docs/README.ru.md) · [English](docs/README.en.md)

**License:** [Apache 2.0](LICENSE) · [Open-source policy (RU)](docs/OPEN_SOURCE.ru.md) · [Open-source policy (EN)](docs/OPEN_SOURCE.en.md)

**Contributing:** [Guidelines](CONTRIBUTING.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

## Quick start

Requires Python 3.12+.

```bash
python -m unittest discover -s tests -v
python web_codegen.py examples/workflow.intent --output build/web/index.html
```

Open `build/web/index.html` in a browser.

To generate an Android/Compose project:

```bash
python android_codegen_v03.py examples/workflow.intent --output build/generated-android
```

The generated Android project additionally requires Java, Android SDK and Gradle.

## Architecture

Intent source → restricted typed AST (`intent_core.py`) → interpreter / Android backend / web backend.

Each action computes a candidate state. All declared invariants must hold before changes are committed. The same source program is used by both code generators.

## Status

**Experimental, not production-ready.** Android 0.3 has been manually tested on a device. Web 0.4 generation and its automated tests are under validation. Python/JavaScript differential conformance tests cover selected scenarios, not all possible programs.

Development branch: `feature/intent-0.7-open-source`.
