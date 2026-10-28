# Intent

<p align="center"><img src="assets/branding/intent-logo-512.png" alt="Intent programming language logo" width="240"></p>

Experimental declarative programming language for application state, transitions, invariants and executable tests.

**Documentation:** [Русский](docs/README.ru.md) · [English](docs/README.en.md)

**Install from PyPI (published version 0.7.0):** [`intent-lng`](https://pypi.org/project/intent-lng/). The command-line tool is named `intent`.

```bash
python -m pip install --upgrade intent-lng==0.7.0
intent --version
```

The active 0.8/0.9 development features (`derive`, `persist`, `input`, conditional widgets) are **not part of the published 0.7.0 release**. For those features, use the development branch and its CI artifacts.

**License:** [Apache 2.0](LICENSE) · [Open-source policy (RU)](docs/OPEN_SOURCE.ru.md) · [Open-source policy (EN)](docs/OPEN_SOURCE.en.md)

**Contributing:** [Guidelines](CONTRIBUTING.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

## Quick start

Requires Python 3.10+ according to package metadata; CI covers Python 3.12 and 3.13.

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

**Experimental, not production-ready.** Android 0.3 has been manually tested on a device. Web generation has automated tests; coverage remains limited. Python/JavaScript differential conformance tests cover selected scenarios, not all possible programs.

Published package: [`intent-lng` 0.7.0](https://pypi.org/project/intent-lng/). [0.7 release history](docs/RELEASE_NOTES_0_7.ru-en.md). The repository's `pyproject.toml` may still describe the earlier alpha source version; it must be synchronized as part of a separate release preparation, not treated as proof that the PyPI package is outdated.
