# tc_analyzer/analyzer.py
from .models import FileAnalysis, FunctionAnalysis, ComplexityResult, LineContribution
from .builtins import get_builtin_complexity, is_builtin, get_numpy_complexity, is_numpy_call, NUMPY_COMPLEXITY
from .datastructures import detect_ds_operation, DS_COMPLEXITY
from .patterns import detect_algorithm_type
import ast
import re

def analyze(source: str, target: str = None):
    """
    Analyze time complexity of Python code.

    Args:
        source: Code string or file path
        target: Optional target specification
                'function:name' - analyze specific function
                None - analyze all

    Returns:
        FileAnalysis or FunctionAnalysis
    """
    # Determine if source is file path or code string
    if source.endswith('.py') and len(source) < 200:
        # Likely a file path
        try:
            with open(source, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            code = source  # Treat as code string
    else:
        code = source

    # Parse the code
    tree = ast.parse(code)

    # Analyze all functions
    functions = _analyze_functions(tree, code)

    # Handle target specification
    if target and target.startswith('function:'):
        func_name = target.split(':')[1]
        for func in functions:
            if func.name == func_name:
                return func
        return None

    # Determine overall complexity
    if functions:
        overall = max((f.complexity.overall for f in functions), key=_complexity_order)
    else:
        overall = 'O(1)'

    return FileAnalysis(functions=functions, overall=overall)

def _analyze_functions(tree, code):
    """Analyze all function definitions in the AST."""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_analysis = _analyze_single_function(node, code)
            functions.append(func_analysis)

    # If no functions found, analyze module-level code
    if not functions:
        module_analysis = _analyze_module_level(tree, code)
        if module_analysis:
            functions.append(module_analysis)

    return functions

def _analyze_module_level(tree, code):
    """Analyze module-level code (code without function definitions)."""
    # Check if there's any meaningful code at module level
    has_loops = False
    has_calls = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.For, ast.While)):
            has_loops = True
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            has_calls = True
        if isinstance(node, ast.Assign):
            has_calls = True  # Assignment might involve complex operations

    if not has_loops and not has_calls:
        return None

    loops = _count_loops(tree)
    operations = _detect_all_operations(tree)
    # Only consider builtin/numpy/ds operations, not loops (loops are counted separately)
    builtin_ops = [op for op in operations if op['type'] in ('builtin', 'numpy', 'ds_operation')]
    builtin_complexity = max((op['complexity'] for op in builtin_ops), key=_complexity_order) if builtin_ops else 'O(1)'

    complexity_str = _combine_complexities(_compute_complexity_from_loops(loops), builtin_complexity)
    explanation = _build_explanation(loops, builtin_complexity)
    derivation = _build_derivation(loops, operations, complexity_str)

    return FunctionAnalysis(
        name='<module>',
        complexity=ComplexityResult(
            overall=complexity_str,
            confidence=0.9 if loops > 0 or builtin_complexity != 'O(1)' else 0.5,
            explanation=explanation,
            derivation=derivation
        ),
        lines=_extract_module_line_contributions(tree, code),
        loops=loops,
        recursion=False,
        algorithm_type='unknown'
    )

def _analyze_single_function(node, code):
    """Analyze a single function's complexity."""
    loops = _count_loops(node)
    operations = _detect_all_operations(node)
    # Only consider builtin/numpy/ds operations, not loops (loops are counted separately)
    builtin_ops = [op for op in operations if op['type'] in ('builtin', 'numpy', 'ds_operation')]
    builtin_complexity = max((op['complexity'] for op in builtin_ops), key=_complexity_order) if builtin_ops else 'O(1)'
    recursion = _detect_recursion(node)
    algorithm_type = detect_algorithm_type(node)

    # Analyze recursion complexity if present
    if recursion:
        recursion_complexity, recursion_derivation = _analyze_recursion_complexity(node)
        complexity_str = recursion_complexity
        explanation = f'recursive function with {recursion_complexity} complexity'
        derivation = recursion_derivation
    else:
        # Combine loop and builtin complexity
        complexity_str = _combine_complexities(_compute_complexity_from_loops(loops), builtin_complexity)
        explanation = _build_explanation(loops, builtin_complexity)
        derivation = _build_derivation(loops, operations, complexity_str)

    return FunctionAnalysis(
        name=node.name,
        complexity=ComplexityResult(
            overall=complexity_str,
            confidence=0.9 if loops > 0 or recursion or builtin_complexity != 'O(1)' else 0.5,
            explanation=explanation,
            derivation=derivation
        ),
        lines=_extract_line_contributions(node, code),
        loops=loops,
        recursion=recursion,
        algorithm_type=algorithm_type
    )

