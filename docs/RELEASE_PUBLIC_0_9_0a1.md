# Sedrava 0.9.0a1 — First Public Alpha

**Experimental prerelease · 29 October 2026 · [source tag](https://github.com/VasiliiBabkin/sedrava/tree/v0.9.0a1)**

Describe the application; get the application. / Опиши приложение — получи приложение.

This is the first public **Sedrava** alpha, not a stable production release. No PyPI publication.

## Features / Возможности

- Declarative language with signed 32-bit integer and boolean state, pure derived expressions, atomic actions, invariants and embedded tests.
- CLI: `sedrava --version`, `check`, `run` (JSON output), `test`, `build web`, `build android`.
- Standalone Web HTML/JavaScript and experimental Android Jetpack Compose generation from the same source.
- Validated numeric input, conditional UI and persistence of accepted state.
- Reference applications, documentation and repeatable builds.

## Fixes / Исправления

Integer overflow and minimum int32 handling; validation of initial/intermediate derived values; atomic rejection of invalid changes; damaged persistence recovery; HTML/Kotlin escaping; identifier collisions; resource limits and Android Activity state restoration.

## Verified / Проверено

- 88 unit/integration/conformance tests; 720 additional Python/JavaScript differential steps.
- Seven real Chromium scenarios and two Android JVM tests.
- Python 3.10/3.12/3.13 on Linux, clean-install wheel/sdist and source checkout.
- Android reference APK and countdown APK compile; Lint, APK signing and permissions checks pass.
- **New APK was not run on a device or emulator**: no ADB device or /dev/kvm was available. Earlier physical Android 16 acceptance covers an older reference build, not this binary.
- Windows and macOS have not been verified.

See [audit](https://github.com/VasiliiBabkin/sedrava/blob/v0.9.0a1/docs/ALPHA_AUDIT.md) and [CI](https://github.com/VasiliiBabkin/sedrava/actions).

## Getting started / Начало работы

Read the [Quick Start](https://github.com/VasiliiBabkin/sedrava/blob/v0.9.0a1/docs/QUICKSTART.md), [language reference](https://github.com/VasiliiBabkin/sedrava/blob/v0.9.0a1/docs/LANGUAGE_0_9.md), [build guide](https://github.com/VasiliiBabkin/sedrava/blob/v0.9.0a1/docs/BUILD.md) and [examples](https://github.com/VasiliiBabkin/sedrava/tree/v0.9.0a1/examples).

## Downloads / Загрузки

The release attachments contain the Python wheel and source distribution, reference Android debug APK, generated Web examples and `SHA256SUMS`. Verify downloaded files against the included checksums. The APK is a demonstration, not a production application.

## Known limitations / Ограничения

Single screen, int32/bool state only, no strings/collections, navigation, automatic timers, encrypted storage or configurable Android application ID. Not intended for secrets or production use. See [known limitations](https://github.com/VasiliiBabkin/sedrava/blob/v0.9.0a1/docs/KNOWN_LIMITATIONS.md) and [security boundaries](https://github.com/VasiliiBabkin/sedrava/blob/v0.9.0a1/docs/SECURITY.md).

**Русский:** первая публичная экспериментальная альфа Sedrava. Язык, CLI, Web-генерация и сборка Android APK проверены автоматическими тестами. Новый APK не запускался на устройстве; ограничения перечислены выше. Пакет не опубликован в PyPI.
