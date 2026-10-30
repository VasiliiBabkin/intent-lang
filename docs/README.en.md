> Current Sedrava documentation / Актуальная документация: [Quick Start](QUICKSTART.md), [Language reference / Справочник](LANGUAGE_0_9.md), [Build / Сборка](BUILD.md), [FAQ](FAQ.md), [Limitations / Ограничения](KNOWN_LIMITATIONS.md), [Audit / Аудит](ALPHA_AUDIT.md). Older prototype commands below are historical.

# Sedrava documentation (English)

**Status:** experimental language; not production-ready.

Sedrava describes application state, actions, invariants and executable tests. Its restricted, typed AST is interpreted in Python or compiled to Android (Kotlin/Compose) and the web (standalone HTML/JavaScript).

## Quick start

Python 3.10+ (CI checks 3.10, 3.12 and 3.13):

```sh
python -m unittest discover -s tests -v
python -m sedrava_cli build web examples/workflow.sdr --output build/web/index.html
```

Open `build/web/index.html` in a browser. Android generation:

```sh
python -m sedrava_cli build android examples/workflow.sdr --output build/generated-android
```

## Language elements

- `app "Name"`: application name.
- `state name = value`: integer, boolean or text state.
- `action name:`: assignments and `if` / `else` blocks.
- `rule expression`: invariant, checked after an action.
- `test name: action, action -> expression`: independent test starting from initial state.
- `screen main:`: basic `text`, `value` and `button` widgets.

Expressions support integer arithmetic, comparisons and boolean operators. Each action runs on a private candidate state; invariants either commit the whole action or reject it without changes.

See [Russian guide](README.ru.md) and [example](../examples/workflow.sdr).

## Current limitations

No user-defined functions, modules, IO, async or standard library. Text, bounded records/collections and navigation are implemented in the unreleased 0.10 sources. Bounded Python/JavaScript/Kotlin conformance and real browser/emulator scenarios are tested; this is not exhaustive equivalence or a stable-support claim. See the [stability audit](STABILITY_AUDIT_010.md) and [compatibility contract](COMPATIBILITY_010.md).

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

## Records and collections / Записи и коллекции (unreleased 0.10)

Current unreleased sources integrate typed records and bounded ordered lists into `.sdr`,
with stable IDs, atomic actions, strict snapshots and generated Web/Compose UI.
Записи и списки доступны в языке на ветке разработки; 0.10 не выпущена.

- [English task-manager guide](RECORDS_QUICKSTART.en.md)
- [Руководство на русском](RECORDS_QUICKSTART.ru.md)
- [Measured coverage / Фактические проверки](COLLECTIONS_010_REPORT.md)

## Multi-screen navigation / Многоэкранная навигация (unreleased 0.10)

Named screens, guarded atomic transitions and a bounded Back stack are implemented
in the core and both generators. One `.sdr` file generates the two-screen task manager.
Экраны и переходы — возможность языка; опубликованного выпуска 0.10 нет.

- [English guide](NAVIGATION_QUICKSTART.en.md)
- [Русское руководство](NAVIGATION_QUICKSTART.ru.md)
- [Syntax and semantics](NAVIGATION_010_CONTRACT.md)
- [Measured report](NAVIGATION_010_REPORT.md)

## Release readiness / Подготовка к RC (unreleased 0.10)

Independent deterministic Android IDs and `--application-id` are implemented.
Независимые Android-приложения собираются с постоянным ID; название отделено от пакета.
[English identity/build guide](ANDROID_ID.en.md) · [Русская инструкция](ANDROID_ID.ru.md).
Wheel/sdist include examples, documentation and license under `sys.prefix/share/sedrava`.
Дистрибутив содержит примеры, документацию и лицензию; публикация 0.10 не выполнялась.

Measured RC readiness / Фактическая готовность RC: [report / отчёт](RELEASE_READINESS_010_REPORT.md).

## 0.10.0rc1 preparation / Подготовка RC (not published)

[Release notes EN](RELEASE_NOTES_0_10_0rc1.en.md) · [RU](RELEASE_NOTES_0_10_0rc1.ru.md) · [Upgrade/rollback EN](UPGRADE_0_10_0rc1.en.md) · [RU](UPGRADE_0_10_0rc1.ru.md) · [RC report](RC_010_REPORT.md).
Use a verified local wheel in a separate environment; no PyPI/TestPyPI RC has been published.
Установка — из проверенного локального wheel в отдельное окружение; автоматической миграции данных нет.

Stability / стабильность: [audit](STABILITY_AUDIT_010.md), [compatibility](COMPATIBILITY_010.md), [stable gates](STABLE_RELEASE_GATES_010.md). Исправления аудита требуют нового rc2; подготовленные артефакты rc1 не меняются.

## 0.10.0rc2 preparation / Подготовка RC2 (not published)

[Release notes EN](RELEASE_NOTES_0_10_0rc2.en.md) · [RU](RELEASE_NOTES_0_10_0rc2.ru.md) · [Upgrade/rollback EN](UPGRADE_0_10_0rc2.en.md) · [RU](UPGRADE_0_10_0rc2.ru.md) · [RC2 report](RC2_010_REPORT.md).
Current source version: **0.10.0rc2**, Android versionCode **10002**. This is a separately prepared experimental candidate, not stable 0.10.0 or a publication. The original rc1 kit remains immutable.
Текущая версия исходников — 0.10.0rc2, код Android — 10002. Публикация требует отдельного решения владельца; физическое устройство не проверено.
