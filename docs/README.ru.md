# Intent — документация на русском языке

**Статус:** экспериментальный язык, не готов к промышленному использованию.

Intent описывает состояние приложения, действия, ограничения и исполняемые проверки. Один исходный файл может интерпретироваться на Python либо компилироваться в Android (Kotlin/Compose) или автономную веб-страницу (HTML/JavaScript).

## Быстрый старт

Требуется Python 3.12 или новее. Для генерации веб-страницы сторонние пакеты не нужны.

```bash
python -m unittest discover -s tests -v
python web_codegen.py examples/workflow.intent --output build/web/index.html
```

Откройте `build/web/index.html` в браузере. Для Android:

```bash
python android_codegen_v03.py examples/workflow.intent --output build/generated-android
```

Затем соберите проект с помощью Gradle и Android SDK. Готовая веб-страница не требует сервера.

## Пример

```intent
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


## Установка из PyPI — опубликованная версия 0.7.0

Пакет опубликован под именем [`intent-lng`](https://pypi.org/project/intent-lng/); команда после установки называется `intent`. Рекомендуется Python 3.10+ согласно метаданным пакета.

```bash
python -m pip install --upgrade intent-lng==0.7.0
intent --version
```

Основные команды CLI:

```bash
intent check examples/workflow.intent
intent test examples/workflow.intent
intent build web examples/workflow.intent --output build/web/index.html
intent build android examples/workflow.intent --output build/generated-android
```

Для сборки Android необходимы Java, Android SDK и Gradle. Пакет остаётся экспериментальным, даже несмотря на выпуск версии без суффикса alpha.

### Разработка 0.8/0.9 и опубликованный пакет

Конструкции `derive`, `persist`, `input` и `show` разрабатываются в ветках после версии 0.7.0. **Они не входят в опубликованный пакет 0.7.0.** Для тестирования актуальных примеров используйте исходники ветки [`feature/intent-0.9-security-integrated`](https://github.com/VasiliiBabkin/intent-lang/tree/feature/intent-0.9-security-integrated) и результаты GitHub Actions. Не путайте номер ветки разработки с версией, доступной через pip.

История первой альфы: [заметки к выпуску 0.7](RELEASE_NOTES_0_7.ru-en.md).
