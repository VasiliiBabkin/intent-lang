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
## Architecture decisions to specify before implementation

Keep the existing typed expression/action core; add explicit typed widget/screen nodes instead of encoding more unrelated tuples. Add source spans while extending the AST, without rewriting the working interpreter. Give each state, screen and widget a stable identifier for focus, test selectors, persistence and diagnostics.

- **Text input:** specify string state, length/Unicode rules, draft/accepted separation, validation, escaping and persistence before adding the widget. A narrow string subset in 0.10 must not silently imply the full 0.11 data model.
- **Toggle:** bind only to boolean state; apply the same atomic candidate/constraint path as numeric input.
- **Lists/cards:** begin with static declarative composition or explicitly scoped read-only data. Mutable collections need the 0.11 type/identity semantics; do not fake them with string APIs.
- **Navigation:** introduce screen identifiers and explicit transitions with back-stack and restoration semantics; distinguish navigation state from domain state and specify Web history and Android back behavior.
- **Themes/responsiveness:** shared semantic tokens and layout constraints, mapped to native Compose and CSS. No platform pixels in the language core.
- **Accessibility:** labels, roles, focus order, keyboard navigation, dynamic errors and screen-reader announcements are acceptance requirements, not decorative attributes.

Use an editor-shaped multi-screen reference (source text, validation messages, preview) to preserve the long-term prospect of a Sedrava editor implemented in Sedrava. Full self-hosting is not a 0.10 promise. Every new node needs interpreter/model semantics, Web tests, Android compile tests and device acceptance before being called implemented.
