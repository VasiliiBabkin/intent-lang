# Sedrava 0.10.0rc2 — release candidate preparation / Подготовка RC2

Status: **IN PROGRESS; NOT RELEASED; NOT APPROVED FOR MERGE OR PUBLICATION**.

## Source baseline

- Base main commit: `6aa5f3f3402b402481bf4a5f262c41b099c66d07` (includes stability audit fixes and dedication).
- Proposed Python/package/CLI version: `0.10.0rc2`.
- Proposed Android versionName: `0.10.0rc2`, versionCode: `10002` (rc1: `10001`).
- This file records intentions, **not successful test evidence**.

## Required evidence before technical GO

- [ ] Final SHA recorded and all applicable GitHub Actions workflows pass on that SHA.
- [ ] Python 3.10/3.12/3.13 tests, existing 0.9/0.10 regressions, no skipped required checks.
- [ ] Python / JavaScript / Kotlin differential state and rejection checks.
- [ ] Chromium UI and persistence, corrupt storage protection, browser navigation and focus.
- [ ] Android JVM, Lint, APK signature/permissions, API 35 emulator Back, rotation, restart, simultaneous app isolation.
- [ ] **Real rc1 → rc2 APK upgrade** with the *same application ID and signing key*, increasing versionCode, preserved valid SharedPreferences and rejection of invalid data without overwrite. Do not confuse clean installs with upgrades.
- [ ] Clean wheel and sdist installs; package metadata, bundled docs/examples, hash manifests, archive safety and verified 0.9 baseline rollback.
- [ ] Immutable RC2 artifacts tied to exact source SHA, toolchain versions, checksums, test logs and manifest; RC1 kit unchanged.
- [ ] Update release notes, compatibility/upgrade guides and README, retaining explicit no-automatic-migration and single-writer limitations.
- [ ] Document physical-device testing or explicitly acknowledge emulator-only Android verification.
- [ ] Record unresolved P0/P1 findings (required: zero) and owner-defined observation window.

Read `docs/STABLE_RELEASE_GATES_010.md`, `docs/COMPATIBILITY_010.md` and `docs/STABILITY_AUDIT_010.md` as normative local acceptance criteria.

## Authorization boundary

Do not merge, tag, publish GitHub Releases, upload to PyPI/TestPyPI, or deploy the website without explicit owner approval. A green CI run alone does not authorize publication.
