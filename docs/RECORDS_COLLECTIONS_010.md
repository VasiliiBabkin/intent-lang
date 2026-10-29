# Sedrava 0.10 — records and collections contract (proposal)

Status: design only. This document does not claim implementation. Baseline: merged text support, published 0.9 backward compatibility. Parent: [Describe → Get](DESCRIBE_GET_010.md).

## Product test

One concise source describes a task list with a title and completion flag, adding, completing and deleting tasks, plus local persistence. Standard CLI generates working Web and Android applications with no manual edits to generated code. Do not confuse this with a static list of widgets.

## Data model

- Named record types with typed fields (`text`, `bool`, `int32`) and immutable record values. No implicit coercions.
- Bounded ordered collections of homogeneous records; default safe maximum 100 entries, explicitly configurable within a documented global cap.
- Stable per-record identity distinct from list position; generated IDs must not collide after restoration or deletion/re-addition. No reliance on platform-specific clocks or randomness unless specified.
- Atomic operations: create record, update a record by identity, delete by identity, toggle boolean field, select by identity. Rejected operations leave the entire state unchanged.
- `persist` supports structured state with schema version, corruption recovery and a documented compatibility/migration policy. No silent loss of valid data.
- Rules and derived values are pure; complexity, nesting, collection size and expression evaluation have bounded costs.
- Deterministic JSON serialization for CLI and compatible Web/Android state semantics.

## Syntax design constraints

First define a small grammar that lets the author declare *intent*, not imperative list manipulation. Proposed **illustrative pseudocode, NOT supported Sedrava syntax**:

```text
app "Tasks"
record Task:
    title: text(120)
    done: bool = false
collection tasks of Task limit 100
persist tasks
operations:
    add Task to tasks with title
    toggle tasks.done by id
    remove from tasks by id
screen tasks:
    list tasks showing title, done
    add form title
    open item -> detail
screen detail:
    show selected task
    toggle done
    remove
```

Avoid exposing raw indexes, hand-written JavaScript/Kotlin callbacks, SQL, serialization glue or manual UI synchronization. Keep old 0.9 and new text syntax valid.

## Required tests

- Parser/type checker: invalid field names, duplicate declarations, wrong types, invalid operations and limits.
- Interpreter: identity stability, insertion order, add/update/delete, empty collection, max capacity, invalid identity, atomic multi-field failure and deterministic JSON.
- Persistence: reload, corruption, wrong schema, invalid nested values, duplicate IDs, capacity overflow and migration behavior.
- Web: differential trace against Python, real Chromium interactions, reload, keyboard operation, HTML escaping and accessibility.
- Android: generation, Gradle compilation, Lint, JVM conformance, APK verification and actual UI/rotation tests if an emulator/device is available.
- Compatibility: all 0.9 reference examples, text-profile example and CLI continue to pass.

## Definition of done

The task-list example builds and works in both Web and Android from the same source; collection behavior is tested against the interpreter; no generated code is edited. Evidence and limitations are documented. This milestone is **not** permission to tag/release 0.10 or publish to PyPI.

## Delivery sequence

1. Agree and implement record/collection AST and pure semantics.
2. Implement typed operations and persistence, including recovery.
3. Generate list UI for Web and Android.
4. Add navigation and detail screen in a subsequent increment if necessary; keep each increment honest about what's implemented.
