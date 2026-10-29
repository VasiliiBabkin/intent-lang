# Sedrava Programming Language

Experimental declarative programming language for application state, transitions, invariants and executable tests.

**Documentation:** [Русский](docs/README.ru.md) · [English](docs/README.en.md)

**Install from this checkout:** `python -m pip install .` (CLI: `sedrava`). The `sedrava` distribution has **not** been published on PyPI.

**License:** [Apache 2.0](LICENSE) · [Open-source policy (RU)](docs/OPEN_SOURCE.ru.md) · [Open-source policy (EN)](docs/OPEN_SOURCE.en.md)

**Contributing:** [Guidelines](CONTRIBUTING.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

## Quick start

Requires Python 3.10+ according to package metadata; CI covers Python 3.12 and 3.13.

```bash
python -m unittest discover -s tests -v
python web_codegen.py examples/workflow.sdr --output build/web/index.html
```

Open `build/web/index.html` in a browser.

To generate an Android/Compose project:

```bash
python android_codegen_v03.py examples/workflow.sdr --output build/generated-android
```

The generated Android project additionally requires Java, Android SDK and Gradle.

## Architecture

Sedrava source → restricted typed AST (`sedrava_core.py`) → interpreter / Android backend / web backend.

Each action computes a candidate state. All declared invariants must hold before changes are committed. The same source program is used by both code generators.

## Status

**Experimental, not production-ready.** Android 0.3 has been manually tested on a device. Web generation has automated tests; coverage remains limited. Python/JavaScript differential conformance tests cover selected scenarios, not all possible programs.

**Development candidate: Sedrava 0.9.0a1 (unreleased).** The 0.7.1a1 version was an abandoned rebrand release candidate, not a GitHub Release. See [0.9 integration status](docs/SEDRAVA_0_9_STATUS.md) and [roadmap](docs/ROADMAP.md). No PyPI release.

The GitHub repository is now `VasiliiBabkin/sedrava`. `sedrava.com` is a proposed domain, not an official website.

### Sedrava 0.9 reference application

The [reference application](examples/reference_09.sdr) exercises persistent state, validated numeric input, derived values, guarded actions and conditional UI. [Device verification checklist and APK build instructions](docs/REFERENCE_09.md). This is a test application, not a production UI.