def _detect_all_operations(node):
    """Detect all operations with their complexity details."""
    operations = []

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            # Check built-in (direct function call like sum(arr))
            if isinstance(child.func, ast.Name) and is_builtin(child.func.id):
                complexity = get_builtin_complexity(child.func.id)
                operations.append({
                    'type': 'builtin',
                    'name': child.func.id,
                    'complexity': complexity,
                    'reason': f"Python built-in function '{child.func.id}' has complexity {complexity}"
                })

            # Check numpy/module call (like np.sum, np.dot)
            if isinstance(child.func, ast.Attribute):
                if isinstance(child.func.value, ast.Name):
                    module_name = child.func.value.id
                    attr_name = child.func.attr
                    if is_numpy_call(module_name, attr_name):
                        complexity = get_numpy_complexity(attr_name)
                        reason = _get_numpy_reason(attr_name, complexity)
                        operations.append({
                            'type': 'numpy',
                            'name': f"{module_name}.{attr_name}",
                            'complexity': complexity,
                            'reason': reason
                        })

            # Check data structure operation
            ds_result = detect_ds_operation_detail(child)
            if ds_result:
                operations.append(ds_result)

    # Check loops
    loop_depths = _get_loop_depths(node)
    for depth in loop_depths:
        operations.append({
            'type': 'loop',
            'name': f'nested_loop_depth_{depth}',
            'complexity': _compute_complexity_from_loops(depth),
            'reason': f"{depth} nested loop(s), each iterating O(n) times"
        })

    return operations

def _get_numpy_reason(attr_name, complexity):
    """Generate detailed reason for numpy operation complexity."""
    reasons = {
        'sum': f"np.sum 遍历数组所有元素，每个元素执行 O(1) 加法，总计 {complexity}",
        'mean': f"np.mean 需要先求和 {complexity} 再除以元素数 O(1)，总计 {complexity}",
        'dot': f"np.dot 矩阵乘法，对于 (n,k) 和 (k,m) 矩阵，执行 n×k×m 乘法和加法，总计 {complexity}",
        'matmul': f"np.matmul 矩阵乘法，同 np.dot，总计 {complexity}",
        'sort': f"np.sort 使用高效排序算法，时间复杂度 {complexity}",
        'argsort': f"np.argsort 返回排序索引，内部使用排序，时间复杂度 {complexity}",
        'reshape': f"np.reshape 只改变数组视图，不复制数据，时间复杂度 {complexity}",
        'transpose': f"np.transpose 只改变轴顺序，不复制数据，时间复杂度 {complexity}",
        'inv': f"np.linalg.inv 矩阵求逆，使用 LU 分解等算法，时间复杂度 {complexity}",
        'svd': f"np.linalg.svd 奇异值分解，时间复杂度 {complexity}",
        'fft': f"np.fft 快速傅里叶变换，使用分治算法，时间复杂度 {complexity}",
        'sqrt': f"np.sqrt 对每个元素执行开方运算 O(1)，遍历所有元素，总计 {complexity}",
        'exp': f"np.exp 对每个元素执行指数运算 O(1)，遍历所有元素，总计 {complexity}",
        'log': f"np.log 对每个元素执行对数运算 O(1)，遍历所有元素，总计 {complexity}",
        'square': f"np.square 对每个元素执行平方运算 O(1)，遍历所有元素，总计 {complexity}",
        'abs': f"np.abs 对每个元素取绝对值 O(1)，遍历所有元素，总计 {complexity}",
        'max': f"np.max 需要遍历所有元素比较，总计 {complexity}",
        'min': f"np.min 需要遍历所有元素比较，总计 {complexity}",
        'argmax': f"np.argmax 需要遍历所有元素找最大值索引，总计 {complexity}",
        'argmin': f"np.argmin 需要遍历所有元素找最小值索引，总计 {complexity}",
    }
    return reasons.get(attr_name, f"numpy.{attr_name} 操作，时间复杂度 {complexity}")

