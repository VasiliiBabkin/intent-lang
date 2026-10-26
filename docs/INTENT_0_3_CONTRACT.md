# Intent 0.3 design contract

The next compiler core must parse actions into a typed AST and use the same AST in both interpreter and Android generator.

## Semantics

- A transition starts from a snapshot of current state.
- Statements run sequentially against a private candidate state.
- Conditions read the candidate state, including prior assignments.
- Invariants are checked against the final candidate.
- If an invariant fails, no changes are committed.
- Tests start from independent initial states.
- Unsupported expressions must fail compilation; no Python eval/exec.

## Target syntax

```intent
app "Workflow"
state count = 0
state completed = false

action advance:
    if count < 3:
        count = count + 1
    if count == 3:
        completed = true

action reset:
    count = 0
    completed = false

rule count >= 0 and count <= 3
rule completed == (count == 3)
test finish: advance, advance, advance -> completed == true

screen main:
    text "Workflow"
    value count
    value completed
    button "Next" -> advance
    button "Reset" -> reset
```

## Release gate

Python syntax checks, AST unit tests, Android code generation, Gradle APK build, and manual device verification must pass before 0.3 is called released.
