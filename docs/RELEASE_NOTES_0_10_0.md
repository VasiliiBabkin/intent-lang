# Sedrava 0.10.0 — заметки о стабильном выпуске / Release notes

**Описал приложение — получил приложение.** Sedrava позволяет описать небольшое приложение в одном `.sdr` и сгенерировать автономное Web-приложение или проект Android/Jetpack Compose.

## Возможности / Capabilities

- Строгие типы text (до 1024 Unicode scalar values), signed int32, boolean.
- Типизированные записи и упорядоченные списки (до 100 элементов) с устойчивыми ID.
- Атомарные действия с откатом, инварианты и встроенные тесты.
- Экраны, навигация с ограниченным стеком до 32 и guarded transitions.
- Web: история, восстановление сохранённых значений. Android: системный Back, сохранение принятого сеанса.
- CLI: `check`, `test`, `run`, `build web`, `build android`; Python >=3.10, без внешних runtime dependencies.

## Установка после публикации / Installation after publication

```sh
python -m pip install sedrava==0.10.0
sedrava --version
```

Ожидаемая версия: `sedrava 0.10.0`. Само наличие инструкций не означает, что PyPI-пакет уже опубликован.

## Проверка / Verification

Для RC2 существуют отчёты Python/JavaScript/Kotlin/Chromium/Android emulator ([RC2 report](RC2_010_REPORT.md)). Для финального 0.10.0 требуется повторная проверка по [release gates](STABLE_RELEASE_GATES_010.md) на окончательном SHA. Успешное выполнение физического теста не подтверждено: см. [device checklist](PHYSICAL_DEVICE_010.md).

## Совместимость и ограничения / Compatibility and limitations

Android versionCode **10003** > rc2 **10002**. Обновление возможно лишь при совпадении application ID и подписи. Автоматических миграций нет; несовместимые данные отклоняются с сохранением оригинального снимка. При ошибке записи принятые изменения могут остаться только в памяти. Одновременные авторы записи не синхронизируются. Web storage зависит от origin; данные Android не шифруются самим Sedrava. Нет модулей, циклов, deep links и гарантии стабильного API. Подробности: [compatibility](COMPATIBILITY_010.md), [known limitations](KNOWN_LIMITATIONS.md), [Android IDs](ANDROID_ID.en.md).

**Назначение:** учебная и экспериментальная разработка, не production.

**English:** Sedrava 0.10.0 prepares a stable language release with text, records, bounded collections, atomic actions, invariants and navigation. Final-SHA validation, owner device acceptance and PyPI/GitHub publication are separate steps; this document does not assert they already occurred.
