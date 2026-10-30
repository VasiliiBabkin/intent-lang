> Historical 0.9 limits below. This development branch adds bounded text; see [text semantics](LANGUAGE_0_10_TEXT.md) for the supported unreleased increment and remaining limitations. Lists/navigation/full 0.10 remain unimplemented.

# Known limitations / Известные ограничения 0.9.0a1

- Experimental API/grammar; no stable compatibility promise before 1.0. The development branch supports int32, bool, text and bounded record lists. No division, modules, loops, background services, actual timers or navigation. See [records limits](RECORDS_COLLECTIONS_010.md).
- Single simple screen, no layout/theme customization API. Android scrolls; no comprehensive accessibility certification. Native and HTML input draft behavior differs (see [reference](LANGUAGE_0_9.md)).
- CLI interpretation is stateless between invocations. UI persistence is local, unencrypted, best effort, without schema migrations or cross-app separation on Android. Generated examples share `org.sedrava.generated`.
- Diagnostics have useful line/columns for many parse errors but no complete runtime source maps. Cross-declaration/runtime errors can omit positions.
- Source/AST/derived/block/interpreter limits are safeguards, not an adversarial sandbox. Compilation and browser/Android UI operations still consume host resources. Very large allowed programs may exceed native compiler limits; applications should remain small in this alpha.
- Historical prototype entry points remain for compatibility. Use `sedrava` for 0.9; do not infer current semantics from historical 0.3/0.7 documents.
- No Gradle wrapper, release signing, package identity configuration, encrypted storage, dependency lockfiles, SBOM or bit-for-bit APK reproducibility guarantee. Direct Android versions are pinned; review transitive dependency changes when refreshing caches.
- Python/Node/Chromium tests and APK compilation have different coverage. Historical physical Android 16 acceptance applies to its previously tested APK; it does not establish UI acceptance of newly generated binaries. See [audit evidence](ALPHA_AUDIT.md).

Русский: версия предназначена для изучения и небольших экспериментов. Нет автоматического времени и навигации. Строки, записи и ограниченные списки реализованы в экспериментальной разработке 0.10. Сохранение не предназначено для секретов; все Android-примеры заменяют друг друга при установке. Публичный выпуск допустим только после проверок точного коммита; успешная сборка APK не означает успешный UI-тест.
