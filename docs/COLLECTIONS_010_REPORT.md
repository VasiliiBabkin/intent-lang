> Historical report for the records increment. Multi-screen navigation is now implemented; see [navigation evidence](NAVIGATION_010_REPORT.md).

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
| Python suite including 0.9/text regressions | 121 tests passed |
| Python/generated JavaScript oracle | passed, including accepted/rejected CRUD and strict snapshot corpus |
| Real Chromium | 17 scenarios passed, including task CRUD, reload, capacity, corrupt storage and invalid input |
| Kotlin/JVM emitted state functions | 3 task-manager + 1 generic-record JUnit tests passed; shared oracle includes Unicode/control text, int32, strict snapshots and canonical JSON |
| Wheel/sdist metadata and module audit | passed; final clean wheel installation recorded in PR validation |
| Android APK, Gradle JVM tests, Lint | passed locally (JDK 17, SDK 35, Gradle 8.11.1), including instrumentation compilation and signature/permission audit |
| Compose emulator interaction/rotation | passed on Android 15 x86_64: CRUD, invalid input, orientation change and Activity recreation; force-stop/relaunch verification added in the follow-up |
| Physical Android device | unavailable; NOT tested for this increment |

The initial PR head `bba0695` had seven successful workflows. That evidence covers
only the original reference increment, not this integration. The first integrated tree `1a058c0` passed all eight PR workflows, including the
[Android emulator run](https://github.com/VasiliiBabkin/sedrava/actions/runs/41001733230).
Its [APK, standalone Web and test evidence](https://github.com/VasiliiBabkin/sedrava/actions/runs/41001733230/artifacts/12954166109)
are downloadable without a deployment. The PR description records final-head CI
and artifacts after follow-up generic-record and process-relaunch checks.
A green earlier tree does not establish the result for a later revision.

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

## Reproduction / Повторение

```sh
python -m unittest discover -s tests -v
python scripts/test_web_browser.py
python -m sedrava_cli build android examples/task_manager.sdr --output build/tasks-android
python scripts/prepare_records_android_tests.py build/tasks-android
python scripts/prepare_records_ui_tests.py build/tasks-android
gradle -p build/tasks-android --no-daemon :app:assembleDebug :app:testDebugUnitTest :app:lintDebug :app:assembleDebugAndroidTest
# With a running emulator / при запущенном эмуляторе:
bash scripts/test_records_emulator.sh
```

The test-preparation scripts add test sources and test dependencies; they do not
rewrite generated application Kotlin. Process relaunch checks inspect actual
SharedPreferences after force-stop and verify restored text through UIAutomator.
The additional generic fixture covers two record types, reordered constructor
fields, int32 field limits, overflow rollback and nested capacity enforcement.
Python/Web additionally test the full-state resource bound and a transaction that
exceeds it temporarily but returns to a valid final candidate. The resource limit
applies to accepted final state; declared capacities still apply to each operation.
