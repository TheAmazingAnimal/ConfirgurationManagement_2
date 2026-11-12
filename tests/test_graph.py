"""Тесты построения графа, порядка загрузки и визуализации."""

import unittest

from graph import ascii_tree, build_graph, load_order, to_dot

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

    def test_dot(self):
        """DOT содержит все рёбра графа."""
        text = to_dot(SIMPLE, "A")
        self.assertTrue(text.startswith("digraph"))
        self.assertIn('"A" -> "B";', text)
        self.assertIn('"C" -> "D";', text)

    def test_ascii_tree(self):
        """Повторный пакет помечается (*), цикл - (цикл)."""
        self.assertEqual(
            ascii_tree(SIMPLE, "A"),
            "A\n├── B\n│   └── D\n└── C\n    └── D (*)",
        )
        self.assertIn("A (цикл)", ascii_tree(CYCLE, "A"))


if __name__ == "__main__":
    unittest.main()
