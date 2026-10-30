# Records integration report / Отчёт о записях и коллекциях

Development branch `feature/010-records-collections-spec`, PR #14. **Unreleased,
experimental 0.10; 0.9 compatibility baseline is preserved.**

## Implementation / Реализация

- Record declarations and bounded typed collection state are accepted directly in
  `.sdr`. Constructors, scalar field access, count, ID allocation/lookup, immutable
  append/update/remove and action requirements use the shared typed AST.
- Atomic candidate transitions, deterministic insertion order and stable monotonic
  IDs; explicit overflow/capacity/Unicode/resource rejection.
- Strict schema-1 snapshots, declaration fingerprint, duplicate-key rejection and
  whole-snapshot validation. CLI `run --state-file` atomically replaces a snapshot
  only after successful execution; corrupt files are preserved and reported.
- Web and Compose generate list selection, scalar inputs and action buttons from
  [one source](../examples/task_manager.sdr). CRUD and offline storage require no
  handwritten target code. Full accepted state is encoded for Android recreation;
  only persistent declarations survive relaunch.
- `sedrava_records.py` is an internal generic component; the original
  `sedrava_collections.py` compatibility API delegates mutations to it while
  retaining its legacy snapshot format and stricter task-title policy.

## Measured evidence / Фактические проверки

Local development evidence (2026-10-30):

| Check | Result |
| --- | --- |
| Python suite including 0.9/text regressions | 118 tests passed |
| Python/generated JavaScript oracle | passed, including accepted/rejected CRUD and strict snapshot corpus |
| Real Chromium | 17 scenarios passed, including task CRUD, reload, capacity, corrupt storage and invalid input |
| Kotlin/JVM emitted state functions | 3 JUnit tests passed with Kotlin 2.0.21; expanded snapshot corpus awaits rerun |
| Wheel/sdist metadata and module audit | passed; clean install to be repeated after final changes |
| Android APK, Gradle JVM tests, Lint | running; not yet claimed successful |
| Compose emulator interaction/rotation | workflow added; not yet verified |
| Physical Android device | unavailable; NOT tested for this increment |

The initial PR head `bba0695` had seven successful workflows. That evidence covers
only the original reference increment, not this integration. Final-head CI links
and artifacts will be recorded after the implementation checks complete.

## Limits / Ограничения

No nested records/lists, record/list equality, indexing, migrations, list sorting,
multi-screen navigation, custom list layouts or per-app Android package identity.
Records are constructed values used as collection elements and derives; standalone
record state declarations are not part of this increment. Lists have at most 100
items and records at most 16 scalar fields. Full state is bounded to a 200000
UTF-16-code-unit envelope. Text has 1024 Unicode scalars; no normalization/trimming.
Local storage is unencrypted. Invalid drafts need not survive Android recreation.
No physical-device or accessibility certification is implied by JVM/APK checks.

Русский: коллекции интегрированы в язык и генераторы; это экспериментальная
разработка, а не выпуск 0.10. Таблица выше разделяет проверки Python, настоящего
браузера, JVM, APK, эмулятора и устройства. Отсутствующая проверка не считается
успешной. Публикация и слияние PR не выполняются.

Guides: [English](RECORDS_QUICKSTART.en.md), [Русский](RECORDS_QUICKSTART.ru.md).
