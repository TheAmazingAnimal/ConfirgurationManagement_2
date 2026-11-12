"""CLI-инструмент визуализации графа зависимостей пакетов Alpine Linux."""

import argparse
import os
import shutil
import subprocess
import sys

from config import ConfigError, load_config
from graph import ascii_tree, build_graph, load_order, to_dot
from repo import RepoError, make_dep_getter

OUTPUT_DIR = "output"
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
    parser.add_argument("--no-image", action="store_true",
                        help="не строить и не открывать изображение графа")
    return parser.parse_args(argv)


def print_config(config):
    """Выводит параметры конфигурации в формате ключ-значение."""
    for key, value in config.items():
        print(f"{key} = {value}")


def show_image(dot_text, name):
    """Сохраняет граф в .dot, рисует .png через Graphviz и открывает его."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dot_path = os.path.join(OUTPUT_DIR, name + ".dot")
    png_path = os.path.join(OUTPUT_DIR, name + ".png")
    with open(dot_path, "w", encoding="utf-8") as file:
        file.write(dot_text + "\n")
    print(f"\nDOT-файл сохранён: {dot_path}")
    if shutil.which("dot") is None:
        print("Graphviz (команда dot) не установлен, изображение не создано.")
        return
    subprocess.run(["dot", "-Tpng", dot_path, "-o", png_path], check=True)
    print(f"Изображение сохранено: {png_path}")
    if sys.platform == "darwin":
        subprocess.run(["open", png_path], check=False)
    elif sys.platform == "win32":
        os.startfile(png_path)
    else:
        subprocess.run(["xdg-open", png_path], check=False)


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
        print(f"Прямые зависимости {root}:")
        for dep in get_deps(root):
            print(f"  {dep}")
        return 0
    graph = build_graph(root, get_deps)
    if args.order:
        print_order(graph, root)
        return 0
    dot_text = to_dot(graph, root)
    print(dot_text)
    if config["ascii_tree"]:
        print("\n" + ascii_tree(graph, root))
    if not args.no_image:
        show_image(dot_text, root)
    return 0


def main(argv=None):
    """Точка входа: обрабатывает ошибки и печатает их понятным текстом.

    Рабочая папка меняется на корень проекта, чтобы относительные пути
    (config.csv, examples/, output/) работали при любом способе запуска.
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
