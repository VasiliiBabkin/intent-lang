# Stable release gates / Условия стабильного выпуска 0.10

Passing CI is necessary, not sufficient. This audit recommends **rc2**, because
rc1 contains reproduced storage and int32 defects. No stable version is announced.

1. **Zero open P0/P1** from this audit and subsequent candidate use. Each closed
   defect needs a failing baseline reproduction and a passing regression. P0:
   data loss/security/serious semantic divergence; P1: supported reproducible
   incorrect behavior; P2: noncritical with a documented workaround; P3: optional
   enhancement outside this stabilization scope.
2. Full Python suite passes on **3.10, 3.12, 3.13**, with zero skipped required
   platform checks. Preserve 0.9 reference and all existing 0.10 tests.
3. All bounded differential corpus steps agree in Python, emitted JavaScript and
   emitted Kotlin: accepted/rejected flag and complete domain state after each
   step, including int32 minimum, overflow, missing identity, capacity, rollback,
   exact Unicode and save/restore. Existing navigation traces must also match.
4. Real Chromium scenarios pass with no unhandled page errors. Include CRUD,
   browser Back/Forward, reload, keyboard/focus, long text, invalid drafts,
   corruption/schema rejection without overwrite and duplicate editor feedback.
5. Kotlin JVM, untouched generated APKs, Android Lint (zero errors), debug signature
   and permission audits pass on the **same final SHA**. Native API 35 emulator
   covers Back, rotation, Activity recreation, cold launch, two simultaneous apps
   with independent storage, and same-key updates from development and rc1 source.
   Test rejection preservation using actual Android SharedPreferences. Archive XML,
   screenshots, test XML and signature/package reports. A build is not a UI test.
6. Clean wheel **and** sdist installation outside the checkout passes documented
   commands and all four representative examples. Check metadata, licenses,
   packaged docs/examples/templates, archive safety, deterministic payloads and
   rollback using the actual verified historical 0.9.0a1 wheel.
7. [Compatibility](COMPATIBILITY_010.md) is accepted as the actual storage/update
   contract. Release notes explicitly warn about exact fingerprint rejection,
   quarantined original data, volatile changes on write failure, no migrations,
   single-writer limitations and Android identity/signature requirements.
8. Prepare a **new separately versioned rc2** after owner decision; do not mutate
   rc1. Its immutable manifest must bind SHA, toolchains, artifact hashes and all
   test evidence. Test the upgrade from rc1 again with the real candidate's ID,
   key and increasing versionCode. Allow a documented owner-defined observation
   period for rc2; do not invent evidence of field stability.
9. Physical 0.10 device verification is currently unavailable. Before stable
   Android support, either obtain a recorded device model/OS/scenario result or
   explicitly narrow the support claim to the tested emulator configuration and
   accept that limitation in the owner's stable-release decision. Do not reuse
   historical 0.9 physical-device evidence as 0.10 evidence.
10. All applicable final-SHA workflows successful, no hidden cancelled/failed
    required job; working tree clean. Explicit owner authorization remains
    necessary for merge/tag/release/index upload/deployment. Technical GO does
    not grant publication authorization.

Русский: стабильный выпуск требует отсутствия открытых P0/P1, согласованной
семантики на трёх реализациях и полного CI на одном SHA. После исправлений нужен
новый rc2 с неизменяемыми артефактами и повторной проверкой обновления, затем период
наблюдения по решению владельца. Физическое устройство не проверено. Никакая
успешная проверка сама по себе не разрешает публикацию.
