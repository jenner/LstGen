# coding: utf-8
"""
Base code generators module
"""
from .php import PhpGenerator
from .python import PythonGenerator
from .go import GoGenerator
from .java import JavaGenerator
from .javascript import JavascriptGenerator

__all__ = [
    'PhpGenerator',
    'PythonGenerator',
    'GoGenerator',
    'JavaGenerator',
    'JavascriptGenerator'
]

GENERATORS = {
    'php': PhpGenerator,
    'python': PythonGenerator,
    'go': GoGenerator,
    'java': JavaGenerator,
    'javascript': JavascriptGenerator
}
