# Sedrava 0.10 — Records and bounded collections (design contract)

**Status: design proposal, NOT IMPLEMENTED.** The published compatibility baseline is 0.9.0a1. The text core is an unreleased 0.10 development increment. None of the illustrative syntax below is accepted by the compiler yet.

## Why this is the next increment

The [Describe → Get 0.10 target](DESCRIBE_GET_010.md) requires an offline task list. First-class text alone cannot represent multiple independently editable tasks. Records and bounded ordered collections must preserve the existing atomic state/rule model on Python, Web and Android before introducing list UI or navigation.

## Proposed data model (not valid Sedrava syntax)

```text
record Task:
    id: int
    title: text
    done: bool
state tasks: list<Task>(max=100) = []
persist tasks
```

The spelling, type grammar, and whether identifiers use integers or an opaque identity type remain open decisions. Do not implement this pseudocode as a platform-specific shortcut.

## Required semantic decisions and acceptance gates

1. **Records:** fixed, named, statically typed fields; exact field order and initialization rules; no implicit conversions. Record values are immutable snapshots. Define structural equality or explicitly disallow it in the first increment.
2. **Collections:** finite ordered sequences of one declared element type; explicit capacity; deterministic insertion/removal order; capacity checked before acceptance; no implicit truncation or unbounded allocations. Specify whether equality is supported before parsing it.
3. **Identity:** task identity must not depend on list index. Define stable IDs, uniqueness, lookup of missing IDs, and behavior after removal and restoration. No silent update of the wrong task after a deletion.
4. **Actions:** add, replace/update, remove and lookup must use typed operations with atomic rollback. Invalid indices, missing IDs, duplicate IDs, over-capacity inserts, invalid fields and rule violations must leave all accepted state unchanged.
5. **Persistence:** explicit schema version, strict decoding, per-field type/length validation and collection capacity validation. Malformed or incompatible snapshots must not partially restore state. State migration must be specified or restoration must safely fall back to defaults.
6. **Cross-target determinism:** preserve exact Unicode scalar semantics, int32 overflow checks, ordered iteration and JSON serialization across Python, JS and Kotlin. Validate equality and ordering only where specified.
7. **Resource bounds:** define limits for number of fields, record nesting, list size and serialized payload. Reject pathological declarations before generation.
8. **Backward compatibility:** all 0.9 and current text fixtures must still check/test/build; changes to legacy grammar need explicit diagnostics and migration notes.

## Proposed implementation order

- **A — Specification and negative fixtures:** settle grammar, identity, equality, bounds and persistence with explicit examples of accepted/rejected programs.
- **B — Typed core:** parser/AST/type checker/interpreter, typed atomic operations, state serialization and tests.
- **C — Web/Android parity:** generators, restoration, deterministic conformance, hostile input and clean builds.
- **D — Product UI:** list rendering, task detail, navigation and accessibility; only then call the reference task manager functional.

## Release and evidence rules

Do not publish 0.10, tag a release, or claim task-list support based on this document. Each implementation increment needs a test report naming Python/browser/JVM/device coverage separately. An Android APK build does not prove Compose interaction or rotation behavior. Documentation in both languages must distinguish design, implementation and release status.

## Design review questions

- Prefer a bounded `list<Task>` with explicit unique `id` versus a map keyed by ID?
- Should field updates be expressed as pure record replacement, or as an atomic typed operation on a selected ID?
- What is the minimum migration policy that avoids silently discarding user data when schemas evolve?

Until answered, these are intentionally **open questions**, not promises.
