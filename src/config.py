"""Чтение и проверка конфигурационного файла в формате CSV."""

import csv
import os
import re

REQUIRED_KEYS = (
    "package_name",
    "repo_url",
    "test_mode",
    "version",
    "ascii_tree",
)
HEADER_KEY = "parameter"
ROW_SIZE = 2
TRUE_VALUES = ("true", "yes", "1")
FALSE_VALUES = ("false", "no", "0")
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
VERSION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
URL_PREFIXES = ("http://", "https://")


class ConfigError(Exception):
    """Ошибка в конфигурационном файле."""


def read_csv(path):
    """Читает пары ключ-значение из CSV-файла и возвращает словарь."""
    if not os.path.isfile(path):
        raise ConfigError(f"Файл конфигурации не найден: {path}")
    params = {}
    with open(path, encoding="utf-8", newline="") as file:
        for line_no, row in enumerate(csv.reader(file), start=1):
            if not row or row[0].strip().startswith("#"):
                continue
            if len(row) != ROW_SIZE:
                raise ConfigError(
                    f"Строка {line_no}: ожидалось 2 поля (ключ,значение), "
                    f"получено {len(row)}"
                )
            key, value = row[0].strip(), row[1].strip()
            if key == HEADER_KEY:
                continue
            if key in params:
                raise ConfigError(f"Параметр '{key}' указан дважды")
            params[key] = value
    return params


def parse_bool(key, value):
    """Преобразует строку в bool или выбрасывает ConfigError."""
    text = value.lower()
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    raise ConfigError(
        f"Параметр '{key}' должен быть true или false, получено '{value}'"
    )


def check_keys(params):
    """Проверяет, что заданы все нужные параметры и нет лишних."""
    unknown = [key for key in params if key not in REQUIRED_KEYS]
    if unknown:
        raise ConfigError("Неизвестные параметры: " + ", ".join(unknown))
    missing = [key for key in REQUIRED_KEYS if key not in params]
    if missing:
        raise ConfigError("Не заданы параметры: " + ", ".join(missing))
    empty = [key for key in REQUIRED_KEYS if not params[key]]
    if empty:
        raise ConfigError("Пустые значения параметров: " + ", ".join(empty))


def check_repo(repo, test_mode):
    """Проверяет URL репозитория или путь к тестовому файлу."""
    if test_mode:
        if not os.path.isfile(repo):
            raise ConfigError(f"Файл тестового репозитория не найден: {repo}")
    elif not repo.startswith(URL_PREFIXES):
        raise ConfigError(
            f"repo_url должен начинаться с http:// или https://: {repo}"
        )


def load_config(path):
    """Читает и проверяет конфигурацию, возвращает словарь параметров."""
    params = read_csv(path)
    check_keys(params)
    if not NAME_PATTERN.match(params["package_name"]):
        raise ConfigError(
            f"Некорректное имя пакета: '{params['package_name']}'"
        )
    if not VERSION_PATTERN.match(params["version"]):
        raise ConfigError(f"Некорректная версия: '{params['version']}'")
    test_mode = parse_bool("test_mode", params["test_mode"])
    check_repo(params["repo_url"], test_mode)
    return {
        "package_name": params["package_name"],
        "repo_url": params["repo_url"],
        "test_mode": test_mode,
        "version": params["version"],
        "ascii_tree": parse_bool("ascii_tree", params["ascii_tree"]),
    }
