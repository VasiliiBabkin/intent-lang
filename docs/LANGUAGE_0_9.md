# Sedrava 0.9 language reference / Справочник языка

> Published 0.9 compatibility baseline. Development text extensions are specified separately in [unreleased 0.10 text reference](LANGUAGE_0_10_TEXT.md); the 0.9 release/tag is unchanged.

Normative for this candidate. Syntax is English. Historical `sedrava.py` and `android_codegen.py` entry points implement earlier subsets and are compatibility tools; use **`sedrava` CLI**, `sedrava_core`, `web_codegen`, and `android_codegen_v03` for 0.9.

## Source and declarations

UTF-8, at most 100,000 characters. Blank lines and whole-line `#` comments are ignored; inline comments are not part of the grammar. Indentation uses spaces; tabs in indentation are rejected. Top-level declarations have zero indentation. A block uses one consistent deeper indentation level; four spaces are recommended. At most 32 nested conditional blocks (plus the outer action block).

Identifiers: `[A-Za-z_][A-Za-z_0-9]*`, case-sensitive. Python keywords and `true`/`false` cannot name a state or derive. Backend names are implementation details, not application identifiers. No Unicode identifiers, string state, implicit conversion or arbitrary Python execution.

```sedrava
app "My application"
state goal = 5
state count = 0
persist goal
persist count
derive reached = count >= goal
action add:
    if count < goal:
        count = count + 1
    else:
        count = count
rule goal >= 1 and goal <= 20
rule count >= 0 and count <= goal
test initial: -> count == 0
test once: add -> count == 1
screen main:
    text "Progress"
    input goal
    value count
    value reached
    show reached : text "Done"
    button "Add" -> add
```

Exactly one nonempty `app "name"` is required. It can appear anywhere at top level; placing it first is recommended. `state name = expression` initializers are closed expressions (no state references). Type is inferred as integer or boolean. State and derive declarations must precede actions, rules, tests and screens. State/derive names share a namespace and cannot be redeclared. Derives may refer only to previously declared state/derives; no cycles or forward references. `persist name` marks a previously declared state exactly once. Actions have a separate namespace, unique names and nonempty bodies; inline `action reset: count = 0` is supported. A single optional `screen main:` is supported; a nonempty screen is required to build UI targets. A screenless program can be checked, tested and interpreted.

## Expressions and types

| Form | Meaning |
| --- | --- |
| `0`, `-1`, `2147483647`, `-2147483648` | Signed 32-bit integers |
| `true`, `false` | Booleans |
| `name`, `(expression)` | Read a declared value; grouping |
| `-n`, `a + b`, `a - b`, `a * b` | Checked integer operations |
| `not b`, `a and b`, `a or b` | Boolean operations; `and`/`or` short-circuit |
| `a == b`, `a != b` | Equal types only |
| `a < b`, `a <= b`, `a > b`, `a >= b` | Integers only; one comparison at a time |

Precedence follows Python: parentheses, unary minus, multiplication, addition/subtraction, comparisons, `not`, `and`, `or`. Use parentheses rather than chained comparisons: `n >= 0 and n <= 10`. The AST is restricted and type-checked; calls, attributes, indexing, comprehensions, imports, floats, exponentiation, division and remainder are rejected. Division by zero is therefore a syntax/type error, never an available runtime operation. Python-compatible integer literal spelling (including hexadecimal and separators) is accepted. `True`/`False` are accepted compatibility spellings; prefer `true`/`false`.

Every literal and arithmetic intermediate must fit `[-2147483648, 2147483647]`. Unary minimum literal is supported; negating a minimum-valued variable overflows. No wrapping or float promotion. Each expression is limited to 256 AST nodes. Expanded derived expressions are limited to 4096 nodes to bound generator inlining.

## State, actions and invariants

