# tests/test_analyzer.py
from tc_analyzer import analyze

def test_analyze_string_input():
    code = '''
def foo(n):
    for i in range(n):
        print(i)
'''
    result = analyze(code)
    assert result is not None
    assert len(result.functions) == 1
    assert result.functions[0].name == 'foo'

def test_analyze_detects_loop():
    code = '''
def foo(n):
    for i in range(n):
        print(i)
'''
    result = analyze(code)
    assert result.functions[0].loops == 1
    assert 'O(n)' in result.functions[0].complexity.overall

def test_analyze_nested_loops():
    code = '''
def bar(n):
    for i in range(n):
        for j in range(n):
            print(i, j)
'''
    result = analyze(code)
    assert result.functions[0].loops == 2
    assert 'O(n^2)' in result.functions[0].complexity.overall