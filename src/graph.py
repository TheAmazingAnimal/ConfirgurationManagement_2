"""Построение графа зависимостей и операции над ним."""

IN_PROGRESS = "in_progress"
DONE = "done"


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


def load_order(graph, root):
    """Возвращает порядок загрузки (сначала зависимости) и найденные циклы.

    Используется обход в глубину: пакет добавляется в список только
    после всех своих зависимостей. Ребро, ведущее в пакет, который
    ещё обрабатывается, означает цикл - оно запоминается и пропускается.
    """
    order = []
    cycles = []
    state = {}

    def visit(name):
        """Обходит пакет name и его зависимости."""
        state[name] = IN_PROGRESS
        for dep in graph.get(name, []):
            if state.get(dep) == IN_PROGRESS:
                cycles.append((name, dep))
            elif dep not in state:
                visit(dep)
        state[name] = DONE
        order.append(name)

    visit(root)
    return order, cycles


def to_dot(graph, root):
    """Возвращает описание графа на языке Graphviz (DOT)."""
    lines = ["digraph dependencies {", "    rankdir=LR;"]
    lines.append(f'    "{root}" [style=filled, fillcolor=lightblue];')
    for name, deps in graph.items():
        if not deps:
            lines.append(f'    "{name}";')
        for dep in deps:
            lines.append(f'    "{name}" -> "{dep}";')
    lines.append("}")
    return "\n".join(lines)


def ascii_tree(graph, root):
    """Возвращает зависимости в виде ASCII-дерева (строка)."""
    lines = [root]
    add_children(graph, root, "", lines, {root}, [root])
    return "\n".join(lines)


def add_children(graph, name, prefix, lines, shown, path):
    """Рекурсивно добавляет в lines строки для зависимостей пакета name.

    Пакет, который уже был выведен раньше, помечается (*) и не
    раскрывается повторно. Возврат к пакету из текущего пути - (цикл).
    """
    deps = graph.get(name, [])
    for index, dep in enumerate(deps):
        is_last = index == len(deps) - 1
        branch = "└── " if is_last else "├── "
        if dep in path:
            lines.append(prefix + branch + dep + " (цикл)")
        elif dep in shown:
            lines.append(prefix + branch + dep + " (*)")
        else:
            lines.append(prefix + branch + dep)
            shown.add(dep)
            child_prefix = prefix + ("    " if is_last else "│   ")
            add_children(graph, dep, child_prefix, lines, shown, path + [dep])
