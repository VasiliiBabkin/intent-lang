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

Local implementation checks so far:

| Check | Measured result |
| --- | --- |
| Python regression + navigation | 132 tests; final revision must pass CI |
| Python/generated JS | task CRUD and session trace; bounded-stack and rejected-rule traces agree |
| Chromium | 19 scenarios passed, including app/browser Back, Forward, focus, deletion, reload, invalid input and 375px layout |
| Android APK/JVM/Lint | initial task-manager build passed; expanded saver/instrumentation and scalar-only fixture checks running |
| Android emulator | workflow added; not yet claimed successful |
| Physical device | unavailable; NOT tested for this increment |

Final-head CI links, test counts and APK/Web artifacts are recorded in PR #15 after
all checks finish. Earlier green runs do not establish later revisions.

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
