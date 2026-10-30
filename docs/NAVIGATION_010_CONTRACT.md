# Sedrava 0.10 multi-screen navigation — implementation contract

**Status:** proposed; no navigation syntax implemented by this document. Baseline: merged records/collections PR #14.

## Objective / Цель

A single `.sdr` source generates a task list screen and a task-detail screen for offline Web and Android. Screens share one accepted domain state; navigation has deterministic semantics and requires no author-written JavaScript, Kotlin or Android navigation controller.

## Proposed grammar (subject to parser validation)

```sdr
app "Tasks"
state selected = 0
screen main:
    text "Tasks"
    button "Details" -> open_details
screen details:
    text "Task details"
    button "Back" -> back
navigation:
    initial main
    action open_details -> details
    action back -> pop
```

**Not executable yet.** The compiler must distinguish domain actions from navigation commands and reject ambiguous names.

## Normative behavior to implement

1. Named screens are unique; `main` remains the implicit initial screen for legacy programs. Explicit initial screen is allowed only when declared.
2. Navigation stack is nonempty, bounded (suggested maximum 32), and stores screen IDs, never mutable widget instances. Opening a screen pushes it; `pop` returns to the previous screen; popping the root is a deterministic no-op.
3. Domain state is shared across screens; navigation never silently commits rejected edits. Failed domain actions do not navigate.
4. Invalid targets, duplicate screens, unreachable navigation actions and conflicting action names are compile errors with line/column.
5. Web browser Back and Android system Back must match the language stack semantics. Forward/history behavior and reload restoration must be specified explicitly before coding.
6. Rotation/Activity recreation must preserve accepted domain state and active screen. Cold launch restores persisted domain state; screen restoration behavior must be documented and tested.
7. No hidden network, permissions, generated-file edits or arbitrary host-language callbacks.
8. Screen-reader labels, keyboard focus and visible errors are acceptance criteria.

## Implementation and evidence

- Extend Program/AST and parser with explicit screen/navigation nodes and source positions; retain all 0.9 and 0.10 examples.
- Interpreter exposes a deterministic navigation transition model testable without a UI.
- Web: real browser tests for list → detail → back, invalid action, reload, browser Back and focus.
- Android: generated Compose screens, system Back, rotation/recreation, cold launch and JVM conformance; build and emulator test.
- Create `examples/task_manager_navigation.sdr` using real collection CRUD on two screens, generated unchanged for both targets.
- Test Python 3.10/3.12/3.13, Chromium and Android; compare state and navigation traces across platforms.
- Update README, roadmap, changelog and bilingual quickstarts after implementation, not before.
- Keep the PR draft until all evidence is recorded. No merge, tag, release, PyPI publish or deployment.

## Non-goals

Nested records, schema migrations, routing parameters, deep links, tabs, animation systems and multi-window UI are separate milestones.

## Acceptance / Приёмка

The reference source compiles unchanged to a usable standalone Web app and Android APK; actual Web/Android interactions and back-stack semantics match the Python oracle; existing tests pass. Unsupported checks must be reported as unavailable, never as passed.
