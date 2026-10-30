# Переход на 0.10.0rc1 и откат (RC не опубликован)

Имя дистрибутива и команды — **sedrava**. Опубликованная база — [GitHub v0.9.0a1](https://github.com/VasiliiBabkin/sedrava/releases/tag/v0.9.0a1), версия пакета `0.9.0a1`. Это не установка `sedrava==0.9` из PyPI; исторический `intent-lng` не является заменой. Комплект RC сейчас подготавливается как Actions artifact, не как релиз PyPI/TestPyPI.

1. Сохраните старое окружение. Запишите путь интерпретатора, вывод `python -m pip show sedrava` и `sedrava --version`. Отдельно скопируйте `.sdr`, нужные сгенерированные файлы и сохранённые данные. RC проверяйте на копиях проектов; автоматической миграции нет.
2. Скачайте комплект точного проверенного SHA, проверьте внешний digest артефакта и внутренние файлы по [процедуре](RC_PUBLISHING.md). Сохраните исходный комплект и SHA256SUMS для диагностики и отката.
3. Создайте **другое** виртуальное окружение и установите проверенный wheel:

```sh
python -m venv .venv-sedrava-rc1
. .venv-sedrava-rc1/bin/activate
python -m pip install --no-index /absolute/path/to/verified-kit/sedrava-0.10.0rc1-py3-none-any.whl
sedrava --version
python -m pip show sedrava
sedrava check /path/to/copied/project.sdr
sedrava test /path/to/copied/project.sdr
sedrava run /path/to/copied/project.sdr
sedrava build web /path/to/copied/project.sdr --output build/rc-web/index.html
sedrava build android /path/to/copied/project.sdr --output build/rc-android
```

4. Проверьте также `reference_09.sdr`, `text_profile.sdr`, `task_manager.sdr` и `task_manager_navigation.sdr` из `sys.prefix/share/sedrava/examples`. Выполните реальные сценарии Web/Android до использования важных данных. [Заметки RC](RELEASE_NOTES_0_10_0rc1.ru.md).
5. Откат — выход из RC-окружения и активация прежнего. Для Windows используйте `ENV\Scripts\activate`, для POSIX — `ENV/bin/activate`.

```sh
deactivate
. /absolute/path/to/original-09-environment/bin/activate
sedrava --version
# Ожидается: sedrava 0.9.0a1
sedrava check /path/to/original-09-project.sdr
sedrava test /path/to/original-09-project.sdr
```

Если прежнее окружение потеряно, создайте новое и установите проверенный historical wheel из GitHub Release. Его реальное имя — `sedrava-0.9.0a1-py3-none-any.whl`, SHA-256 **b6e3a54df2355803fa1e47b5e7e849ba242bfd6437f226534db13aabc4210339**. Скачайте release `SHA256SUMS`, сверьте wheel перед `pip install --no-index /path/to/that-wheel`. Скрипт `scripts/check_upgrade_rollback.py` действительно скачивает этот опубликованный wheel, проверяет хеш/список файлов, выполняет check/test/run/Web/Android в двух отдельных окружениях вне репозитория, сравнивает результат действия 0.9 и возвращается к неизменённому старому окружению. Исходный проект сохраняется побайтно. Установка из вымышленного имени пакета/версии не используется.

## Данные и границы обновления Android

0.9 не понимает новые строки/записи/навигацию. Возврат интерпретатора не переводит проект в старый синтаксис. Сохраните исходные проекты в системе контроля версий. Не передавайте новые снимки коллекций старой версии и не перезаписывайте единственную исходную копию данных. Несовместимая схема/сигнатура отвергается целиком; автоматической миграции/понижения данных нет. Регрессия подтверждает поддержанные 0.9-программы, а не любой сторонний формат хранения.

При обновлении Android нужны прежние application ID и сертификат подписи; Android также проверяет versionCode. Старые генераторы 0.9 использовали `org.sedrava.generated`, текущие default ID зависят от точного названия. Явный `--application-id org.sedrava.generated` допустим только для того же старого приложения с прежним ключом и совместимой схемой. Другой ID создаёт отдельное приложение. Debug-ключи разных машин/CI jobs могут различаться. Не используйте удаление/очистку данных как способ обновления: это удаляет данные. Код RC — 10001; Android может отказать установке старого code 1 поверх него. Храните старый APK и данные отдельно; `adb install -d` не гарантирует безопасное понижение формата. В комплекте нет production-инструмента резервного копирования/миграции.

Эмулятор проверяет настоящее обновление с main `2ff3994dd503d453c2fc81c133cc1c95a9c3d3b1` (`0.10.0.dev0`, code 1) на RC (10001), подписанных одним тестовым ключом: задача создана через UI, её ID и данные сохраняются. Это не проверка обновления поверх опубликованного 0.9 APK с другим debug-ключом и не миграция произвольной схемы. В Web хранилище зависит от URL-пути и названия; их изменение не переносит данные автоматически.

[English](UPGRADE_0_10_0rc1.en.md).
