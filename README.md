# Sedrava — 0.9.0a1 Alpha candidate

**Describe the application; get the application. / Опиши приложение — получи приложение.**

Sedrava is an experimental declarative programming language for small applications: describe integer/boolean state, derived values, atomic actions, invariants and a simple UI; generate a standalone Web app or an Android/Compose project from the same source.

**For learning and experimental development, not production.** This is an unreleased candidate until the exact release commit passes its gates. No Sedrava package is published on PyPI. Historical Intent 0.7 releases are a separate project history.

[Quick Start / Быстрый старт](docs/QUICKSTART.md) · [Русский](docs/README.ru.md) · [English](docs/README.en.md)

## Install and try

Python 3.10+ and Git are required. Run from a virtual environment:

```sh
git clone https://github.com/VasiliiBabkin/sedrava.git
cd sedrava
python -m pip install .
sedrava --version
sedrava check examples/reference_09.sdr
sedrava test examples/reference_09.sdr
sedrava run examples/reference_09.sdr add add
sedrava build web examples/reference_09.sdr --output build/web/index.html
python -m http.server 8000 --directory build/web
```

Open http://localhost:8000. Android generation:

```sh
sedrava build android examples/reference_09.sdr --output build/reference-09-android
```

To produce an APK, install a full JDK, SDK 35 and Gradle 8.11.1 and follow the [build guide](docs/BUILD.md). `build android` generates sources; it does not invoke Gradle. No accounts, telemetry, advertising or cloud runtime services.

## Documentation

- [Quick Start: installation and first program](docs/QUICKSTART.md)
- [0.9 syntax, types, state, actions, rules, input and persistence](docs/LANGUAGE_0_9.md)
- [Web and Android builds](docs/BUILD.md)
- [Complete executable examples](examples/README.md): constrained counter, manual countdown, habit progress, validated input and Sedrava 0.9 Lab
- [FAQ and troubleshooting](docs/FAQ.md) · [Known limitations](docs/KNOWN_LIMITATIONS.md)
- [Changelog](CHANGELOG.md) · [Release notes](docs/RELEASE_NOTES_0_9_0a1.md) · [Engineering audit and evidence](docs/ALPHA_AUDIT.md)
- [Roadmap](docs/ROADMAP.md) · [0.10 design](docs/PLAN_0_10_UI.md)

## Architecture and verification

Source → restricted typed AST (`sedrava_core.py`) → interpreter / Web (`web_codegen.py`) / Android (`android_codegen_v03.py`). Builds run embedded language tests. Actions change a candidate state sequentially; all final rules must hold before atomic commit. Integers and arithmetic intermediates are checked signed 32-bit values. Python runtime has no third-party dependencies and never executes source through `eval`/`exec`.

```sh
python -m unittest discover -s tests -v
python -m pip install playwright
python -m playwright install --with-deps chromium
python scripts/test_web_browser.py
python -m pip install build twine
python -m build
python -m twine check dist/*
python scripts/audit_dist.py
```

Node.js is needed for differential conformance tests; Chromium tests are a separate real-browser suite. Android build/Lint is separate from UI acceptance. Previously supplied manual Android 16 results are preserved in [acceptance evidence](docs/ANDROID_09_ACCEPTANCE.md); they do not verify newly changed APKs. See the audit for current results and infrastructure limitations.

**License:** [Apache 2.0](LICENSE) · [Contributing](CONTRIBUTING.md) · [Code of Conduct](CODE_OF_CONDUCT.md). `sedrava.com` is a proposed domain, not an official website.
