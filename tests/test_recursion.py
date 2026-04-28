# tests/test_recursion.py
from tc_analyzer import analyze

def test_simple_recursion():
    code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''
    result = analyze(code)
    assert result.functions[0].recursion == True
    assert 'O(n)' in result.functions[0].complexity.overall

def test_binary_recursion():
    code = '''
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
'''
    result = analyze(code)
    assert result.functions[0].recursion == True
    assert 'O(2^n)' in result.functions[0].complexity.overall or 'exponential' in result.functions[0].complexity.explanation.lower()

def test_divide_conquer():
    code = '''
def binary_search(arr, low, high, x):
    if high >= low:
        mid = (low + high) // 2
        if arr[mid] == x:
            return mid
        if arr[mid] > x:
            return binary_search(arr, low, mid-1, x)
        return binary_search(arr, mid+1, high, x)
    return -1
'''
    result = analyze(code)
    assert result.functions[0].recursion == True