def detect_ds_operation_detail(node):
    """Detect data structure operation with detailed info."""
    if not isinstance(node, ast.Call):
        return None

    # Method call like lst.append(x)
    if isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            var_name = node.func.value.id
            method_name = node.func.attr
            key = ('list', method_name)  # Simplified - assume list

            if key in DS_COMPLEXITY:
                complexity = DS_COMPLEXITY[key]
                return {
                    'type': 'ds_operation',
                    'name': f"{var_name}.{method_name}",
                    'complexity': complexity,
                    'reason': f"列表方法 '{method_name}' 操作，复杂度 {complexity}"
                }

    return None

def _get_loop_depths(node):
    """Get all loop nesting depths in the code."""
    depths = set()

    def visit(node, depth=0):
        if isinstance(node, (ast.For, ast.While)):
            depth += 1
            depths.add(depth)
        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    visit(node)
    return sorted(depths)

def _build_derivation(loops, operations, final_complexity):
    """Build detailed mathematical derivation."""
    lines = []

    lines.append("Step-by-step derivation:")
    lines.append("")

    # Sort operations by complexity order
    sorted_ops = sorted(operations, key=lambda x: _complexity_order(x['complexity']), reverse=True)

    if not sorted_ops:
        lines.append("No complexity-generating operations detected.")
        lines.append("All operations are O(1) constant time.")
        lines.append(f"\nConclusion: T(n) = O(1)")
        return '\n'.join(lines)

    # List each operation
    lines.append("Operations found:")
    for i, op in enumerate(sorted_ops, 1):
        lines.append(f"  {i}. {op['name']}: {op['complexity']}")
        lines.append(f"     → {op['reason']}")

    lines.append("")

    # Mathematical derivation
    lines.append("Complexity calculation:")

    # Get the dominant operations
    max_ops = [op for op in sorted_ops if op['complexity'] == sorted_ops[0]['complexity']]

    if loops > 0:
        loop_complexity = _compute_complexity_from_loops(loops)
        builtin_ops = [op for op in sorted_ops if op['type'] in ('builtin', 'numpy', 'ds_operation')]

        if builtin_ops:
            highest_builtin = builtin_ops[0]['complexity']
            combined = _combine_complexities(loop_complexity, highest_builtin)

            lines.append(f"  • Loop structure: {loops} nested levels → {loop_complexity}")
            lines.append(f"  • Built-in/Library calls: highest is {highest_builtin}")

            if combined == highest_builtin and _complexity_order(highest_builtin) > _complexity_order(loop_complexity):
                lines.append(f"  • Since {highest_builtin} > {loop_complexity}, the builtin dominates")
            elif loop_complexity == 'O(n)' and highest_builtin == 'O(n)':
                lines.append(f"  • Loop O(n) × Builtin O(n) = O(n × n) = O(n²)")
            elif loop_complexity == 'O(n)' and highest_builtin == 'O(n log n)':
                lines.append(f"  • Loop O(n) × Builtin O(n log n) = O(n log n)")
            else:
                lines.append(f"  • Combined: {combined}")
        else:
            lines.append(f"  • Only loop structure: {loops} nested levels")
            lines.append(f"  • Each level contributes O(n) iterations")
            lines.append(f"  • T(n) = n × n × ... × n ({loops} times) = {loop_complexity}")

    else:
        # No loops, just operations
        dominant = sorted_ops[0]
        lines.append(f"  • No loop structure detected")
        lines.append(f"  • Dominant operation: {dominant['name']} with {dominant['complexity']}")

    lines.append("")
    lines.append(f"Final Result: T(n) = {final_complexity}")

    return '\n'.join(lines)

