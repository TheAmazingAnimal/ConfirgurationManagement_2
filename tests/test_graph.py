"""Тесты построения графа зависимостей."""

import unittest

from graph import build_graph

SIMPLE = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A"]}


class GraphTest(unittest.TestCase):
    """Проверка функций модуля graph."""

    def test_build_simple(self):
        """BFS находит все транзитивные зависимости."""
        graph = build_graph("A", lambda name: SIMPLE.get(name, []))
        self.assertEqual(set(graph), {"A", "B", "C", "D"})
        self.assertEqual(list(graph), ["A", "B", "C", "D"])

    def test_build_cycle(self):
        """Цикл не приводит к зависанию, каждый пакет ровно один раз."""
        graph = build_graph("A", lambda name: CYCLE.get(name, []))
        self.assertEqual(graph, CYCLE)

    def test_build_from_middle(self):
        """Граф строится только из достижимых пакетов."""
        graph = build_graph("B", lambda name: SIMPLE.get(name, []))
        self.assertEqual(set(graph), {"B", "D"})


if __name__ == "__main__":
    unittest.main()
