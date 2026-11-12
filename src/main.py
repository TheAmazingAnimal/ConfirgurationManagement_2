"""CLI-инструмент визуализации графа зависимостей пакетов Alpine Linux."""

import argparse
import os
import sys

from config import ConfigError, load_config
from graph import build_graph, load_order
from repo import RepoError, make_dep_getter

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_args(argv):
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей пакетов Alpine (apk)"
    )
    parser.add_argument("config", nargs="?", default="config.csv",
                        help="путь к конфигурационному CSV-файлу")
    parser.add_argument("--show-config", action="store_true",
                        help="вывести параметры конфигурации (этап 1)")
    parser.add_argument("--direct", action="store_true",
                        help="вывести только прямые зависимости (этап 2)")
    parser.add_argument("--order", action="store_true",
                        help="вывести порядок загрузки зависимостей (этап 4)")
    return parser.parse_args(argv)


def print_config(config):
    """Выводит параметры конфигурации в формате ключ-значение."""
    for key, value in config.items():
        print(f"{key} = {value}")


def print_direct(root, get_deps):
    """Выводит прямые зависимости пакета root."""
    print(f"Прямые зависимости {root}:")
    for dep in get_deps(root):
        print(f"  {dep}")


def print_graph(graph):
    """Выводит граф: каждый пакет и список его прямых зависимостей."""
    print("Граф зависимостей:")
    for name, deps in graph.items():
        print(f"  {name}: {' '.join(deps)}")


def print_order(graph, root):
    """Выводит порядок загрузки зависимостей и найденные циклы."""
    order, cycles = load_order(graph, root)
    print("Порядок загрузки:")
    for number, name in enumerate(order, start=1):
        print(f"{number}. {name}")
    for name, dep in cycles:
        print(f"Обнаружен цикл: {name} -> {dep} (ребро пропущено)")


def run(args):
    """Выполняет программу по аргументам, возвращает код завершения."""
    config = load_config(args.config)
    if args.show_config:
        print_config(config)
        return 0
    root = config["package_name"]
    get_deps = make_dep_getter(config)
    if args.direct:
        print_direct(root, get_deps)
        return 0
    graph = build_graph(root, get_deps)
    if args.order:
        print_order(graph, root)
        return 0
    print_graph(graph)
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
    except (ConfigError, RepoError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
