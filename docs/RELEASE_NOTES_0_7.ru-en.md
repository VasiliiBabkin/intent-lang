# Intent 0.7 — история выпусков / Release history

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

### Установка опубликованной версии 0.7.0 из PyPI

```bash
python -m pip install intent-lng==0.7.0
intent --version
```

### Ограничения
Это **альфа**, не стабильный язык: синтаксис и API могут измениться без обратной совместимости. Поддерживается небольшой набор типов, выражений и виджетов. Не доказана полная эквивалентность бэкендов; переполнение целых чисел и платформенные различия требуют отдельной проработки. Android-генератор требует SDK/Gradle для сборки. Отсутствуют гарантии пригодности для production.

### Проверки
Установка и CLI из TestPyPI подтверждены на независимом VDS; `check`, два встроенных теста и генерация HTML прошли. GitHub Actions для кандидата на выпуск прошли по сообщению владельца проекта. Версия 0.7.0 опубликована в основном PyPI. Ранее проверенная версия 0.7.0a1 была предварительным выпуском. Новые возможности веток 0.8/0.9 не включены в 0.7.0.

## English

Intent is an experimental declarative language for application state, actions, invariants and executable tests. This alpha provides a typed interpreter, atomic transitions, embedded tests, a standalone Web backend, an experimental Android/Compose backend and a CLI. It is licensed under Apache-2.0.

Install the **published 0.7.0 release** from PyPI:

```bash
python -m pip install intent-lng==0.7.0a1
intent --version
```

**Release limitations:** syntax and APIs may change; supported types, expressions and widgets are limited; full cross-backend equivalence is not established; integer portability needs further work. Not production-ready. The earlier 0.7.0a1 alpha preceded 0.7.0; later 0.8/0.9 development features are not part of the published 0.7.0 package.
