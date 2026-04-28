# tests/test_models.py
from tc_analyzer.models import ComplexityResult, LineContribution, FunctionAnalysis, FileAnalysis

def test_complexity_result_creation():
    result = ComplexityResult(overall='O(n)', confidence=0.9, explanation='Single loop')
    assert result.overall == 'O(n)'
    assert result.confidence == 0.9
    assert result.explanation == 'Single loop'

def test_line_contribution_creation():
    line = LineContribution(line_number=5, code='for i in range(n):', contribution='loop', complexity_impact='O(n)')
    assert line.line_number == 5
    assert line.contribution == 'loop'

def test_function_analysis_creation():
    func = FunctionAnalysis(
        name='foo',
        complexity=ComplexityResult(overall='O(n)', confidence=0.9, explanation='test'),
        lines=[],
        loops=1,
        recursion=False,
        algorithm_type='unknown'
    )
    assert func.name == 'foo'
    assert func.loops == 1

def test_file_analysis_creation():
    file = FileAnalysis(functions=[], overall='O(1)')
    assert file.overall == 'O(1)'