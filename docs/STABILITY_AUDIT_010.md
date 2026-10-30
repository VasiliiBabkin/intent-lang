# Sedrava 0.10 stability audit / Аудит стабильности

Baseline: main `69a65ada11dc8becec12c017d2668ebabd990b57`, merged PR #17.
Branch: `stabilization/010-audit`. [Draft PR #18](https://github.com/VasiliiBabkin/sedrava/pull/18).
This is an independent code/boundary audit, not a stable release announcement.
The existing rc1 kit, version metadata, application IDs and schema are unchanged.

## Findings / Дефекты

| ID | Priority | Baseline reproduction and consequence | Fix and regression |
| --- | --- | --- | --- |
| S01 | P0 | Seed malformed JSON or an incompatible schema in Web localStorage / Android snapshot preferences; launch defaults, accept an edit/action. The next save replaced the rejected original, potentially destroying recoverable user data. Legacy scalar apps could likewise overwrite rejected fields. | Preserve rejected originals; validate current storage before writes, report failures; retain legacy recovery-preview behavior without persisting over rejected input. Node regressions, real Chromium edits/actions/reload, native SharedPreferences test. |
| S02 | P1 | `rule edge >= -2147483648` or `remove(entries, -2147483648)` rejected as integer overflow, although the same minimum worked as a state initializer. Normalization omitted AST fields containing lists. | AST transformer folds signed minimum at every position before range validation. Positive overflow and negation overflow still reject. Independent .sdr fixture and Python/JS/Kotlin per-step oracle. |
| S03 | P1 | Existing Web output was opened/truncated before a failed write completed. A failed build could destroy a previously valid output; explicitly selecting the source as output also destroyed the source. | Same-directory temporary write, flush/fsync, replace and cleanup; reject output/source collision. Fault-injected replacement failures preserve target/source bytes. CLI state writes share the helper. |
| S04 | P1 | Two `input n` widgets generated identical error IDs. Invalid input in the second editor updated the first error element, breaking visible feedback and its accessibility relationship. | Keep historical first ID; suffix subsequent editor IDs and resolve each input's aria-describedby. Chromium verifies two distinct IDs and correct error visibility. |

**Found: 4 defects; fixed: 4. Known remaining open P0/P1: 0**, conditional on
successful final-SHA regression verification recorded below/with CI evidence.
No tests are disabled. No feature or public syntax was added.

## Independent coverage / Проверенные подсистемы

Reviewed parser/type rules, literal decoder, int32 evaluation and code emission,
record/list validation and identity operations, resource bounds, transaction/rule
checks, navigation session normalization, snapshots, both generator adapters,
CLI output paths, package inventory and CI/security policy. Existing tests were
read as evidence, not treated as an exhaustive specification.

New `tests/fixtures/stability_boundaries.sdr` contains a record with scalar fields,
a capacity-three collection, minimum int32, transient/persistent fields and
multi-assignment actions. A fixed prefix guarantees overflow, invariant failure,
missing identity and full-capacity rejection. Ten deterministic seeds add forty
bounded operations each: **550 Python/JavaScript compared steps**. Every outcome
compares full state and accepted/rejected status; invalid actions preserve state.
The canonical 55-step seed is also emitted as a separate Kotlin JVM test with
full-state comparison after every step, including transient fields and restoration.
Existing navigation and text/records oracles remain in place.

Boundary coverage includes empty text, maximum Unicode, overlong emoji input,
combining marks, bidi controls, NUL, HTML/script-looking text, int32 extrema,
nonexistent IDs and repeated removals/actions. Existing suites cover duplicate IDs,
corrupt/oversized/duplicate-key JSON, incompatible fingerprints, ID exhaustion,
maximum stack depth, deleted guarded selection and atomic failed navigation.
There is no open-ended fuzzing, external fuzz corpus or claim of exhaustive proof.

Compatibility tests vary defaults/actions versus field types/capacity/persist
flags. See [actual storage compatibility](COMPATIBILITY_010.md). Fault injection
covers failed replacement, not actual power cuts or process kills during kernel
writes. Native tests recreate the actual Activity after corrupting its preferences,
accept edits/actions, and verify that the original remains unchanged while the
accepted volatile session survives recreation. Separate guarded emulator checks
force-stop/cold-launch malformed and incompatible snapshots, inspect the real UI
and saved bytes, then restore the original fixture data in finally.
Native tests use real preferences and real emulator UI; no fake emulator
or in-memory model is reported as a device test.

## Verification record / Доказательства

Local checks: **159 Python tests**, **26 real Chromium scenarios**, the 550-step
Node differential corpus and the 55-step Kotlin JVM corpus all pass. APK/Lint and
instrumentation compilation pass. Independent execution against the detached
baseline reproduced all four symptoms: S01 `overwritten: true`; S02
`Line 3: column 6: Integer overflow`; S03 exit 1 with target contents `partial`;
S04 both editors referencing `error-n`. The baseline worktree was not modified. The full
CI matrix additionally runs Python 3.10/3.12/3.13, clean wheel/sdist installation,
0.9 rollback/regression, Web/Android generation, native emulator lifecycle,
signatures/permissions, two-app storage and real same-key APK updates.

The update suite retains the original main development-code-1 scenario and adds
an exact rc1-source rebuild (`6ddae99fc837d67b465285f629d9f5a2ec52e870`) with the same
job-local debug key. It seeds a task through the UI, installs the audit APK with
`adb install -r`, checks snapshot equality and cold UI rendering. This is a rebuild
of rc1 source for signing compatibility; it does not alter or pretend to install
the immutable rc1 artifact signed in another runner. Audit builds intentionally
retain versionCode 10001; equal-code reinstall is allowed. A future rc2 must use
its own increasing release versionCode and repeat the update check.

Test development exposed a mistaken new browser fixture assumption (daily_steps
has no input). It was corrected to use text_profile; the browser check was rerun.
Documentation also corrects the stale Russian Python 3.12 minimum (supported:
3.10+), branch-only feature wording and the obsolete claim that E2E verification
is still entirely outstanding. Existing ID-based regressions required keeping
the first historical error ID;
only duplicates receive a suffix. These failures were not waived. One superseded
push run (`41071221406`) reported failure while its job remained queued with no
steps or downloadable logs; no test failure could be diagnosed from that record.
It is not counted as a passing run or used as final evidence. Final-SHA checks
must pass independently.

Final SHA, actual Python counts and run URL are appended by
`scripts/write_stability_evidence.py` to the copy of this report uploaded as
`sedrava-stability-python-<version>` in the alpha workflow. This avoids an
impossible self-referential Git SHA in the tracked report. Final native/browser
counts and immutable artifact links are recorded in the final PR body and Actions.

- [All PR checks](https://github.com/VasiliiBabkin/sedrava/pull/18/checks)
- [Actions](https://github.com/VasiliiBabkin/sedrava/actions)
- Test logs/traces: alpha Python artifacts and `sedrava-browser-traces`.
- Native reports/APKs: `sedrava-navigation-apk-web-evidence` and
  `sedrava-records-task-manager-apk-web-evidence`.
- The RC-only collector is skipped for stabilization branches so no replacement
  rc1 kit is prepared; all underlying regression/build/install checks still run.

## Remaining risks / Оставшиеся риски

P2: no multi-writer conflict resolution (last valid writer wins); no automatic
migration or recovery/export UI; filesystem/power-cut behavior is not certified;
legacy scalar formats cannot identify every same-type schema change; runtime
source maps and some cross-declaration locations are incomplete; very large
valid inputs may exceed native compiler limits. Workarounds/limits are explicit
in compatibility and known-limitations documents. Debug keys are not production
signing. Two synchronous-commit Lint recommendations are deliberately retained
because write failures must be observed; zero Lint errors are required.

No physical Android device is available; 0.10 physical-device testing is **not
performed**. Local KVM is unavailable; native lifecycle execution belongs to CI's
API35 emulator, not local compilation. No new PyPI/TestPyPI availability or
publication claim is made. No language extensions or P3 enhancements are included.

## Recommendation / Рекомендация

**Prepare rc2; do not declare stable 0.10.0 from rc1.** The P0 storage risk and P1
parser/output/UI fixes warrant a new reviewed candidate and observation period.
Use [stable release gates](STABLE_RELEASE_GATES_010.md). Passing this branch's CI
can validate fixes; it cannot retroactively fix the immutable rc1 kit or establish
field stability. No merge, tag, release, package upload or deployment is performed.

Русский: найдено и исправлено четыре дефекта, включая риск уничтожения отвергнутых
сохранений. Публичный синтаксис, формат и Android ID сохранены. Подробные результаты
привязаны к SHA в CI-отчёте и PR. Открытых известных P0/P1 после успешной регрессии —
ноль; это не доказательство отсутствия всех дефектов. Для стабильного выпуска
рекомендуется сначала rc2. Физическое устройство не проверялось.
