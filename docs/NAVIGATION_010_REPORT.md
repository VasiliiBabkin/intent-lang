> Historical increment evidence below. Current 0.10 Android builds use [independent application IDs](ANDROID_ID.en.md); [readiness report](RELEASE_READINESS_010_REPORT.md) supersedes the old shared-package limitation.

# Navigation engineering report / Отчёт о навигации

Branch `feature/010-multiscreen-navigation`, PR #15. Experimental, unreleased 0.10.
The baseline is merged records/collections PR #14, not a parallel implementation.

## Implementation / Реализация

Named screen/widget/navigation AST nodes retain line/column spans. The Python core
owns the nonempty stack, guarded entry, push/pop, data/selection transactions,
normalization after deletion and navigation restoration. JavaScript and Kotlin
reuse their existing emitted domain adapters and port the bounded session model.

`examples/task_manager_navigation.sdr` generates a two-screen offline task manager
with separate new-task/editor states, stable IDs, Save, completion, deletion and
Back. Responsive Web cards and native Compose surfaces use declared title/status
roles, labels and focus. No application code is edited by test harnesses.

Contract resolution: PR #15 originally did not specify how domain actions compose
with transitions or how missing records protect details. Optional `using` and bool
screen guards resolve this in the language core. Navigation and domain persistence
are deliberately separate: reload/cold start use initial screen; Android recreation
saves the entire accepted session. Browser history does not restore old task data.

## Evidence / Проверки

Before edits: `main` at `cab7c97`, PR head `0a7e880`; all seven existing PR workflows
were green. The original 121 Python tests passed unchanged.

Measured checks for implementation tree `f54b65376e7b507c1471389e36907b45410d7cef` (2026-10-30):

| Check | Measured result |
| --- | --- |
| Python regression + navigation | 133 tests passed on Python 3.10, 3.12 and 3.13 |
| Python/generated JS | 26-step task/session trace and 67-step stack traces agree, including accepted/rejected outcomes and domain data |
| Chromium | 21 scenarios passed, including app/browser Back, Forward, focus, deletion, reload, invalid input and 375px layout |
| Android APK/JVM/Lint | 3 APK builds passed; 4 navigation JVM tests passed (2 task manager + 1 empty-domain + 1 scalar/text), plus Lint, instrumentation compilation and signature/permission audit |
| Android emulator | passed on Android 15 x86_64: system Back, unsaved accepted editing through rotation/recreation, deletion by ID and cold-start/preferences checks |
| Physical device | unavailable; NOT tested for this increment |

The implementation tree passed all 8 PR workflows, including unchanged 0.9,
text and records regressions. The report-only commit that follows changes no
runtime code; its final HEAD and CI are recorded in PR #15.

- [Navigation APK/JVM/Lint/emulator CI](https://github.com/VasiliiBabkin/sedrava/actions/runs/41031998829)
- [Python matrix, Chromium and package verification](https://github.com/VasiliiBabkin/sedrava/actions/runs/41031998879)
- [APK, standalone Web, JVM/Lint/device reports, actual preferences and cold-launch screenshot](https://github.com/VasiliiBabkin/sedrava/actions/runs/41031998829/artifacts/12965564038)
- [Browser traces](https://github.com/VasiliiBabkin/sedrava/actions/runs/41031998879/artifacts/12966835719)

The emulator force-stops the process, inspects real SharedPreferences (surviving
record ID 2, next_id 3, title Second, done true), starts a new process and verifies
the initial screen via UIAutomator. No physical-device results are claimed.
The wheel/sdist pass Twine and module audits; a clean venv outside the checkout
runs check/test/navigation run and both build commands using installed modules.

## Limits / Ограничения

32 named screens, 64 navigation bindings, 32 stack frames including root, screen
and navigation identifiers up to 64 ASCII characters. Initial screen is unguarded;
all screens must be statically reachable and navigation bindings used by controls.
No route parameters, deep links, tabs, per-screen domain state, schema migrations,
custom themes, general layout/component system or full accessibility certification.
Android examples still share an application ID; local storage is unencrypted.
Drafts may be discarded; full accepted data and stack survive valid recreation.
Physical-device behavior is not established by an emulator or APK build.

Русский: семантика переходов реализована в ядре, а не только в генераторах.
Недоступная запись не открывается; её удаление убирает недопустимый экран со стека.
Проверки браузера, JVM, эмулятора и устройства разделены выше. Сборка APK сама по
себе не является проверкой интерфейса. Слияние, релиз, публикация и развёртывание
не выполняются.

Guides: [English](NAVIGATION_QUICKSTART.en.md), [Русский](NAVIGATION_QUICKSTART.ru.md).


Follow-up browser hardening covers repeated-screen focus, numeric drafts including
`-0` → `-01`, native editor DOM continuity, reactive conditional text and safe
view-expression overflow. Active editors are retained during accepted input;
transitions restore heading focus and ordinary actions retain button focus.
The reference layout was visually inspected at desktop and mobile sizes; this is
not a claim of WCAG certification or physical-device acceptance.
