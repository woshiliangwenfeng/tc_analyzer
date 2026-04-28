# tc_analyzer/patterns.py
"""Algorithm pattern recognition."""
import ast

ALGORITHM_PATTERNS = {
    'sorting': {
        'names': ['sort', 'quick_sort', 'merge_sort', 'heap_sort', 'bubble_sort',
                  'insertion_sort', 'selection_sort', 'radix_sort', 'bucket_sort'],
        'keywords': ['partition', 'pivot', 'merge', 'heap', 'swap', 'compare'],
    },
    'search': {
        'names': ['search', 'binary_search', 'linear_search', 'find', 'lookup',
                  'dfs', 'bfs', 'depth_first', 'breadth_first'],
        'keywords': ['mid', 'binary', 'target', 'found', 'search'],
    },
    'dp': {
        'names': ['dp', 'dynamic', 'memo', 'memoize', 'fibonacci', 'fib'],
        'keywords': ['memo', 'cache', 'dp', 'table', 'state'],
    },
    'graph': {
        'names': ['dfs', 'bfs', 'topological', 'shortest', 'dijkstra', 'bellman',
                  'floyd', 'kruskal', 'prim'],
        'keywords': ['graph', 'node', 'edge', 'vertex', 'path', 'visited'],
    },
}

def detect_algorithm_type(node):
    """Detect algorithm type from function."""
    func_name = node.name.lower()

    # Check by name
    for algo_type, patterns in ALGORITHM_PATTERNS.items():
        if any(name in func_name for name in patterns['names']):
            return algo_type

    # Check by keywords in function body
    keywords_found = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            keywords_found.add(child.id.lower())
        elif isinstance(child, ast.Constant) and isinstance(child.value, str):
            keywords_found.add(child.value.lower())

    for algo_type, patterns in ALGORITHM_PATTERNS.items():
        if any(kw in keywords_found for kw in patterns['keywords']):
            return algo_type

    return 'unknown'