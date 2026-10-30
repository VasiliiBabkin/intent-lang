# Known limitations / Известные ограничения (unreleased 0.10)

Implemented: int32/bool/text, typed records, ordered bounded collections, atomic actions, strict snapshots, guarded multi-screen navigation, Web/Compose and independent [Android identities](ANDROID_ID.en.md). Sedrava 0.10 is **not released**; 0.9.0a1 is the historical published baseline.

- Experimental grammar/API; no stable pre-1.0 compatibility promise. No division, modules, loops, services, timers, deep links, route parameters, nested records or migrations. [Records](RECORDS_COLLECTIONS_010.md), [navigation](NAVIGATION_010_CONTRACT.md).
- Bounds: int32, text 1024 Unicode scalars, list capacity 100, 16 record fields, 16 record/list declarations; 32 screens/stack entries, 64 navigation bindings. Further source/AST/resource guards apply. These are safeguards, not an adversarial sandbox; very large valid programs may exceed native compiler limits.
- Responsive defaults and native controls are provided; no general layout/component/theme API or full accessibility/WCAG certification. Navigation actions using domain changes and card selection are disabled while a visible input draft is invalid; pure screen transitions and Back remain available and discard drafts. Accepted model state is unchanged. Legacy single-screen draft behavior remains compatible.
- Cold launch/reload restores only `persist` fields and opens initial screen; Android rotation/Activity recreation retains accepted session/stack. CLI sessions are stateless unless `run --state-file` is used; this file stores persistent domain data, not routes.
- Storage is local, unencrypted and best effort. No schema/data migration, cross-device sync or backup policy. Android ID changes create separate storage. Same-title defaults deliberately share identity; use distinct explicit IDs. See [ID instructions](ANDROID_ID.en.md).
- Source diagnostics cover syntax/type errors; runtime source maps are incomplete. Some cross-declaration errors have no exact location.
- No Gradle wrapper, release signing/version management, dependency lockfiles or SBOM. Direct toolchain/dependency versions are pinned; first builds download dependencies. Generated source/Web and archive payload reproducibility are tested; bit-for-bit APK/archive timestamps and transitive dependency immutability are not guaranteed.
- Emulator checks are bounded scenarios, not every Android/device configuration. Historical physical-device acceptance covers 0.9 only; new 0.10 APKs have **not** been tested on a physical device. Debug certificates differ between machines. See [readiness evidence](RELEASE_READINESS_010_REPORT.md).

Русский: строки, записи, списки, навигация и независимые Android ID реализованы. Холодный запуск открывает начальный экран; поворот сохраняет принятое состояние. Хранение не зашифровано, миграций нет. Одинаковые названия дают одинаковый ID; используйте [явный ID](ANDROID_ID.ru.md) для независимых приложений. Нет произвольной вёрстки и полной сертификации доступности. Новые APK проверяются эмулятором; физическое устройство для 0.10 недоступно. Версия ещё не выпущена.

## 0.10.0rc1 preparation / Подготовка RC (not published)

[Release notes EN](RELEASE_NOTES_0_10_0rc1.en.md) · [RU](RELEASE_NOTES_0_10_0rc1.ru.md) · [Upgrade/rollback EN](UPGRADE_0_10_0rc1.en.md) · [RU](UPGRADE_0_10_0rc1.ru.md) · [RC report](RC_010_REPORT.md).
Use a verified local wheel in a separate environment; no PyPI/TestPyPI RC has been published.
Установка — из проверенного локального wheel в отдельное окружение; автоматической миграции данных нет.

## Stability audit / Аудит стабильности

[Audit](STABILITY_AUDIT_010.md) · [Compatibility](COMPATIBILITY_010.md) · [Stable gates](STABLE_RELEASE_GATES_010.md). Rejected saved data is preserved; edits may remain temporary until recovery. Concurrent writers are last-writer-wins; no migration or power-cut certification. The audit recommends rc2 before stable 0.10.0.

Отвергнутые данные защищены от перезаписи; перед ручным сбросом сделайте копию. Новые изменения могут оставаться в памяти. Рекомендуется rc2, а не немедленный стабильный выпуск.
