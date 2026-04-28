# tests/test_builtins.py
from tc_analyzer import analyze

def test_sorted_builtin():
    code = '''
def sort_list(arr):
    return sorted(arr)
'''
    result = analyze(code)
    assert 'O(n log n)' in result.functions[0].complexity.overall

def test_len_builtin():
    code = '''
def get_length(lst):
    return len(lst)
'''
    result = analyze(code)
    assert result.functions[0].complexity.overall == 'O(1)'

def test_max_builtin():
    code = '''
def find_max(lst):
    return max(lst)
'''
    result = analyze(code)
    assert 'O(n)' in result.functions[0].complexity.overall

def test_builtin_in_loop():
    code = '''
def process(arr):
    for x in arr:
        sorted(x)
'''
    result = analyze(code)
    assert 'O(n log n)' in result.functions[0].complexity.overall