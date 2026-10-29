# Sedrava 0.10 UI implementation plan / План интерфейсов 0.10

**Status:** design and engineering backlog, not implemented or released.

## Goal

Build a multi-screen reference application with matching language semantics on Android/Compose and Web. Keep English keywords and bilingual documentation.

## Proposed minimal syntax (subject to parser design review)

```sdr
app "Notes"
state selected = 0
screen home:
    text "My notes"
    button "Settings" -> open_settings
screen settings:
    text "Settings"
    button "Back" -> open_home
```

The example above is illustrative, **not executable syntax yet**. Navigation action and screen state representation must be specified before implementation.

## Engineering sequence

1. Specify navigation semantics, initial screen, screen identifiers and action transitions; reject missing/duplicate screens.
2. Extend typed AST and parser without changing 0.9 program meaning; add parser and interpreter tests.
3. Generate Android navigation using Compose state and proper back behavior; generate Web navigation with equivalent state transitions.
4. Add text fields, toggles, lists and cards incrementally with validation and accessibility labels.
5. Specify responsive layout and themes with safe defaults; preserve platform-native widgets.
6. Build a real two-screen reference app and an automated Android APK workflow; compare behavior on Web and Android.
7. Complete device accessibility smoke checks, documentation and release gates.

## Acceptance criteria

- A two-screen reference app runs on Android and Web.
- Navigation is deterministic; invalid target screens fail with useful diagnostics.
- State and persistence are consistent across screens.
- Text fields and toggles have explicit semantics and error handling.
- Keyboard, focus, screen reader labels and back navigation have documented behavior.
- CI passes parser/interpreter, Web conformance and Android compile tests; device check recorded.

## Scope exclusions

- Collections/records and structured local data belong to 0.11.
- Files, notifications, camera and permissions belong to 0.12.
- Modules, reusable components and IDE features are later milestones.

Reference: [roadmap](ROADMAP.md).