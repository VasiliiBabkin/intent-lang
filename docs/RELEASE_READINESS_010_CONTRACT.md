# Sedrava 0.10 — release-readiness engineering contract

Status: **planned, not implemented**. Base: main after merged navigation PR #15. No tag, release, PyPI publication or site deployment is authorized.

## Goal
Make generated Web and Android apps safe to install side by side, predictable to build, usable, and ready for a measured 0.10 release-candidate review. Preserve all 0.9/0.10 semantics.

## 1. Android package identity
- Derive a deterministic unique default applicationId/namespace from the application identity, or support an explicitly validated package ID; document collision policy.
- Enforce Android-compatible naming and length; reject invalid names with actionable diagnostics.
- Separate Android package identity from user-facing app title. Ensure two distinct example apps can be installed simultaneously and retain independent data.
- Confirm manifests, generated Kotlin namespaces, Gradle config, test harnesses, APK checks and documentation use the resolved identity consistently.
- Include regression tests for Unicode titles, whitespace, punctuation, duplicates, length, stability and explicit overrides.

## 2. UI quality
- Audit generated Web and Compose screens for phone widths, long text, large fonts, keyboard/focus, disabled/invalid states, errors, empty lists, selection, navigation and screen reader labels.
- Improve shared semantic defaults without adding platform-specific markup to `.sdr`.
- Maintain observable semantic parity; avoid redesign that breaks existing applications.

## 3. CLI and reproducibility
- Check project before build; return stable nonzero codes and source-location diagnostics for malformed input.
- Verify clean builds from installed wheel/sdist, not just repository checkout.
- Audit deterministic generation, no network requirement at runtime, permissions, APK signature, package metadata and dependency handling.

## 4. Evidence
- Python 3.10/3.12/3.13, Chromium E2E, JVM conformance, Android APK/Lint and emulator including cold launch and simultaneous installation of two distinct generated apps.
- Verify old examples and records/navigation reference apps unchanged.
- Record what is and is not tested, especially physical-device coverage.

## 5. Documentation and gates
- Update RU/EN quickstarts, README, language/build references, roadmap, changelog and known limitations after implementation.
- Produce a release-readiness report with exact commands, results, artifacts, remaining blockers and a go/no-go recommendation.
- Keep this PR draft until all checks pass. No merge, release, tag, PyPI publication or deployment without explicit user approval.
