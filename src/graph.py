"""Построение графа зависимостей и операции над ним."""

def build_graph(root, get_deps):
    """Строит граф зависимостей пакета root обходом в ширину (BFS).

    Граф - словарь: имя пакета -> список его прямых зависимостей.
    """
    return bfs_level([root], get_deps, {}, {root})


def bfs_level(level, get_deps, graph, visited):
    """Рекурсивный шаг BFS: обрабатывает один уровень графа.

    Пакеты из visited повторно не добавляются, поэтому циклические
    зависимости не приводят к бесконечной рекурсии.
    """
    if not level:
        return graph
    next_level = []
    for name in level:
        deps = get_deps(name)
        graph[name] = deps
        for dep in deps:
            if dep not in visited:
                visited.add(dep)
                next_level.append(dep)
    return bfs_level(next_level, get_deps, graph, visited)