# Intent — Roadmap / Дорожная карта

**Status / Статус:** development plan, not a release commitment.  
**Published package / Опубликованный пакет:** `intent-lng 0.7.0` (per project owner).  
**Active work / Текущая разработка:** experimental 0.8–0.9 features; not included in the published 0.7.0 package.

## Vision / Видение

**Describe the application; get the application. / Опиши приложение — получи приложение.**

Intent should turn concise, declarative descriptions into useful applications without platform boilerplate. The goal is not to reproduce Kotlin, Python or JavaScript. See [Origin and Vision](ORIGIN_AND_VISION.md).

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
| **0.10** | Rich UI / Интерфейс: text fields, toggles, lists, cards, navigation, themes, responsive layout | Multi-screen example runs on Android and Web; accessibility basics |
| **0.11** | Data / Данные: strings, collections, records, local data model | Type and persistence semantics specified; migration strategy; working sample |
| **0.12** | Device capabilities / Устройство: files, notifications, permissions, camera | Explicit capability declarations, graceful unsupported-platform behavior |
| **0.13** | App architecture / Архитектура: reusable components, modules, structured errors | Tested multi-file reference application |
| **0.14** | Developer tools / Инструменты: editor integration, syntax highlighting, completion, preview, debugger | Documented, repeatable edit-build-preview workflow |
| **0.15** | Desktop / Настольные приложения: Windows-first target | Verified executable app and packaging workflow on Windows |
| **0.16–0.19** | Hardening / Стабилизация: performance, accessibility, security, compatibility | Supported platform matrix and representative apps pass release gates |
| **1.0** | Stable language / Стабильный язык: specification, CLI, compatibility and migration policy | Versioned specification, repeatable releases, documented support commitments |

**Version numbers are planning labels, not promised release dates. / Номера версий — ориентиры, не сроки и не гарантии.**

## Immediate backlog / Ближайшие задачи

- [ ] Add visible Android validation errors for rejected numeric input; preserve editable draft.
- [ ] Add Web parity and regression tests for empty, invalid, overflow, corrected input and state changes.
- [ ] Verify that only accepted persistent state survives restart.
- [ ] Document 0.9 syntax, semantics and platform differences.
- [ ] Keep the published 0.7.0 release distinct from unreleased development features.
- [ ] Define branch, version and PyPI release procedure before the next publication.
- [ ] Create a complete reference application for 0.10.

## Release gate / Условия завершения этапа

A milestone is ready only when its behavior is specified, relevant generators and interpreter are tested, examples run, documentation is updated, CI is green and device-specific behavior is verified or explicitly labeled unverified. A Git branch or pull request is **not** a release.

## Beyond 1.0 / После 1.0

Visual app builder, reusable component ecosystem, optional AI-assisted authoring and additional platforms. **AI is optional; the language runtime must work without it.**

## Historical progress / Уже сделано

- [x] Parser, interpreter, actions, invariants and independent tests.
- [x] Shared typed AST and experimental Kotlin/Compose Android generator.
- [x] Standalone Web/JavaScript generator.
- [x] CLI and first public PyPI releases in the 0.7 series.
- [x] Android APK builds in GitHub Actions and device tests.
- [x] Initial cross-backend differential tests and CI.
- [ ] Formal language specification and comprehensive conformance suite.
