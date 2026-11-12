# Визуализатор зависимостей пакетов Alpine Linux

Практическая работа №2 по дисциплине «Конфигурационное управление»,
вариант 7.

## Описание

Программа получает зависимости пакета Alpine Linux (apk) напрямую из
репозитория (файл APKINDEX) без менеджеров пакетов и сторонних библиотек.
Сейчас программа строит полный граф зависимостей с учётом транзитивности и циклов.

## Настройки

Параметры задаются в файле `config.csv` (строки `ключ,значение`):

- `package_name` — имя пакета;
- `repo_url` — адрес репозитория или путь к тестовому файлу;
- `test_mode` — режим тестового репозитория (`true` / `false`);
- `version` — версия пакета;
- `ascii_tree` — выводить ли ASCII-дерево (`true` / `false`).

Флаги запуска:

- `--show-config` — вывести параметры конфигурации;
- `--direct` — вывести только прямые зависимости;

Тестовый репозиторий — текстовый файл, где пакеты обозначены большими
латинскими буквами, например `A: B C` (примеры в папке `examples/`).

## Функции

- `config.py` — `load_config()` читает и проверяет настройки;
- `repo.py` — `download_index()` скачивает APKINDEX, `parse_index()` разбирает его, `resolve_deps()` находит прямые зависимости;
- `repo.py` — `load_test_repo()` читает тестовый репозиторий;
- `graph.py` — `build_graph()` строит граф алгоритмом BFS с рекурсией;
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
$ ./run.sh --show-config
package_name = curl
repo_url = https://dl-cdn.alpinelinux.org/alpine/v3.22/main/x86_64
test_mode = False
version = 8.14.1-r4
ascii_tree = True

$ ./run.sh examples/config_bad_bool.csv
Ошибка: Параметр 'test_mode' должен быть true или false, получено 'maybe'
```

```
$ ./run.sh --direct
Прямые зависимости curl:
  libcurl
  musl
  zlib
```

```
$ ./run.sh examples/config_cycle.csv
Граф зависимостей:
  A: B
  B: C
  C: A D
  D:
```
