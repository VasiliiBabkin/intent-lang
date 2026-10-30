> Current development increment: [first-class text](LANGUAGE_0_10_TEXT.md), [measured report](TEXT_010_REPORT.md). 0.9.0a1 is published; 0.10 remains unreleased and incomplete.

# Sedrava — Roadmap / Дорожная карта

**Status / Статус:** development plan, not a release commitment.  
**Published package / Опубликованный пакет:** historical `intent-lng` 0.7 series; Sedrava has not been published on PyPI.  
**Active work / Текущая разработка:** Sedrava 0.9.0a1 is published on GitHub; 0.10 text work is an unreleased development increment.

## Vision / Видение

**Describe the application; get the application. / Опиши приложение — получи приложение.**

Sedrava should turn concise, declarative descriptions into useful applications without platform boilerplate. The goal is not to reproduce Kotlin, Python or JavaScript. See [Origin and Vision](ORIGIN_AND_VISION.md).

## Principles / Принципы

1. **Minimal ceremony / Минимум служебного кода:** describe what the app does, not how to initialize its framework.
2. **Shared semantics / Общая семантика:** actions, state, rules and tests behave consistently across backends.
3. **Native experience / Нативность:** each platform should feel natural, not pixel-identical.
4. **Safe defaults / Безопасность:** validate input, bound computations, declare permissions and persistence explicitly.
5. **Working examples / Практическая проверка:** each milestone includes a real app and automated tests.
6. **Offline-first where possible / По возможности без сервера:** simple apps should run locally.
7. **Honest releases / Честные выпуски:** branches and prototypes are not published versions.

## Milestones / Этапы

| Version | Focus / Направление | Exit criteria / Результат |
| --- | --- | --- |
| **0.9** | Reliable foundations / Надёжная основа: checked arithmetic, persistence, numeric input, conditional widgets, diagnostics | Clear input validation feedback; Android/Web regression and conformance tests; device check |
| **0.10** | Text, records, bounded collections and richer UI / Строки, записи, списки и интерфейс | Multi-screen example runs on Android and Web; accessibility basics |
| **0.11** | Data / Данные: migrations, nested schemas, local data model | Type and persistence semantics specified; migration strategy; working sample |
| **0.12** | Device capabilities / Устройство: files, notifications, permissions, camera | Explicit capability declarations, graceful unsupported-platform behavior |
| **0.13** | App architecture / Архитектура: reusable components, modules, structured errors | Tested multi-file reference application |
| **0.14** | Developer tools / Инструменты: editor integration, syntax highlighting, completion, preview, debugger | Documented, repeatable edit-build-preview workflow |
| **0.15** | Desktop / Настольные приложения: Windows-first target | Verified executable app and packaging workflow on Windows |
| **0.16–0.19** | Hardening / Стабилизация: performance, accessibility, security, compatibility | Supported platform matrix and representative apps pass release gates |
| **1.0** | Stable language / Стабильный язык: specification, CLI, compatibility and migration policy | Versioned specification, repeatable releases, documented support commitments |

**Version numbers are planning labels, not promised release dates. / Номера версий — ориентиры, не сроки и не гарантии.**

## Immediate backlog / Ближайшие задачи

- [x] Android validation errors and preserved editable draft confirmed on physical device; see [acceptance report](ANDROID_09_ACCEPTANCE.md).
- [x] Extend Web parity tests to cover empty, invalid, overflow, corrected input and persistence after restart (basic checks exist).
- [x] Accepted persistent goal, progress and sessions survive relaunch in the tested Android scenario; see [acceptance report](ANDROID_09_ACCEPTANCE.md).
- [x] Complete normative 0.9 language syntax/semantics and platform-difference specification: [reference](LANGUAGE_0_9.md).
- [x] Distinguish the historical Intent 0.7 release from the published Sedrava 0.9 alpha.
- [x] Define separate integration branch and 0.9.0a1 candidate version; PyPI publication deferred.
- [ ] Create a complete multi-screen reference application for 0.10. The single-screen 0.9 [reference app](REFERENCE_09.md) is separate.

## Release gate / Условия завершения этапа

A milestone is ready only when its behavior is specified, relevant generators and interpreter are tested, examples run, documentation is updated, CI is green and device-specific behavior is verified or explicitly labeled unverified. A Git branch or pull request is **not** a release.

## Beyond 1.0 / После 1.0

Visual app builder, reusable component ecosystem, optional AI-assisted authoring and additional platforms. **AI is optional; the language runtime must work without it.**

## Historical progress / Уже сделано

- [x] Parser, interpreter, actions, invariants and independent tests.
- [x] Shared typed AST and experimental Kotlin/Compose Android generator.
- [x] Standalone Web/JavaScript generator.
- [x] historical Intent 0.7 releases; Sedrava has not been published on PyPI.
- [x] Android APK builds in GitHub Actions and device tests.
- [x] Initial cross-backend differential tests and CI.
- [x] Normative alpha language reference and expanded conformance/browser suite; exhaustive coverage is not claimed.

## Sedrava integration status (2026-10-29)

0.9.0a1 is published on GitHub; its checked source, tag and release assets are preserved. Basic Android Workflow launch and actions were confirmed on a physical device on 2026-10-29; advanced numeric input, invalid-input rejection, overflow rejection and persistence passed the documented physical-device acceptance scenarios. See [reference test plan](REFERENCE_09.md). The historical Intent 0.7 PyPI release is not a Sedrava release. English-language syntax only. Release gates: CI, clean install, Android and Web builds, conformance, documentation, device testing. No PyPI publication planned.

### Physical device evidence (2026-10-29)

A tester installed the 0.9 Lab reference APK and supplied screenshots of initial state and accepted goal 6/progress 6/sessions 6/reached true, confirming launch, actions, derived state and conditional UI. See [reference verification](REFERENCE_09.md). Subsequent device tests confirmed rejected-input handling, overflow rejection and persistence after relaunch; see [Android acceptance](ANDROID_09_ACCEPTANCE.md).

### Device acceptance closure

The planned physical Android 0.9 Lab acceptance tests passed, including accepted-state persistence and rejection of invalid, relationally inconsistent and overflowing input. Evidence and limitations: [Android 0.9 acceptance](ANDROID_09_ACCEPTANCE.md). The later alpha engineering pass closed its release gates; new 0.10 binaries need their own measured verification.

## First 0.10 increment

Text state/derive/equality/actions, inferred text input and persistence are implemented on `feature/010-string-core` with Python/JS/JVM and browser conformance. The records branch now integrates records, collections and a single-screen task manager; see [coverage](COLLECTIONS_010_REPORT.md). Multi-screen navigation remains open. The [Describe → Get contract](DESCRIBE_GET_010.md) remains the product gate for the full milestone.
