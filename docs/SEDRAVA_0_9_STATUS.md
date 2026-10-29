# Sedrava 0.9 integration status / Статус интеграции Sedrava 0.9

**Date / Дата:** 2026-10-29

## Version truth / Версии без путаницы

- Historical **Intent 0.7**: published as the separate legacy `intent-lng` project, not Sedrava.
- Sedrava `main`: contains the integrated 0.9.0a1 candidate after PR #6; the `0.7.1a1` release proposal was **not published**.
- Sedrava `integration/sedrava-0.9`: historical integration branch, merged via PR #6. Package metadata `0.9.0a1` means **candidate only**, not a release.
- **No Sedrava package has been published on PyPI. No Sedrava 0.9 GitHub Release exists.**

## Implemented / Реализовано

- Checked 32-bit integer arithmetic; bounded AST and action evaluation.
- Typed numeric input, state persistence declarations, derived state, conditional UI.
- CLI diagnostics with line numbers (column 1 is a placeholder).
- Web and Android/Compose generation; examples `daily_steps.sdr`, `input_goal.sdr`, `derived_progress.sdr`.
- Ported Python, JavaScript conformance and Android generation regression tests.

## Verification / Проверка

- Python unit tests and Web differential conformance: CI on the integration branch.
- Distribution wheel/sdist verification: dedicated workflow, **without publishing**.
- Android APK: CI compile gate passed for the basic Workflow example. A tester confirmed installation, launch and expected basic action behavior on a physical Android device on 2026-10-29.
- **Reference app**: `examples/reference_09.sdr` and [test checklist](REFERENCE_09.md) cover numeric input, persistence and derived state; physical-device acceptance **confirmed on 2026-10-29**, including invalid input, relational constraints, overflow rejection, editable draft, and persistence of goal/progress/sessions across relaunch. See [Android acceptance](ANDROID_09_ACCEPTANCE.md).

## Remaining release gates / Что остаётся

1. CI and clean wheel installation green on the final exact commit.
2. Android APK builds for reference examples, and test on physical device or explicitly disclose unverified behavior.
3. Verify Android input error feedback, draft preservation, and persistence after restart; ensure Web parity for rejected/corrected input.
4. Complete language syntax and cross-platform semantics documentation.
5. Review release notes, security limitations and versioned release tag before a public GitHub pre-release.

**Language syntax remains English.** Documentation may be bilingual. PyPI publishing remains explicitly postponed.

### Reference persistence evidence (2026-10-29)

A physical Android tester confirmed goal value 20 survives application relaunch (screenshot). This verifies the tested persistent-goal path only; nonzero progress/session persistence and rejected/overflow input behavior remain open. See [reference verification](REFERENCE_09.md).

## Release readiness checkpoint (2026-10-29)

- Android reference app physical-device acceptance: **PASS** ([details](ANDROID_09_ACCEPTANCE.md)).
- CI and Android APK generation: previously passed on `main` commit `981fbc011648ea724bb9c1007bcbfae1fe4ceeff`.
- Python package: `0.9.0a1` is a candidate, not a published release.
- Open: complete normative language/platform specification, broaden Web parity cases, audit release archive and verify final exact release commit/tag. GitHub Release has not been created. PyPI remains out of scope.
