# Executable examples / Эталонные программы

Every `.sdr` file has embedded tests. From a source checkout, substitute the file below:

```sh
sedrava check examples/countdown.sdr
sedrava test examples/countdown.sdr
sedrava run examples/countdown.sdr start tick tick
sedrava build web examples/countdown.sdr --output build/countdown/index.html
sedrava build android examples/countdown.sdr --output build/countdown-android
```

For Android APK instructions see [build guide](../docs/BUILD.md). All UI examples are generated twice and compared byte for byte in `tests/test_examples_alpha.py`; Chromium opens every UI example in `scripts/test_web_browser.py`.

| File | Purpose / Назначение | Try / Попробовать |
| --- | --- | --- |
| `counter.sdr` | Counter with nonnegative constraint / Счётчик с ограничением | Add, subtract at zero (rejected), reset |
| `countdown.sdr` | Manual countdown / Ручная модель отсчёта | Start, Tick five times, reset; no automatic clock |
| `daily_steps.sdr` | Persistent habit progress / Прогресс привычки | Add three times, reload, reset |
| `input_goal.sdr` | Validated integer input / Проверяемый ввод | Enter 5, reject 11, correct to 3, reload |
| `text_profile.sdr` | First-class text profile / Текстовое имя с сохранением | Unicode input, rejected blank input/action, reload; [guide](../docs/LANGUAGE_0_10_TEXT.md) |
| `reference_09.sdr` | Sedrava 0.9 Lab | Goal, progress, sessions, relational constraints, persistence |
| `derived_progress.sdr` | Chained derived values / Вычисляемые значения | Next three times; Reset |
| `workflow.sdr` | Sequential atomic updates / Последовательные атомарные изменения | Next three times; Reset |
| `timer.sdr` | Historical interpreter-only start/stop model | `sedrava run examples/timer.sdr start`; no screen or automatic clock |

No example uses fictitious APIs. `timer.sdr` remains for compatibility; use `countdown.sdr` for a complete manual countdown UI. Время само не течёт: действие `tick` вызывает пользователь.

## Records and collections / Записи и коллекции (unreleased 0.10)

The development branch integrates typed records and bounded ordered lists into `.sdr`,
with stable IDs, atomic actions, strict snapshots and generated Web/Compose UI.
Записи и списки доступны в языке на ветке разработки; 0.10 не выпущена.

- [English task-manager guide](../docs/RECORDS_QUICKSTART.en.md)
- [Руководство на русском](../docs/RECORDS_QUICKSTART.ru.md)
- [Measured coverage / Фактические проверки](../docs/COLLECTIONS_010_REPORT.md)

## Multi-screen navigation / Многоэкранная навигация (unreleased 0.10)

Named screens, guarded atomic transitions and a bounded Back stack are implemented
in the core and both generators. One `.sdr` file generates the two-screen task manager.
Экраны и переходы — возможность языка; опубликованного выпуска 0.10 нет.

- [English guide](../docs/NAVIGATION_QUICKSTART.en.md)
- [Русское руководство](../docs/NAVIGATION_QUICKSTART.ru.md)
- [Syntax and semantics](../docs/NAVIGATION_010_CONTRACT.md)
- [Measured report](../docs/NAVIGATION_010_REPORT.md)

## Release readiness / Подготовка к RC (unreleased 0.10)

Independent deterministic Android IDs and `--application-id` are implemented.
Независимые Android-приложения собираются с постоянным ID; название отделено от пакета.
[English identity/build guide](../docs/ANDROID_ID.en.md) · [Русская инструкция](../docs/ANDROID_ID.ru.md).
Wheel/sdist include examples, documentation and license under `sys.prefix/share/sedrava`.
Дистрибутив содержит примеры, документацию и лицензию; публикация 0.10 не выполнялась.
