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

    def make_files(self, repo=None):
        """Создаёт временную папку с тестовым репозиторием.

        Возвращает текст корректного конфига и функцию для записи CSV.
        Папка удаляется автоматически после теста.
        """
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo_path = os.path.join(tmp.name, "repo.txt")
        with open(repo_path, "w", encoding="utf-8") as file:
            file.write("A: B\n")

        def write(text):
            """Записывает текст во временный CSV и возвращает путь к нему."""
            path = os.path.join(tmp.name, "config.csv")
            with open(path, "w", encoding="utf-8") as file:
                file.write(text)
            return path

        return GOOD_CONFIG.format(repo=repo or repo_path), write

    def test_good_config(self):
        """Корректный файл читается, булевы значения преобразуются."""
        text, write = self.make_files()
        config = load_config(write(text))
        self.assertEqual(config["package_name"], "A")
        self.assertTrue(config["test_mode"])
        self.assertFalse(config["ascii_tree"])

    def test_missing_file(self):
        """Отсутствующий файл конфигурации - ошибка."""
        with self.assertRaises(ConfigError):
            load_config("no_such_file.csv")

    def test_bad_bool(self):
        """Неверное булево значение - ошибка."""
        text, write = self.make_files()
        text = text.replace("ascii_tree,false", "ascii_tree,maybe")
        with self.assertRaises(ConfigError):
            load_config(write(text))

    def test_missing_param(self):
        """Отсутствующий параметр - ошибка."""
        text, write = self.make_files()
        text = text.replace("version,1.0\n", "")
        with self.assertRaises(ConfigError):
            load_config(write(text))

    def test_unknown_param(self):
        """Лишний параметр - ошибка."""
        text, write = self.make_files()
        text += "color,red\n"
        with self.assertRaises(ConfigError):
            load_config(write(text))

    def test_bad_url(self):
        """В обычном режиме URL должен начинаться с http(s)://."""
        text, write = self.make_files(repo="ftp://x")
        text = text.replace("test_mode,true", "test_mode,false")
        with self.assertRaises(ConfigError):
            load_config(write(text))

    def test_missing_test_repo(self):
        """В тестовом режиме файл репозитория должен существовать."""
        text, write = self.make_files(repo="nothing.txt")
        with self.assertRaises(ConfigError):
            load_config(write(text))

    def test_bad_package_name(self):
        """Имя пакета с пробелами и спецсимволами - ошибка."""
        text, write = self.make_files()
        text = text.replace("package_name,A", "package_name,bad name!")
        with self.assertRaises(ConfigError):
            load_config(write(text))


if __name__ == "__main__":
    unittest.main()
