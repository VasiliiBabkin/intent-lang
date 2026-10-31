# Sedrava — unreleased 0.10 text, records, collections and navigation

**Describe the application; get the application. / Описал — получил.**

**[Dedication / Посвящение](DEDICATION.md):** Геннадию Ивановичу Смирных — учителю информатики, благодаря которому автор Sedrava понял и полюбил программирование.

The published compatibility baseline is [Sedrava 0.9.0a1](https://github.com/VasiliiBabkin/sedrava/releases/tag/v0.9.0a1). This branch adds first-class text, typed records bounded collections and multi-screen navigation end-to-end and identifies local development builds as **0.10.0rc2** (experimental RC preparation, not published); no 0.10 release, tag or PyPI publication is created.

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

## Release readiness / Подготовка к RC (unreleased 0.10)

Independent deterministic Android IDs and `--application-id` are implemented.
Независимые Android-приложения собираются с постоянным ID; название отделено от пакета.
[English identity/build guide](docs/ANDROID_ID.en.md) · [Русская инструкция](docs/ANDROID_ID.ru.md).
Wheel/sdist include examples, documentation and license under `sys.prefix/share/sedrava`.
Дистрибутив содержит примеры, документацию и лицензию; публикация 0.10 не выполнялась.

Measured RC readiness / Фактическая готовность RC: [report / отчёт](docs/RELEASE_READINESS_010_REPORT.md).

## 0.10.0rc1 preparation / Подготовка RC (not published)

[Release notes EN](docs/RELEASE_NOTES_0_10_0rc1.en.md) · [RU](docs/RELEASE_NOTES_0_10_0rc1.ru.md) · [Upgrade/rollback EN](docs/UPGRADE_0_10_0rc1.en.md) · [RU](docs/UPGRADE_0_10_0rc1.ru.md) · [RC report](docs/RC_010_REPORT.md).
Use a verified local wheel in a separate environment; no PyPI/TestPyPI RC has been published.
Установка — из проверенного локального wheel в отдельное окружение; автоматической миграции данных нет.

Stability / стабильность: [audit](docs/STABILITY_AUDIT_010.md), [compatibility](docs/COMPATIBILITY_010.md), [release gates](docs/STABLE_RELEASE_GATES_010.md). Stabilization changes are not a new release; rc1 artifacts remain unchanged.

## 0.10.0rc2 preparation / Подготовка RC2 (not published)

[Release notes EN](docs/RELEASE_NOTES_0_10_0rc2.en.md) · [RU](docs/RELEASE_NOTES_0_10_0rc2.ru.md) · [Upgrade/rollback EN](docs/UPGRADE_0_10_0rc2.en.md) · [RU](docs/UPGRADE_0_10_0rc2.ru.md) · [RC2 report](docs/RC2_010_REPORT.md).
Current source version: **0.10.0rc2**, Android versionCode **10002**. This is a separately prepared experimental candidate, not stable 0.10.0 or a publication. The original rc1 kit remains immutable.
Текущая версия исходников — 0.10.0rc2, код Android — 10002. Публикация требует отдельного решения владельца; физическое устройство не проверено.

## Experimental Web UI 0.11 / Экспериментальный Web UI 0.11

Source-branch feature, separate from published RC2. Режим из этой ветки, отдельно от опубликованного RC2.

```sh
sedrava check examples/web_ui_011_landing.sdr
sedrava build site examples/web_ui_011_landing.sdr --output build/site
python -m http.server 8000 --directory build/site
```

13 static primitives, responsive layouts and safe assets; no deployment. 13 статических компонентов, адаптивность и безопасные ресурсы; без публикации сайта. [English](docs/WEB_UI_011.en.md) · [Русский](docs/WEB_UI_011.ru.md). Existing application commands are unchanged. Команды приложений не изменены.
