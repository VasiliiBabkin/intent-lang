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

Пользовательские функции, строки как тип состояния, списки, словари, модули, ввод-вывод, асинхронность, стандартная библиотека и полноценные сообщения об ошибках компиляции. Это пока узкоспециализированный язык, а не замена Kotlin или JavaScript.

## Статус переносимости

Android-версия 0.3 проверена на устройстве. Веб-компилятор 0.4 экспериментальный: его генерация покрыта тестами, но одинаковое поведение в браузере и на Android необходимо дополнительно проверять сквозными тестами.


## Установка CLI (экспериментальная версия 0.5)

Пока пакет не опубликован в PyPI. Установить исходную ветку можно командой:

```bash
python -m pip install "git+https://github.com/VasiliiBabkin/sedrava-lang.git@feature/sedrava-0.5-cli-package"
```

Для изолированной установки CLI рекомендуется `pipx`, если он доступен:

```bash
pipx install "git+https://github.com/VasiliiBabkin/sedrava-lang.git@feature/sedrava-0.5-cli-package"
```

Команды после установки:

```bash
sedrava --version
sedrava check examples/workflow.sdr
sedrava test examples/workflow.sdr
sedrava build web examples/workflow.sdr --output build/web/index.html
sedrava build android examples/workflow.sdr --output build/generated-android
```

Для Android необходимы Java, Android SDK и Gradle. Имя пакета в PyPI и лицензия проекта ещё не утверждены. До проверки CI установка из GitHub также считается экспериментальной.

## Sedrava 0.6 (экспериментальная ветка)

Установка в виртуальном окружении:

```bash
python -m pip install --upgrade "git+https://github.com/VasiliiBabkin/sedrava-lang.git@feature/sedrava-0.6-quality"
sedrava --version
sedrava check workflow.sdr
sedrava test workflow.sdr
sedrava build web workflow.sdr --output index.html
```

Новые проверки сравнивают последовательности состояний интерпретатора Python и сгенерированного JavaScript через Node.js. Это проверка совместимости на примере Workflow, а не доказательство эквивалентности всех возможных программ. Для запуска полного набора тестов требуется Node.js. Артефакты предназначены для проверки перед TestPyPI; публикация в реестр не выполняется автоматически.


> Sedrava is not yet published on PyPI. Install from this source checkout using `python -m pip install .`; the CLI is `sedrava`, and source files end in `.sdr`. The GitHub repository has not yet been renamed. The domain sedrava.com is prospective only.
