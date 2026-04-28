# tc_analyzer/models.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class ComplexityResult:
    """Represents the complexity analysis result."""
    overall: str           # 'O(n)', 'O(n^2)', 'O(n log n)'
    confidence: float      # 0.0 - 1.0
    explanation: str       # Human-readable explanation
    derivation: str = ''   # Detailed mathematical derivation

@dataclass
class LineContribution:
    """Represents a single line's contribution to complexity."""
    line_number: int
    code: str
    contribution: str      # 'loop', 'nested_loop', 'recursion', 'builtin', 'ds_operation', 'constant'
    complexity_impact: str # 'O(n)', 'O(1)', 'O(n log n)', etc.
    derivation: str = ''   # Why this line has this complexity

@dataclass
class FunctionAnalysis:
    """Analysis result for a single function."""
    name: str
    complexity: ComplexityResult
    lines: List[LineContribution] = field(default_factory=list)
    loops: int = 0
    recursion: bool = False
    algorithm_type: str = 'unknown'  # 'sorting', 'search', 'dp', 'unknown'

    def report(self) -> str:
        """Generate a detailed analysis report."""
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"Complexity Analysis Report: {self.name}")
        lines.append(f"{'='*60}")
        lines.append(f"\nOverall Complexity: {self.complexity.overall}")
        lines.append(f"Confidence: {self.complexity.confidence:.1%}")
        lines.append(f"Algorithm Type: {self.algorithm_type}")
        lines.append(f"Loops: {self.loops} nested level(s)")
        lines.append(f"Recursion: {self.recursion}")
        lines.append(f"\n{'='*60}")
        lines.append("Derivation:")
        lines.append(f"{'='*60}")
        lines.append(self.complexity.derivation)
        lines.append(f"\n{'='*60}")
        lines.append("Line-by-Line Analysis:")
        lines.append(f"{'='*60}")

        for line in self.lines:
            if line.contribution != 'constant':
                lines.append(f"\nLine {line.line_number}: {line.code}")
                lines.append(f"  Contribution: {line.contribution}")
                lines.append(f"  Complexity: {line.complexity_impact}")
                if line.derivation:
                    lines.append(f"  Reason: {line.derivation}")

        lines.append(f"\n{'='*60}")
        lines.append("Summary:")
        lines.append(f"{'='*60}")
        lines.append(f"Final Result: {self.complexity.overall}")

        return '\n'.join(lines)

@dataclass
class FileAnalysis:
    """Analysis result for a file/module."""
    functions: List[FunctionAnalysis] = field(default_factory=list)
    overall: str = 'O(1)'

    def report(self) -> str:
        """Generate a detailed analysis report for all functions."""
        if len(self.functions) == 1:
            return self.functions[0].report()

        lines = []
        lines.append(f"{'='*60}")
        lines.append("Complexity Analysis Report")
        lines.append(f"{'='*60}")
        lines.append(f"\nOverall Complexity: {self.overall}")

        for func in self.functions:
            lines.append(f"\n{func.report()}")

        return '\n'.join(lines)