def _count_loops(node):
    """Count maximum nesting depth of loops."""
    max_depth = 0

    def visit(node, depth=0):
        nonlocal max_depth
        if isinstance(node, (ast.For, ast.While)):
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    visit(node)
    return max_depth

def _compute_complexity_from_loops(loops):
    """Convert loop count to Big-O notation."""
    if loops == 0:
        return 'O(1)'
    elif loops == 1:
        return 'O(n)'
    elif loops == 2:
        return 'O(n^2)'
    elif loops == 3:
        return 'O(n^3)'
    else:
        return f'O(n^{loops})'

def _extract_line_contributions(node, code):
    """Extract line-by-line contributions."""
    lines = code.split('\n')

    # Handle module-level code (no lineno)
    if not hasattr(node, 'lineno') or node.lineno is None:
        return _extract_module_line_contributions(node, code)

    contributions = []
    for i, line in enumerate(lines[node.lineno - 1: node.end_lineno], start=node.lineno):
        stripped = line.strip()
        line_ops = _detect_line_operations(line, i)

        if stripped.startswith('for ') or stripped.startswith('while '):
            depth = _get_line_loop_depth(node, i)
            contributions.append(LineContribution(
                line_number=i,
                code=stripped,
                contribution='loop',
                complexity_impact='O(n)',
                derivation=f"Loop iteration, adds one O(n) factor (nesting depth: {depth})"
            ))
        elif line_ops:
            # Line has operations
            for op in line_ops:
                contributions.append(LineContribution(
                    line_number=i,
                    code=stripped,
                    contribution=op['type'],
                    complexity_impact=op['complexity'],
                    derivation=op['reason']
                ))
        elif stripped and not stripped.startswith('#') and not stripped.startswith('def '):
            contributions.append(LineContribution(
                line_number=i,
                code=stripped,
                contribution='constant',
                complexity_impact='O(1)',
                derivation='Basic operation with constant time'
            ))

    return contributions

def _detect_line_operations(line_text, line_num):
    """Detect operations in a single line of code."""
    operations = []
    try:
        line_ast = ast.parse(line_text)
        for node in ast.walk(line_ast):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and is_builtin(node.func.id):
                    complexity = get_builtin_complexity(node.func.id)
                    operations.append({
                        'type': 'builtin',
                        'name': node.func.id,
                        'complexity': complexity,
                        'reason': f"Built-in '{node.func.id}' has {complexity}"
                    })
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        module_name = node.func.value.id
                        attr_name = node.func.attr
                        if is_numpy_call(module_name, attr_name):
                            complexity = get_numpy_complexity(attr_name)
                            reason = _get_numpy_reason(attr_name, complexity)
                            operations.append({
                                'type': 'numpy',
                                'name': f"{module_name}.{attr_name}",
                                'complexity': complexity,
                                'reason': reason
                            })
    except:
        pass
    return operations

def _get_line_loop_depth(node, line_num):
    """Get loop depth for a specific line."""
    depth = 0
    target_line = None

    def find_line(n, current_depth=0):
        if isinstance(n, (ast.For, ast.While)):
            current_depth += 1
            if hasattr(n, 'lineno') and n.lineno == line_num:
                target_line = current_depth
        for child in ast.iter_child_nodes(n):
            find_line(child, current_depth)

    find_line(node)
    return target_line or 1

