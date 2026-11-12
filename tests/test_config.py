"""Тесты чтения и проверки конфигурации."""

import os
import tempfile
import unittest

from config import ConfigError, load_config

GOOD_CONFIG = """parameter,value
package_name,A
repo_url,{repo}
test_mode,true
version,1.0
ascii_tree,false
"""


class ConfigTest(unittest.TestCase):
    """Проверка load_config на корректных и ошибочных файлах."""

    def setUp(self):
        """Создаёт временную папку с тестовым репозиторием."""
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "repo.txt")
        with open(self.repo, "w", encoding="utf-8") as file:
            file.write("A: B\n")

    def tearDown(self):
        """Удаляет временную папку."""
        self.tmp.cleanup()

    def write(self, text):
        """Записывает текст во временный CSV и возвращает путь к нему."""
        path = os.path.join(self.tmp.name, "config.csv")
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        return path

    def test_good_config(self):
        """Корректный файл читается, булевы значения преобразуются."""
        config = load_config(self.write(GOOD_CONFIG.format(repo=self.repo)))
        self.assertEqual(config["package_name"], "A")
        self.assertTrue(config["test_mode"])
        self.assertFalse(config["ascii_tree"])

    def test_missing_file(self):
        """Отсутствующий файл конфигурации - ошибка."""
        with self.assertRaises(ConfigError):
            load_config("no_such_file.csv")

    def test_bad_bool(self):
        """Неверное булево значение - ошибка."""
        text = GOOD_CONFIG.format(repo=self.repo).replace(
            "ascii_tree,false", "ascii_tree,maybe")
        with self.assertRaises(ConfigError):
            load_config(self.write(text))

    def test_missing_param(self):
        """Отсутствующий параметр - ошибка."""
        text = GOOD_CONFIG.format(repo=self.repo).replace("version,1.0\n", "")
        with self.assertRaises(ConfigError):
            load_config(self.write(text))

    def test_unknown_param(self):
        """Лишний параметр - ошибка."""
        text = GOOD_CONFIG.format(repo=self.repo) + "color,red\n"
        with self.assertRaises(ConfigError):
            load_config(self.write(text))

    def test_bad_url(self):
        """В обычном режиме URL должен начинаться с http(s)://."""
        text = GOOD_CONFIG.format(repo="ftp://x").replace(
            "test_mode,true", "test_mode,false")
        with self.assertRaises(ConfigError):
            load_config(self.write(text))

    def test_missing_test_repo(self):
        """В тестовом режиме файл репозитория должен существовать."""
        text = GOOD_CONFIG.format(repo="nothing.txt")
        with self.assertRaises(ConfigError):
            load_config(self.write(text))

    def test_bad_package_name(self):
        """Имя пакета с пробелами и спецсимволами - ошибка."""
        text = GOOD_CONFIG.format(repo=self.repo).replace(
            "package_name,A", "package_name,bad name!")
        with self.assertRaises(ConfigError):
            load_config(self.write(text))


if __name__ == "__main__":
    unittest.main()
