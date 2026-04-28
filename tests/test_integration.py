# tests/test_integration.py
from tc_analyzer import analyze
import tempfile
import os

def test_full_analysis():
    code = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''
    result = analyze(code)
    assert len(result.functions) == 3

    bubble = next(f for f in result.functions if f.name == 'bubble_sort')
    assert 'O(n^2)' in bubble.complexity.overall
    assert bubble.algorithm_type == 'sorting'

    search = next(f for f in result.functions if f.name == 'linear_search')
    assert 'O(n)' in search.complexity.overall
    assert search.algorithm_type == 'search'

    fact = next(f for f in result.functions if f.name == 'factorial')
    assert fact.recursion == True

def test_file_analysis():
    code = '''
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = analyze(temp_path)
        assert len(result.functions) == 1
        assert result.functions[0].name == 'merge_sort'
    finally:
        os.unlink(temp_path)

def test_target_specific_function():
    code = '''
def foo(n):
    for i in range(n):
        print(i)

def bar(n):
    for i in range(n):
        for j in range(n):
            print(i, j)
'''
    result = analyze(code, target='function:bar')
    assert result.name == 'bar'
    assert 'O(n^2)' in result.complexity.overall