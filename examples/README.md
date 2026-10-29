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
| `reference_09.sdr` | Sedrava 0.9 Lab | Goal, progress, sessions, relational constraints, persistence |
| `derived_progress.sdr` | Chained derived values / Вычисляемые значения | Next three times; Reset |
| `workflow.sdr` | Sequential atomic updates / Последовательные атомарные изменения | Next three times; Reset |
| `timer.sdr` | Historical interpreter-only start/stop model | `sedrava run examples/timer.sdr start`; no screen or automatic clock |

No example uses fictitious APIs. `timer.sdr` remains for compatibility; use `countdown.sdr` for a complete manual countdown UI. Время само не течёт: действие `tick` вызывает пользователь.
