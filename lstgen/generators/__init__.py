# coding: utf-8
"""
Base code generators module
"""
from .php import PhpGenerator
from .python import PythonGenerator
from .java import JavaGenerator
from .javascript import JavascriptGenerator

__all__ = ['PhpGenerator', 'PythonGenerator', 'JavaGenerator', 'JavascriptGenerator']

GENERATORS = {
    'php': PhpGenerator,
    'python': PythonGenerator,
    'java': JavaGenerator,
    'javascript': JavascriptGenerator
}
