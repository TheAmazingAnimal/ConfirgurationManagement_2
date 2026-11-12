"""Тесты построения графа и порядка загрузки."""

import unittest

from graph import build_graph, load_order

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

    def test_load_order(self):
        """Зависимости идут раньше пакетов, которые от них зависят."""
        order, cycles = load_order(SIMPLE, "A")
        self.assertEqual(order, ["D", "B", "C", "A"])
        self.assertEqual(cycles, [])

    def test_load_order_cycle(self):
        """Цикл обнаруживается, порядок всё равно строится."""
        order, cycles = load_order(CYCLE, "A")
        self.assertEqual(order, ["C", "B", "A"])
        self.assertEqual(cycles, [("C", "A")])


if __name__ == "__main__":
    unittest.main()
