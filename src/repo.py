"""Получение прямых зависимостей пакетов из репозитория Alpine Linux.

Данные берутся из индекса репозитория (файл APKINDEX.tar.gz).
"""

import io
import os
import re
import ssl
import tarfile
import urllib.error
import urllib.request

INDEX_FILE = "APKINDEX.tar.gz"
INDEX_NAME = "APKINDEX"
TIMEOUT = 30
LATEST = "latest"
SYSTEM_CA_FILE = "/etc/ssl/cert.pem"


class RepoError(Exception):
    """Ошибка получения данных из репозитория."""


def make_ssl_context():
    """Создаёт SSL-контекст с проверкой сертификатов.

    Python с python.org на macOS не видит системные сертификаты, поэтому
    дополнительно подключается системный файл /etc/ssl/cert.pem.
    """
    context = ssl.create_default_context()
    if os.path.isfile(SYSTEM_CA_FILE):
        context.load_verify_locations(SYSTEM_CA_FILE)
    return context


def download_index(repo_url):
    """Скачивает APKINDEX.tar.gz и возвращает текст файла APKINDEX."""
    url = repo_url.rstrip("/") + "/" + INDEX_FILE
    try:
        with urllib.request.urlopen(
                url, timeout=TIMEOUT, context=make_ssl_context()) as response:
            data = response.read()
    except (urllib.error.URLError, OSError, ValueError) as err:
        raise RepoError(f"Не удалось скачать {url}: {err}") from err
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            content = tar.extractfile(INDEX_NAME).read()
    except (tarfile.TarError, KeyError, AttributeError) as err:
        raise RepoError(f"Некорректный архив {url}: {err}") from err
    return content.decode("utf-8")


def parse_block(block):
    """Разбирает один блок APKINDEX в словарь вида {буква: значение}."""
    fields = {}
    for line in block.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key] = value
    return fields


def strip_version(dep):
    """Убирает из зависимости ограничение версии: 'so:x>=1' -> 'so:x'."""
    return re.split(r"[<>=~]", dep)[0]


def parse_index(text):
    """Разбирает APKINDEX.

    Возвращает два словаря: пакеты (имя -> версия и зависимости) и
    provides (виртуальное имя, например so:libc.so -> имя пакета).
    """
    packages = {}
    provides = {}
    for block in text.split("\n\n"):
        fields = parse_block(block)
        name = fields.get("P")
        if not name:
            continue
        packages[name] = {
            "version": fields.get("V", ""),
            "depends": fields.get("D", "").split(),
        }
        for item in fields.get("p", "").split():
            provides.setdefault(strip_version(item), name)
    return packages, provides


def resolve_deps(name, packages, provides):
    """Возвращает список прямых зависимостей пакета (имена пакетов)."""
    result = []
    for dep in packages.get(name, {}).get("depends", []):
        if dep.startswith("!"):
            continue
        dep_name = strip_version(dep)
        if dep_name not in packages:
            dep_name = provides.get(dep_name, dep_name)
        if dep_name != name and dep_name not in result:
            result.append(dep_name)
    return result


def check_version(packages, name, version):
    """Проверяет, что в репозитории есть пакет нужной версии."""
    if name not in packages:
        raise RepoError(f"Пакет '{name}' не найден в репозитории")
    real = packages[name]["version"]
    if version != LATEST and real != version:
        raise RepoError(
            f"Версия '{version}' пакета '{name}' не найдена, "
            f"в репозитории есть только '{real}'"
        )


def make_dep_getter(config):
    """Возвращает функцию name -> список прямых зависимостей."""
    name = config["package_name"]
    if config["test_mode"]:
        raise RepoError("Тестовый режим будет реализован на этапе 3")
    packages, provides = parse_index(download_index(config["repo_url"]))
    check_version(packages, name, config["version"])
    return lambda pkg: resolve_deps(pkg, packages, provides)
