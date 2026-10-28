# Sedrava 0.9 integration status / Статус интеграции Sedrava 0.9

**Date / Дата:** 2026-10-29

## Version truth / Версии без путаницы

- Historical **Intent 0.7**: published as the separate legacy `intent-lng` project, not Sedrava.
- Sedrava `main`: rebranded 0.7 foundation; the `0.7.1a1` release proposal was **not published**.
- Sedrava `integration/sedrava-0.9`: experimental integration of the old 0.8–0.9 branch; package metadata `0.9.0a1` means **candidate only**, not a release.
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
- Android APK: CI compile gate; passing a build does not establish physical-device behavior.
- Actual physical-device verification: **not yet confirmed for this 0.9 candidate**.

## Remaining release gates / Что остаётся

1. CI and clean wheel installation green on the final exact commit.
2. Android APK builds for reference examples, and test on physical device or explicitly disclose unverified behavior.
3. Verify Android input error feedback, draft preservation, and persistence after restart; ensure Web parity for rejected/corrected input.
4. Complete language syntax and cross-platform semantics documentation.
5. Review release notes, security limitations and versioned release tag before a public GitHub pre-release.

**Language syntax remains English.** Documentation may be bilingual. PyPI publishing remains explicitly postponed.
