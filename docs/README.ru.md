> Current 0.9 alpha documentation / Актуальная документация: [Quick Start](QUICKSTART.md), [Language reference / Справочник](LANGUAGE_0_9.md), [Build / Сборка](BUILD.md), [FAQ](FAQ.md), [Limitations / Ограничения](KNOWN_LIMITATIONS.md), [Audit / Аудит](ALPHA_AUDIT.md). Older prototype commands below are historical.

# Sedrava — документация на русском языке

**Статус:** экспериментальный язык, не готов к промышленному использованию.

Sedrava описывает состояние приложения, действия, ограничения и исполняемые проверки. Один исходный файл может интерпретироваться на Python либо компилироваться в Android (Kotlin/Compose) или автономную веб-страницу (HTML/JavaScript).

## Быстрый старт

Требуется Python 3.12 или новее. Для генерации веб-страницы сторонние пакеты не нужны.

```bash
python -m unittest discover -s tests -v
python web_codegen.py examples/workflow.sdr --output build/web/index.html
```

Откройте `build/web/index.html` в браузере. Для Android:

```bash
python android_codegen_v03.py examples/workflow.sdr --output build/generated-android
```

Затем соберите проект с помощью Gradle и Android SDK. Готовая веб-страница не требует сервера.

## Пример

```sedrava
app "Workflow"
state count = 0
state completed = false

action advance:
    if count < 3:
        count = count + 1
    if count == 3:
        completed = true

action reset:
    count = 0
    completed = false

rule count >= 0 and count <= 3
rule completed == (count == 3)

test finish: advance, advance, advance -> completed == true

screen main:
    text "Workflow"
    value count
    value completed
    button "Next" -> advance
    button "Reset" -> reset
```

## Основные конструкции

- `app "Имя"` — название приложения.
- `state имя = значение` — объявление состояния. Сейчас поддерживаются целые числа и логические значения `true` / `false`.
- `action имя:` — последовательность присваиваний и условий `if` / `else`; поддерживается также одно присваивание в строке.
- `rule выражение` — инвариант состояния.
- `test имя: действие, действие -> выражение` — исполняемая проверка из начального состояния.
- `screen main:` — минимальное описание интерфейса: `text`, `value`, `button`.

Выражения: `+`, `-`, `*`, сравнения `==`, `!=`, `<`, `<=`, `>`, `>=`, логические `and`, `or`, `not`, скобки.

## Семантика действий

Каждое действие получает копию текущего состояния. Присваивания выполняются последовательно, а условия читают уже изменённые значения. После выполнения всех инструкций проверяются `rule`. Если хотя бы одно ограничение нарушено, всё действие отклоняется, а прежнее состояние сохраняется. Тесты запускаются независимо друг от друга.

## Что ещё не поддерживается

Пользовательские функции, словари, модули, ввод-вывод, асинхронность и стандартная библиотека. Строки, записи и ограниченные списки реализованы в разработке 0.10. Это пока узкоспециализированный язык, а не замена Kotlin или JavaScript.

## Статус переносимости

Android-версия 0.3 проверена на устройстве. Веб-компилятор 0.4 экспериментальный: его генерация покрыта тестами, но одинаковое поведение в браузере и на Android необходимо дополнительно проверять сквозными тестами.


## Установка из исходного кода

Дистрибутив `sedrava` пока не опубликован в PyPI. В корне клонированного репозитория выполните:

```bash
python -m pip install .
sedrava --version
sedrava check examples/workflow.sdr
sedrava test examples/workflow.sdr
sedrava build web examples/workflow.sdr --output build/web/index.html
sedrava build android examples/workflow.sdr --output build/generated-android
```

Сборка Android дополнительно требует Java, Android SDK и Gradle. Репозиторий переименован: `VasiliiBabkin/sedrava`. Домен `sedrava.com` рассматривается, но не является действующим сайтом.

## Records and collections / Записи и коллекции (unreleased 0.10)

The development branch integrates typed records and bounded ordered lists into `.sdr`,
with stable IDs, atomic actions, strict snapshots and generated Web/Compose UI.
Записи и списки доступны в языке на ветке разработки; 0.10 не выпущена.

- [English task-manager guide](RECORDS_QUICKSTART.en.md)
- [Руководство на русском](RECORDS_QUICKSTART.ru.md)
- [Measured coverage / Фактические проверки](COLLECTIONS_010_REPORT.md)

## Multi-screen navigation / Многоэкранная навигация (unreleased 0.10)

Named screens, guarded atomic transitions and a bounded Back stack are implemented
in the core and both generators. One `.sdr` file generates the two-screen task manager.
Экраны и переходы — возможность языка; опубликованного выпуска 0.10 нет.

- [English guide](NAVIGATION_QUICKSTART.en.md)
- [Русское руководство](NAVIGATION_QUICKSTART.ru.md)
- [Syntax and semantics](NAVIGATION_010_CONTRACT.md)
- [Measured report](NAVIGATION_010_REPORT.md)

## Release readiness / Подготовка к RC (unreleased 0.10)

Independent deterministic Android IDs and `--application-id` are implemented.
Независимые Android-приложения собираются с постоянным ID; название отделено от пакета.
[English identity/build guide](ANDROID_ID.en.md) · [Русская инструкция](ANDROID_ID.ru.md).
Wheel/sdist include examples, documentation and license under `sys.prefix/share/sedrava`.
Дистрибутив содержит примеры, документацию и лицензию; публикация 0.10 не выполнялась.

Measured RC readiness / Фактическая готовность RC: [report / отчёт](RELEASE_READINESS_010_REPORT.md).

## 0.10.0rc1 preparation / Подготовка RC (not published)

[Release notes EN](RELEASE_NOTES_0_10_0rc1.en.md) · [RU](RELEASE_NOTES_0_10_0rc1.ru.md) · [Upgrade/rollback EN](UPGRADE_0_10_0rc1.en.md) · [RU](UPGRADE_0_10_0rc1.ru.md) · [RC report](RC_010_REPORT.md).
Use a verified local wheel in a separate environment; no PyPI/TestPyPI RC has been published.
Установка — из проверенного локального wheel в отдельное окружение; автоматической миграции данных нет.
