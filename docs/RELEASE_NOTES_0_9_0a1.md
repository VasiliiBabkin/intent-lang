# Sedrava 0.9.0a1 — GitHub alpha release candidate

**DRAFT / НЕ ОПУБЛИКОВАНО.** This is neither a GitHub Release nor a tag. PyPI publication is postponed.

## Highlights / Изменения

- Experimental declarative language, Python interpreter and CLI.
- Android Jetpack Compose and standalone Web generators.
- Persistent integer state, numeric input, guarded actions, derived values and conditional UI.
- Checked 32-bit arithmetic and rule-based rejection of invalid state transitions.
- Reference applications: `workflow.sdr`, `reference_09.sdr`.

## Device verification / Проверки

- Android 16 reference app: installation, launch, actions, conditional UI, goal/progress/sessions persistence after relaunch, invalid and relational input rejection, and overflow input rejection confirmed by tester.
- CI: Python and Android build workflows passed on baseline `main` commit `981fbc011648ea724bb9c1007bcbfae1fe4ceeff`.
- See [device acceptance report](ANDROID_09_ACCEPTANCE.md).

## Known limitations / Ограничения

- Experimental pre-1.0 APIs and no compatibility guarantee.
- Single-screen reference UI; multi-screen UI, strings/collections and device capabilities are future milestones.
- Some CLI diagnostic columns remain placeholders.
- Android device acceptance does not constitute comprehensive Web parity, accessibility or security certification.

## Publication checklist / Условия выпуска

- [ ] Final exact release-commit CI is green.
- [ ] Clean wheel/sdist install and CLI smoke tests pass.
- [ ] Android APK and Web output checked on final commit.
- [ ] Documentation, security limitations and release archive reviewed.
- [ ] GitHub tag and pre-release created only with explicit owner approval.
- [ ] PyPI publication remains disabled.

See [roadmap](ROADMAP.md) and [status](SEDRAVA_0_9_STATUS.md).