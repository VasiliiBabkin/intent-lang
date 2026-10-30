# Quick Start / Быстрый старт

For the current unreleased sources: [unreleased first-class text guide](LANGUAGE_0_10_TEXT.md). Published baseline: 0.9.0a1; current experimental candidate: 0.10.0rc2, not a published 0.10.

**Describe the application; get the application. / Опиши приложение — получи приложение.**

Sedrava describes local application state, rules, actions and a small UI. The 0.9 alpha targets learning and experimental offline applications; it is not a production framework. No accounts, cloud service or runtime Python dependencies are required.

## Install / Установка

Install Python 3.10+ and Git. From a terminal:

```sh
git clone https://github.com/VasiliiBabkin/sedrava.git
cd sedrava
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install .
sedrava --version
sedrava --help
```

Text, records and navigation are integrated in the current sources. Read the [stability audit](STABILITY_AUDIT_010.md) before distributing applications; the audit recommends rc2 and does not replace the original rc1 kit. Do not `pip install sedrava` from PyPI: no Sedrava package has been published there. On Windows `py -3` may be needed instead of `python`; quote paths containing spaces.

Create `hello.sdr` (plain UTF-8):

```sedrava
app "Hello Sedrava"
state count = 0
action add: count = count + 1
rule count >= 0 and count <= 10
test once: add -> count == 1
screen main:
    text "Hello Sedrava"
    value count
    button "Add" -> add
```

```sh
sedrava check hello.sdr
sedrava test hello.sdr
sedrava run hello.sdr add add
sedrava build web hello.sdr --output build/web/index.html
python -m http.server 8000 --directory build/web
```

Open http://localhost:8000. `run` prints `{"count": 2}`; it is a deterministic interpreter, with no UI or event loop. `check` checks declarations, types, initial values and rules; `test` executes embedded tests. Builds also execute embedded tests. Ctrl+C stops the HTTP server.

Next: [language syntax and semantics](LANGUAGE_0_9.md), [complete examples](../examples/README.md), [Web/Android build guide](BUILD.md), [FAQ](FAQ.md), [known limitations](KNOWN_LIMITATIONS.md).

Русский: установите Python и Git, создайте виртуальное окружение и установите проект командой `python -m pip install .`. Сохраните пример в UTF-8, проверьте его командами `check` и `test`. `run` выводит состояние после указанных действий; `build web` создаёт HTML, а `build android` — исходный Gradle-проект. Для APK нужны дополнительные инструменты из инструкции сборки. Синтаксис языка остаётся английским.

## First-class text / Полноценный текст

Run `sedrava check examples/text_profile.sdr`, `sedrava test examples/text_profile.sdr`, `sedrava run examples/text_profile.sdr rename`, then `sedrava build web examples/text_profile.sdr --output build/text-web/index.html`. Serve that directory as above. `sedrava build android examples/text_profile.sdr --output build/text-android` produces the Android project without manual application-code changes. Follow the [text guide](LANGUAGE_0_10_TEXT.md) for APK/JVM/Lint commands and input/restore semantics.

## Records and collections / Записи и коллекции (unreleased 0.10)

The development branch integrates typed records and bounded ordered lists into `.sdr`,
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

## 0.10.0rc2 preparation / Подготовка RC2 (not published)

[Release notes EN](RELEASE_NOTES_0_10_0rc2.en.md) · [RU](RELEASE_NOTES_0_10_0rc2.ru.md) · [Upgrade/rollback EN](UPGRADE_0_10_0rc2.en.md) · [RU](UPGRADE_0_10_0rc2.ru.md) · [RC2 report](RC2_010_REPORT.md).
Current source version: **0.10.0rc2**, Android versionCode **10002**. This is a separately prepared experimental candidate, not stable 0.10.0 or a publication. The original rc1 kit remains immutable.
Текущая версия исходников — 0.10.0rc2, код Android — 10002. Публикация требует отдельного решения владельца; физическое устройство не проверено.
