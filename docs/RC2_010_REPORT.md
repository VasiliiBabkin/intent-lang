# Sedrava 0.10.0rc2 — engineering report / Инженерный отчёт

Work: existing branch `release/0.10.0rc2-preparation`, [PR #20](https://github.com/VasiliiBabkin/sedrava/pull/20).
Baseline main `6aa5f3f3402b402481bf4a5f262c41b099c66d07` includes PR #17,
the four stability fixes in #18, and the dedication in #19. Their executable
implementation is retained. No new syntax, language feature or schema is added.
Version source: `sedrava_version.py`, `0.10.0rc2` and Android code `10002`.

## Work and corrected blockers / Изменения

- Replace stale rc1-only test assertions with canonical version agreement and
  explicit rc2/10002 checks. Historical rc1 documentation and kit are retained.
- Isolate independent emulator update fixtures: after a previous scenario has
  installed 10002, Android correctly refuses installing baseline 10001 over it.
  Provision the old app before each seed; after seed/corruption, perform genuine
  install -r without uninstall/clear, with strict ID/key/code checks. This fixes
  the test harness without weakening Android downgrade protection.
- Extend actual rc1→rc2 testing to malformed and incompatible saved data and a
  second cold restart. Preserve original snapshots; no migration is introduced.
- Strengthen the collector: require rc1/10001→rc2/10002 evidence, same certificate,
  exact tested target APK SHA-256, cold restart and both rejection cases. A clean
  install/equal-code/wrong-key or substituted APK cannot satisfy the gate.
- Include and require the independent full-state Kotlin boundary corpus from
  the records workflow. Keep separate baseline test executions when method names
  coincide; retain raw generic JVM XML too.
- Include PR #19's DEDICATION.md in wheel/sdist, fixing the installed README's
  missing dedication target; check its presence in clean installations.
- Add separate bilingual RC2 notes and upgrade/rollback guides; update current
  version references, preserving historical rc1 materials. No source-code runtime
  defect P0/P1 is newly identified; release/packaging/verification blockers are fixed.

New negative regressions cover wrong ID/key, nonincreasing code, clean install,
missing cold restart, wrong baseline/target bytes, missing rejected-data cases,
physical-device evidence substitution, skipped/failed native XML and changed rc1
artifact metadata. Existing audit fixtures still test atomicity, int32 minimum,
overflow, Unicode, stable IDs, capacity and exact schema rejection.

## Verification and immutable delivery / Проверки

The actual final SHA, test counts, tool versions, artifact hashes and Actions URLs
are generated **after all applicable same-SHA jobs pass**, inside the RC2 kit's
`RC2_010_REPORT.md`, `manifest.json`, `manifest.md`, `checks.json` and SHA256SUMS.
The separate delivery receipt records the actual uploaded ZIP ID/digest and
post-upload download/byte verification. The tracked report cannot contain its own
Git SHA; the generated report and final PR description contain literal final SHA.
No intended/pending check is reported as a successful execution here.

Required full matrix: Python 3.10/3.12/3.13; Chromium real UI/history/keyboard/focus;
Python/JavaScript/Kotlin complete-state traces; Android JVM/APK/Lint/signature/
permissions; API35 x86_64 emulator lifecycle, valid and invalid rc1 updates, two
installed apps; clean wheel and sdist commands/examples/license/docs/dedication;
archive/source inventory; reproducible payloads; actual published 0.9.0a1 rollback.

Collector assembly uses the tested package/Web/APK bytes, not a fresh untested
rebuild. It verifies immutable source artifact digests and checks the target APK
against update evidence. It rechecks actual APK signatures/IDs/versions/permissions
using SDK tools. Actual Chromium/Playwright/Node versions, Python/Android toolchains, dependencies and pinned Actions SHAs
are recorded. SHA256SUMS includes both manifests; the outer Actions digest binds
SHA256SUMS without a circular self-hash. Local exact-inventory and remote roundtrip
checks fail on substitution. The original rc1 kit's known ID/digest/source is
checked read-only and recorded in the new manifest.

## Recorded failed intermediate checks / Промежуточный отказ

At SHA `5e85067655d1c15b3d63b0e37ed6150245da6e15`, records workflow
[41143939647](https://github.com/VasiliiBabkin/sedrava/actions/runs/41143939647)
passed both native tests and the saved-data assertion, but the cold UI scan failed.
Its retained XML showed Android's **Quickstep isn't responding** system dialog,
not the tested app; preferences still contained `restart persisted` with ID 2.
The collector correctly refused GO. The driver now records XML/PNG/JSON and may
close only that exact Android-owned launcher dialog on the disposable API35
emulator (at most twice). It brings the existing tested Activity forward, without
replaying an app action, resetting data or replacing model state. App/unknown
ANRs fail and are never dismissed. A negative regression enforces this boundary.
All required checks must pass again on the new final SHA; this failed run is not
counted as success.

## Limits, risks and decision / Ограничения и решение

Technical GO is conditional on the actual final CI manifest, not this source text.
Open P0/P1 must be zero. A failed/unavailable required check means NO-GO. Debug
APKs are not production-signed. rc1 is rebuilt from its immutable source for a
same-job test key; its original artifact/private key is not modified/reused.

Physical Android device unavailable: **not tested**. Local KVM unavailable;
real lifecycle testing runs in GitHub's API35 emulator. TestPyPI is not a target
or an availability claim. No migration, export/reset UI, encryption, multi-writer
coordination, crash/power-cut certification, transitive locks or byte-identical
APK guarantee. Schema changes can reject data; transient defaults and final rules
matter. Rejected originals are retained; accepted edits may remain volatile.
See [compatibility](COMPATIBILITY_010.md) and [limits](KNOWN_LIMITATIONS.md).

The owner's observation window has not been specified or performed. RC2 technical
readiness does **not** establish stable 0.10.0 readiness and does not authorize
publication. No merge, tag, GitHub Release, PyPI/TestPyPI upload or deployment.

[Notes EN](RELEASE_NOTES_0_10_0rc2.en.md) · [RU](RELEASE_NOTES_0_10_0rc2.ru.md) ·
[Upgrade EN](UPGRADE_0_10_0rc2.en.md) · [RU](UPGRADE_0_10_0rc2.ru.md) ·
[Stable gates](STABLE_RELEASE_GATES_010.md) · [Preparation contract](RC2_010_PREPARATION.md).

Русский: все четыре исправления аудита сохранены. Исправлены препятствия
версионирования, упаковки и доказательности выпуска. Реальные результаты берутся
из финального комплекта CI с точным SHA; успешная сборка не заменяет обновление
APK и UI-проверки. Требуется ноль открытых P0/P1. Физическое устройство не проверено;
период наблюдения и разрешение публикации остаются отдельными решениями владельца.
