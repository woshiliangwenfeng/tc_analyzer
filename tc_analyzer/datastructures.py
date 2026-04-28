# tc_analyzer/datastructures.py
"""Data structure operation complexity mappings."""
import ast

DS_COMPLEXITY = {
    # List operations
    ('list', 'append'): 'O(1)',
    ('list', 'extend'): 'O(k)',  # k is number of items added
    ('list', 'insert'): 'O(n)',
    ('list', 'remove'): 'O(n)',
    ('list', 'pop'): 'O(1)',       # default (end)
    ('list', 'pop', '0'): 'O(n)',  # pop from beginning
    ('list', 'clear'): 'O(1)',
    ('list', 'index'): 'O(n)',
    ('list', 'count'): 'O(n)',
    ('list', 'sort'): 'O(n log n)',
    ('list', 'reverse'): 'O(n)',
    ('list', 'copy'): 'O(n)',
    ('list', '__getitem__'): 'O(1)',
    ('list', '__setitem__'): 'O(1)',
    ('list', '__contains__'): 'O(n)',  # in operator

    # Dict operations
    ('dict', 'get'): 'O(1)',
    ('dict', 'setdefault'): 'O(1)',
    ('dict', 'pop'): 'O(1)',
    ('dict', 'popitem'): 'O(1)',
    ('dict', 'clear'): 'O(1)',
    ('dict', 'update'): 'O(k)',
    ('dict', 'copy'): 'O(n)',
    ('dict', 'keys'): 'O(1)',
    ('dict', 'values'): 'O(1)',
    ('dict', 'items'): 'O(1)',
    ('dict', '__getitem__'): 'O(1)',
    ('dict', '__setitem__'): 'O(1)',
    ('dict', '__contains__'): 'O(1)',  # in operator

    # Set operations
    ('set', 'add'): 'O(1)',
    ('set', 'remove'): 'O(1)',
    ('set', 'discard'): 'O(1)',
    ('set', 'pop'): 'O(1)',
    ('set', 'clear'): 'O(1)',
    ('set', 'copy'): 'O(n)',
    ('set', 'union'): 'O(n)',
    ('set', 'intersection'): 'O(n)',
    ('set', 'difference'): 'O(n)',
    ('set', '__contains__'): 'O(1)',  # in operator

    # String operations
    ('str', 'join'): 'O(n)',
    ('str', 'split'): 'O(n)',
    ('str', 'find'): 'O(n)',
    ('str', 'replace'): 'O(n)',
    ('str', '__contains__'): 'O(n)',  # substring search
}

def get_ds_complexity(obj_type: str, method: str, arg_hint: str = None) -> str:
    """Get complexity for data structure operation."""
    if arg_hint:
        key = (obj_type, method, arg_hint)
        if key in DS_COMPLEXITY:
            return DS_COMPLEXITY[key]
    key = (obj_type, method)
    return DS_COMPLEXITY.get(key, 'O(1)')

def detect_ds_operation(call_node):
    """Detect data structure operation from AST call node."""
    if isinstance(call_node.func, ast.Attribute):
        obj = call_node.func.value
        method = call_node.func.attr

        # Try to infer type from variable name
        obj_type = _infer_type_from_name(obj)
        if obj_type:
            return get_ds_complexity(obj_type, method)

    return None

def _infer_type_from_name(node):
    """Try to infer data structure type from variable name."""
    if isinstance(node, ast.Name):
        name = node.id.lower()
        if name in ('lst', 'list', 'arr', 'array', 'items', 'data'):
            return 'list'
        elif name in ('d', 'dict', 'mapping', 'map', 'dictionary'):
            return 'dict'
        elif name in ('s', 'set', 'unique'):
            return 'set'
        elif name in ('str', 'string', 'text'):
            return 'str'
    return None