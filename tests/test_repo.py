"""Тесты разбора APKINDEX и тестового репозитория."""

import unittest

from repo import RepoError, check_version, parse_index, resolve_deps

INDEX = """C:Q1abc=
P:curl
V:8.14.1-r4
D:ca-certificates so:libcurl.so.4 so:libc.musl-x86_64.so.1 !curl-old

P:libcurl
V:8.14.1-r4
D:so:libc.musl-x86_64.so.1 zlib>=1.2
p:so:libcurl.so.4=4.8.0

P:musl
V:1.2.5-r10
p:so:libc.musl-x86_64.so.1=1

P:zlib
V:1.3.1-r2
"""


class RepoTest(unittest.TestCase):
    """Проверка функций модуля repo."""

    def setUp(self):
        """Разбирает пример APKINDEX."""
        self.packages, self.provides = parse_index(INDEX)

    def test_parse(self):
        """Все пакеты и версии прочитаны."""
        self.assertEqual(set(self.packages),
                         {"curl", "libcurl", "musl", "zlib"})
        self.assertEqual(self.packages["curl"]["version"], "8.14.1-r4")

    def test_resolve(self):
        """so:-зависимости заменяются пакетами, конфликты (!) пропускаются."""
        deps = resolve_deps("curl", self.packages, self.provides)
        self.assertEqual(deps, ["ca-certificates", "libcurl", "musl"])
        deps = resolve_deps("libcurl", self.packages, self.provides)
        self.assertEqual(deps, ["musl", "zlib"])

    def test_check_version(self):
        """Неверная версия или неизвестный пакет - ошибка."""
        check_version(self.packages, "curl", "8.14.1-r4")
        check_version(self.packages, "curl", "latest")
        with self.assertRaises(RepoError):
            check_version(self.packages, "curl", "1.0")
        with self.assertRaises(RepoError):
            check_version(self.packages, "wget", "latest")


if __name__ == "__main__":
    unittest.main()
