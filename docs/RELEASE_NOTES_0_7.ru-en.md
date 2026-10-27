# Intent v0.7.0a1 — First public alpha / Первая публичная альфа

## Русский

Имя пакета в основном PyPI: `intent-lng`; язык и CLI по-прежнему называются Intent. В TestPyPI пакет опубликован под прежним именем `intent-lang`.

Intent — экспериментальный декларативный язык для описания состояния приложения, действий, инвариантов и исполняемых тестов.

### Что уже работает
- Разбор ограниченного типизированного синтаксиса и интерпретация переходов состояний.
- Атомарное принятие или отклонение изменений по правилам-инвариантам.
- Встроенные тесты сценариев.
- Генерация самостоятельного HTML/JavaScript-приложения.
- Экспериментальная генерация Android/Jetpack Compose.
- CLI: `intent check`, `intent test`, `intent build web`, `intent build android`.
- CI на Linux, Windows и macOS; дифференциальные тесты Python/JavaScript для отдельных сценариев.
- Открытый исходный код под Apache License 2.0.

### Установка после публикации в основном PyPI

```bash
python -m pip install intent-lng==0.7.0a1
intent --version
```

### Ограничения
Это **альфа**, не стабильный язык: синтаксис и API могут измениться без обратной совместимости. Поддерживается небольшой набор типов, выражений и виджетов. Не доказана полная эквивалентность бэкендов; переполнение целых чисел и платформенные различия требуют отдельной проработки. Android-генератор требует SDK/Gradle для сборки. Отсутствуют гарантии пригодности для production.

### Проверки
Установка и CLI из TestPyPI подтверждены на независимом VDS; `check`, два встроенных теста и генерация HTML прошли. GitHub Actions для кандидата на выпуск прошли по сообщению владельца проекта. Публикация в основном PyPI ещё не выполнена.

## English

Intent is an experimental declarative language for application state, actions, invariants and executable tests. This alpha provides a typed interpreter, atomic transitions, embedded tests, a standalone Web backend, an experimental Android/Compose backend and a CLI. It is licensed under Apache-2.0.

Install **after** the official PyPI release:

```bash
python -m pip install intent-lng==0.7.0a1
intent --version
```

**Alpha limitations:** syntax and APIs may change; supported types, expressions and widgets are limited; full cross-backend equivalence is not established; integer portability needs further work. Not production-ready.
