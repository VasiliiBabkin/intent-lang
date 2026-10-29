# Sedrava 0.9.0a1 — first public Alpha candidate

**Unreleased. No tag or GitHub Release has been created by this engineering pass. No PyPI upload.**

Describe the application; get the application. / Опиши приложение — получи приложение.

## Scope / Возможности

Sedrava describes signed 32-bit integer/boolean state, pure derived values, sequential atomic actions, invariant rules, embedded tests and a single-screen interface. One source generates standalone Web HTML/JavaScript or an Android/Compose Gradle project. Numeric input validates before commit; `persist` saves accepted UI state; conditional text responds to derived booleans. Python runtime dependencies: none.

CLI: `--version`, `--help`, `check`, `run`, `test`, `build web`, `build android`. `run FILE [ACTION ...]` prints deterministic JSON and starts from defaults. Android generation is followed by a separate Gradle build.

## Fixes / Исправления

This pass fixes signed-minimum literals, initially overflowing derives, intermediate derive validation, atomic overflow handling in UI callbacks, invalid restored snapshots, Android preference type corruption, HTML script-end injection, Kotlin interpolation/name collisions, duplicate screens and unbounded derived expansion/block nesting. Accepted Android state uses `rememberSaveable` for Activity recreation; Android layout scrolls. See [changelog](../CHANGELOG.md) and [audit](ALPHA_AUDIT.md).

## Learn / Начало работы

[Quick Start](QUICKSTART.md) → [language reference](LANGUAGE_0_9.md) → [examples](../examples/README.md) → [Web/Android build](BUILD.md).

Complete examples include a constrained counter, manual countdown, habit progress, validated input and Sedrava 0.9 Lab. The countdown is an explicit action model, not an automatic timer.

## Verification and limitations / Проверки и ограничения

Current measured evidence, including exact commit links and Android build outcome, belongs to [ALPHA_AUDIT.md](ALPHA_AUDIT.md). Chromium tests are real-browser tests; Node conformance compares runtime traces; Android compilation/JVM/Lint do not imply UI acceptance. Previously confirmed manual Android 16 acceptance remains [separate historical evidence](ANDROID_09_ACCEPTANCE.md). Newly changed binaries need device/rotation acceptance; no connected device or accelerated emulator was available locally.

[Known limitations](KNOWN_LIMITATIONS.md) include no string state, navigation, lists, real timers, encrypted persistence or configurable Android application identity. The alpha is for learning and experimental apps, not production or secrets. [Security review boundaries](SECURITY.md).

## Why 0.9.0a1 / Почему версия сохранена

No Sedrava 0.9 release has been published. Changes repair invalid/unsafe behavior of the unpublished candidate and complete its planned CLI; they do not expand 0.9 with 0.10 features. Retain `0.9.0a1`. Historical Intent 0.7 and the abandoned Sedrava 0.7.1 proposal are not this release.

## Publication checklist / Публикация

1. Review/merge the alpha PR; if merging changes the source tree, rerun all gates on the resulting commit.
2. Require green **Sedrava alpha checks** and **Sedrava 0.9 reference Android APK** for that exact commit. Download wheel/sdist, Web examples, debug APK, JVM/Lint reports and browser traces.
3. Confirm clean install and reproduce the reference build using [BUILD.md](BUILD.md). Inspect APK signature and merged permissions. Disclose the lack of new device UI verification; do not reuse historical acceptance as proof of a new APK.
4. Only after these checks, create a GitHub **pre-release** `v0.9.0a1` targeting the checked commit; attach checked wheel, sdist, reference debug APK, Web bundle and SHA-256 checksums. Use these notes and the audit, including limitations. Do not mark stable/latest or upload to PyPI.

Example final owner command after checks (set `CHECKED_COMMIT` to the verified full SHA):

```sh
gh release create v0.9.0a1 --repo VasiliiBabkin/sedrava --target "$CHECKED_COMMIT" --prerelease --title 'Sedrava 0.9.0a1 Alpha' --notes-file docs/RELEASE_NOTES_0_9_0a1.md dist/*.whl dist/*.tar.gz build/release/app-debug.apk build/release/web-examples.zip build/release/SHA256SUMS
```

Do not run this while any mandatory check is pending/failing. Release publication is a separate verified action, not an implication of package metadata.

Русский: первая Alpha описывает реальные возможности языка и исправляет ошибки семантики/генерации. Установка, примеры и сборка приведены в документации. Результаты проверок перечислены в аудите. Необнаруженное устройство и отсутствие `/dev/kvm` не позволяют утверждать, что новые APK прошли UI-тесты. До публикации нужны зелёные проверки точного коммита и проверенные артефакты; PyPI исключён.
