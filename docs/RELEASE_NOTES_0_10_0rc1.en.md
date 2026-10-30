# Sedrava 0.10.0rc1 — experimental release candidate (prepared, not published)

**Describe the application; get the application.** Sedrava is a declarative language for small offline applications: describe typed state, rules, actions, tests and screens in one `.sdr` file; generate standalone Web or a native Kotlin/Jetpack Compose Android project. This RC is intended for controlled experiments and feedback, not production or a stability commitment. No 0.10 tag, release or index upload has been made by preparation.

## What changes from 0.9

0.9's checked int32 arithmetic, booleans, invariants, actions, input and persistence remain supported. 0.10 adds bounded Unicode text, typed records, bounded ordered collections with stable IDs, atomic append/update/remove, strict schema-checked collection snapshots, and guarded multi-screen navigation with a bounded Back stack. Web has browser Back/Forward, focus and keyboard handling; Android has native Back and accepted-state restoration through rotation/Activity recreation. Cold launch/reload starts the declared initial screen and restores persistent domain fields.

Different application titles now produce independent deterministic Android identities. `--application-id com.example.daybook` fixes identity across title changes or separates same-title apps. RC `versionName` is `0.10.0rc1`, development `versionCode` is **10001** (previous builds used 1); neither changes application ID. Launcher names are escaped string resources. These are debug APKs, not production-signed application releases.

## Install the checked candidate

Actual package name: **sedrava**. The published 0.9 baseline is on GitHub Releases, not PyPI; historical `intent-lng` is not a Sedrava replacement. Obtain the kit from the successful **Prepare experimental RC kit (no publication)** Actions run for the reviewed SHA, not a moving branch/latest artifact. [Verification and publication procedure](RC_PUBLISHING.md) describes immutable artifact ID/digest verification. Inspect `manifest.json`, `manifest.md`, `availability.json`, `SHA256SUMS` and the separate delivery identity. No invented download links are required: CI creates actual links after upload.

```sh
python -m venv .venv-sedrava-rc1
# POSIX; Windows: .venv-sedrava-rc1\Scripts\activate
. .venv-sedrava-rc1/bin/activate
python -m pip install --no-index /absolute/path/to/verified-kit/sedrava-0.10.0rc1-py3-none-any.whl
sedrava --version
# Expected: sedrava 0.10.0rc1
```

Use a trusted checkout's `python scripts/verify_rc_bundle.py /path/to/verified-kit` and independently compare the immutable Actions artifact digest before installation. The CLI has no runtime dependencies. Installed examples/docs/license are under `sys.prefix/share/sedrava`. To install the sdist, use its verified local path with `pip`; isolated build downloads the exact backend versions in `pyproject.toml`. For an offline build, preinstall those backend wheels from a separately checked wheelhouse and use `--no-build-isolation`. Do **not** use `pip install sedrava==0.10.0rc1` now: the RC is not published. A later authorized index publication must be checked independently.

## First application

```sdr
app "First RC app"
state name = "Guest"
state visits = 0
persist name
action welcome: visits = visits + 1
test once: welcome -> visits == 1
screen main:
    text "Welcome"
    input name
    value visits
    button "Visit" -> welcome
```

Save as `hello.sdr` (UTF-8), then:

```sh
sedrava check hello.sdr
sedrava test hello.sdr
sedrava run hello.sdr welcome
sedrava build web hello.sdr --output build/web/index.html
sedrava build android hello.sdr --output build/android --application-id com.example.firstapp
gradle -p build/android --no-daemon :app:assembleDebug :app:lintDebug
```

For installed examples, obtain their directory with `python -c "import sys; from pathlib import Path; print(Path(sys.prefix)/'share/sedrava/examples')"`. Try `text_profile.sdr`, `task_manager.sdr` and `task_manager_navigation.sdr`. The two task managers generate unchanged from one `.sdr` each; the kit includes both independent APKs and Web examples. Serve static Web files locally with `python -m http.server --directory build/web`; runtime needs no external service. This is not a deployment command.

## Platforms and limits

Measured target: Python 3.10/3.12/3.13 on Linux, Chromium, Android API 35 emulator x86_64. Android minimum API 26, compile/target SDK 35; JDK 17, Gradle 8.11.1, AGP 8.9.2, Kotlin 2.0.21, Compose BOM 2024.12.01. First Android build downloads dependencies. Other browser/device combinations are not comprehensively validated; **these RC APKs have not been tested on a physical device**.

Bounds: int32, text 1024 Unicode scalar values, lists up to 100 records, 16 fields/record, 32 screens/stack frames, 64 navigation bindings, further source/expression/state limits. No implicit conversions or silent truncation. No nesting/migrations/encrypted storage, route parameters/deep links, modules, background services, general layout/theme API, Gradle wrapper, production signing or stable pre-1.0 compatibility guarantee. Reproducible sources and archive payloads do not imply byte-identical signed APKs or immutable transitive dependencies. [All limits](KNOWN_LIMITATIONS.md), [syntax](LANGUAGE_0_10_TEXT.md), [records](RECORDS_COLLECTIONS_010.md), [navigation](NAVIGATION_010_CONTRACT.md).

Tests and verified file hashes belong to a **specific SHA** in the CI-created manifest; [RC report](RC_010_REPORT.md) distinguishes final checks from physical-device limits and technical readiness from owner authorization. [Upgrade/rollback](UPGRADE_0_10_0rc1.en.md). [Русский](RELEASE_NOTES_0_10_0rc1.ru.md).
