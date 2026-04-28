# tests/test_patterns.py
from tc_analyzer import analyze

def test_quick_sort_pattern():
    code = '''
def quick_sort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)
'''
    result = analyze(code)
    assert result.functions[0].algorithm_type == 'sorting'

def test_binary_search_pattern():
    code = '''
def binary_search(arr, low, high, x):
    if high >= low:
        mid = (low + high) // 2
        if arr[mid] == x:
            return mid
        if arr[mid] > x:
            return binary_search(arr, low, mid - 1, x)
        return binary_search(arr, mid + 1, high, x)
    return -1
'''
    result = analyze(code)
    assert result.functions[0].algorithm_type == 'search'