def _extract_module_line_contributions(tree, code):
    """Extract line-by-line contributions for module-level code."""
    lines = code.split('\n')
    contributions = []

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        line_ops = _detect_line_operations(line, i)

        if stripped.startswith('for ') or stripped.startswith('while '):
            contributions.append(LineContribution(
                line_number=i,
                code=stripped,
                contribution='loop',
                complexity_impact='O(n)',
                derivation="Loop iteration, adds one O(n) factor"
            ))
        elif line_ops:
            for op in line_ops:
                contributions.append(LineContribution(
                    line_number=i,
                    code=stripped,
                    contribution=op['type'],
                    complexity_impact=op['complexity'],
                    derivation=op['reason']
                ))
        elif stripped and not stripped.startswith('#') and not stripped.startswith('def '):
            contributions.append(LineContribution(
                line_number=i,
                code=stripped,
                contribution='constant',
                complexity_impact='O(1)',
                derivation='Basic operation with constant time'
            ))

    return contributions

def _complexity_order(complexity_str):
    """Return numeric order for complexity comparison."""
    order = {
        'O(1)': 0,
        'O(log n)': 1,
        'O(n)': 2,
        'O(nk)': 2.5,  # Between O(n) and O(n log n), depends on dimensions
        'O(n log n)': 3,
        'O(nk log nk)': 3.5,  # FFT on 2D matrix
        'O(n^2)': 4,
        'O(n^3)': 5,
        'O(2^n)': 6,
        'O(n!)': 7
    }
    return order.get(complexity_str, 0)

def _detect_builtin_complexity(node):
    """Detect highest complexity built-in or DS call in function."""
    max_complexity = 'O(1)'

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            # Check built-in (direct function call like sum(arr))
            if isinstance(child.func, ast.Name) and is_builtin(child.func.id):
                complexity = get_builtin_complexity(child.func.id)
                if _complexity_order(complexity) > _complexity_order(max_complexity):
                    max_complexity = complexity

            # Check numpy/module call (like np.sum, np.dot)
            if isinstance(child.func, ast.Attribute):
                # Get module name and attribute name
                if isinstance(child.func.value, ast.Name):
                    module_name = child.func.value.id
                    attr_name = child.func.attr
                    if is_numpy_call(module_name, attr_name):
                        complexity = get_numpy_complexity(attr_name)
                        if _complexity_order(complexity) > _complexity_order(max_complexity):
                            max_complexity = complexity

            # Check data structure operation
            ds_complexity = detect_ds_operation(child)
            if ds_complexity and _complexity_order(ds_complexity) > _complexity_order(max_complexity):
                max_complexity = ds_complexity

    return max_complexity

def _combine_complexities(loop_complexity, builtin_complexity):
    """Combine loop and builtin complexity."""
    loop_order = _complexity_order(loop_complexity)
    builtin_order = _complexity_order(builtin_complexity)

    # If builtin is more complex, it dominates
    if builtin_order > loop_order:
        return builtin_complexity

    # Loop O(n) with builtin O(n log n) -> O(n log n)
    if loop_complexity == 'O(n)' and builtin_complexity == 'O(n log n)':
        return 'O(n log n)'

    # Loop O(n) with builtin O(n) -> O(n^2)
    if loop_complexity == 'O(n)' and builtin_complexity == 'O(n)':
        return 'O(n^2)'

    # Loop O(n) with builtin O(nk) -> O(nk) (nk typically larger than n)
    if loop_complexity == 'O(n)' and builtin_complexity == 'O(nk)':
        return 'O(nk)'

    # Loop O(n^k) with builtin O(n log n) or O(n)
    if loop_complexity.startswith('O(n^'):
        # Extract power: O(n^2) -> 2
        match = re.search(r'O\(n\^(\d+)\)', loop_complexity)
        if match:
            power = int(match.group(1))
            if builtin_complexity == 'O(n log n)':
                return f'O(n^{power} log n)'
            elif builtin_complexity == 'O(n)':
                return f'O(n^{power + 1})'

    return loop_complexity if loop_order >= builtin_order else builtin_complexity

