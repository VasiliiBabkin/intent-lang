# Intent 0.8 development notes / Заметки о разработке

## Русский

- Ошибки синтаксиса и типов теперь сопровождаются номерами строк; неизвестные имена указываются явно.
- CLI выводит сообщения в формате `путь:строка:столбец: error: описание`. **Столбец пока всегда 1 и не является точной позицией ошибки.** Это временный формат для интеграции с редакторами; корректное вычисление столбца запланировано отдельно.
- Добавлены регрессионные тесты Web/Python на отклонённые переходы и Android/Kotlin на атомарное применение состояния и правила.
- Проверки Android сейчас анализируют текст сгенерированного Kotlin; компиляцию и исполнение на Android они не подтверждают.
- Это ветка разработки, а не новая версия пакета в PyPI.

## English

- Parser/type errors now include line numbers; unknown identifiers are named.
- CLI reports `path:line:column: error: message`, but **column is currently a placeholder of 1**, not the exact source location.
- New Web/Python rejected-transition tests and Android/Kotlin atomic-update code generation checks.
- Android tests inspect generated Kotlin; they do not compile or execute an Android APK.
- Development branch only; no PyPI release.
