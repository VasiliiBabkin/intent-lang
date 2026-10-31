# Sedrava 0.10.0rc2 — экспериментальный кандидат, не опубликован

**Описал приложение — получил приложение.** Sedrava описывает типизированные
состояния, действия, инварианты, проверки и экраны в одном `.sdr`. Его можно
исполнить на Python или получить автономное Web-приложение и Kotlin/Jetpack Compose
для Android. RC2 не добавляет возможностей языка и не объявляется стабильным.

По сравнению с опубликованной на GitHub 0.9.0a1 реализованы текст (до 1024 Unicode
scalar values), типизированные записи, упорядоченные ограниченные коллекции
(1–100 элементов, устойчивые ID), атомарные действия с откатом, строгие снимки
данных и навигация со стеком до 32 экранов. Web поддерживает историю браузера,
клавиатуру, фокус и восстановление после перезагрузки; Android — системный Back,
пересоздание принятого сеанса и независимые application ID. Неявных преобразований,
нормализации строк и молчаливого усечения нет.

По сравнению с rc1 включены [исправления аудита](STABILITY_AUDIT_010.md): защита
от перезаписи отвергнутого хранилища, корректный int32 minimum во всех позициях,
атомарная запись Web-результата CLI и отдельные ошибки повторных полей. Версия
Python/CLI/Android — `0.10.0rc2`, Android versionCode **10002** вместо **10001**.
Идентификаторы приложений и формат хранения сохранены. Артефакты rc1 не меняются.

Установка проверенного локального wheel в отдельное окружение:

```sh
python -m venv .venv-sedrava-rc2
. .venv-sedrava-rc2/bin/activate
python -m pip install --no-index /absolute/path/to/verified-kit/sedrava-0.10.0rc2-py3-none-any.whl
sedrava --version
# sedrava 0.10.0rc2
```

Для Windows PowerShell: `.venv-sedrava-rc2\Scripts\Activate.ps1`.
Примеры установленного пакета: `sys.prefix/share/sedrava/examples`. В checkout:

```sh
sedrava check examples/task_manager_navigation.sdr
sedrava test examples/task_manager_navigation.sdr
sedrava run examples/reference_09.sdr add
sedrava build web examples/task_manager_navigation.sdr --output build/web/index.html
python -m http.server 8000 --directory build/web
sedrava build android examples/task_manager_navigation.sdr --output build/android
```

Web: http://localhost:8000. APK: `gradle -p build/android :app:assembleDebug`,
JDK17, Gradle8.11.1, SDK35; подробности в [Build](BUILD.md). Python >=3.10;
матрица проверок — 3.10/3.12/3.13, Chromium, эмулятор Android API35 x86_64.
**Физическое Android-устройство для 0.10 не проверено.** APK подписаны отладочными
ключами; это не производственная подпись.

Перед обновлением сохраните проекты и данные. Автоматических миграций, экспорта,
сброса и понижения форматов нет. Строгий снимок требует точного fingerprint;
новые правила и значения непостоянных состояний могут отклонить сохранение.
Отвергнутый оригинал защищён; новые принятые изменения могут остаться в памяти
при ошибке записи. Старый скалярный формат имеет отдельный контракт. Одинаковое
название даёт одинаковый Android ID; Web-хранилище зависит от origin/пути/названия.
Одновременные записи не согласуются: побеждает последняя. Нет синхронизации и
шифрования, вложенных записей, модулей, циклов, фоновых сервисов, deep links,
универсальной вёрстки, полной сертификации доступности, Gradle wrapper,
производственной подписи, transitive lockfiles и гарантии побитово одинаковых APK.

[Совместимость](COMPATIBILITY_010.md) · [Ограничения](KNOWN_LIMITATIONS.md) ·
[Обновление и откат](UPGRADE_0_10_0rc2.ru.md).
Фактический SHA, тесты, инструменты и SHA-256 находятся в манифесте и отчёте CI.
Техническая готовность RC не заменяет период наблюдения и
[условия стабильного выпуска](STABLE_RELEASE_GATES_010.md). Публикация, merge,
тег и развёртывание требуют отдельного решения владельца.

[English](RELEASE_NOTES_0_10_0rc2.en.md) · [Отчёт RC2](RC2_010_REPORT.md).