Actions contain state assignments and `if`/`else` only. Conditions must be boolean; assignment must preserve the state's exact type. Assigning to a derive is forbidden. No loops, recursion, action calls or asynchronous events. Each action is limited to 10,000 syntactic statements (including both branches); the interpreter also limits visited statements to 10,000.

An action starts with a candidate copy. Assignments execute sequentially, reading the current candidate. Derived values are pure and recomputed from candidate values; all derives must be evaluable initially and after each assignment. Arithmetic failure aborts the whole action. Rules are boolean invariants checked against the **final** candidate, so temporary rule violations within an action are allowed. If any final rule is false, the entire candidate is rejected. Accepted state changes atomically. Python `transition` returns `(state, accepted)` for rule rejection and raises `ValueError` for arithmetic failure without mutating its input. Generated UIs preserve accepted state and display an error. The interpreter CLI exits nonzero on either rejection.

Embedded `test name: action, action -> predicate` starts from defaults independently for each test. An empty sequence tests defaults. Rejected actions, arithmetic errors or false predicates fail the test; there is no expected-rejection test syntax. Host-language tests cover rejection. Build commands also run embedded tests before writing their target application.

## UI and numeric input

`text "literal"`, `value name`, `button "label" -> action`, `input integerState`, `show booleanName : text "literal"`. No escaping syntax in source strings: strings end at the next double quote and cannot span lines. `$`, backslashes, HTML text and non-ASCII text are literal content; generators escape them for their targets. No string interpolation. Widgets form a single vertical layout; Android scrolls; Web uses normal document flow. `value` can display state or derive. `show` takes a boolean name, not an arbitrary expression.

Input is a draft until accepted: trimmed ASCII `-?[0-9]+`, signed 32-bit range, all derives evaluable and all rules true. A valid edit commits immediately. Invalid text never changes accepted state and shows an error. Empty drafts preserve accepted state; Web restores the accepted value on blur. Native numeric keyboards and HTML number inputs filter some characters differently. Android drafts are transient and can reset on recreation; accepted state survives Activity recreation. No promise to persist rejected drafts.

## Persistence and platform differences

`persist` stores only accepted declared fields: Web `localStorage`, Android private `SharedPreferences`. Missing, malformed, wrong-type or out-of-range saved fields use defaults; if the resulting snapshot violates rules or overflows derives, the entire snapshot uses defaults. Persistent storage is optional on Web (blocked/quota errors are caught); Android uses asynchronous `apply`, so abrupt process/device failure can lose the last write. No encryption, migration API, transactional durability guarantee, cloud sync or secure-secret storage. The interpreter `run` starts from defaults each invocation and never reads UI storage.

Web storage key includes URL pathname and app name; moving/renaming the app starts a separate snapshot. Serve over HTTP for repeatable browser persistence. All generated Android projects currently share application ID `org.sedrava.generated` and preferences name `sedrava_state`; installing another generated example replaces the previous app and may reuse compatible saved fields. Uninstall/clear app data before comparing examples. Production package identity and migrations are future work.

## Diagnostics / Диагностика

CLI errors include source path and available line/column. Unknown identifiers and expression starts have useful columns; some structural errors use column 1. Runtime overflow and cross-declaration errors can lack a precise location. Exit status: 0 success, 1 source/runtime/I/O/test failure, 2 invalid CLI arguments. No traceback for ordinary invalid programs. `--help` explains commands. Position precision is an alpha limitation, not a full source-map implementation.

Русское резюме: состояния имеют тип `int32` или `bool`; `derive` не хранится и не присваивается. Действие выполняет последовательные изменения копии; арифметическая ошибка или нарушение итогового `rule` отменяет всё действие. Все вычисляемые значения должны оставаться вычислимыми после каждого присваивания. Ввод проверяется до принятия. `persist` хранит только принятое состояние в интерфейсе, а CLI каждый раз начинает с исходных значений. Автоматических таймеров, строковых полей и нескольких экранов в 0.9 нет.
