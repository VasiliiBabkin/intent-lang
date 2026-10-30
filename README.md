# Sedrava — unreleased 0.10 text, records, collections and navigation

**Describe the application; get the application. / Описал — получил.**

The published compatibility baseline is [Sedrava 0.9.0a1](https://github.com/VasiliiBabkin/sedrava/releases/tag/v0.9.0a1). This branch adds first-class text, typed records bounded collections and multi-screen navigation end-to-end and identifies local development builds as **0.10.0.dev0**; no 0.10 release, tag or PyPI publication is created.

Start with [Quick Start](docs/QUICKSTART.md), the [text reference](docs/LANGUAGE_0_10_TEXT.md), [text profile example](examples/text_profile.sdr), and [measured report](docs/TEXT_010_REPORT.md). The [task manager](examples/task_manager.sdr) now uses records and lists directly in `.sdr`; the [navigation example](docs/NAVIGATION_QUICKSTART.en.md) adds guarded screens and Back.

## Published 0.9 baseline and common tooling

**Describe the application; get the application. / Опиши приложение — получи приложение.**

Sedrava is an experimental declarative programming language for small applications: describe text/int32/boolean state, typed record collections, derived values, atomic actions, invariants and a simple UI; generate a standalone Web app or an Android/Compose project from the same source.

**For learning and experimental development, not production.** 0.9.0a1 is published; this checkout is an unreleased 0.10 development increment. No Sedrava package is published on PyPI. Historical Intent 0.7 releases are a separate project history.

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
python -m pip install ".[test]"
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

## Records and collections / Записи и коллекции (unreleased 0.10)

The development branch integrates typed records and bounded ordered lists into `.sdr`,
with stable IDs, atomic actions, strict snapshots and generated Web/Compose UI.
Записи и списки доступны в языке на ветке разработки; 0.10 не выпущена.

- [English task-manager guide](docs/RECORDS_QUICKSTART.en.md)
- [Руководство на русском](docs/RECORDS_QUICKSTART.ru.md)
- [Measured coverage / Фактические проверки](docs/COLLECTIONS_010_REPORT.md)

## Multi-screen navigation / Многоэкранная навигация (unreleased 0.10)

Named screens, guarded atomic transitions and a bounded Back stack are implemented
in the core and both generators. One `.sdr` file generates the two-screen task manager.
Экраны и переходы — возможность языка; опубликованного выпуска 0.10 нет.

- [English guide](docs/NAVIGATION_QUICKSTART.en.md)
- [Русское руководство](docs/NAVIGATION_QUICKSTART.ru.md)
- [Syntax and semantics](docs/NAVIGATION_010_CONTRACT.md)
- [Measured report](docs/NAVIGATION_010_REPORT.md)
