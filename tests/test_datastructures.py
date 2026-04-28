# tests/test_datastructures.py
from tc_analyzer import analyze

import ast

def test_list_append():
    code = '''
def add_item(lst, item):
    lst.append(item)
'''
    result = analyze(code)
    assert result.functions[0].complexity.overall == 'O(1)'

def test_list_insert():
    code = '''
def insert_item(lst, index, item):
    lst.insert(index, item)
'''
    result = analyze(code)
    assert 'O(n)' in result.functions[0].complexity.overall

def test_dict_get():
    code = '''
def lookup(d, key):
    return d.get(key)
'''
    result = analyze(code)
    assert result.functions[0].complexity.overall == 'O(1)'

def test_list_in_loop():
    code = '''
def process(lst):
    for item in lst:
        lst.insert(0, item)
'''
    result = analyze(code)
    assert 'O(n^2)' in result.functions[0].complexity.overall