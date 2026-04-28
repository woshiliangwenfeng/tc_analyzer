# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test file
pytest tests/test_analyzer.py

# Run specific test
pytest tests/test_analyzer.py::test_analyze_function
```

## Architecture

This is a Python library that analyzes time complexity of code via AST parsing. The main entry point is the `analyze()` function in `tc_analyzer/__init__.py`.

### Analysis Pipeline

1. **Entry** (`__init__.py`): `analyze(source, target)` accepts either a code string or file path
2. **AST Parsing** (`analyzer.py`): Parses code into AST, extracts all `FunctionDef` nodes
3. **Per-Function Analysis** (`analyzer.py:_analyze_single_function`):
   - Counts max loop nesting depth → O(n^k)
   - Detects recursive calls and classifies pattern (linear/divide-and-conquer/exponential)
   - Scans for built-in function calls with known complexity
   - Scans for data structure operations (list.append, dict.get, etc.)
4. **Complexity Combination** (`analyzer.py:_combine_complexities`): Merges loop + builtin + recursion complexities using polynomial arithmetic
5. **Pattern Recognition** (`patterns.py`): Classifies algorithm type by function name/keywords (sorting, search, dp, graph)

### Key Modules

| Module | Purpose |
|--------|---------|
| `analyzer.py` | Core AST traversal and complexity calculation |
| `builtins.py` | Complexity mappings for ~50 Python built-ins |
| `datastructures.py` | Complexity for list/dict/set/string operations |
| `patterns.py` | Algorithm type detection via naming heuristics |
| `models.py` | Result dataclasses (`ComplexityResult`, `FunctionAnalysis`, etc.) |

### Complexity Detection Strategy

The analyzer combines multiple signals in priority order:
1. **Recursion**: Detects self-calls and classifies by recursive pattern
2. **Loop nesting**: Maximum depth determines polynomial complexity
3. **Built-ins**: Looks up pre-defined complexity in `builtins.py` and `datastructures.py`

When multiple complexity sources exist, they're combined multiplicatively (e.g., O(n) loop containing O(n) builtin → O(n^2)).

### Extending Built-in Complexity

To add support for new built-in functions, edit `builtins.py`. The `BUILTIN_COMPLEXITY` dict maps function names to complexity strings like `"O(n)"` or `"O(n log n)"`.

### Testing

Tests are organized by feature:
- `test_analyzer.py` - Core analyzer functionality
- `test_recursion.py` - Recursion detection and classification
- `test_builtins.py` - Built-in function complexity
- `test_datastructures.py` - Data structure operations
- `test_patterns.py` - Algorithm pattern recognition
- `test_integration.py` - End-to-end scenarios