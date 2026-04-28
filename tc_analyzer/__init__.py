# tc_analyzer/__init__.py
from .models import ComplexityResult, LineContribution, FunctionAnalysis, FileAnalysis
from .analyzer import analyze

__version__ = "0.1.0"
__all__ = ['analyze', 'ComplexityResult', 'LineContribution', 'FunctionAnalysis', 'FileAnalysis']