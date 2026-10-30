# Sedrava 0.10.0rc1 — экспериментальный релиз-кандидат (подготовлен, не опубликован)

**«Описал приложение — получил приложение».** Sedrava — декларативный язык небольших автономных приложений: типизированные данные, правила, действия, тесты и экраны описываются в одном `.sdr`, из которого генерируются Web и Kotlin/Jetpack Compose Android. RC предназначен для контролируемых экспериментов и обратной связи, не для production и не как обещание стабильности. Подготовка не создаёт тег, релиз или публикацию 0.10.

## Отличия от 0.9

Сохранены int32 с проверкой переполнения, bool, инварианты, атомарные действия, ввод и сохранение. Добавлены ограниченный Unicode-текст, типизированные записи, упорядоченные ограниченные коллекции с устойчивыми ID, операции добавления/изменения/удаления, строгая проверка снимков коллекций и многоэкранная навигация с охраняемыми переходами и ограниченным стеком возврата. Web поддерживает историю браузера, клавиатуру и фокус; Android — системный Back, поворот и пересоздание Activity. Холодный запуск открывает начальный экран и восстанавливает только `persist`-данные.

Разные названия приложений получают разные детерминированные Android ID. Явный `--application-id com.example.daybook` позволяет менять название, сохраняя ID, или разделять приложения с одинаковыми названиями. `versionName` RC — `0.10.0rc1`, тестовый `versionCode` — **10001** вместо прежнего 1; ID от версии не зависит. Название лаунчера хранится строковым ресурсом. APK в комплекте имеют **debug-подпись**, не производственную подпись для распространения.

## Установка проверенного комплекта

Имя Python-пакета — **sedrava**. Опубликованная 0.9 находится в GitHub Releases, а не в PyPI; исторический `intent-lng` не является заменой Sedrava. Скачайте комплект из успешного Actions-прогона **Prepare experimental RC kit (no publication)** для проверенного SHA. Не используйте движущийся branch/latest. [Проверка и публикация](RC_PUBLISHING.md) объясняет привязку к artifact ID и digest. Изучите `manifest.json`, `manifest.md`, `availability.json`, `SHA256SUMS` и отдельный delivery-файл; реальные ссылки формируются CI после загрузки.

```sh
python -m venv .venv-sedrava-rc1
# POSIX; Windows: .venv-sedrava-rc1\Scripts\activate
. .venv-sedrava-rc1/bin/activate
python -m pip install --no-index /absolute/path/to/verified-kit/sedrava-0.10.0rc1-py3-none-any.whl
sedrava --version
# Ожидается: sedrava 0.10.0rc1
```

До установки проверьте внешний digest неизменяемого Actions-артефакта, затем выполните из доверенного checkout `python scripts/verify_rc_bundle.py /path/to/verified-kit`. У CLI нет runtime-зависимостей; примеры, документация и лицензия устанавливаются в `sys.prefix/share/sedrava`. Sdist устанавливается по проверенному локальному пути; изолированная сборка скачивает точные версии backend из `pyproject.toml`. Для офлайн-сборки предварительно установите эти backend wheels из отдельно проверенного wheelhouse и используйте `--no-build-isolation`. Команда `pip install sedrava==0.10.0rc1` сейчас не поддерживает установку: RC не опубликован. Возможная будущая публикация требует отдельной проверки и решения владельца.

## Первое приложение

```sdr
app "First RC app"
state name = "Guest"
state visits = 0
persist name
action welcome: visits = visits + 1
test once: welcome -> visits == 1
screen main:
    text "Welcome"
    input name
    value visits
    button "Visit" -> welcome
```

Сохраните как `hello.sdr` в UTF-8:

```sh
sedrava check hello.sdr
sedrava test hello.sdr
sedrava run hello.sdr welcome
sedrava build web hello.sdr --output build/web/index.html
sedrava build android hello.sdr --output build/android --application-id com.example.firstapp
gradle -p build/android --no-daemon :app:assembleDebug :app:lintDebug
```

Путь установленных примеров: `python -c "import sys; from pathlib import Path; print(Path(sys.prefix)/'share/sedrava/examples')"`. Проверьте `text_profile.sdr`, `task_manager.sdr`, `task_manager_navigation.sdr`. Каждый менеджер задач генерируется из одного `.sdr` без ручных изменений. Комплект содержит оба независимых APK и Web-примеры. Локальный просмотр: `python -m http.server --directory build/web`; внешнего сервиса во время работы не требуется. Это локальный сервер, не развёртывание сайта.

## Платформы и ограничения

Проверяется Python 3.10/3.12/3.13 на Linux, Chromium и эмулятор Android API 35 x86_64. Минимальный Android API — 26, compile/target SDK — 35. Инструменты: JDK 17, Gradle 8.11.1, AGP 8.9.2, Kotlin 2.0.21, Compose BOM 2024.12.01; при первой сборке загружаются зависимости. Другие браузеры и устройства не проверены исчерпывающе. **Физическое устройство для этих RC APK недоступно.**

Пределы: int32, 1024 Unicode-скаляра в тексте, до 100 записей в коллекции, 16 полей записи, 32 экрана/элемента стека, 64 навигационные команды; действуют дополнительные ограничения исходников, выражений и состояния. Нет неявного преобразования или обрезания строк. Нет вложенных записей, миграций, шифрования, параметров маршрутов/deep links, модулей, фоновых служб, произвольной вёрстки/тем, Gradle wrapper, production-подписи и гарантии совместимости до 1.0. Воспроизводимость исходников и содержимого архивов не означает побитно одинаковые APK и неизменность транзитивных зависимостей. [Все ограничения](KNOWN_LIMITATIONS.md), [справочник](LANGUAGE_0_10_TEXT.md), [записи](RECORDS_COLLECTIONS_010.md), [навигация](NAVIGATION_010_CONTRACT.md).

Числа тестов и SHA-256 относятся к конкретному SHA в созданном CI манифесте. [RC-отчёт](RC_010_REPORT.md) разделяет фактические проверки, ограничения устройств, техническую готовность и разрешение владельца. [Обновление и откат](UPGRADE_0_10_0rc1.ru.md). [English](RELEASE_NOTES_0_10_0rc1.en.md).
