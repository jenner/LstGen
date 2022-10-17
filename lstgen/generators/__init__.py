# coding: utf-8
"""
Base code generators module
"""
from .php import PhpGenerator
from .python import PythonGenerator
from .golang import GoLangGenerator
from .java import JavaGenerator
from .javascript import JavascriptGenerator

__all__ = [
    'PhpGenerator',
    'PythonGenerator',
    'GoLangGenerator',
    'JavaGenerator',
    'JavascriptGenerator'
]

GENERATORS = {
    'php': PhpGenerator,
    'python': PythonGenerator,
    'golang': GoLangGenerator,
    'java': JavaGenerator,
    'javascript': JavascriptGenerator
}
