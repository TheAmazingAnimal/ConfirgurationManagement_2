"""CLI-инструмент визуализации графа зависимостей пакетов Alpine Linux."""

import argparse
import os
import sys

from config import ConfigError, load_config

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_args(argv):
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей пакетов Alpine (apk)"
    )
    parser.add_argument("config", nargs="?", default="config.csv",
                        help="путь к конфигурационному CSV-файлу")
    return parser.parse_args(argv)


def print_config(config):
    """Выводит параметры конфигурации в формате ключ-значение."""
    for key, value in config.items():
        print(f"{key} = {value}")


def run(args):
    """Выполняет программу по аргументам, возвращает код завершения."""
    config = load_config(args.config)
    print_config(config)
    return 0


def main(argv=None):
    """Точка входа: обрабатывает ошибки и печатает их понятным текстом.

    Рабочая папка меняется на корень проекта, чтобы относительные пути
    (config.csv, examples/) работали при любом способе запуска.
    """
    os.chdir(PROJECT_DIR)
    args = parse_args(argv)
    try:
        return run(args)
    except ConfigError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
