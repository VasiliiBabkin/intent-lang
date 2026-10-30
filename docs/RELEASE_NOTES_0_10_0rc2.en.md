# Sedrava 0.10.0rc2 — experimental candidate, not published

**Describe the application; get the application.** Sedrava describes typed state,
actions, invariants, executable tests and screens in one `.sdr` source, interpreted
in Python or generated as an offline Web / native Kotlin–Jetpack Compose app.
This candidate adds no language features and makes no stable-production claim.

Compared with published GitHub 0.9.0a1, 0.10 implements text (1024 Unicode scalars),
named typed records, ordered bounded collections (stable IDs, capacity 1–100),
atomic actions with invariant rollback, strict collection/navigation snapshots,
and guarded multi-screen navigation with a bounded 32-entry stack. Web includes
browser history, keyboard/focus handling and reload persistence. Android includes
system Back, accepted session recreation and independent application identities.
No implicit conversion, string normalization or silent truncation is provided.

Compared with rc1, rc2 includes the [stability audit](STABILITY_AUDIT_010.md) fixes:
rejected storage cannot be overwritten by recovery edits; int32 minimum works in
all expression positions; CLI Web output replacement is atomic; repeated scalar
editors have separate accessible error targets. CLI/package/Android versionName
is `0.10.0rc2`; Android versionCode is **10002** (rc1: **10001**). Existing app IDs
and storage encoding/fingerprints are unchanged. rc1 files remain immutable.

Install the verified **local** wheel in a separate environment:

```sh
python -m venv .venv-sedrava-rc2
. .venv-sedrava-rc2/bin/activate
python -m pip install --no-index /absolute/path/to/verified-kit/sedrava-0.10.0rc2-py3-none-any.whl
sedrava --version
# sedrava 0.10.0rc2
```

Windows activation: `.venv-sedrava-rc2\Scripts\Activate.ps1` in PowerShell.
Find bundled examples at `sys.prefix/share/sedrava/examples`; from a source checkout:

```sh
sedrava check examples/task_manager_navigation.sdr
sedrava test examples/task_manager_navigation.sdr
sedrava run examples/reference_09.sdr add
sedrava build web examples/task_manager_navigation.sdr --output build/web/index.html
python -m http.server 8000 --directory build/web
sedrava build android examples/task_manager_navigation.sdr --output build/android
```

Open http://localhost:8000; Android requires the documented JDK17, Gradle8.11.1,
SDK35 toolchain and `gradle -p build/android :app:assembleDebug`. Python >=3.10;
the verification matrix is 3.10/3.12/3.13. Tests cover Chromium and Android API35
x86_64 emulator. **No 0.10 physical-device validation** is claimed. Debug APKs are
cryptographically signed with development keys, not production-signed releases.

Back up projects and saved state before changing builds. No schema migration,
downgrade or automatic export/reset is implemented. Strict snapshots require the
exact fingerprint; transient defaults and new rules can reject previously saved
values. Rejected originals remain protected; new accepted edits can be temporary
when storage is rejected/unavailable. Legacy scalar restoration differs from the
strict envelope. Same-title Android IDs coincide; Web origin/path/title selects
storage. Concurrent writers are last-writer-wins; no sync or encryption.

No nested records, modules, loops, background services, route parameters/deep
links, general layout/theme API, full accessibility certification, Gradle wrapper,
production signing, transitive lockfiles or bit-identical APK guarantee. Read
[compatibility](COMPATIBILITY_010.md), [limits](KNOWN_LIMITATIONS.md),
[upgrade/rollback](UPGRADE_0_10_0rc2.en.md), [build](BUILD.md).

Actual successful tests, final SHA, toolchains and file hashes are recorded in the
CI-created RC2 manifest/report, not inferred from these notes. Technical RC GO
requires all final-SHA gates. Stable 0.10.0 additionally requires the owner's
observation period and [stable gates](STABLE_RELEASE_GATES_010.md). Publication,
merge, tag and deployment require separate owner authorization.

[Русский](RELEASE_NOTES_0_10_0rc2.ru.md) · [RC2 report](RC2_010_REPORT.md).