def _build_explanation(loops, builtin_complexity):
    """Build human-readable explanation."""
    parts = []
    if loops > 0:
        parts.append(f'{loops} nested loop(s)')
    if builtin_complexity != 'O(1)':
        parts.append(f'built-in function with {builtin_complexity}')
    return ' and '.join(parts) if parts else 'no complexity factors detected'

def _detect_recursion(node):
    """Detect if function calls itself."""
    func_name = node.name
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id == func_name:
                return True
    return False

def _count_recursive_calls(node):
    """Count number of recursive calls in function."""
    func_name = node.name
    count = 0
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id == func_name:
                count += 1
    return count

def _analyze_recursion_complexity(node):
    """Analyze recursion complexity pattern."""
    call_count = _count_recursive_calls(node)

    # Check for divide-by-2 pattern
    divides_by_two = False
    for child in ast.walk(node):
        if isinstance(child, ast.BinOp):
            if isinstance(child.op, (ast.Div, ast.FloorDiv)):
                # Check if dividing by 2
                if isinstance(child.right, ast.Constant) and child.right.value == 2:
                    divides_by_two = True

    # Build derivation
    derivation_lines = []
    derivation_lines.append("Recursion analysis:")
    derivation_lines.append(f"  • Number of recursive calls per invocation: {call_count}")

    # Determine complexity
    if call_count == 0:
        derivation_lines.append("  • No recursive calls found")
        derivation_lines.append(f"\nConclusion: T(n) = O(1)")
        return 'O(1)', '\n'.join(derivation_lines)
    elif call_count == 1:
        if divides_by_two:
            derivation_lines.append("  • Problem size reduced by half each call (n → n/2)")
            derivation_lines.append("  • Recurrence: T(n) = T(n/2) + O(1)")
            derivation_lines.append("  • Solution: T(n) = O(log n)")
            derivation_lines.append(f"\nConclusion: T(n) = O(log n)")
            return 'O(log n)', '\n'.join(derivation_lines)
        else:
            derivation_lines.append("  • Problem size reduced by constant (n → n-1)")
            derivation_lines.append("  • Recurrence: T(n) = T(n-1) + O(1)")
            derivation_lines.append("  • Solution: T(n) = n × O(1) = O(n)")
            derivation_lines.append(f"\nConclusion: T(n) = O(n)")
            return 'O(n)', '\n'.join(derivation_lines)  # Linear recursion (n-1 pattern)
    elif call_count == 2:
        if divides_by_two:
            derivation_lines.append("  • Two recursive calls with problem size halved")
            derivation_lines.append("  • Recurrence: T(n) = 2T(n/2) + O(1)")
            derivation_lines.append("  • By Master Theorem: T(n) = O(n)")
            derivation_lines.append(f"\nConclusion: T(n) = O(n)")
            return 'O(n)', '\n'.join(derivation_lines)  # T(n) = 2T(n/2) + O(1)
        else:
            derivation_lines.append("  • Two recursive calls with problem size reduced by 1")
            derivation_lines.append("  • Recurrence: T(n) = 2T(n-1) + O(1)")
            derivation_lines.append("  • This is exponential: T(n) = O(2^n)")
            derivation_lines.append(f"\nConclusion: T(n) = O(2^n)")
            return 'O(2^n)', '\n'.join(derivation_lines)  # T(n) = 2T(n-1) exponential
    else:
        derivation_lines.append(f"  • {call_count} recursive calls (branching factor)")
        derivation_lines.append(f"  • Recurrence: T(n) = {call_count}T(n-1) + O(1)")
        derivation_lines.append(f"  • This is exponential: T(n) = O({call_count}^n)")
        derivation_lines.append(f"\nConclusion: T(n) = O({call_count}^n)")
        return f'O({call_count}^n)', '\n'.join(derivation_lines)  # k recursive calls, exponential