# coding: utf-8
"""
Base code generators module
"""
from .php import PhpGenerator
from .python import PythonGenerator
from .go import GoGenerator
from .golang import GoLangGenerator
from .java import JavaGenerator
from .javascript import JavascriptGenerator

__all__ = [
    'PhpGenerator',
    'PythonGenerator',
    'GoGenerator',
    'GoLangGenerator',
    'JavaGenerator',
    'JavascriptGenerator'
]

GENERATORS = {
    'php': PhpGenerator,
    'python': PythonGenerator,
    'go': GoGenerator,
    'golang': GoLangGenerator,
    'java': JavaGenerator,
    'javascript': JavascriptGenerator
}
