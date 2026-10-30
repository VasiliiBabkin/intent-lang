# Sedrava 0.10 — Collection core increment / Ядро коллекций

**Status: experimental Python reference implementation; NOT integrated into Sedrava grammar, interpreter, CLI, Web or Android. Not a release.**

Files: [reference module](../sedrava_collections.py), [seven focused regression tests](../tests/test_collections_010.py), [Python CI matrix](../.github/workflows/collections-010.yml).

## Implemented reference semantics

- Immutable typed task records: positive int32 identity, Unicode scalar text (at most 1024), boolean completion.
- Immutable ordered task collection of at most 100 records, unique stable identifiers, monotonic ID allocation with explicit exhaustion.
- Pure add, update, remove and final-invariant-gated atomic operations; rejected operations do not mutate accepted snapshots.
- JSON persistence with schema 1; strict record field names and types, capacity and identity validation; incompatible snapshots rejected as a whole.
- No implicit truncation, Unicode normalization or identifier reuse.

## Verification / Проверка

The committed seven-test reference core passed GitHub Actions on Python 3.10, 3.12 and 3.13 at commit `f27ae0a0` (workflow run `40999851723`). Since then an eighth test and strict duplicate-key / payload-size restoration checks were added. **The latest revision must pass CI again; earlier green runs do not validate subsequent commits.**

Run the exact repository tests:

```sh
python -m unittest discover -s tests -p test_collections_010.py -v
```

This is not an end-to-end Sedrava test. No parser, compiler, Web generator, Android APK, UI, device or persistence migration conformance has been tested for collections.

## Remaining integration work

1. Agree normative record/list grammar, typed AST and deterministic operation semantics.
2. Integrate records and collections into the Sedrava parser, interpreter, CLI and state type system.
3. Implement identical operations and persistence in Web and Android, then cross-target conformance.
4. Generate list/detail UI and complete the offline task-list example, including device acceptance.

**Русский:** реализовано самостоятельное экспериментальное Python-ядро записей и ограниченного списка задач. Оно ещё не является возможностью языка Sedrava: исходные файлы `.sdr` не умеют объявлять коллекции, а генераторы Web/Android не используют новый модуль. Выпуск 0.10 не состоялся.
