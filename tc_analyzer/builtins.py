# tc_analyzer/builtins.py
"""Built-in function complexity mappings."""

BUILTIN_COMPLEXITY = {
    # Sorting - O(n log n)
    'sorted': 'O(n log n)',
    'sort': 'O(n log n)',

    # Linear operations - O(n)
    'max': 'O(n)',
    'min': 'O(n)',
    'sum': 'O(n)',
    'any': 'O(n)',
    'all': 'O(n)',
    'list': 'O(n)',
    'set': 'O(n)',
    'tuple': 'O(n)',
    'dict': 'O(n)',
    'frozenset': 'O(n)',
    'enumerate': 'O(n)',  # iteration
    'zip': 'O(n)',
    'map': 'O(n)',        # iteration
    'filter': 'O(n)',     # iteration
    'reversed': 'O(n)',   # iteration
    'join': 'O(n)',       # string

    # Constant - O(1)
    'len': 'O(1)',
    'abs': 'O(1)',
    'round': 'O(1)',
    'int': 'O(1)',
    'float': 'O(1)',
    'str': 'O(1)',
    'bool': 'O(1)',
    'chr': 'O(1)',
    'ord': 'O(1)',
    'hex': 'O(1)',
    'bin': 'O(1)',
    'oct': 'O(1)',
    'type': 'O(1)',
    'id': 'O(1)',
    'hash': 'O(1)',
    'isinstance': 'O(1)',
    'issubclass': 'O(1)',
    'callable': 'O(1)',
    'hasattr': 'O(1)',
    'getattr': 'O(1)',
    'setattr': 'O(1)',
    'delattr': 'O(1)',
    'globals': 'O(1)',
    'locals': 'O(1)',
    'vars': 'O(1)',
    'dir': 'O(1)',
    'range': 'O(1)',  # creation is O(1), iteration is O(n)
    'print': 'O(1)',

    # Higher complexity
    'pow': 'O(log n)',  # exponentiation by squaring
}

# NumPy operations complexity
# These are accessed via module.attribute (e.g., np.sum, np.dot)
# For matrices, use O(nk) to indicate total element count
NUMPY_COMPLEXITY = {
    # Element-wise operations - O(nk) for matrices (遍历所有元素)
    'sum': 'O(nk)',
    'mean': 'O(nk)',
    'std': 'O(nk)',
    'var': 'O(nk)',
    'max': 'O(nk)',
    'min': 'O(nk)',
    'prod': 'O(nk)',
    'cumsum': 'O(nk)',
    'cumprod': 'O(nk)',
    'argmax': 'O(nk)',
    'argmin': 'O(nk)',
    'abs': 'O(nk)',
    'sqrt': 'O(nk)',
    'exp': 'O(nk)',
    'log': 'O(nk)',
    'sin': 'O(nk)',
    'cos': 'O(nk)',
    'tan': 'O(nk)',
    'arcsin': 'O(nk)',
    'arccos': 'O(nk)',
    'arctan': 'O(nk)',
    'floor': 'O(nk)',
    'ceil': 'O(nk)',
    'round': 'O(nk)',
    'power': 'O(nk)',
    'square': 'O(nk)',
    'reshape': 'O(1)',  # just changes view
    'transpose': 'O(1)',
    'flatten': 'O(nk)',
    'ravel': 'O(nk)',
    'copy': 'O(nk)',
    'concatenate': 'O(nk)',
    'stack': 'O(nk)',
    'vstack': 'O(nk)',
    'hstack': 'O(nk)',
    'split': 'O(nk)',
    'array': 'O(nk)',
    'asarray': 'O(nk)',
    'zeros': 'O(nk)',
    'ones': 'O(nk)',
    'empty': 'O(nk)',
    'full': 'O(nk)',
    'arange': 'O(n)',
    'linspace': 'O(n)',
    'where': 'O(nk)',
    'clip': 'O(nk)',
    'take': 'O(nk)',
    'put': 'O(nk)',
    'fill': 'O(nk)',
    'sort': 'O(nk log nk)',
    'argsort': 'O(nk log nk)',
    'searchsorted': 'O(log n)',
    'unique': 'O(nk log nk)',
    'in1d': 'O(nk log nk)',
    'intersect1d': 'O(nk log nk)',
    'setdiff1d': 'O(nk log nk)',
    'union1d': 'O(nk log nk)',
    # Matrix operations - O(nk) for (n, k) matrix, or O(n^2) for (n, n)
    'dot': 'O(nk)',        # matrix multiplication
    'matmul': 'O(nk)',
    'inner': 'O(nk)',
    'outer': 'O(nk)',
    'tensordot': 'O(nk)',
    'einsum': 'O(nk)',
    # Linear algebra - O(n^3) for matrix operations
    'inv': 'O(n^3)',
    'linalg.inv': 'O(n^3)',
    'det': 'O(n^3)',
    'linalg.det': 'O(n^3)',
    'eig': 'O(n^3)',
    'linalg.eig': 'O(n^3)',
    'eigh': 'O(n^3)',
    'linalg.eigh': 'O(n^3)',
    'svd': 'O(n^3)',
    'linalg.svd': 'O(n^3)',
    'solve': 'O(n^3)',
    'linalg.solve': 'O(n^3)',
    'lstsq': 'O(n^3)',
    'linalg.lstsq': 'O(n^3)',
    'norm': 'O(nk)',
    'linalg.norm': 'O(nk)',
    # FFT - O(n log n)
    'fft': 'O(n log n)',
    'fft.fft': 'O(n log n)',
    'fft.ifft': 'O(n log n)',
    'fft.fft2': 'O(nk log nk)',
    'fft.ifft2': 'O(nk log nk)',
}

# Common aliases for numpy
NUMPY_ALIAS = {'np', 'numpy'}

def get_builtin_complexity(name: str) -> str:
    """Get complexity for a built-in function."""
    return BUILTIN_COMPLEXITY.get(name, 'O(1)')

def is_builtin(name: str) -> bool:
    """Check if name is a known built-in."""
    return name in BUILTIN_COMPLEXITY

def get_numpy_complexity(attr_name: str) -> str:
    """Get complexity for a numpy function."""
    return NUMPY_COMPLEXITY.get(attr_name, 'O(n)')

def is_numpy_call(module_name: str, attr_name: str) -> bool:
    """Check if this is a numpy module call (e.g., np.sum)."""
    return module_name in NUMPY_ALIAS and attr_name in NUMPY_COMPLEXITY