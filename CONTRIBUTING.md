# Contributing to Intent / Участие в разработке Intent

Intent is an experimental declarative language. Contributions are welcome, but language semantics and portability must remain deliberate and testable.

## Русский

1. Сначала откройте issue с описанием проблемы или предложения. Для небольших исправлений можно сразу подготовить pull request.
2. Создайте отдельную ветку, внесите минимальные изменения и добавьте тесты.
3. Запустите `python -m unittest discover -s tests -v`. Для изменений веб-бэкенда необходим Node.js.
4. Для изменений синтаксиса опишите поведение интерпретатора и обоих генераторов (Web и Android), а также обратную совместимость.
5. Не добавляйте секреты, токены, чужой код без разрешения или зависимости с несовместимыми лицензиями.
6. Отправьте pull request с объяснением изменений, тестов и ограничений.

Отправляя вклад в проект, вы подтверждаете право предоставить его на условиях Apache License 2.0 согласно разделу 5 лицензии. Если нужны другие условия, согласуйте их до отправки.

## English

1. Open an issue for bugs or design proposals; small fixes may go directly to a pull request.
2. Work on a separate branch and add regression tests.
3. Run `python -m unittest discover -s tests -v`. Web backend changes require Node.js.
4. Syntax changes should document interpreter, Web and Android semantics and compatibility.
5. Do not commit secrets, unauthorized third-party code or incompatible dependencies.
6. Explain the change, validation and limitations in your pull request.

By submitting a contribution, you confirm you have the right to contribute it under Apache License 2.0, consistent with section 5 of the license, unless explicitly agreed otherwise.
