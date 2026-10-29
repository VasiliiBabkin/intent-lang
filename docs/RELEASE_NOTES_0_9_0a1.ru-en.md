# Sedrava 0.9.0a1 — GitHub Alpha release notes / Примечания к альфа-выпуску

**Status: release candidate, not yet published.** This document describes the intended first Sedrava GitHub pre-release. It is not a PyPI publication.

## What's included / Что входит

- Declarative English-language syntax with Python parser, typed AST, interpreter, actions and invariants.
- Checked integer arithmetic, bounded evaluation, explicit persistent state, numeric input and conditional UI.
- Web/JavaScript and experimental native Android/Jetpack Compose generators.
- CLI diagnostics, sample programs and automated Python/Web regression tests.
- [Sedrava 0.9 Lab](../examples/reference_09.sdr), with dedicated [Android APK build](https://github.com/VasiliiBabkin/sedrava/actions/workflows/reference-09-android.yml).

## Verified / Проверено

- Python CI, package build and Android APK compilation on the integration candidate.
- Physical Android 16 acceptance of the reference app: launch, action updates, derived state, visible validation errors, preserved editable drafts, rejection of out-of-range and relationally inconsistent values, rejection of integer overflow, persistence of nonzero goal/progress/sessions after relaunch.
- Detailed [manual acceptance report](ANDROID_09_ACCEPTANCE.md).

## Limitations / Ограничения

- Experimental API and language grammar: breaking changes are expected before 1.0.
- Single-screen reference UI; no stable navigation, collections, modules or desktop backend.
- Android tests were performed on one device, not a compatibility matrix.
- Web/Android parity is tested for representative cases, not formally established for all inputs.
- Diagnostics column is not yet fully precise in all cases.
- No guarantee of production suitability, comprehensive security review, accessibility audit or performance guarantees.
- The historical Intent 0.7 release is a different distribution. Sedrava has **not** been published on PyPI.

## Install from source / Запуск из исходников

```bash
git clone https://github.com/VasiliiBabkin/sedrava.git
cd sedrava
python -m pip install .
sedrava test examples/reference_09.sdr
```

To use a release tag, checkout the published tag when one exists. Do not treat this note as evidence that a tag or release already exists.

## Release checklist / Условия публикации

- [x] Android physical-device reference acceptance documented.
- [x] Python and Android CI green on the integration branch and main checkpoint.
- [ ] Verify final release commit and run CI plus clean-install on that exact SHA.
- [ ] Confirm release archive contents and public source checkout.
- [ ] Finish explicit Web parity and normative language semantics gaps, or mark them experimental in release announcement.
- [ ] Create version tag and GitHub **pre-release** after checks; do not publish to PyPI.

See [roadmap](ROADMAP.md) and [integration status](SEDRAVA_0_9_STATUS.md).
