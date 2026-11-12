# Визуализатор зависимостей пакетов Alpine Linux

Практическая работа №2 по дисциплине «Конфигурационное управление»,
вариант 7.

## Описание

Программа получает зависимости пакета Alpine Linux (apk) напрямую из
репозитория (файл APKINDEX) без менеджеров пакетов и сторонних библиотек.
Сейчас реализовано чтение и проверка настроек из CSV-файла.

## Настройки

Параметры задаются в файле `config.csv` (строки `ключ,значение`):

- `package_name` — имя пакета;
- `repo_url` — адрес репозитория или путь к тестовому файлу;
- `test_mode` — режим тестового репозитория (`true` / `false`);
- `version` — версия пакета;
- `ascii_tree` — выводить ли ASCII-дерево (`true` / `false`).

## Функции

- `config.py` — `load_config()` читает и проверяет настройки;
- `main.py` — точка входа программы.

## Запуск и тесты

```bash
./run.sh                 # запуск с config.csv
./run.sh <файл.csv>      # запуск с другим конфигом
./run.sh test            # тесты
```

На Windows — `run.bat`.

## Примеры

```
$ ./run.sh
package_name = curl
repo_url = https://dl-cdn.alpinelinux.org/alpine/v3.22/main/x86_64
test_mode = False
version = 8.14.1-r4
ascii_tree = True

$ ./run.sh examples/config_bad_bool.csv
Ошибка: Параметр 'test_mode' должен быть true или false, получено 'maybe'
```
