# Changelog

## 0.10.0.dev0 — unreleased text increment

- First-class immutable text state, derived aliases/booleans, exact equality, assignments, rules/tests and CLI JSON.
- Strict escaped literals shared by expressions and UI labels; bounded Unicode scalar values and rejection of invalid surrogates.
- Inferred validated multiline input, accepted-state persistence and atomic mixed-type actions on Web and Android.
- Pure generated Kotlin state adapters shared by Compose and JVM conformance; hostile-string fixture and text profile example.
- Expanded Python/JavaScript/browser/JVM tests, Android APK/Lint workflow and normative text guide.
- Explicit label-backslash migration and native HTML textarea line-ending boundary, both tested. No full 0.10 milestone, tag or publication.

The published 0.9.0a1 release/tag/assets remain unchanged. Older candidate notes below are historical.


## 0.9.0a1 — unreleased first Sedrava public alpha candidate

- Shared restricted typed AST for integer/boolean state, derived values, sequential atomic actions, rules and embedded tests.
- Numeric input, accepted-state persistence and conditional text on Web and Android.
- Added `sedrava run FILE [ACTION ...]` with deterministic JSON output alongside check/test/build commands.
- Fixed signed-minimum integer literals; reject oversized literals even in short-circuited expressions.
- Reject initially overflowing derives; validate all derived values after every assignment and before input/restored-state acceptance.
- Handle action overflow and invariant rejection visibly without partial state updates in generated interfaces.
- Validate restored snapshots, recover from wrong-type Android preferences and preserve accepted state across Activity recreation.
- Escape HTML script content and Kotlin dollar interpolation; namespace generated Kotlin variables to avoid collisions; support prototype-like identifiers safely on Web.
- Bound nested blocks and expanded derived expressions; reject duplicate screens, tab indentation and reserved state names; allow initial-state tests with an empty action sequence.
- Added full manual countdown example, browser regression suite, example/determinism tests, normative language reference and installation/build/troubleshooting guides.
- Source distributions now include examples, documentation and validation scripts; CI prepares downloadable candidate artifacts without PyPI publishing.

This is Sedrava's first candidate; historical Intent 0.7 and abandoned Sedrava 0.7.1 proposals are not releases of this version. No stable-language compatibility promise is made.

## Unreleased 0.10 records integration / Записи и коллекции

- `.sdr` record declarations, bounded list state, typed constructors, lookup and immutable mutations.
- Stable monotonic IDs, atomic actions and `require`, strict versioned whole-state snapshots.
- Generated selectable lists in Web and Compose; offline task manager from one source file.
- Python/JS/Kotlin oracle, Chromium CRUD and Android test harnesses; see
  [measured results](docs/COLLECTIONS_010_REPORT.md). No release or publication.

## Unreleased 0.10 navigation / Многоэкранность

- Named screens, explicit initial screen, bounded push/pop stack and bool guards.
- Atomic navigation bindings with domain actions; selected stable ID preserved;
  missing/deleted records cannot leave an invalid details screen active.
- Web Back/Forward, keyboard focus and responsive cards; native Compose Back and
  complete accepted-session recreation. Cold launch/reload start at initial.
- One two-screen task manager source, shared Python/JS/Kotlin oracles, browser and
  emulator harnesses. [Measured evidence](docs/NAVIGATION_010_REPORT.md).
- Навигация реализована в ядре и генераторах; 0.10 не выпущена.
